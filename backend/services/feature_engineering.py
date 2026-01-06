"""
Feature Engineering Service
Generates ML-ready features from cleaned transaction data
"""

from typing import List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models import CleanedTransaction, FeatureEngineering, DailySalesSummary
import logging

logger = logging.getLogger(__name__)


def calculate_daily_revenue(db: Session, transaction_date: date) -> float:
    """
    Calculate total revenue for a specific day
    
    Args:
        db: Database session
        transaction_date: Date to calculate revenue for
        
    Returns:
        Total revenue for that day
    """
    result = db.query(
        func.sum(CleanedTransaction.total_amount)
    ).filter(
        CleanedTransaction.transaction_date == transaction_date
    ).scalar()
    
    return result or 0.0


def calculate_customer_lifetime_value(db: Session, customer_id: str, current_date: date) -> float:
    """
    Calculate cumulative Customer Lifetime Value (CLV) up to current transaction
    
    Args:
        db: Database session
        customer_id: Customer identifier
        current_date: Current transaction date
        
    Returns:
        Cumulative CLV for the customer
    """
    result = db.query(
        func.sum(CleanedTransaction.total_amount)
    ).filter(
        CleanedTransaction.customer_id == customer_id,
        CleanedTransaction.transaction_date <= current_date
    ).scalar()
    
    return result or 0.0


def calculate_transaction_frequency(db: Session, customer_id: str, current_date: date) -> int:
    """
    Calculate number of transactions for a customer up to current date
    
    Args:
        db: Database session
        customer_id: Customer identifier
        current_date: Current transaction date
        
    Returns:
        Number of transactions
    """
    result = db.query(
        func.count(CleanedTransaction.id)
    ).filter(
        CleanedTransaction.customer_id == customer_id,
        CleanedTransaction.transaction_date <= current_date
    ).scalar()
    
    return result or 0


def calculate_days_since_first_transaction(db: Session, customer_id: str, current_date: date) -> int:
    """
    Calculate days since customer's first transaction
    
    Args:
        db: Database session
        customer_id: Customer identifier
        current_date: Current transaction date
        
    Returns:
        Number of days since first transaction, or None if this is the first
    """
    first_transaction = db.query(
        func.min(CleanedTransaction.transaction_date)
    ).filter(
        CleanedTransaction.customer_id == customer_id
    ).scalar()
    
    if first_transaction and first_transaction < current_date:
        delta = current_date - first_transaction
        return delta.days
    elif first_transaction == current_date:
        # This is the first transaction
        return 0
    else:
        return None


def calculate_average_transaction_value(db: Session, customer_id: str, current_date: date) -> float:
    """
    Calculate average transaction value for customer up to current date
    
    Args:
        db: Database session
        customer_id: Customer identifier
        current_date: Current transaction date
        
    Returns:
        Average transaction value
    """
    result = db.query(
        func.avg(CleanedTransaction.total_amount)
    ).filter(
        CleanedTransaction.customer_id == customer_id,
        CleanedTransaction.transaction_date <= current_date
    ).scalar()
    
    return result or 0.0


def store_feature_engineering(db: Session, cleaned_transactions: List[CleanedTransaction]) -> int:
    """
    Generate and store ML-ready features for cleaned transactions
    
    Features generated:
    - total_amount: quantity * price (already calculated)
    - daily_revenue: Total revenue for that day
    - customer_lifetime_value: Cumulative CLV for customer
    - transaction_frequency: Number of transactions for customer
    - days_since_first_transaction: Days since customer's first transaction
    - average_transaction_value: Average transaction value for customer
    
    Args:
        db: Database session
        cleaned_transactions: List of CleanedTransaction objects
        
    Returns:
        Number of feature records created
    """
    try:
        features_created = 0
        
        # Process transactions in chronological order for accurate feature calculation
        sorted_transactions = sorted(
            cleaned_transactions,
            key=lambda t: (t.transaction_date, t.id)
        )
        
        for transaction in sorted_transactions:
            try:
                # Check if features already exist for this transaction
                if transaction.transaction_id:
                    existing = db.query(FeatureEngineering).filter(
                        FeatureEngineering.transaction_id == transaction.transaction_id
                    ).first()
                    if existing:
                        continue
                
                # Calculate features
                daily_revenue = calculate_daily_revenue(db, transaction.transaction_date)
                customer_clv = calculate_customer_lifetime_value(
                    db, transaction.customer_id, transaction.transaction_date
                )
                transaction_freq = calculate_transaction_frequency(
                    db, transaction.customer_id, transaction.transaction_date
                )
                days_since_first = calculate_days_since_first_transaction(
                    db, transaction.customer_id, transaction.transaction_date
                )
                avg_transaction_value = calculate_average_transaction_value(
                    db, transaction.customer_id, transaction.transaction_date
                )
                
                # Create feature engineering record
                feature_record = FeatureEngineering(
                    transaction_id=transaction.transaction_id,
                    customer_id=transaction.customer_id,
                    transaction_date=transaction.transaction_date,
                    total_amount=transaction.total_amount,
                    quantity=transaction.quantity,
                    price=transaction.price,
                    daily_revenue=daily_revenue,
                    customer_lifetime_value=customer_clv,
                    transaction_frequency=transaction_freq,
                    days_since_first_transaction=days_since_first,
                    average_transaction_value=avg_transaction_value,
                    category=transaction.category,
                    payment_method=transaction.payment_method,
                    city=transaction.city
                )
                
                db.add(feature_record)
                features_created += 1
                
            except Exception as e:
                logger.warning(f"Error generating features for transaction {transaction.id}: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Generated {features_created} feature engineering records")
        return features_created
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in store_feature_engineering: {str(e)}")
        raise


def get_feature_engineering_stats(db: Session) -> dict:
    """
    Get statistics about feature engineering data
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with feature statistics
    """
    try:
        total_features = db.query(func.count(FeatureEngineering.id)).scalar() or 0
        unique_customers = db.query(
            func.count(func.distinct(FeatureEngineering.customer_id))
        ).scalar() or 0
        
        avg_clv = db.query(
            func.avg(FeatureEngineering.customer_lifetime_value)
        ).scalar() or 0.0
        
        avg_frequency = db.query(
            func.avg(FeatureEngineering.transaction_frequency)
        ).scalar() or 0.0
        
        return {
            "total_features": total_features,
            "unique_customers": unique_customers,
            "average_clv": round(avg_clv, 2),
            "average_transaction_frequency": round(avg_frequency, 2)
        }
    except Exception as e:
        logger.error(f"Error getting feature stats: {str(e)}")
        return {
            "total_features": 0,
            "unique_customers": 0,
            "average_clv": 0.0,
            "average_transaction_frequency": 0.0
        }
