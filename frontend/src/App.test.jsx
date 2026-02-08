import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import App from './App'

const MOCK_UI = {
  title: 'A Game',
  loading: 'Loading...',
  errorPrefix: 'Error:',
  pointsLabel: 'pts',
  userLabel: 'User:',
  buttons: [
    { amount: 1, label: '+1 Point' },
    { amount: 5, label: '+5 Points' },
    { amount: 10, label: '+10 Points' },
  ],
}

const MOCK_USER = {
  user_id: '550e8400-e29b-41d4-a716-446655440000',
  name: null,
  created_at: '2026-01-01T00:00:00',
  points: 0,
}

function setupFetchMock(overrides = {}) {
  const responses = {
    '/agame/api/user/me/': MOCK_USER,
    '/agame/content/ui.json': MOCK_UI,
    ...overrides,
  }

  global.fetch = vi.fn((url, opts) => {
    if (url === '/agame/api/user/me/points/' && opts?.method === 'POST') {
      const body = JSON.parse(opts.body)
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ ...MOCK_USER, points: body.amount }),
      })
    }
    const data = responses[url]
    if (data) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(data),
      })
    }
    return Promise.reject(new Error(`Unmocked: ${url}`))
  })
}

async function renderAndWaitForLoad() {
  render(<App />)
  await waitFor(() => {
    expect(screen.getByText('A Game')).toBeInTheDocument()
  })
}

afterEach(() => {
  vi.restoreAllMocks()
})

describe('App rendering', () => {
  it('renders loading state initially', () => {
    global.fetch = vi.fn(() => new Promise(() => {}))
    render(<App />)
    expect(document.querySelector('.min-h-screen')).toBeInTheDocument()
  })

  it('renders game after data loads', async () => {
    setupFetchMock()
    await renderAndWaitForLoad()
    expect(screen.getByText(/0 pts/)).toBeInTheDocument()
  })

  it('renders all buttons from ui.json', async () => {
    setupFetchMock()
    await renderAndWaitForLoad()
    expect(screen.getByText('+1 Point')).toBeInTheDocument()
    expect(screen.getByText('+5 Points')).toBeInTheDocument()
    expect(screen.getByText('+10 Points')).toBeInTheDocument()
  })

  it('sets document title from ui.json', async () => {
    setupFetchMock()
    await renderAndWaitForLoad()
    expect(document.title).toBe('A Game')
  })

  it('renders error state on fetch failure', async () => {
    global.fetch = vi.fn(() => Promise.reject(new Error('Network down')))
    render(<App />)
    await waitFor(() => {
      expect(screen.getByText(/Network down/)).toBeInTheDocument()
    })
  })
})

describe('App interactions', () => {
  beforeEach(() => {
    setupFetchMock()
  })

  it('clicking button calls points API', async () => {
    await renderAndWaitForLoad()
    fireEvent.click(screen.getByText('+1 Point'))
    await waitFor(() => {
      const calls = global.fetch.mock.calls
      const pointsCall = calls.find(([url]) => url === '/agame/api/user/me/points/')
      expect(pointsCall).toBeTruthy()
      expect(JSON.parse(pointsCall[1].body)).toEqual({ amount: 1 })
    })
  })

  it('points update after clicking', async () => {
    await renderAndWaitForLoad()
    fireEvent.click(screen.getByText('+5 Points'))
    await waitFor(() => {
      expect(screen.getByText(/5 pts/)).toBeInTheDocument()
    })
  })

  it('buttons disabled while clicking', async () => {
    let resolvePoints
    const originalFetch = global.fetch
    global.fetch = vi.fn((url, opts) => {
      if (url === '/agame/api/user/me/points/') {
        return new Promise((resolve) => {
          resolvePoints = () => resolve({
            ok: true,
            json: () => Promise.resolve({ ...MOCK_USER, points: 1 }),
          })
        })
      }
      return originalFetch(url, opts)
    })

    await renderAndWaitForLoad()
    fireEvent.click(screen.getByText('+1 Point'))

    expect(screen.getByText('+1 Point')).toBeDisabled()
    expect(screen.getByText('+5 Points')).toBeDisabled()

    resolvePoints()
    await waitFor(() => {
      expect(screen.getByText('+1 Point')).not.toBeDisabled()
    })
  })
})

describe('Content loading', () => {
  it('fetches ui.json from content path', async () => {
    setupFetchMock()
    await renderAndWaitForLoad()
    const urls = global.fetch.mock.calls.map(([url]) => url)
    expect(urls).toContain('/agame/content/ui.json')
  })

  it('fetches user from API path', async () => {
    setupFetchMock()
    await renderAndWaitForLoad()
    const urls = global.fetch.mock.calls.map(([url]) => url)
    expect(urls).toContain('/agame/api/user/me/')
  })
})
