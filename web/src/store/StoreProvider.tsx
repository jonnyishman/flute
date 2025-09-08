import { Provider } from 'jotai'
import { ReactNode } from 'react'

interface StoreProviderProps {
  children: ReactNode
}

export const StoreProvider = ({ children }: StoreProviderProps) => {
  return <Provider>{children}</Provider>
}

export default StoreProvider