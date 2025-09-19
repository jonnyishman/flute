import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import apiClient, { api } from './client'
import type {
  CreateBookRequest,
  BookSummariesRequest,
  CreateTermRequest,
  UpdateTermRequest,
  LearningStatus,
  SortOption,
  SortOrder,
} from './types'

// Mock console.error for testing error handling
const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Health Check', () => {
    it('should successfully fetch health status', async () => {
      const mockResponse = { status: 'healthy', message: 'API is running' }
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => mockResponse,
      })

      const result = await api.health.check()

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/health'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          credentials: 'include',
        })
      )
      expect(result).toEqual(mockResponse)
    })

    it('should handle health check failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Internal Server Error', msg: 'Service unavailable' }),
      })

      await expect(api.health.check()).rejects.toThrow('Service unavailable')
      expect(consoleErrorSpy).toHaveBeenCalledWith('[API Error] Service unavailable', expect.objectContaining({
        variant: 'error',
      }))
    })
  })

  describe('Books API', () => {
    describe('createBook', () => {
      it('should create a book successfully', async () => {
        const request: CreateBookRequest = {
          title: 'Test Book',
          language_id: 1,
          chapters: ['Chapter 1 content', 'Chapter 2 content'],
          source: 'test-source',
          cover_art_filepath: '/path/to/cover.jpg',
        }
        const mockResponse = { book_id: 123 }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 201,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => mockResponse,
        })

        const result = await api.books.create(request)

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/books'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(request),
          })
        )
        expect(result).toEqual(mockResponse)
      })

      it('should handle book creation errors', async () => {
        const request: CreateBookRequest = {
          title: 'Test Book',
          language_id: 999,
          chapters: [],
        }

        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 404,
          json: async () => ({ error: 'Not Found', msg: 'invalid language_id: 999' }),
        })

        await expect(api.books.create(request)).rejects.toThrow('invalid language_id: 999')
        expect(consoleErrorSpy).toHaveBeenCalledWith('[API Error] invalid language_id: 999', expect.objectContaining({
          variant: 'error',
        }))
      })
    })

    describe('getBookSummaries', () => {
      it('should fetch book summaries with all parameters', async () => {
        const request: BookSummariesRequest = {
          language_id: 1,
          sort_option: SortOption.TITLE,
          sort_order: SortOrder.ASC,
          page: 1,
          per_page: 10,
        }
        const mockResponse = {
          summaries: [
            {
              book_id: 1,
              title: 'Book 1',
              cover_art_filepath: '/cover1.jpg',
              total_terms: 1000,
              known_terms: 500,
              learning_terms: 300,
              unknown_terms: 200,
            },
          ],
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => mockResponse,
        })

        const result = await api.books.getSummaries(request)

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/books?language_id=1&sort_option=title&sort_order=asc&page=1&per_page=10'),
          expect.objectContaining({
            method: 'GET',
          })
        )
        expect(result).toEqual(mockResponse)
      })

      it('should handle partial parameters correctly', async () => {
        const request: BookSummariesRequest = {
          language_id: 1,
        }
        const mockResponse = { summaries: [] }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 200,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => mockResponse,
        })

        await api.books.getSummaries(request)

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/books?language_id=1'),
          expect.any(Object)
        )
      })
    })
  })

  describe('Terms API', () => {
    describe('createTerm', () => {
      it('should create a term successfully', async () => {
        const request: CreateTermRequest = {
          term: 'test',
          language_id: 1,
          status: 'learning' as LearningStatus,
          learning_stage: 2,
          display: 'Test',
          translation: 'prueba',
        }
        const mockResponse = { term_id: 456 }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 201,
          headers: new Headers({ 'content-type': 'application/json' }),
          json: async () => mockResponse,
        })

        const result = await api.terms.create(request)

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/terms'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(request),
          })
        )
        expect(result).toEqual(mockResponse)
      })

      it('should handle term creation validation errors', async () => {
        const request: CreateTermRequest = {
          term: 'test',
          language_id: 1,
          status: 'learning' as LearningStatus,
          display: 'INVALID',
        }

        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 400,
          json: async () => ({ error: 'Bad Request', msg: "display must match the term's normalized form" }),
        })

        await expect(api.terms.create(request)).rejects.toThrow("display must match the term's normalized form")
      })
    })

    describe('updateTerm', () => {
      it('should update a term successfully', async () => {
        const termId = 123
        const request: UpdateTermRequest = {
          status: 'known' as LearningStatus,
          learning_stage: 5,
          translation: 'updated translation',
        }

        mockFetch.mockResolvedValueOnce({
          ok: true,
          status: 204,
          headers: new Headers(),
        })

        await api.terms.update(termId, request)

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining(`/api/terms/${termId}`),
          expect.objectContaining({
            method: 'PATCH',
            body: JSON.stringify(request),
          })
        )
      })

      it('should handle term not found error', async () => {
        const termId = 999
        const request: UpdateTermRequest = {
          status: 'known' as LearningStatus,
        }

        mockFetch.mockResolvedValueOnce({
          ok: false,
          status: 404,
          json: async () => ({ error: 'Not Found', msg: 'invalid term_id: 999' }),
        })

        await expect(api.terms.update(termId, request)).rejects.toThrow('invalid term_id: 999')
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'))

      await expect(api.health.check()).rejects.toThrow('Failed to fetch')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[API Error] Network error. Please check your connection and try again.',
        expect.objectContaining({
          variant: 'error',
        })
      )
    })

    it('should handle non-JSON error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => { throw new Error('Invalid JSON') },
        text: async () => 'Internal Server Error',
      })

      await expect(api.health.check()).rejects.toThrow('Request failed with status 500')
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        '[API Error] Request failed with status 500',
        expect.objectContaining({
          variant: 'error',
        })
      )
    })

    it('should handle empty response body correctly', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 204,
        headers: new Headers({ 'content-length': '0' }),
      })

      const result = await apiClient.updateTerm(1, { status: 'known' as LearningStatus })
      expect(result).toEqual({})
    })
  })

  describe('URL Building', () => {
    it('should build URLs correctly with base path', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ status: 'ok' }),
      })

      await api.health.check()

      const callArgs = mockFetch.mock.calls[0]
      const url = new URL(callArgs[0])
      expect(url.pathname).toBe('/api/health')
    })

    it('should handle query parameters with null and undefined values', async () => {
      const request: BookSummariesRequest = {
        language_id: 1,
        sort_option: null,
        sort_order: undefined as any,
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        headers: new Headers({ 'content-type': 'application/json' }),
        json: async () => ({ summaries: [] }),
      })

      await api.books.getSummaries(request)

      const callArgs = mockFetch.mock.calls[0]
      const url = new URL(callArgs[0])
      expect(url.searchParams.has('sort_option')).toBe(false)
      expect(url.searchParams.has('sort_order')).toBe(false)
      expect(url.searchParams.get('language_id')).toBe('1')
    })
  })
})