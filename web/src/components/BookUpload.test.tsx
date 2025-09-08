import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import BookUpload from './BookUpload'

const BookUploadWithRouter = () => (
  <BrowserRouter>
    <BookUpload />
  </BrowserRouter>
)

describe('BookUpload', () => {
  it('renders the page title', () => {
    render(<BookUploadWithRouter />)
    
    expect(screen.getByText('Import New Book')).toBeInTheDocument()
    expect(screen.getByText('Add New Book')).toBeInTheDocument()
  })

  it('renders all required form fields', () => {
    render(<BookUploadWithRouter />)
    
    expect(screen.getByLabelText(/Book Title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Source\/Author \(Optional\)/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Book Contents/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Render Option/i)).toBeInTheDocument()
  })

  it('renders cover art upload options', () => {
    render(<BookUploadWithRouter />)
    
    expect(screen.getByText('Cover Art (Optional)')).toBeInTheDocument()
    expect(screen.getByText('Upload Image')).toBeInTheDocument()
    expect(screen.getByText('Paste Image')).toBeInTheDocument()
  })

  it('renders import button', () => {
    render(<BookUploadWithRouter />)
    
    expect(screen.getByText('Import Book')).toBeInTheDocument()
  })

  it('renders back button', () => {
    render(<BookUploadWithRouter />)
    
    expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument()
  })
})