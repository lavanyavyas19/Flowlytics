"""
Transformation & Aggregation Layer
Performs business logic transformations and creates aggregated datasets
"""

from typing import List
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import CleanedTransaction, DailySalesSummary, CustomerSummary
import logging

logger = logging.getLogger(__name__)


def calculate_total_amount(quantity: float, price: float) -> float:
    """
    Calculate total amount for a transaction
    (This is already done in cleaning, but kept for consistency)
    
    Args:
        quantity: Transaction quantity
        price: Transaction price
        
    Returns:
        Total amount
    """
    return quantity * price


def aggregate_daily_sales(db: Session) -> int:
    """
    Aggregate cleaned transactions into daily sales summary
    Creates or updates daily_sales_summary table
    
    Args:
        db: Database session
        
    Returns:
        Number of daily summaries created/updated
    """
    try:
        # Get all cleaned transactions grouped by date
        daily_data = db.query(
            CleanedTransaction.transaction_date,
            func.sum(CleanedTransaction.total_amount).label('total_revenue'),
            func.count(CleanedTransaction.id).label('total_orders'),
            func.sum(CleanedTransaction.quantity).label('total_quantity')
        ).group_by(
            CleanedTransaction.transaction_date
        ).all()
        
        summaries_updated = 0
        
        for day_data in daily_data:
            # Check if summary already exists for this date
            existing_summary = db.query(DailySalesSummary).filter(
                DailySalesSummary.date == day_data.transaction_date
            ).first()
            
            if existing_summary:
                # Update existing summary
                existing_summary.total_revenue = day_data.total_revenue or 0.0
                existing_summary.total_orders = day_data.total_orders or 0
                existing_summary.total_quantity = day_data.total_quantity or 0.0
            else:
                # Create new summary
                new_summary = DailySalesSummary(
                    date=day_data.transaction_date,
                    total_revenue=day_data.total_revenue or 0.0,
                    total_orders=day_data.total_orders or 0,
                    total_quantity=day_data.total_quantity or 0.0
                )
                db.add(new_summary)
            
            summaries_updated += 1
        
        db.commit()
        logger.info(f"Aggregated {summaries_updated} daily sales summaries")
        return summaries_updated
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error aggregating daily sales: {str(e)}")
        raise


def aggregate_customer_summary(db: Session) -> int:
    """
    Aggregate cleaned transactions into customer-level summary
    Creates or updates customer_summary table
    
    Args:
        db: Database session
        
    Returns:
        Number of customer summaries created/updated
    """
    try:
        # Get all cleaned transactions grouped by customer
        customer_data = db.query(
            CleanedTransaction.customer_id,
            func.sum(CleanedTransaction.total_amount).label('total_revenue'),
            func.count(CleanedTransaction.id).label('total_orders'),
            func.max(CleanedTransaction.transaction_date).label('last_transaction_date')
        ).group_by(
            CleanedTransaction.customer_id
        ).all()
        
        summaries_updated = 0
        
        for cust_data in customer_data:
            # Calculate average order value
            avg_order_value = (cust_data.total_revenue or 0.0) / (cust_data.total_orders or 1)
            
            # Check if summary already exists for this customer
            existing_summary = db.query(CustomerSummary).filter(
                CustomerSummary.customer_id == cust_data.customer_id
            ).first()
            
            if existing_summary:
                # Update existing summary
                existing_summary.total_revenue = cust_data.total_revenue or 0.0
                existing_summary.total_orders = cust_data.total_orders or 0
                existing_summary.average_order_value = avg_order_value
                existing_summary.last_transaction_date = cust_data.last_transaction_date
            else:
                # Create new summary
                new_summary = CustomerSummary(
                    customer_id=cust_data.customer_id,
                    total_revenue=cust_data.total_revenue or 0.0,
                    total_orders=cust_data.total_orders or 0,
                    average_order_value=avg_order_value,
                    last_transaction_date=cust_data.last_transaction_date
                )
                db.add(new_summary)
            
            summaries_updated += 1
        
        db.commit()
        logger.info(f"Aggregated {summaries_updated} customer summaries")
        return summaries_updated
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error aggregating customer summary: {str(e)}")
        raise


def run_full_transformation_pipeline(db: Session) -> dict:
    """
    Run the complete transformation pipeline
    Aggregates data into all summary tables
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with transformation results
    """
    try:
        daily_count = aggregate_daily_sales(db)
        customer_count = aggregate_customer_summary(db)
        
        return {
            "daily_summaries": daily_count,
            "customer_summaries": customer_count
        }
    except Exception as e:
        logger.error(f"Error in transformation pipeline: {str(e)}")
        raise


def get_daily_revenue_timeseries(db: Session, limit: int = 365) -> List[dict]:
    """
    Get time-series data for daily revenue (for charts)
    
    Args:
        db: Database session
        limit: Maximum number of days to return
        
    Returns:
        List of dictionaries with date and revenue
    """
    daily_summaries = db.query(DailySalesSummary).order_by(
        DailySalesSummary.date
    ).limit(limit).all()
    
    return [
        {
            "date": str(summary.date),
            "revenue": summary.total_revenue
        }
        for summary in daily_summaries
    ]


def get_top_customers(db: Session, limit: int = 10) -> List[dict]:
    """
    Get top customers by revenue (for charts)
    
    Args:
        db: Database session
        limit: Maximum number of customers to return
        
    Returns:
        List of dictionaries with customer data
    """
    top_customers = db.query(CustomerSummary).order_by(
        desc(CustomerSummary.total_revenue)
    ).limit(limit).all()
    
    return [
        {
            "customer_id": customer.customer_id,
            "revenue": customer.total_revenue
        }
        for customer in top_customers
    ]

