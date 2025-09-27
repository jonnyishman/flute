import { enqueueSnackbar } from 'notistack'
import type {
  ApiError,
  BookCountRequest,
  BookCountResponse,
  BookSummariesRequest,
  BookSummariesResponse,
  CreateBookRequest,
  CreateBookResponse,
  CreateTermRequest,
  HealthCheckResponse,
  TermIdResponse,
  UpdateTermRequest,
} from './types'

// Configure base URL from environment or use default
const BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Type for HTTP methods
type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'

// Type for request options
interface RequestOptions {
  method: HttpMethod
  headers?: Record<string, string>
  body?: unknown
  params?: Record<string, unknown>
}

// Type for API response
interface ApiResponse<T> {
  data: T
  status: number
  headers: Headers
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private buildUrl(endpoint: string, params?: Record<string, unknown>): string {
    const url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin)

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          // Properly convert values to strings, handling special cases
          if (typeof value === 'boolean') {
            url.searchParams.append(key, value ? 'true' : 'false')
          } else if (typeof value === 'number') {
            url.searchParams.append(key, value.toString())
          } else if (Array.isArray(value)) {
            // Handle arrays by adding multiple params with same key
            value.forEach(item => {
              if (item !== undefined && item !== null) {
                url.searchParams.append(key, String(item))
              }
            })
          } else {
            url.searchParams.append(key, String(value))
          }
        }
      })
    }

    return url.toString()
  }

  private async request<T>(endpoint: string, options: RequestOptions): Promise<ApiResponse<T>> {
    const { method, headers = {}, body, params } = options

    const url = this.buildUrl(endpoint, params)
    const requestHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      ...headers,
    }

    const config: RequestInit = {
      method,
      headers: requestHeaders,
      credentials: 'include', // Include cookies for session management
    }

    if (body !== undefined && body !== null && method !== 'GET') {
      config.body = JSON.stringify(body)
    }

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        const errorData = await this.parseErrorResponse(response)
        this.handleError(errorData, response.status)
        throw new Error(errorData.msg || `Request failed with status ${response.status}`)
      }

      const data = await this.parseResponse<T>(response)

      return {
        data,
        status: response.status,
        headers: response.headers,
      }
    } catch (error) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        this.handleNetworkError()
      }
      throw error
    }
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type')

    if (response.status === 204 || response.headers.get('content-length') === '0') {
      return {} as T
    }

    if (contentType?.includes('application/json')) {
      return await response.json()
    }

    const text = await response.text()
    try {
      return JSON.parse(text)
    } catch {
      return text as T
    }
  }

  private async parseErrorResponse(response: Response): Promise<ApiError> {
    try {
      return await response.json()
    } catch {
      return {
        error: 'Unknown Error',
        msg: `Request failed with status ${response.status}`,
      }
    }
  }

  private handleError(error: ApiError, status: number): void {
    const message = error.msg || error.error || 'An unexpected error occurred'

    // Use notistack for error display
    enqueueSnackbar(message, {
      variant: 'error',
    })

    // Log error for debugging
    console.error(`API Error (${status}):`, error)
  }

  private handleNetworkError(): void {
    enqueueSnackbar('Network error. Please check your connection and try again.', {
      variant: 'error',
    })
  }

  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.request<HealthCheckResponse>('/health', {
      method: 'GET',
    })
    return response.data
  }

  // Books API
  async createBook(request: CreateBookRequest): Promise<CreateBookResponse> {
    const response = await this.request<CreateBookResponse>('/books', {
      method: 'POST',
      body: request,
    })
    return response.data
  }

  async getBookSummaries(request: BookSummariesRequest): Promise<BookSummariesResponse> {
    const response = await this.request<BookSummariesResponse>('/books', {
      method: 'GET',
      params: request as unknown as Record<string, unknown>,
    })
    return response.data
  }

  async getBookCount(request: BookCountRequest): Promise<BookCountResponse> {
    const response = await this.request<BookCountResponse>('/books/count', {
      method: 'GET',
      params: request as unknown as Record<string, unknown>,
    })
    return response.data
  }

  // Terms API
  async createTerm(request: CreateTermRequest): Promise<TermIdResponse> {
    const response = await this.request<TermIdResponse>('/terms', {
      method: 'POST',
      body: request,
    })
    return response.data
  }

  async updateTerm(termId: number, request: UpdateTermRequest): Promise<void> {
    await this.request<void>(`/terms/${termId}`, {
      method: 'PATCH',
      body: request,
    })
  }
}

// Create and export a singleton instance
const apiClient = new ApiClient(BASE_URL)

export default apiClient

// Export individual API functions for convenience
export const api = {
  health: {
    check: () => apiClient.healthCheck(),
  },
  books: {
    create: (request: CreateBookRequest) => apiClient.createBook(request),
    getSummaries: (request: BookSummariesRequest) => apiClient.getBookSummaries(request),
    getCount: (request: BookCountRequest) => apiClient.getBookCount(request),
  },
  terms: {
    create: (request: CreateTermRequest) => apiClient.createTerm(request),
    update: (termId: number, request: UpdateTermRequest) => apiClient.updateTerm(termId, request),
  },
}