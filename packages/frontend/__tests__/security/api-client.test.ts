import { apiRequest, get, post, put, patch, del, ApiError } from '@/lib/api-client'
import { getOrCreateCSRFToken } from '@/lib/csrf'

// fetchのモック
global.fetch = jest.fn()

/**
 * APIクライアントのセキュリティテスト
 *
 * テスト内容:
 * - CSRFトークンの自動付与
 * - 認証エラー時のリダイレクト
 * - エラーハンドリング
 */
describe('API Client Security', () => {
  beforeEach(() => {
    // fetchのモックをリセット
    ;(global.fetch as jest.Mock).mockClear()
    // セッションストレージをクリア
    sessionStorage.clear()
  })

  describe('CSRFトークンの自動付与', () => {
    it('POSTリクエストにCSRFトークンが含まれる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await post('/api/test', { data: 'test' })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      const headers = callArgs[1].headers

      expect(headers['X-CSRF-Token']).toBeDefined()
      expect(headers['X-CSRF-Token']).toHaveLength(32)
    })

    it('PUTリクエストにCSRFトークンが含まれる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await put('/api/test', { data: 'test' })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      const headers = callArgs[1].headers

      expect(headers['X-CSRF-Token']).toBeDefined()
    })

    it('DELETEリクエストにCSRFトークンが含まれる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      })

      await del('/api/test')

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      const headers = callArgs[1].headers

      expect(headers['X-CSRF-Token']).toBeDefined()
    })

    it('PATCHリクエストにCSRFトークンが含まれる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await patch('/api/test', { data: 'test' })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      const headers = callArgs[1].headers

      expect(headers['X-CSRF-Token']).toBeDefined()
    })

    it('GETリクエストにはCSRFトークンが含まれない', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'test' }),
      })

      await get('/api/test')

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      const headers = callArgs[1].headers

      expect(headers['X-CSRF-Token']).toBeUndefined()
    })

    it('同じセッション内で同じCSRFトークンが使用される', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await post('/api/test1', { data: 'test1' })
      await post('/api/test2', { data: 'test2' })

      const call1Headers = (global.fetch as jest.Mock).mock.calls[0][1].headers
      const call2Headers = (global.fetch as jest.Mock).mock.calls[1][1].headers

      expect(call1Headers['X-CSRF-Token']).toBe(call2Headers['X-CSRF-Token'])
    })
  })

  describe('認証エラーハンドリング', () => {
    // Note: window.location.hrefの変更テストはJSDOMの制限によりスキップ
    it.skip('401エラー時にログインページへリダイレクトする', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ message: 'Unauthorized' }),
      })

      await expect(get('/api/test')).rejects.toThrow(ApiError)
    })

    it('401エラーでApiErrorをスローする', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({ message: 'Unauthorized' }),
      })

      try {
        await get('/api/test')
        fail('Should have thrown an error')
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError)
        if (error instanceof ApiError) {
          expect(error.status).toBe(401)
          expect(error.message).toBe('Unauthorized')
        }
      }
    })

    it('403エラーで適切なエラーメッセージを返す', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden',
        json: async () => ({ message: 'Forbidden' }),
      })

      await expect(get('/api/test')).rejects.toThrow(
        'Forbidden: You do not have permission to access this resource'
      )
    })

    it('404エラーで適切なエラーメッセージを返す', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ message: 'Not Found' }),
      })

      await expect(get('/api/test')).rejects.toThrow('Resource not found')
    })
  })

  describe('credentials設定', () => {
    it('全てのリクエストでcredentials: includeが設定される', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await get('/api/test')

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].credentials).toBe('include')
    })

    it('HttpOnly Cookieが送信される設定である', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await post('/api/test', { data: 'test' })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].credentials).toBe('include')
    })
  })

  describe('エラーハンドリング', () => {
    it('ネットワークエラーを適切に処理する', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))

      await expect(get('/api/test')).rejects.toThrow('Network Error: Network error')
    })

    it('JSONパースエラーを処理する', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON')
        },
        text: async () => 'Server Error',
      })

      await expect(get('/api/test')).rejects.toThrow(ApiError)
    })

    it('ApiErrorに適切な情報が含まれる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Database error' }),
      })

      try {
        await get('/api/test')
        fail('Should have thrown an error')
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError)
        if (error instanceof ApiError) {
          expect(error.status).toBe(500)
          expect(error.data).toEqual({ error: 'Database error' })
        }
      }
    })
  })

  describe('レスポンス処理', () => {
    it('204 No Contentで空オブジェクトを返す', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      })

      const result = await del('/api/test')
      expect(result).toEqual({})
    })

    it('JSONレスポンスを正しくパースする', async () => {
      const responseData = { id: 1, name: 'Test' }
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => responseData,
      })

      const result = await get('/api/test')
      expect(result).toEqual(responseData)
    })
  })

  describe('セキュリティヘッダー', () => {
    it('Content-Typeヘッダーが設定される', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await post('/api/test', { data: 'test' })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].headers['Content-Type']).toBe('application/json')
    })

    it('カスタムヘッダーを追加できる', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      })

      await get('/api/test', {
        headers: {
          'X-Custom-Header': 'custom-value',
        },
      })

      const callArgs = (global.fetch as jest.Mock).mock.calls[0]
      expect(callArgs[1].headers['X-Custom-Header']).toBe('custom-value')
    })
  })
})
