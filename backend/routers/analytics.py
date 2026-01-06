"""
Analytics Router - Handles analytics and KPI endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import logging

from database import get_db
from models import CleanedTransaction, DailySalesSummary, CustomerSummary, RawTransaction
from services.transformation import get_daily_revenue_timeseries, get_top_customers
from services.data_quality import get_latest_quality_metrics, get_aggregate_quality_metrics
from schemas import (
    KPIsResponse,
    DatasetStatsResponse,
    DailySalesSummaryResponse,
    CustomerSummaryResponse,
    DataQualityResponse,
    AggregateQualityResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/kpis", response_model=KPIsResponse)
async def get_kpis(db: Session = Depends(get_db)):
    """
    Get Key Performance Indicators for dashboard
    
    Returns:
        KPIsResponse with total revenue, orders, AOV, and customer count
    """
    try:
        # Calculate KPIs from cleaned transactions
        kpi_data = db.query(
            func.sum(CleanedTransaction.total_amount).label('total_revenue'),
            func.count(CleanedTransaction.id).label('total_orders'),
            func.count(func.distinct(CleanedTransaction.customer_id)).label('total_customers')
        ).first()
        
        total_revenue = kpi_data.total_revenue or 0.0
        total_orders = kpi_data.total_orders or 0
        total_customers = kpi_data.total_customers or 0
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
        
        return KPIsResponse(
            total_revenue=round(total_revenue, 2),
            total_orders=total_orders,
            average_order_value=round(average_order_value, 2),
            total_customers=total_customers
        )
        
    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating KPIs: {str(e)}")


@router.get("/dataset-stats", response_model=DatasetStatsResponse)
async def get_dataset_stats(db: Session = Depends(get_db)):
    """
    Get dataset statistics
    
    Returns:
        DatasetStatsResponse with counts and metadata
    """
    try:
        # Count records
        raw_count = db.query(func.count(RawTransaction.id)).scalar() or 0
        cleaned_count = db.query(func.count(CleanedTransaction.id)).scalar() or 0
        
        # Get date range
        date_range_query = db.query(
            func.min(CleanedTransaction.transaction_date).label('min_date'),
            func.max(CleanedTransaction.transaction_date).label('max_date')
        ).first()
        
        date_range = {
            "min": str(date_range_query.min_date) if date_range_query.min_date else None,
            "max": str(date_range_query.max_date) if date_range_query.max_date else None
        }
        
        # Get unique counts
        unique_customers = db.query(
            func.count(func.distinct(CleanedTransaction.customer_id))
        ).scalar() or 0
        
        unique_products = db.query(
            func.count(func.distinct(CleanedTransaction.product))
        ).scalar() or 0
        
        return DatasetStatsResponse(
            raw_transactions_count=raw_count,
            cleaned_transactions_count=cleaned_count,
            date_range=date_range,
            unique_customers=unique_customers,
            unique_products=unique_products
        )
        
    except Exception as e:
        logger.error(f"Error getting dataset stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting dataset stats: {str(e)}")


@router.get("/daily-revenue", response_model=List[dict])
async def get_daily_revenue(db: Session = Depends(get_db)):
    """
    Get daily revenue time-series data for charts
    
    Returns:
        List of dictionaries with date and revenue
    """
    try:
        return get_daily_revenue_timeseries(db)
    except Exception as e:
        logger.error(f"Error getting daily revenue: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting daily revenue: {str(e)}")


@router.get("/top-customers", response_model=List[dict])
async def get_top_customers_endpoint(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get top customers by revenue for charts
    
    Args:
        limit: Maximum number of customers to return
        
    Returns:
        List of dictionaries with customer_id and revenue
    """
    try:
        return get_top_customers(db, limit)
    except Exception as e:
        logger.error(f"Error getting top customers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting top customers: {str(e)}")


@router.get("/daily-sales", response_model=List[DailySalesSummaryResponse])
async def get_daily_sales(db: Session = Depends(get_db)):
    """
    Get all daily sales summaries
    
    Returns:
        List of DailySalesSummaryResponse objects
    """
    try:
        summaries = db.query(DailySalesSummary).order_by(
            DailySalesSummary.date
        ).all()
        return summaries
    except Exception as e:
        logger.error(f"Error getting daily sales: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting daily sales: {str(e)}")


@router.get("/customer-summaries", response_model=List[CustomerSummaryResponse])
async def get_customer_summaries(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get customer summaries
    
    Args:
        limit: Maximum number of customers to return
        
    Returns:
        List of CustomerSummaryResponse objects
    """
    try:
        summaries = db.query(CustomerSummary).order_by(
            CustomerSummary.total_revenue.desc()
        ).limit(limit).all()
        return summaries
    except Exception as e:
        logger.error(f"Error getting customer summaries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting customer summaries: {str(e)}")


@router.get("/data-quality", response_model=DataQualityResponse)
async def get_data_quality(db: Session = Depends(get_db)):
    """
    Get latest data quality metrics
    
    Returns:
        DataQualityResponse with quality statistics
        Returns default values (all zeros) if no metrics exist yet
    """
    try:
        metrics = get_latest_quality_metrics(db)
        logger.info(f"Retrieved quality metrics: {metrics}")
        # Ensure we always return valid data structure
        response = DataQualityResponse(**metrics)
        logger.info(f"Returning quality response: total_records={response.total_records}, cleaned={response.cleaned_records}, dropped={response.dropped_records}, quality={response.data_quality_percentage}%")
        return response
    except Exception as e:
        logger.error(f"Error getting data quality metrics: {str(e)}")
        # Return default values instead of throwing error
        return DataQualityResponse(
            batch_id=None,
            total_records=0,
            total_records_ingested=0,
            invalid_records=0,
            duplicate_records=0,
            dropped_records=0,
            cleaned_records=0,
            data_quality_percentage=0.0,
            created_at=None
        )


@router.get("/data-quality/aggregate", response_model=AggregateQualityResponse)
async def get_aggregate_data_quality(db: Session = Depends(get_db)):
    """
    Get aggregate data quality metrics across all batches
    
    Returns:
        AggregateQualityResponse with overall statistics
    """
    try:
        metrics = get_aggregate_quality_metrics(db)
        return AggregateQualityResponse(**metrics)
    except Exception as e:
        logger.error(f"Error getting aggregate quality metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting aggregate quality metrics: {str(e)}")

