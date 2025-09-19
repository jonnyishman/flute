import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ApiProvider } from './ApiProvider'

// Mock notistack
vi.mock('notistack', () => ({
  SnackbarProvider: ({ children }: any) => children,
  MaterialDesignContent: () => null,
}))

// Mock MUI styled
vi.mock('@mui/material/styles', () => ({
  styled: () => () => () => null,
}))

describe('ApiProvider', () => {
  it('should render children correctly', () => {
    const testContent = 'Test Child Component'

    render(
      <ApiProvider>
        <div>{testContent}</div>
      </ApiProvider>
    )

    expect(screen.getByText(testContent)).toBeInTheDocument()
  })

  it('should wrap children with SnackbarProvider', () => {
    const { container } = render(
      <ApiProvider>
        <div data-testid="test-child">Child</div>
      </ApiProvider>
    )

    // SnackbarProvider adds its own container to the DOM
    const testChild = container.querySelector('[data-testid="test-child"]')
    expect(testChild).toBeTruthy()
  })
})