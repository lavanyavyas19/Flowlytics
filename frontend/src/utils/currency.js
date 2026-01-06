/**
 * Currency formatting utilities for INR
 * Reusable functions for formatting Indian Rupees throughout the application
 */

/**
 * Format amount as Indian Rupees (₹)
 * Uses Indian number formatting (en-IN locale)
 * 
 * @param {number} amount - The amount to format
 * @param {object} options - Formatting options
 * @returns {string} Formatted currency string (e.g., "₹1,23,456.78")
 */
export const formatINR = (amount, options = {}) => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '₹0.00'
  }

  const {
    minimumFractionDigits = 2,
    maximumFractionDigits = 2,
    notation = 'standard'
  } = options

  // Validate fraction digits range (0-20)
  const minDigits = Math.max(0, Math.min(20, minimumFractionDigits))
  const maxDigits = Math.max(0, Math.min(20, maximumFractionDigits))

  // For compact notation, fraction digits are limited to 0-2
  const formatOptions = {
    style: 'currency',
    currency: 'INR',
    notation
  }

  // Only add fraction digits if not using compact notation, or use safe values
  if (notation === 'compact') {
    formatOptions.maximumFractionDigits = Math.min(2, maxDigits)
  } else {
    formatOptions.minimumFractionDigits = minDigits
    formatOptions.maximumFractionDigits = maxDigits
  }

  try {
    return new Intl.NumberFormat('en-IN', formatOptions).format(amount)
  } catch (error) {
    // Fallback formatting if there's an error
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
  }
}

/**
 * Format amount as INR with compact notation (e.g., ₹1.23L, ₹12.3K)
 * 
 * @param {number} amount - The amount to format
 * @returns {string} Formatted currency string in compact notation
 */
export const formatINRCompact = (amount) => {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '₹0'
  }

  try {
    // For compact notation with currency, use a different approach
    // Compact notation with currency style has limitations, so we format it differently
    const formatter = new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      notation: 'compact',
      maximumFractionDigits: 2
    })
    return formatter.format(amount)
  } catch (error) {
    // Fallback to standard formatting if compact fails
    return formatINR(amount)
  }
}

/**
 * Format number with Indian locale (no currency symbol)
 * Useful for non-currency numbers
 * 
 * @param {number} value - The number to format
 * @returns {string} Formatted number string (e.g., "1,23,456")
 */
export const formatNumber = (value) => {
  if (value === null || value === undefined || isNaN(value)) {
    return '0'
  }

  return new Intl.NumberFormat('en-IN').format(value)
}

