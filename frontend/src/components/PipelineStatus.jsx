import React from 'react'

function PipelineStatus({ pipelineStatus }) {
  // Default status - all complete if data exists, or all pending if no data
  const defaultStatus = {
    ingestion: pipelineStatus?.ingestion !== false,
    cleaning: pipelineStatus?.cleaning !== false,
    transformation: pipelineStatus?.transformation !== false,
    aggregation: pipelineStatus?.aggregation !== false
  }

  const stages = [
    {
      id: 'ingestion',
      label: 'Ingestion',
      description: 'CSV parsing and raw data storage',
      status: defaultStatus.ingestion
    },
    {
      id: 'cleaning',
      label: 'Cleaning',
      description: 'Data validation and cleaning',
      status: defaultStatus.cleaning
    },
    {
      id: 'transformation',
      label: 'Transformation',
      description: 'Feature engineering and calculations',
      status: defaultStatus.transformation
    },
    {
      id: 'aggregation',
      label: 'Aggregation',
      description: 'Daily and customer summaries',
      status: defaultStatus.aggregation
    }
  ]

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Pipeline Stage Status
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stages.map((stage) => (
          <div
            key={stage.id}
            className={`border rounded-lg p-4 ${
              stage.status
                ? 'border-green-200 bg-green-50'
                : 'border-gray-200 bg-gray-50'
            }`}
          >
            <div className="flex items-center gap-3 mb-2">
              {stage.status ? (
                <svg
                  className="w-5 h-5 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              )}
              <span
                className={`font-semibold ${
                  stage.status ? 'text-green-700' : 'text-gray-500'
                }`}
              >
                {stage.status ? '✓' : '○'} {stage.label}
              </span>
            </div>
            <p className="text-xs text-gray-600 mt-1">{stage.description}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PipelineStatus

