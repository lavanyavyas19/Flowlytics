"""
Ingestion Layer - Raw Data Ingestion Service
Handles CSV file parsing and initial data storage
"""

import csv
import io
from typing import List, Dict, Sequence
from sqlalchemy.orm import Session
from models import RawTransaction
import logging

logger = logging.getLogger(__name__)


def validate_csv_schema(header: Sequence[str] | None) -> bool:
    """
    Validate that CSV has required columns
    Supports both old format (basic) and new format (enhanced)
    
    Args:
        header: Sequence of column names from CSV (can be None)
        
    Returns:
        bool: True if schema is valid
    """
    if not header:
        raise ValueError("CSV header is empty or None")
    
    header_set = {col.strip().lower() for col in header}
    
    # Required columns (minimum set)
    required_columns = {"transaction_date", "customer_id", "product", "quantity", "price"}
    
    if not required_columns.issubset(header_set):
        missing = required_columns - header_set
        raise ValueError(f"Missing required columns: {missing}")
    
    # Optional columns (will be stored if present)
    optional_columns = {"transaction_id", "category", "payment_method", "city"}
    
    logger.info(f"CSV schema validated. Required columns: {required_columns}")
    logger.info(f"Optional columns found: {optional_columns.intersection(header_set)}")
    
    return True


def parse_csv_file(file_content: bytes) -> List[Dict[str, str]]:
    """
    Parse CSV file content into list of dictionaries
    
    Args:
        file_content: Raw bytes from uploaded file
        
    Returns:
        List of dictionaries with transaction data
    """
    try:
        # Decode bytes to string
        content = file_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        # Get header and validate schema
        header = csv_reader.fieldnames
        if not header:
            raise ValueError("CSV file is empty or has no header")
        
        validate_csv_schema(header)
        
        # Normalize column names (case-insensitive)
        normalized_header = {col: col.strip().lower() for col in header}
        
        # Parse rows
        transactions = []
        for row in csv_reader:
            normalized_row = {
                normalized_header[col]: value.strip() if value else ""
                for col, value in row.items()
            }
            transactions.append(normalized_row)
        
        logger.info(f"Parsed {len(transactions)} transactions from CSV")
        return transactions
        
    except Exception as e:
        logger.error(f"Error parsing CSV: {str(e)}")
        raise ValueError(f"Failed to parse CSV file: {str(e)}")


def ingest_raw_data(db: Session, transactions: List[Dict[str, str]]) -> tuple[int, int]:
    """
    Store raw transaction data in database
    Tracks invalid rows during ingestion
    
    Args:
        db: Database session
        transactions: List of transaction dictionaries
        
    Returns:
        Tuple of (records_ingested, invalid_rows_count)
    """
    try:
        records_ingested = 0
        invalid_rows = 0
        
        for idx, transaction in enumerate(transactions, start=1):
            try:
                # Validate required fields are present
                if not transaction.get("transaction_date") or not transaction.get("customer_id") or \
                   not transaction.get("product"):
                    logger.warning(f"Row {idx}: Missing required fields - skipping")
                    invalid_rows += 1
                    continue
                
                # Create raw transaction record (store all fields as strings)
                raw_transaction = RawTransaction(
                    transaction_id=transaction.get("transaction_id") or None,
                    transaction_date=transaction.get("transaction_date", ""),
                    customer_id=transaction.get("customer_id", ""),
                    product=transaction.get("product", ""),
                    category=transaction.get("category") or None,
                    quantity=transaction.get("quantity") or None,  # Can be None
                    price=transaction.get("price") or None,  # Can be None
                    payment_method=transaction.get("payment_method") or None,
                    city=transaction.get("city") or None
                )
                
                db.add(raw_transaction)
                records_ingested += 1
                
            except Exception as e:
                logger.warning(f"Row {idx}: Error ingesting - {str(e)}")
                invalid_rows += 1
                continue
        
        db.commit()
        logger.info(f"Ingested {records_ingested} raw transactions, {invalid_rows} invalid rows skipped")
        return records_ingested, invalid_rows
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting raw data: {str(e)}")
        raise


def get_all_raw_transactions(db: Session, limit: int = 1000):
    """
    Retrieve all raw transactions (for debugging/monitoring)
    
    Args:
        db: Database session
        limit: Maximum number of records to return
        
    Returns:
        List of RawTransaction objects
    """
    return db.query(RawTransaction).limit(limit).all()

