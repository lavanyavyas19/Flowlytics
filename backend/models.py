"""
Database Models - SQLAlchemy ORM Models
Defines all database tables for the data pipeline
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Index
from sqlalchemy.sql import func
from database import Base


class RawTransaction(Base):
    """
    Raw transaction data as ingested from CSV
    Stores unprocessed data exactly as received
    """
    __tablename__ = "raw_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=True, index=True)  # Optional transaction ID
    transaction_date = Column(String, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    product = Column(String, nullable=False)
    category = Column(String, nullable=True)  # Product category
    quantity = Column(String, nullable=True)  # Can be null in raw data
    price = Column(String, nullable=True)  # Can be null in raw data
    payment_method = Column(String, nullable=True)  # Payment method
    city = Column(String, nullable=True)  # City location
    created_at = Column(DateTime, server_default=func.now())
    
    # Index for faster lookups
    __table_args__ = (
        Index('idx_raw_customer_date', 'customer_id', 'transaction_date'),
        Index('idx_raw_transaction_id', 'transaction_id'),
    )


class CleanedTransaction(Base):
    """
    Cleaned and validated transaction data
    After data cleaning and type conversion
    """
    __tablename__ = "cleaned_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=True, unique=True, index=True)  # Unique transaction ID
    transaction_date = Column(Date, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    product = Column(String, nullable=False)
    category = Column(String, nullable=True)  # Product category
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)  # quantity * price
    payment_method = Column(String, nullable=True)  # Payment method
    city = Column(String, nullable=True)  # City location
    raw_transaction_id = Column(Integer, nullable=True)  # Reference to raw data
    created_at = Column(DateTime, server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_cleaned_customer_date', 'customer_id', 'transaction_date'),
        Index('idx_cleaned_date', 'transaction_date'),
        Index('idx_cleaned_category', 'category'),
    )


class DailySalesSummary(Base):
    """
    Aggregated daily sales metrics
    Pre-computed aggregations for fast dashboard queries
    """
    __tablename__ = "daily_sales_summary"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    total_revenue = Column(Float, nullable=False, default=0.0)
    total_orders = Column(Integer, nullable=False, default=0)
    total_quantity = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class CustomerSummary(Base):
    """
    Customer-level aggregated metrics
    Pre-computed customer analytics for dashboard
    """
    __tablename__ = "customer_summary"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, nullable=False, unique=True, index=True)
    total_revenue = Column(Float, nullable=False, default=0.0)
    total_orders = Column(Integer, nullable=False, default=0)
    average_order_value = Column(Float, nullable=False, default=0.0)
    last_transaction_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DataQualityMetrics(Base):
    """
    Data quality metrics tracking
    Stores statistics about data ingestion and cleaning
    """
    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, index=True)
    ingestion_batch_id = Column(String, nullable=True, index=True)  # Batch identifier
    total_records_ingested = Column(Integer, nullable=False, default=0)
    invalid_records = Column(Integer, nullable=False, default=0)
    duplicate_records = Column(Integer, nullable=False, default=0)
    cleaned_records = Column(Integer, nullable=False, default=0)
    dropped_records = Column(Integer, nullable=False, default=0)  # Total dropped (invalid + duplicates)
    data_quality_percentage = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, server_default=func.now())


class FeatureEngineering(Base):
    """
    ML-ready features table
    Stores engineered features for machine learning
    """
    __tablename__ = "feature_engineering"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, nullable=True, index=True)
    customer_id = Column(String, nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    
    # Basic features
    total_amount = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    
    # Engineered features
    daily_revenue = Column(Float, nullable=False)  # Revenue for that day
    customer_lifetime_value = Column(Float, nullable=False)  # Cumulative CLV
    transaction_frequency = Column(Integer, nullable=False)  # Number of transactions for customer
    days_since_first_transaction = Column(Integer, nullable=True)  # Days since customer's first transaction
    average_transaction_value = Column(Float, nullable=False)  # Average transaction value for customer
    
    # Additional features
    category = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_feature_customer_date', 'customer_id', 'transaction_date'),
        Index('idx_feature_date', 'transaction_date'),
    )

