import { renderHook, act } from '@testing-library/react'
import { useDebounce, useDebouncedCallback } from '../../hooks/useDebounce'

// Mock timers
jest.useFakeTimers()

describe('useDebounce', () => {
  afterEach(() => {
    jest.clearAllTimers()
  })

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500))
    
    expect(result.current).toBe('initial')
  })

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    )
    
    expect(result.current).toBe('initial')
    
    // Change value
    rerender({ value: 'updated', delay: 500 })
    expect(result.current).toBe('initial') // Should still be initial
    
    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500)
    })
    
    expect(result.current).toBe('updated')
  })

  it('should reset timer on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    )
    
    // First change
    rerender({ value: 'change1', delay: 500 })
    
    // Fast forward partway
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    expect(result.current).toBe('initial')
    
    // Second change (should reset timer)
    rerender({ value: 'change2', delay: 500 })
    
    // Fast forward the original remaining time
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    expect(result.current).toBe('initial') // Should still be initial
    
    // Fast forward the full delay from second change
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    expect(result.current).toBe('change2')
  })
})

describe('useDebouncedCallback', () => {
  afterEach(() => {
    jest.clearAllTimers()
  })

  it('should debounce callback execution', () => {
    const mockCallback = jest.fn()
    const { result } = renderHook(() => useDebouncedCallback(mockCallback, 500))
    
    // Call the debounced callback
    act(() => {
      result.current('arg1', 'arg2')
    })
    
    expect(mockCallback).not.toHaveBeenCalled()
    
    // Fast forward time
    act(() => {
      jest.advanceTimersByTime(500)
    })
    
    expect(mockCallback).toHaveBeenCalledWith('arg1', 'arg2')
    expect(mockCallback).toHaveBeenCalledTimes(1)
  })

  it('should cancel previous callback on rapid calls', () => {
    const mockCallback = jest.fn()
    const { result } = renderHook(() => useDebouncedCallback(mockCallback, 500))
    
    // First call
    act(() => {
      result.current('call1')
    })
    
    // Fast forward partway
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    // Second call (should cancel first)
    act(() => {
      result.current('call2')
    })
    
    // Fast forward remaining time from first call
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    expect(mockCallback).not.toHaveBeenCalled()
    
    // Fast forward full delay from second call
    act(() => {
      jest.advanceTimersByTime(250)
    })
    
    expect(mockCallback).toHaveBeenCalledWith('call2')
    expect(mockCallback).toHaveBeenCalledTimes(1)
  })
})