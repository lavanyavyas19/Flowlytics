import React from 'react'
import { formatNumber } from '../utils/currency'

function DataQuality({ data }) {
  // Debug logging
  console.log('🔍 DataQuality component render - received data:', data)
  console.log('🔍 DataQuality data type:', typeof data)
  console.log('🔍 DataQuality data keys:', data ? Object.keys(data) : 'null/undefined')
  
  // Get values from API response, using fallbacks for backward compatibility
  // Always use defaults if data is null/undefined
  const totalRecords = data?.total_records || data?.total_records_ingested || 0
  const cleanedRecords = data?.cleaned_records || 0
  const droppedRecords = data?.dropped_records || (data?.invalid_records || 0) + (data?.duplicate_records || 0)
  const qualityPercentage = data?.data_quality_percentage || 0.0
  const invalidRecords = data?.invalid_records || 0
  const duplicateRecords = data?.duplicate_records || 0

  console.log('📊 DataQuality computed values:', { 
    totalRecords, 
    cleanedRecords, 
    droppedRecords, 
    qualityPercentage,
    invalidRecords,
    duplicateRecords,
    'data exists?': !!data,
    'total_records in data?': data?.total_records,
    'cleaned_records in data?': data?.cleaned_records
  })
  
  // Check if values are non-zero (which means data exists)
  const hasRealData = totalRecords > 0 || cleanedRecords > 0 || droppedRecords > 0
  if (hasRealData) {
    console.log('✅ DataQuality has REAL DATA - should display values')
  } else {
    console.log('⚠️ DataQuality has ZERO values')
  }
  
  // Debug: Only warn if we expected data but got zeros
  // (Don't warn on initial load when no data exists yet)
  const hasUploadedData = data && (
    data.total_records > 0 || 
    data.total_records_ingested > 0 || 
    data.cleaned_records > 0
  )
  
  if (hasUploadedData && totalRecords === 0 && cleanedRecords === 0 && droppedRecords === 0) {
    console.warn('⚠️ WARNING: Expected data but all values are zero!')
    console.warn('Received data object:', data)
  }

  // Show loading skeleton only if data is explicitly null (not yet fetched)
  if (data === null) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Data Quality Summary
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="animate-pulse"
            >
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  const qualityCards = [
    {
      title: 'Total Records',
      value: formatNumber(totalRecords),
      icon: (
        <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    {
      title: 'Cleaned Records',
      value: formatNumber(cleanedRecords),
      icon: (
        <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      bgColor: 'bg-green-50',
      textColor: 'text-green-600'
    },
    {
      title: 'Dropped Records',
      value: formatNumber(droppedRecords),
      icon: (
        <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ),
      bgColor: 'bg-red-50',
      textColor: 'text-red-600'
    },
    {
      title: 'Data Quality (%)',
      value: `${qualityPercentage.toFixed(2)}%`,
      icon: (
        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600'
    }
  ]

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Data Quality Summary
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {qualityCards.map((card, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-600">{card.title}</h3>
              <div className={card.bgColor + ' p-2 rounded-lg'}>{card.icon}</div>
            </div>
            <p className={`text-2xl font-bold ${card.textColor}`}>{card.value}</p>
          </div>
        ))}
      </div>
      {(invalidRecords > 0 || duplicateRecords > 0) && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <span>Invalid Records: <span className="font-semibold text-red-600">{formatNumber(invalidRecords)}</span></span>
            <span>Duplicates: <span className="font-semibold text-orange-600">{formatNumber(duplicateRecords)}</span></span>
          </div>
        </div>
      )}
    </div>
  )
}

export default DataQuality

