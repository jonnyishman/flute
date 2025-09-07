import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Typography, Button, Alert, Paper } from '@mui/material'
import { Refresh, Home } from '@mui/icons-material'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Update state with error details
    this.setState({
      error,
      errorInfo
    })

    // Call the optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // Log the error for development
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  handleRefresh = () => {
    // Reset the error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
  }

  handleGoHome = () => {
    // Navigate to home and reset error state
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback UI provided
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Default error UI
      return (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            padding: 3,
            backgroundColor: 'background.default'
          }}
        >
          <Paper 
            elevation={3}
            sx={{
              padding: 4,
              maxWidth: 600,
              textAlign: 'center'
            }}
          >
            <Alert severity="error" sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Something went wrong
              </Typography>
              <Typography variant="body2">
                An unexpected error occurred while rendering this page.
              </Typography>
            </Alert>

            <Box sx={{ mb: 3 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Error details:
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  fontFamily: 'monospace',
                  display: 'block',
                  backgroundColor: 'grey.100',
                  padding: 2,
                  borderRadius: 1,
                  wordBreak: 'break-word',
                  maxHeight: 200,
                  overflow: 'auto'
                }}
              >
                {this.state.error?.message || 'Unknown error'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button
                variant="contained"
                startIcon={<Refresh />}
                onClick={this.handleRefresh}
              >
                Try Again
              </Button>
              <Button
                variant="outlined"
                startIcon={<Home />}
                onClick={this.handleGoHome}
              >
                Go Home
              </Button>
            </Box>

            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <Box sx={{ mt: 3, textAlign: 'left' }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Component stack:
                </Typography>
                <Typography 
                  variant="caption" 
                  sx={{ 
                    fontFamily: 'monospace',
                    display: 'block',
                    backgroundColor: 'grey.100',
                    padding: 2,
                    borderRadius: 1,
                    whiteSpace: 'pre-wrap',
                    fontSize: '0.75rem',
                    maxHeight: 300,
                    overflow: 'auto'
                  }}
                >
                  {this.state.errorInfo.componentStack}
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      )
    }

    // No error, render children normally
    return this.props.children
  }
}

export default ErrorBoundary

// Higher-order component for wrapping components with error boundary
export const withErrorBoundary = <P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode
) => {
  const WrappedComponent = (props: P) => (
    <ErrorBoundary fallback={fallback}>
      <Component {...props} />
    </ErrorBoundary>
  )
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`
  
  return WrappedComponent
}