import { useToast } from "vue-toastification"

// Create a toast instance
const toast = useToast()

// Toast utility functions
export const showToast = {
  success: (message, options = {}) => {
    toast.success(message, {
      timeout: 4000,
      ...options
    })
  },
  
  error: (message, options = {}) => {
    toast.error(message, {
      timeout: 6000,
      ...options
    })
  },
  
  warning: (message, options = {}) => {
    toast.warning(message, {
      timeout: 5000,
      ...options
    })
  },
  
  info: (message, options = {}) => {
    toast.info(message, {
      timeout: 4000,
      ...options
    })
  },
  
  // Specific toast types for common actions
  loginSuccess: (username) => {
    toast.success(`Welcome back, ${username}! 🎉`, {
      timeout: 4000,
      icon: "🚗"
    })
  },
  
  loginError: (message = "Login failed. Please check your credentials.") => {
    toast.error(message, {
      timeout: 6000,
      icon: "❌"
    })
  },
  
  logoutSuccess: () => {
    toast.info("You have been logged out successfully. 👋", {
      timeout: 3000,
      icon: "🚪"
    })
  },
  
  bookingSuccess: (spotNumber, location) => {
    toast.success(`Parking spot ${spotNumber} at ${location} booked successfully! 🅿️`, {
      timeout: 5000,
      icon: "✅"
    })
  },
  
  bookingError: (message = "Failed to book parking spot. Please try again.") => {
    toast.error(message, {
      timeout: 6000,
      icon: "❌"
    })
  },
  
  paymentSuccess: (amount) => {
    toast.success(`Payment of $${amount} processed successfully! 💳`, {
      timeout: 5000,
      icon: "💰"
    })
  },
  
  paymentError: (message = "Payment processing failed. Please try again.") => {
    toast.error(message, {
      timeout: 6000,
      icon: "💳"
    })
  },
  
  profileUpdated: () => {
    toast.success("Profile updated successfully! ✨", {
      timeout: 4000,
      icon: "👤"
    })
  },
  
  profileError: (message = "Failed to update profile. Please try again.") => {
    toast.error(message, {
      timeout: 5000,
      icon: "❌"
    })
  },
  
  spotReleased: (spotNumber, cost) => {
    toast.success(`Spot ${spotNumber} released. Total cost: $${cost} 🚗`, {
      timeout: 5000,
      icon: "🏁"
    })
  },
  
  adminAction: (action, target) => {
    toast.success(`${action} ${target} successfully! 🔧`, {
      timeout: 4000,
      icon: "⚙️"
    })
  },
  
  adminError: (message) => {
    toast.error(`Admin Error: ${message}`, {
      timeout: 6000,
      icon: "🚨"
    })
  },
  
  validationError: (message) => {
    toast.warning(`Validation Error: ${message}`, {
      timeout: 5000,
      icon: "⚠️"
    })
  },
  
  networkError: () => {
    toast.error("Network error. Please check your connection and try again.", {
      timeout: 6000,
      icon: "🌐"
    })
  },
  
  loading: (message = "Processing...") => {
    return toast.info(message, {
      timeout: false, // Don't auto-dismiss
      closeOnClick: false,
      draggable: false,
      icon: "⏳"
    })
  },
  
  dismiss: (toastId) => {
    if (toastId) {
      toast.dismiss(toastId)
    } else {
      toast.clear()
    }
  }
}

// Export individual functions for convenience
export const {
  success,
  error,
  warning,
  info,
  loginSuccess,
  loginError,
  logoutSuccess,
  bookingSuccess,
  bookingError,
  paymentSuccess,
  paymentError,
  profileUpdated,
  profileError,
  spotReleased,
  adminAction,
  adminError,
  validationError,
  networkError,
  loading,
  dismiss
} = showToast

export default showToast
