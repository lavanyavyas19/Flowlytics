"""
Data Quality Tracking Service
Tracks and reports data quality metrics throughout the pipeline
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from models import DataQualityMetrics
import logging

logger = logging.getLogger(__name__)


def calculate_data_quality_percentage(
    total_records: int,
    invalid_records: int,
    duplicate_records: int
) -> float:
    """
    Calculate data quality percentage
    
    Formula: (Cleaned Records / Total Records) * 100
    Where Cleaned Records = Total - Invalid - Duplicates
    
    Args:
        total_records: Total records ingested
        invalid_records: Number of invalid records
        duplicate_records: Number of duplicate records
        
    Returns:
        Data quality percentage (0-100)
    """
    if total_records == 0:
        return 0.0
    
    cleaned_records = total_records - invalid_records - duplicate_records
    quality_percentage = (cleaned_records / total_records) * 100.0
    
    return round(quality_percentage, 2)


def store_quality_metrics(
    db: Session,
    batch_id: str,
    total_records: int,
    invalid_records: int,
    duplicate_records: int,
    cleaned_records: int
) -> None:
    """
    Store data quality metrics for a batch
    
    Args:
        db: Database session
        batch_id: Unique batch identifier
        total_records: Total records ingested
        invalid_records: Number of invalid records
        duplicate_records: Number of duplicate records
        cleaned_records: Number of successfully cleaned records
    """
    try:
        quality_percentage = calculate_data_quality_percentage(
            total_records,
            invalid_records,
            duplicate_records
        )
        
        quality_metric = DataQualityMetrics(
            ingestion_batch_id=batch_id,
            total_records_ingested=total_records,
            invalid_records=invalid_records,
            duplicate_records=duplicate_records,
            cleaned_records=cleaned_records,
            data_quality_percentage=quality_percentage
        )
        
        db.add(quality_metric)
        db.commit()
        
        logger.info(
            f"Stored quality metrics for batch {batch_id}: "
            f"{cleaned_records}/{total_records} records cleaned "
            f"({quality_percentage}% quality)"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error storing quality metrics: {str(e)}")
        raise


def get_latest_quality_metrics(db: Session) -> dict:
    """
    Get the latest data quality metrics (most recent batch)
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with latest quality metrics
    """
    try:
        latest = db.query(DataQualityMetrics).order_by(
            DataQualityMetrics.created_at.desc()
        ).first()
        
        if not latest:
            return {
                "batch_id": None,
                "total_records_ingested": 0,
                "total_records": 0,
                "invalid_records": 0,
                "duplicate_records": 0,
                "dropped_records": 0,
                "cleaned_records": 0,
                "data_quality_percentage": 0.0,
                "created_at": None
            }
        
        # Calculate dropped records (invalid + duplicates)
        dropped_records = latest.invalid_records + latest.duplicate_records
        
        return {
            "batch_id": latest.ingestion_batch_id,
            "total_records_ingested": latest.total_records_ingested,
            "total_records": latest.total_records_ingested,  # Alias for frontend
            "invalid_records": latest.invalid_records,
            "duplicate_records": latest.duplicate_records,
            "dropped_records": dropped_records,
            "cleaned_records": latest.cleaned_records,
            "data_quality_percentage": latest.data_quality_percentage,
            "created_at": latest.created_at.isoformat() if latest.created_at else None
        }
        
    except Exception as e:
        logger.error(f"Error getting latest quality metrics: {str(e)}")
        raise


def get_aggregate_quality_metrics(db: Session) -> dict:
    """
    Get aggregate data quality metrics across all batches
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with aggregate quality metrics
    """
    try:
        aggregate = db.query(
            func.sum(DataQualityMetrics.total_records_ingested).label('total_ingested'),
            func.sum(DataQualityMetrics.invalid_records).label('total_invalid'),
            func.sum(DataQualityMetrics.duplicate_records).label('total_duplicates'),
            func.sum(DataQualityMetrics.cleaned_records).label('total_cleaned'),
            func.avg(DataQualityMetrics.data_quality_percentage).label('avg_quality'),
            func.count(DataQualityMetrics.id).label('total_batches')
        ).first()
        
        total_ingested = aggregate.total_ingested or 0
        total_invalid = aggregate.total_invalid or 0
        total_duplicates = aggregate.total_duplicates or 0
        total_cleaned = aggregate.total_cleaned or 0
        avg_quality = aggregate.avg_quality or 0.0
        total_batches = aggregate.total_batches or 0
        
        # Calculate overall quality percentage
        overall_quality = calculate_data_quality_percentage(
            total_ingested,
            total_invalid,
            total_duplicates
        )
        
        return {
            "total_batches": total_batches,
            "total_records_ingested": total_ingested,
            "total_invalid_records": total_invalid,
            "total_duplicate_records": total_duplicates,
            "total_cleaned_records": total_cleaned,
            "average_quality_percentage": round(avg_quality, 2),
            "overall_quality_percentage": overall_quality
        }
        
    except Exception as e:
        logger.error(f"Error getting aggregate quality metrics: {str(e)}")
        raise
