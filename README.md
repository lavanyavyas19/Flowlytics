# Flowlytics - End-to-End Data Pipeline & Analytics Platform

A production-ready data engineering and analytics web application that ingests raw transactional data, processes it through a multi-layer pipeline, and provides real-time insights via an interactive dashboard.

## 🎯 Features

- **Data Ingestion**: CSV file upload with schema validation and invalid row detection
- **Data Cleaning**: Automatic handling of missing values, invalid dates, duplicates, and type conversion
- **Data Quality Metrics**: Real-time tracking of data quality percentage, invalid records, and cleaning success rates
- **Feature Engineering**: ML-ready features including customer lifetime value, transaction frequency, and daily revenue
- **Data Transformation**: Business logic transformations and aggregations
- **Analytics Dashboard**: Real-time KPIs and visualizations
- **RESTful API**: Comprehensive API endpoints for data operations and quality metrics
- **Idempotent Processing**: Prevents duplicate data ingestion with detailed logging

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Ingestion Layer**: Parses CSV files, validates schema, detects invalid rows, stores raw data
- **Cleaning Layer**: Validates, cleans, normalizes data with detailed error logging
- **Feature Engineering Layer**: Generates ML-ready features (CLV, transaction frequency, daily revenue)
- **Transformation Layer**: Aggregates data into summary tables
- **Data Quality Layer**: Tracks and reports data quality metrics
- **API Layer**: REST endpoints for upload, analytics, and data quality

### Frontend (React + Tailwind CSS)
- **Upload Interface**: CSV file upload with validation feedback
- **KPI Dashboard**: Real-time key performance indicators
- **Data Visualizations**: Line charts and bar charts using Recharts

### Database (SQLite/PostgreSQL)
- **raw_transactions**: Stores unprocessed data with all original columns
- **cleaned_transactions**: Validated and cleaned data with type conversions
- **feature_engineering**: ML-ready features table with engineered attributes
- **daily_sales_summary**: Pre-aggregated daily metrics
- **customer_summary**: Customer-level aggregations
- **data_quality_metrics**: Tracks data quality statistics per ingestion batch

## 📁 Project Structure

```
flowlytics/
│
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic schemas
│   ├── services/
│   │   ├── ingestion.py        # Data ingestion service with validation
│   │   ├── cleaning.py         # Data cleaning service with error logging
│   │   ├── transformation.py   # Data transformation service
│   │   ├── feature_engineering.py  # ML feature generation
│   │   └── data_quality.py     # Data quality metrics tracking
│   ├── routers/
│   │   ├── upload.py           # File upload endpoints
│   │   └── analytics.py        # Analytics endpoints
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard.jsx   # Main dashboard page
│   │   ├── components/
│   │   │   ├── KPI.jsx         # KPI cards component
│   │   │   └── Charts.jsx      # Chart components
│   │   ├── App.jsx             # Root component
│   │   └── main.jsx            # Entry point
│   ├── package.json            # Node.js dependencies
│   └── vite.config.js          # Vite configuration
│
├── sample_data/
│   └── transactions.csv        # Sample transaction data
│
├── generate_transactions.py    # Script to generate test data with dirty data
└── README.md                   # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server**:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📊 Usage

### End-to-End Pipeline Execution

Follow these steps to run the complete pipeline:

#### Step 1: Start Backend Server

```bash
cd backend
source venv/bin/activate  # If not already activated
python main.py
```

Backend will be available at `http://localhost:8000`

#### Step 2: Start Frontend Server (New Terminal)

```bash
cd frontend
npm install  # First time only
npm run dev
```

Frontend will be available at `http://localhost:3000`

#### Step 3: Generate Test Data (Optional)

Generate a test dataset with dirty data to test the data quality features:

```bash
# From project root
python generate_transactions.py
```

This creates `transactions.csv` with 10,000 rows including:
- Missing values (nulls in quantity, price, city)
- Invalid dates ("invalid_date" strings)
- Duplicate transaction IDs
- Various data quality issues

**Note:** Requires pandas: `pip install pandas`

#### Step 4: Upload and Process Data

1. Open the dashboard at `http://localhost:3000`
2. Click "Select CSV File" and choose `transactions.csv` (or any valid CSV)
3. Click "Upload & Process"

The system will automatically:
- ✅ Validate CSV schema
- ✅ Detect and log invalid rows
- ✅ Remove duplicates
- ✅ Clean and convert data types
- ✅ Generate ML-ready features
- ✅ Calculate data quality metrics
- ✅ Create aggregated summaries

#### Step 5: View Results

After processing, you can:
- View KPIs on the dashboard
- Check data quality metrics via API: `GET /api/data-quality`
- View feature engineering data in the database
- Access all analytics via the dashboard

### Upload Transaction Data

1. Open the dashboard at `http://localhost:3000`
2. Click "Select CSV File" and choose a CSV file

**Required columns:**
   - `transaction_date` (format: YYYY-MM-DD)
   - `customer_id`
   - `product`
   - `quantity` (numeric, can be null)
   - `price` (numeric, can be null)

**Optional columns:**
   - `transaction_id` (unique identifier)
   - `category` (product category)
   - `payment_method` (payment method used)
   - `city` (transaction location)

3. Click "Upload & Process" to start the pipeline

The system will:
- Validate CSV schema
- Detect and log invalid rows
- Remove duplicates
- Clean and convert data types
- Generate ML-ready features
- Calculate data quality metrics

### 2. View Analytics

After uploading data, the dashboard will automatically display:
- **KPI Cards**: Total Revenue, Total Orders, Average Order Value, Total Customers
- **Daily Revenue Trend**: Line chart showing revenue over time
- **Top Customers**: Bar chart showing top customers by revenue

### 3. Sample Data

A sample CSV file is provided in `sample_data/transactions.csv`. You can use this to test the application.

## 🔌 API Endpoints

### Upload
- `POST /api/upload` - Upload and process CSV file

### Analytics
- `GET /api/kpis` - Get key performance indicators
- `GET /api/dataset-stats` - Get dataset statistics
- `GET /api/daily-revenue` - Get daily revenue time-series data
- `GET /api/top-customers?limit=10` - Get top customers by revenue
- `GET /api/daily-sales` - Get all daily sales summaries
- `GET /api/customer-summaries?limit=100` - Get customer summaries

### Data Quality
- `GET /api/data-quality` - Get latest data quality metrics for the most recent batch
- `GET /api/data-quality/aggregate` - Get aggregate data quality metrics across all batches

## 🗄️ Database Schema

### raw_transactions
- `id` (Primary Key)
- `transaction_id` (String, Optional) - Unique transaction identifier
- `transaction_date` (String)
- `customer_id` (String)
- `product` (String)
- `category` (String, Optional) - Product category
- `quantity` (String, Optional) - Can be null in raw data
- `price` (String, Optional) - Can be null in raw data
- `payment_method` (String, Optional) - Payment method
- `city` (String, Optional) - Transaction location
- `created_at` (DateTime)

### cleaned_transactions
- `id` (Primary Key)
- `transaction_id` (String, Unique, Optional) - Unique transaction identifier
- `transaction_date` (Date) - Validated and parsed date
- `customer_id` (String)
- `product` (String)
- `category` (String, Optional)
- `quantity` (Float) - Validated and converted
- `price` (Float) - Validated and converted
- `total_amount` (Float) - Calculated: quantity * price
- `payment_method` (String, Optional)
- `city` (String, Optional)
- `raw_transaction_id` (Integer, Foreign Key)
- `created_at` (DateTime)

### feature_engineering
- `id` (Primary Key)
- `transaction_id` (String, Optional)
- `customer_id` (String)
- `transaction_date` (Date)
- `total_amount` (Float)
- `quantity` (Float)
- `price` (Float)
- `daily_revenue` (Float) - Total revenue for that day
- `customer_lifetime_value` (Float) - Cumulative CLV up to transaction date
- `transaction_frequency` (Integer) - Number of transactions for customer
- `days_since_first_transaction` (Integer, Optional)
- `average_transaction_value` (Float) - Average transaction value for customer
- `category` (String, Optional)
- `payment_method` (String, Optional)
- `city` (String, Optional)
- `created_at` (DateTime)

### data_quality_metrics
- `id` (Primary Key)
- `ingestion_batch_id` (String, Optional) - Batch identifier
- `total_records_ingested` (Integer)
- `invalid_records` (Integer) - Records with validation errors
- `duplicate_records` (Integer) - Duplicate records skipped
- `cleaned_records` (Integer) - Successfully cleaned records
- `data_quality_percentage` (Float) - Quality percentage (0-100)
- `created_at` (DateTime)

### daily_sales_summary
- `id` (Primary Key)
- `date` (Date, Unique)
- `total_revenue` (Float)
- `total_orders` (Integer)
- `total_quantity` (Float)
- `updated_at` (DateTime)

### customer_summary
- `id` (Primary Key)
- `customer_id` (String, Unique)
- `total_revenue` (Float)
- `total_orders` (Integer)
- `average_order_value` (Float)
- `last_transaction_date` (Date)
- `updated_at` (DateTime)

## 🔧 Configuration

### Database

By default, the application uses SQLite (`flowlytics.db`). To use PostgreSQL:

1. Set the `DATABASE_URL` environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/dbname"
   ```

2. Update `backend/database.py` if needed for your PostgreSQL setup.

### CORS

CORS is configured to allow requests from `http://localhost:3000` and `http://localhost:5173`. To add more origins, update `backend/main.py`.

## 🧪 Data Pipeline Flow

### 1. Ingestion Layer
- **CSV Parsing**: Reads CSV file and validates schema
- **Schema Validation**: Checks for required columns (transaction_date, customer_id, product, quantity, price)
- **Invalid Row Detection**: Logs rows with missing required fields during ingestion
- **Raw Storage**: Stores all data as strings in `raw_transactions` table (preserves original format)

### 2. Cleaning Layer
- **Date Validation**: 
  - Parses dates in multiple formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
  - Detects and rejects invalid dates (e.g., "invalid_date" strings)
  - Logs all date parsing errors
- **Type Conversion**:
  - Converts quantity and price from strings to floats
  - Handles null/empty values gracefully
  - Removes formatting characters ($, commas, spaces)
- **Data Validation**:
  - Ensures required fields are not empty
  - Validates numeric values are parseable
  - Sets negative values to 0 with warning logs
- **Duplicate Detection**:
  - Checks duplicates by `transaction_id` if available
  - Falls back to composite key matching (date, customer, product, quantity, price)
  - Logs all duplicate detections
- **Error Logging**: Detailed logging of all invalid rows with error reasons
- **Output**: Cleaned data stored in `cleaned_transactions` table

### 3. Feature Engineering Layer
Generates ML-ready features for each cleaned transaction:

- **total_amount**: `quantity * price` (already calculated in cleaning)
- **daily_revenue**: Total revenue for the transaction's date
- **customer_lifetime_value**: Cumulative revenue for customer up to transaction date
- **transaction_frequency**: Number of transactions for customer up to transaction date
- **average_transaction_value**: Average transaction value for customer
- **days_since_first_transaction**: Days between customer's first transaction and current transaction

All features stored in `feature_engineering` table for ML model training.

### 4. Transformation Layer
- **Daily Aggregation**: 
  - Groups by date and calculates daily totals
  - Stores in `daily_sales_summary` table
- **Customer Aggregation**:
  - Groups by customer and calculates customer metrics
  - Stores in `customer_summary` table

### 5. Data Quality Tracking
- **Metrics Calculation**: 
  - Tracks total ingested, invalid records, duplicates, cleaned records
  - Calculates data quality percentage: `(valid_records / total_ingested) * 100`
- **Batch Tracking**: Each upload gets a unique batch ID for tracking
- **Storage**: Metrics stored in `data_quality_metrics` table

## 📊 Dataset Design

### CSV Format
The system supports both basic and enhanced CSV formats:

**Basic Format (Minimum Required):**
```csv
transaction_date,customer_id,product,quantity,price
2024-01-15,CUST001,Widget A,5,29.99
```

**Enhanced Format (With Optional Columns):**
```csv
transaction_id,transaction_date,customer_id,product,category,quantity,price,payment_method,city
TXN100001,2024-01-15,CUST001,Widget A,Electronics,5,29.99,UPI,Mumbai
```

### Data Quality Handling

The system handles various data quality issues:

1. **Missing Values**:
   - Required fields (date, customer_id, product): Row is rejected and logged
   - Optional fields (quantity, price): Row is rejected if both are missing
   - Optional metadata (category, city): Stored as NULL if missing

2. **Invalid Dates**:
   - Detects strings like "invalid_date", "null", empty strings
   - Attempts multiple date format parsing
   - Rejects rows with unparseable dates

3. **Invalid Numerics**:
   - Handles null, empty strings, "null" strings
   - Removes formatting ($, commas)
   - Rejects rows with unparseable numbers

4. **Duplicates**:
   - Primary check: `transaction_id` uniqueness
   - Fallback: Composite key matching
   - All duplicates are logged and skipped

## 🔬 Feature Engineering Logic

### Customer Lifetime Value (CLV)
```python
CLV = SUM(total_amount) for all customer transactions up to current date
```
Cumulative revenue from customer's first transaction to current transaction.

### Transaction Frequency
```python
frequency = COUNT(transactions) for customer up to current date
```
Number of transactions the customer has made up to the current transaction date.

### Daily Revenue
```python
daily_revenue = SUM(total_amount) for all transactions on that date
```
Total revenue generated on the transaction's date (includes all customers).

### Average Transaction Value
```python
avg_value = AVG(total_amount) for customer up to current date
```
Average transaction value for the customer up to the current transaction.

### Days Since First Transaction
```python
days = current_transaction_date - customer_first_transaction_date
```
Number of days between customer's first transaction and current transaction.

These features are stored in the `feature_engineering` table and are ready for:
- Machine learning model training
- Customer segmentation
- Predictive analytics
- Churn prediction
- Revenue forecasting

## 🛠️ Development

### Running Tests

To test the API endpoints, you can use the interactive API documentation at `http://localhost:8000/docs` or use tools like Postman or curl.

### Logging

The application uses Python's logging module. Logs are output to the console.

## 📝 Data Quality Metrics

### Understanding Quality Metrics

After each upload, you can check data quality via the API:

**Latest Batch Quality:**
```bash
GET /api/data-quality
```

Returns:
- `total_records_ingested`: Total rows in CSV
- `invalid_records`: Rows rejected due to validation errors
- `duplicate_records`: Duplicate rows skipped
- `cleaned_records`: Successfully processed rows
- `data_quality_percentage`: Quality score (0-100%)

**Aggregate Quality:**
```bash
GET /api/data-quality/aggregate
```

Returns overall statistics across all batches including:
- Total records across all uploads
- Overall quality percentage
- Cleaning success rate

### Quality Calculation

```
Data Quality % = ((Total Ingested - Invalid - Duplicates) / Total Ingested) * 100
Cleaning Success Rate = (Cleaned Records / Total Ingested) * 100
```

## 📝 Notes

- The application ensures idempotent data ingestion by checking for duplicates before inserting
- All date formats are normalized during the cleaning process
- Negative quantities and prices are automatically set to 0
- The pipeline handles errors gracefully and continues processing valid records
- Invalid rows are logged with detailed error messages for debugging
- Feature engineering runs automatically after data cleaning
- Data quality metrics are tracked per batch and aggregated across all batches

## 🤝 Contributing

This is a production-ready template. Feel free to extend it with:
- Additional data sources
- More complex transformations
- Advanced analytics
- Authentication and authorization
- Unit and integration tests
- Docker containerization

## 📄 License

This project is provided as-is for educational and commercial use.

---

**Built with ❤️ using FastAPI, React, and modern data engineering practices**

# Flowlytics
