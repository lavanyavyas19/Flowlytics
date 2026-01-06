import React, { useState, useEffect } from 'react'
import axios from 'axios'
import KPI from '../components/KPI'
import Charts from '../components/Charts'
import DataQuality from '../components/DataQuality'
import PipelineStatus from '../components/PipelineStatus'

const API_BASE_URL = 'http://localhost:8000/api'

function Dashboard() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState(null)
  const [kpis, setKpis] = useState(null)
  const [dailyRevenue, setDailyRevenue] = useState([])
  const [topCustomers, setTopCustomers] = useState([])
  const [dataQuality, setDataQuality] = useState({
    total_records: 0,
    total_records_ingested: 0,
    cleaned_records: 0,
    dropped_records: 0,
    invalid_records: 0,
    duplicate_records: 0,
    data_quality_percentage: 0.0
  })
  const [pipelineStatus, setPipelineStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const promises = [
        axios.get(`${API_BASE_URL}/kpis`),
        axios.get(`${API_BASE_URL}/daily-revenue`),
        axios.get(`${API_BASE_URL}/top-customers?limit=10`)
      ]
      
      // Try to get data quality, but don't fail if it doesn't exist
      // Silently handle 404 - it's OK if endpoint doesn't exist yet
      const qualityPromise = axios.get(`${API_BASE_URL}/data-quality`)
        .catch((error) => {
          // Silently handle 404 - endpoint might not be registered yet
          if (error.response?.status === 404) {
            return { data: null }
          }
          // Log other errors but don't fail
          if (error.response?.status >= 500) {
            console.warn('Data quality endpoint server error (non-critical):', error.response?.status)
            return { data: null }
          }
          throw error
        })
      
      promises.push(qualityPromise)
      
      const [kpisRes, revenueRes, customersRes, qualityRes] = await Promise.all(promises)

      console.log('Dashboard data fetched:', {
        kpis: kpisRes.data,
        revenue: revenueRes.data?.length,
        customers: customersRes.data?.length,
        quality: qualityRes?.data
      })

      setKpis(kpisRes.data)
      setDailyRevenue(revenueRes.data)
      setTopCustomers(customersRes.data)
      
      if (qualityRes && qualityRes.data) {
        // Ensure we have all required fields - always set data even if zeros
        const qualityData = {
          ...qualityRes.data,
          total_records: qualityRes.data.total_records || qualityRes.data.total_records_ingested || 0,
          dropped_records: qualityRes.data.dropped_records || 
            (qualityRes.data.invalid_records || 0) + (qualityRes.data.duplicate_records || 0)
        }
        console.log('Setting data quality from API:', qualityData)
        setDataQuality(qualityData)
        // Determine pipeline status based on data availability
        setPipelineStatus({
          ingestion: qualityData.total_records > 0,
          cleaning: qualityData.cleaned_records > 0,
          transformation: kpisRes.data.total_orders > 0,
          aggregation: revenueRes.data.length > 0
        })
      } else {
        // No quality data from API - PRESERVE existing data quality
        // DO NOT set zeros if we already have real data (from upload)
        setDataQuality((prevData) => {
          // If previous data has non-zero values, ALWAYS keep it
          if (prevData && (prevData.total_records > 0 || prevData.cleaned_records > 0 || prevData.dropped_records > 0)) {
            console.log('✅ Preserving existing data quality data (has real values):', prevData)
            return prevData
          }
          // Only set zeros if we truly have no data
          console.log('⚠️ No existing data quality - setting zeros (first load, no upload yet)')
          return {
            total_records: 0,
            total_records_ingested: 0,
            cleaned_records: 0,
            dropped_records: 0,
            invalid_records: 0,
            duplicate_records: 0,
            data_quality_percentage: 0.0
          }
        })
        // Determine pipeline status from existing data
        const hasData = kpisRes.data && kpisRes.data.total_orders > 0
        setPipelineStatus({
          ingestion: hasData,
          cleaning: hasData,
          transformation: hasData,
          aggregation: revenueRes.data && revenueRes.data.length > 0
        })
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setUploadMessage({
        type: 'error',
        text: 'Failed to load dashboard data'
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      if (selectedFile.type === 'text/csv' || selectedFile.name.endsWith('.csv')) {
        setFile(selectedFile)
        setUploadMessage(null)
      } else {
        setUploadMessage({
          type: 'error',
          text: 'Please select a CSV file'
        })
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setUploadMessage({
        type: 'error',
        text: 'Please select a file first'
      })
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      setUploading(true)
      setUploadMessage(null)

      console.log('Uploading file to:', `${API_BASE_URL}/upload`)
      
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      console.log('=== UPLOAD RESPONSE RECEIVED ===')
      console.log('Full response:', response)
      console.log('Response data:', response.data)
      console.log('Response data keys:', Object.keys(response.data || {}))
      
      // Validate response has required fields
      if (!response || !response.data) {
        console.error('❌ ERROR: Upload response has no data!')
        throw new Error('Upload response is missing data')
      }
      
      // Validate we have the essential fields
      if (response.data.records_processed === undefined) {
        console.error('❌ ERROR: Upload response missing records_processed!')
        console.error('Available fields:', Object.keys(response.data))
        throw new Error('Upload response missing required fields')
      }

      const uploadData = response.data
      console.log('Upload data fields:', {
        records_processed: uploadData.records_processed,
        records_cleaned: uploadData.records_cleaned,
        invalid_records: uploadData.invalid_records,
        duplicates_skipped: uploadData.duplicates_skipped,
        dropped_records: uploadData.dropped_records,
        data_quality_percentage: uploadData.data_quality_percentage
      })

      setUploadMessage({
        type: 'success',
        text: `Success! Processed ${uploadData.records_processed || 0} records, cleaned ${uploadData.records_cleaned || 0} records, and transformed ${uploadData.records_transformed || 0} summaries. Data quality: ${uploadData.data_quality_percentage?.toFixed(2) || 0}%`
      })
      
      // Update pipeline status after upload
      setPipelineStatus({
        ingestion: true,
        cleaning: (uploadData.records_cleaned || 0) > 0,
        transformation: (uploadData.features_generated || 0) > 0,
        aggregation: (uploadData.records_transformed || 0) > 0
      })
      
      // Calculate data quality metrics from upload response
      const totalRecords = uploadData.records_processed || 0
      const cleanedRecords = uploadData.records_cleaned || 0
      const invalidRecords = uploadData.invalid_records || 0
      const duplicateRecords = uploadData.duplicates_skipped || 0
      const droppedRecords = uploadData.dropped_records || (invalidRecords + duplicateRecords)
      const qualityPercentage = uploadData.data_quality_percentage || 0.0
      
      const qualityData = {
        total_records: totalRecords,
        total_records_ingested: totalRecords,
        cleaned_records: cleanedRecords,
        dropped_records: droppedRecords,
        invalid_records: invalidRecords,
        duplicate_records: duplicateRecords,
        data_quality_percentage: qualityPercentage
      }
      
      console.log('=== CALCULATED QUALITY DATA ===')
      console.log(JSON.stringify(qualityData, null, 2))
      console.log('About to call setDataQuality with:', qualityData)
      
      // Set data quality IMMEDIATELY - this ensures it's displayed
      setDataQuality(qualityData)
      
      // Verify it was set (will log on next render)
      setTimeout(() => {
        console.log('✅ Data quality should be set. Check component logs above.')
      }, 100)
      
      // Refresh other dashboard data (KPIs, charts) but preserve data quality
      // Wait a moment to ensure data quality state is set first
      await new Promise(resolve => setTimeout(resolve, 50))
      
      try {
        const [kpisRes, revenueRes, customersRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/kpis`),
          axios.get(`${API_BASE_URL}/daily-revenue`),
          axios.get(`${API_BASE_URL}/top-customers?limit=10`)
        ])

        console.log('✅ Refreshed KPIs, revenue, and customers after upload')
        console.log('✅ Data quality should still be:', qualityData)
        
        setKpis(kpisRes.data)
        setDailyRevenue(revenueRes.data)
        setTopCustomers(customersRes.data)
        
        // DO NOT overwrite data quality - explicitly preserve it
        // Verify data quality is still set correctly
        setDataQuality((currentData) => {
          // If we have the upload data, keep it
          if (qualityData.total_records > 0) {
            console.log('✅ Preserving upload data quality:', qualityData)
            return qualityData
          }
          // Otherwise keep current (shouldn't happen, but defensive)
          console.log('⚠️ No upload data, keeping current:', currentData)
          return currentData
        })
      } catch (error) {
        console.warn('Error refreshing dashboard data (non-critical):', error)
        // Don't fail the upload if refresh fails - we already have the data
        // Data quality is already set above
      }

      setFile(null)
      // Reset file input
      document.getElementById('csv-upload').value = ''
    } catch (error) {
      console.error('Upload error:', error)
      console.error('Error response:', error.response?.data)
      setUploadMessage({
        type: 'error',
        text: error.response?.data?.detail || `Failed to upload file: ${error.message}`
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Flowlytics</h1>
              <p className="text-sm text-gray-600 mt-1">
                End-to-End Data Pipeline & Analytics Platform
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="h-3 w-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">System Online</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Upload Transaction Data
          </h2>
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label
                htmlFor="csv-upload"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Select CSV File
              </label>
              <input
                id="csv-upload"
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
              {file && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: <span className="font-medium">{file.name}</span>
                </p>
              )}
            </div>
            <button
              onClick={handleUpload}
              disabled={!file || uploading}
              className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </div>

          {/* Upload Message */}
          {uploadMessage && (
            <div
              className={`mt-4 p-4 rounded-md ${
                uploadMessage.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              <p className="text-sm">{uploadMessage.text}</p>
            </div>
          )}
        </div>

        {/* KPI Cards */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading dashboard data...</p>
          </div>
        ) : (
          <>
            <PipelineStatus pipelineStatus={pipelineStatus} />
            <DataQuality data={dataQuality} />
            <KPI data={kpis} />
            <Charts dailyRevenue={dailyRevenue} topCustomers={topCustomers} />
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Flowlytics © 2024 - Data Pipeline & Analytics Platform
          </p>
        </div>
      </footer>
    </div>
  )
}

export default Dashboard

