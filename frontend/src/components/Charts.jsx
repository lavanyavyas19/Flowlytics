import React from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { formatINR, formatINRCompact } from '../utils/currency'

function Charts({ dailyRevenue, topCustomers }) {
  // Format data for charts
  const formatDailyRevenue = () => {
    if (!dailyRevenue || dailyRevenue.length === 0) {
      return []
    }
    return dailyRevenue.map((item) => ({
      date: new Date(item.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
      }),
      revenue: parseFloat(item.revenue.toFixed(2))
    }))
  }

  const formatTopCustomers = () => {
    if (!topCustomers || topCustomers.length === 0) {
      return []
    }
    return topCustomers.map((item) => ({
      customer: item.customer_id.length > 10
        ? item.customer_id.substring(0, 10) + '...'
        : item.customer_id,
      revenue: parseFloat(item.revenue.toFixed(2))
    }))
  }

  const revenueData = formatDailyRevenue()
  const customersData = formatTopCustomers()

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Daily Revenue Trend */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Daily Revenue Trend (₹)
        </h3>
        {revenueData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <p>No revenue data available. Upload a CSV file to see trends.</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                angle={-45}
                textAnchor="end"
                height={80}
                interval="preserveStartEnd"
              />
              <YAxis
                tickFormatter={(value) => {
                  if (value === null || value === undefined || isNaN(value)) return '₹0'
                  return formatINRCompact(value)
                }}
              />
              <Tooltip
                formatter={(value) => formatINR(value)}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#0ea5e9"
                strokeWidth={2}
                name="Revenue (₹)"
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Top Customers by Revenue */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Top Customers by Revenue (₹)
        </h3>
        {customersData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-gray-500">
            <p>
              No customer data available. Upload a CSV file to see top customers.
            </p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={customersData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                type="number"
                tickFormatter={(value) => {
                  if (value === null || value === undefined || isNaN(value)) return '₹0'
                  return formatINRCompact(value)
                }}
              />
              <YAxis
                type="category"
                dataKey="customer"
                width={100}
              />
              <Tooltip
                formatter={(value) => formatINR(value)}
              />
              <Legend />
              <Bar
                dataKey="revenue"
                fill="#10b981"
                name="Revenue (₹)"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

export default Charts

