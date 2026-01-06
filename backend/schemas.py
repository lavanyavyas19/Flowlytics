"""
Pydantic Schemas for Request/Response Validation
Defines API input/output data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


class TransactionCreate(BaseModel):
    """Schema for creating a transaction"""
    transaction_date: str
    customer_id: str
    product: str
    quantity: str
    price: str


class CleanedTransactionResponse(BaseModel):
    """Schema for cleaned transaction response"""
    id: int
    transaction_date: date
    customer_id: str
    product: str
    quantity: float
    price: float
    total_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class DailySalesSummaryResponse(BaseModel):
    """Schema for daily sales summary response"""
    date: date
    total_revenue: float
    total_orders: int
    total_quantity: float

    class Config:
        from_attributes = True


class CustomerSummaryResponse(BaseModel):
    """Schema for customer summary response"""
    customer_id: str
    total_revenue: float
    total_orders: int
    average_order_value: float
    last_transaction_date: Optional[date]

    class Config:
        from_attributes = True


class KPIsResponse(BaseModel):
    """Schema for KPI dashboard response"""
    total_revenue: float
    total_orders: int
    average_order_value: float
    total_customers: int


class DatasetStatsResponse(BaseModel):
    """Schema for dataset statistics response"""
    raw_transactions_count: int
    cleaned_transactions_count: int
    date_range: dict
    unique_customers: int
    unique_products: int


class UploadResponse(BaseModel):
    """Schema for upload response"""
    message: str
    records_processed: int
    records_cleaned: int
    records_transformed: int
    duplicates_skipped: int
    invalid_records: int = 0
    dropped_records: int = 0  # Added: invalid + duplicates
    features_generated: int = 0
    data_quality_percentage: float = 0.0


class DataQualityResponse(BaseModel):
    """Schema for data quality metrics response"""
    batch_id: Optional[str] = None
    total_records: int  # Alias for total_records_ingested
    total_records_ingested: int  # Keep both for compatibility
    cleaned_records: int
    dropped_records: int  # Computed: invalid_records + duplicate_records
    invalid_records: int
    duplicate_records: int
    data_quality_percentage: float
    created_at: Optional[str] = None
    
    class Config:
        populate_by_name = True


class AggregateQualityResponse(BaseModel):
    """Schema for aggregate quality metrics"""
    total_batches: int
    total_records_ingested: int
    total_invalid_records: int
    total_duplicate_records: int
    total_cleaned_records: int
    average_quality_percentage: float
    overall_quality_percentage: float

