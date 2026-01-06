"""
Upload Router - Handles CSV file upload and data ingestion
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import uuid

from database import get_db
from models import RawTransaction, CleanedTransaction
from services.ingestion import parse_csv_file, ingest_raw_data
from services.cleaning import clean_and_store_transactions, get_all_raw_transactions_for_cleaning
from services.transformation import run_full_transformation_pipeline
from services.feature_engineering import store_feature_engineering
from services.data_quality import store_quality_metrics, calculate_data_quality_percentage
from schemas import UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV file and process through the data pipeline
    
    Pipeline steps:
    1. Parse CSV file
    2. Ingest raw data
    3. Clean and validate data
    4. Transform and aggregate data
    
    Args:
        file: CSV file upload
        db: Database session
        
    Returns:
        UploadResponse with processing statistics
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Step 1: Parse CSV
        logger.info(f"Parsing CSV file: {file.filename}")
        transactions = parse_csv_file(file_content)
        
        if not transactions:
            raise HTTPException(status_code=400, detail="No transactions found in CSV")
        
        # Generate batch ID for tracking
        batch_id = f"batch_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        # Step 2: Ingest raw data
        logger.info("Ingesting raw transactions")
        records_processed, invalid_during_ingestion = ingest_raw_data(db, transactions)
        
        # Step 3: Get raw transactions for cleaning
        raw_transactions = db.query(RawTransaction).order_by(
            RawTransaction.id.desc()
        ).limit(records_processed).all()
        
        # Step 4: Clean and store cleaned transactions
        logger.info("Cleaning transactions")
        records_cleaned, duplicates_skipped, invalid_rows = clean_and_store_transactions(
            db, 
            list(reversed(raw_transactions))  # Process in original order
        )
        
        total_invalid = invalid_during_ingestion + invalid_rows
        
        # Step 5: Generate features for cleaned transactions
        logger.info("Generating ML features")
        cleaned_transactions = db.query(CleanedTransaction).order_by(
            CleanedTransaction.id.desc()
        ).limit(records_cleaned).all()
        features_generated = store_feature_engineering(db, list(reversed(cleaned_transactions)))
        
        # Step 6: Run transformation pipeline
        logger.info("Running transformation pipeline")
        transformation_results = run_full_transformation_pipeline(db)
        records_transformed = transformation_results.get("daily_summaries", 0) + \
                            transformation_results.get("customer_summaries", 0)
        
        # Step 7: Calculate and store data quality metrics
        dropped_records = total_invalid + duplicates_skipped
        data_quality_pct = calculate_data_quality_percentage(
            records_processed,
            total_invalid,
            duplicates_skipped
        )
        
        # Store metrics in database
        store_quality_metrics(
            db,
            batch_id,
            records_processed,
            total_invalid,
            duplicates_skipped,
            records_cleaned
        )
        
        logger.info(
            f"Upload complete - Total: {records_processed}, "
            f"Cleaned: {records_cleaned}, Dropped: {dropped_records}, "
            f"Quality: {data_quality_pct}%"
        )
        
        return UploadResponse(
            message="File uploaded and processed successfully",
            records_processed=records_processed,
            records_cleaned=records_cleaned,
            records_transformed=records_transformed,
            duplicates_skipped=duplicates_skipped,
            invalid_records=total_invalid,
            dropped_records=dropped_records,  # Added for frontend
            features_generated=features_generated,
            data_quality_percentage=data_quality_pct
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

