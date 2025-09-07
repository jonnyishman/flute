import { render } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import PWABadge from './PWABadge'

// Mock the workbox-window module
vi.mock('workbox-window', () => ({
  Workbox: vi.fn(() => ({
    register: vi.fn(),
    addEventListener: vi.fn(),
    messageSkipWaiting: vi.fn()
  }))
}))

describe('PWABadge Smoke Tests', () => {
  it('renders without crashing', () => {
    const { container } = render(<PWABadge />)
    expect(container).toBeInTheDocument()
  })

  it('renders the component successfully', () => {
    // This test just ensures the component can be instantiated
    // without throwing errors, which is sufficient for smoke testing
    expect(() => render(<PWABadge />)).not.toThrow()
  })
})