"""
Data Cleaning & Validation Layer
Handles data quality checks, type conversion, and duplicate removal
"""

from typing import List, Dict, Tuple, Set
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from models import RawTransaction, CleanedTransaction
import logging

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> datetime.date:
    """
    Parse date string to date object
    Supports multiple date formats
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        date object
    """
    if not date_str or not date_str.strip():
        raise ValueError("Empty date string")
    
    date_str = date_str.strip()
    
    # Try common date formats
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%m-%d-%Y",
        "%d-%m-%Y"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


def parse_float(value: str) -> float:
    """
    Parse string to float, handling common formatting issues
    
    Args:
        value: String representation of number
        
    Returns:
        float value
    """
    if not value or not value.strip():
        raise ValueError("Empty numeric value")
    
    # Remove common formatting characters
    cleaned = value.strip().replace("$", "").replace(",", "").replace(" ", "")
    
    try:
        return float(cleaned)
    except ValueError:
        raise ValueError(f"Unable to parse as float: {value}")


def clean_transaction(raw_transaction: RawTransaction) -> Dict:
    """
    Clean and validate a single raw transaction
    Handles missing values, invalid dates, and type conversions
    
    Args:
        raw_transaction: RawTransaction object from database
        
    Returns:
        Dictionary with cleaned transaction data
        
    Raises:
        ValueError: If critical fields are invalid or missing
    """
    cleaned_data = {}
    validation_errors = []
    
    # Clean transaction_id (optional)
    if raw_transaction.transaction_id:
        cleaned_data["transaction_id"] = str(raw_transaction.transaction_id).strip()
    else:
        cleaned_data["transaction_id"] = None
    
    # Clean transaction_date (required)
    try:
        if not raw_transaction.transaction_date or raw_transaction.transaction_date.strip().lower() in ["invalid_date", "null", "none", ""]:
            raise ValueError("Invalid or missing transaction_date")
        cleaned_data["transaction_date"] = parse_date(raw_transaction.transaction_date)
    except (ValueError, AttributeError) as e:
        validation_errors.append(f"Invalid date: {raw_transaction.transaction_date}")
        raise ValueError(f"Invalid transaction_date: {raw_transaction.transaction_date}")
    
    # Clean customer_id (required)
    customer_id = str(raw_transaction.customer_id).strip() if raw_transaction.customer_id else ""
    if not customer_id:
        validation_errors.append("Empty customer_id")
        raise ValueError("Empty customer_id")
    cleaned_data["customer_id"] = customer_id
    
    # Clean product (required)
    product = str(raw_transaction.product).strip() if raw_transaction.product else ""
    if not product:
        validation_errors.append("Empty product")
        raise ValueError("Empty product")
    cleaned_data["product"] = product
    
    # Clean category (optional)
    if raw_transaction.category:
        cleaned_data["category"] = str(raw_transaction.category).strip()
    else:
        cleaned_data["category"] = None
    
    # Clean quantity (required, but can be missing in raw data)
    if raw_transaction.quantity is None or str(raw_transaction.quantity).strip().lower() in ["null", "none", ""]:
        validation_errors.append("Missing quantity")
        raise ValueError("Missing quantity")
    
    try:
        cleaned_data["quantity"] = parse_float(raw_transaction.quantity)
        if cleaned_data["quantity"] < 0:
            logger.warning(f"Negative quantity for transaction {raw_transaction.id}, setting to 0")
            cleaned_data["quantity"] = 0.0
    except (ValueError, AttributeError) as e:
        validation_errors.append(f"Invalid quantity: {raw_transaction.quantity}")
        raise ValueError(f"Invalid quantity: {raw_transaction.quantity}")
    
    # Clean price (required, but can be missing in raw data)
    if raw_transaction.price is None or str(raw_transaction.price).strip().lower() in ["null", "none", ""]:
        validation_errors.append("Missing price")
        raise ValueError("Missing price")
    
    try:
        cleaned_data["price"] = parse_float(raw_transaction.price)
        if cleaned_data["price"] < 0:
            logger.warning(f"Negative price for transaction {raw_transaction.id}, setting to 0")
            cleaned_data["price"] = 0.0
    except (ValueError, AttributeError) as e:
        validation_errors.append(f"Invalid price: {raw_transaction.price}")
        raise ValueError(f"Invalid price: {raw_transaction.price}")
    
    # Calculate total_amount
    cleaned_data["total_amount"] = cleaned_data["quantity"] * cleaned_data["price"]
    
    # Clean optional fields
    cleaned_data["payment_method"] = str(raw_transaction.payment_method).strip() if raw_transaction.payment_method else None
    cleaned_data["city"] = str(raw_transaction.city).strip() if raw_transaction.city else None
    
    # Log validation errors if any
    if validation_errors:
        logger.warning(f"Transaction {raw_transaction.id} had validation issues: {', '.join(validation_errors)}")
    
    return cleaned_data


def is_duplicate(db: Session, cleaned_data: Dict) -> bool:
    """
    Check if a cleaned transaction already exists (idempotency check)
    
    Args:
        db: Database session
        cleaned_data: Cleaned transaction data dictionary
        
    Returns:
        True if duplicate exists
    """
    existing = db.query(CleanedTransaction).filter(
        and_(
            CleanedTransaction.transaction_date == cleaned_data["transaction_date"],
            CleanedTransaction.customer_id == cleaned_data["customer_id"],
            CleanedTransaction.product == cleaned_data["product"],
            CleanedTransaction.quantity == cleaned_data["quantity"],
            CleanedTransaction.price == cleaned_data["price"]
        )
    ).first()
    
    return existing is not None


def clean_and_store_transactions(db: Session, raw_transactions: List[RawTransaction]) -> Tuple[int, int, int]:
    """
    Clean raw transactions and store cleaned data
    Tracks invalid rows with detailed logging
    Handles duplicate transaction_ids both from database and within the same batch
    
    Args:
        db: Database session
        raw_transactions: List of RawTransaction objects
        
    Returns:
        Tuple of (cleaned_count, duplicates_skipped, invalid_rows)
    """
    cleaned_count = 0
    duplicates_skipped = 0
    invalid_rows = 0
    invalid_row_details = []  # Store details of invalid rows
    
    # Track transaction_ids processed in this batch to catch duplicates within the same batch
    processed_transaction_ids: Set[str] = set()
    
    try:
        for raw_transaction in raw_transactions:
            try:
                # Clean the transaction
                cleaned_data = clean_transaction(raw_transaction)
                
                # Check for duplicates (by transaction_id if available, or by composite key)
                transaction_id = cleaned_data.get("transaction_id")
                if transaction_id:
                    # Check if we've already processed this transaction_id in this batch
                    if transaction_id in processed_transaction_ids:
                        duplicates_skipped += 1
                        logger.debug(f"Skipping duplicate transaction_id in batch: {transaction_id}")
                        continue
                    
                    # Check if transaction_id exists in database
                    existing = db.query(CleanedTransaction).filter(
                        CleanedTransaction.transaction_id == transaction_id
                    ).first()
                    if existing:
                        duplicates_skipped += 1
                        logger.debug(f"Skipping duplicate transaction_id in database: {transaction_id}")
                        continue
                    
                    # Mark as processed in this batch
                    processed_transaction_ids.add(transaction_id)
                elif is_duplicate(db, cleaned_data):
                    duplicates_skipped += 1
                    logger.debug(f"Skipping duplicate transaction {raw_transaction.id}")
                    continue
                
                # Create cleaned transaction record
                cleaned_transaction = CleanedTransaction(
                    transaction_id=transaction_id,
                    transaction_date=cleaned_data["transaction_date"],
                    customer_id=cleaned_data["customer_id"],
                    product=cleaned_data["product"],
                    category=cleaned_data.get("category"),
                    quantity=cleaned_data["quantity"],
                    price=cleaned_data["price"],
                    total_amount=cleaned_data["total_amount"],
                    payment_method=cleaned_data.get("payment_method"),
                    city=cleaned_data.get("city"),
                    raw_transaction_id=raw_transaction.id
                )
                
                db.add(cleaned_transaction)
                
                # Commit immediately to catch duplicates early and avoid rollback of entire batch
                try:
                    db.commit()
                    cleaned_count += 1
                except IntegrityError as e:
                    # Unique constraint violation - this is a duplicate we missed
                    db.rollback()
                    duplicates_skipped += 1
                    logger.debug(f"Skipping duplicate transaction_id (caught on commit): {transaction_id}")
                    continue
                
                # Periodic batch commit log for performance monitoring
                if cleaned_count > 0 and cleaned_count % 500 == 0:
                    logger.debug(f"Processed {cleaned_count} cleaned transactions so far")
                
            except ValueError as e:
                # Validation error - log details
                invalid_rows += 1
                error_detail = {
                    "raw_transaction_id": raw_transaction.id,
                    "transaction_id": raw_transaction.transaction_id,
                    "customer_id": raw_transaction.customer_id,
                    "error": str(e)
                }
                invalid_row_details.append(error_detail)
                logger.warning(f"Invalid row {raw_transaction.id}: {str(e)}")
                continue
            except IntegrityError as e:
                # This should be caught above, but handle it here as a fallback
                db.rollback()
                duplicates_skipped += 1
                transaction_id = getattr(raw_transaction, 'transaction_id', None)
                if transaction_id:
                    processed_transaction_ids.add(str(transaction_id))
                logger.warning(f"IntegrityError (duplicate, fallback): transaction_id={transaction_id}, error={str(e)}")
                continue
            except Exception as e:
                invalid_rows += 1
                error_detail = {
                    "raw_transaction_id": raw_transaction.id,
                    "transaction_id": raw_transaction.transaction_id,
                    "customer_id": raw_transaction.customer_id,
                    "error": f"Unexpected error: {str(e)}"
                }
                invalid_row_details.append(error_detail)
                logger.error(f"Error cleaning transaction {raw_transaction.id}: {str(e)}")
                continue
        
        # No final commit needed - we commit after each successful transaction
        
        # Log summary
        logger.info(f"Cleaned {cleaned_count} transactions, skipped {duplicates_skipped} duplicates, {invalid_rows} invalid rows")
        if invalid_row_details:
            logger.info(f"Invalid rows details (first 10): {invalid_row_details[:10]}")
        
        return cleaned_count, duplicates_skipped, invalid_rows
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error in clean_and_store_transactions: {str(e)}")
        raise


def get_all_raw_transactions_for_cleaning(db: Session):
    """
    Get all raw transactions that haven't been cleaned yet
    
    Args:
        db: Database session
        
    Returns:
        List of RawTransaction objects
    """
    # Get raw transactions that don't have corresponding cleaned records
    cleaned_ids = db.query(CleanedTransaction.raw_transaction_id).filter(
        CleanedTransaction.raw_transaction_id.isnot(None)
    ).subquery()
    
    return db.query(RawTransaction).filter(
        ~RawTransaction.id.in_(db.query(cleaned_ids.c.raw_transaction_id))
    ).all()

