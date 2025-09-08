import { useAtom } from 'jotai'
import { userPreferencesAtom, UserPreferences } from '../store/atoms'

export const useUserPreferences = () => {
  const [preferences, setPreferences] = useAtom(userPreferencesAtom)
  
  const updatePreferences = (updates: Partial<UserPreferences>) => {
    setPreferences(prev => ({
      ...prev,
      ...updates
    }))
  }
  
  return {
    preferences,
    updatePreferences,
    setPreferences,
  }
}

export default useUserPreferences