// import { SnackbarProvider } from 'notistack'
// import { Alert } from '@mui/material'
import type { ReactNode } from 'react'

interface ApiProviderProps {
  children: ReactNode
}

// Temporary implementation until notistack is installed
// This will be replaced with SnackbarProvider from notistack
export function ApiProvider({ children }: ApiProviderProps) {
  // Once notistack is installed, uncomment the following:
  // return (
  //   <SnackbarProvider
  //     maxSnack={3}
  //     autoHideDuration={5000}
  //     anchorOrigin={{
  //       vertical: 'bottom',
  //       horizontal: 'center',
  //     }}
  //     Components={{
  //       error: (props) => <Alert severity="error" {...props} />,
  //       success: (props) => <Alert severity="success" {...props} />,
  //       warning: (props) => <Alert severity="warning" {...props} />,
  //       info: (props) => <Alert severity="info" {...props} />,
  //     }}
  //   >
  //     {children}
  //   </SnackbarProvider>
  // )

  // Temporary passthrough until notistack is installed
  return <>{children}</>
}