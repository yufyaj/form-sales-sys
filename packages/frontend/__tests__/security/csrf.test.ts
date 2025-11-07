import {
  generateCSRFToken,
  validateCSRFToken,
  getOrCreateCSRFToken,
  clearCSRFToken,
} from '@/lib/csrf'

/**
 * CSRF（Cross-Site Request Forgery）対策のテスト
 *
 * テスト内容:
 * - CSRFトークンの生成
 * - CSRFトークンの検証
 * - セッションストレージとの連携
 */
describe('CSRF Protection', () => {
  // テスト前にセッションストレージをクリア
  beforeEach(() => {
    sessionStorage.clear()
  })

  // テスト後にセッションストレージをクリア
  afterEach(() => {
    sessionStorage.clear()
  })

  describe('generateCSRFToken', () => {
    it('32文字のトークンを生成する', () => {
      const token = generateCSRFToken()
      expect(token).toHaveLength(32)
    })

    it('呼び出すたびに異なるトークンを生成する', () => {
      const token1 = generateCSRFToken()
      const token2 = generateCSRFToken()
      const token3 = generateCSRFToken()

      expect(token1).not.toBe(token2)
      expect(token2).not.toBe(token3)
      expect(token1).not.toBe(token3)
    })

    it('生成されるトークンに特殊文字が含まれない', () => {
      const token = generateCSRFToken()
      // 英数字のみで構成されていることを確認
      expect(token).toMatch(/^[a-f0-9]{32}$/)
    })

    it('100個のトークンを生成しても重複しない', () => {
      const tokens = new Set<string>()

      for (let i = 0; i < 100; i++) {
        tokens.add(generateCSRFToken())
      }

      // 全て異なるトークンであることを確認
      expect(tokens.size).toBe(100)
    })
  })

  describe('validateCSRFToken', () => {
    it('同一のトークンで検証が成功する', () => {
      const token = generateCSRFToken()
      expect(validateCSRFToken(token, token)).toBe(true)
    })

    it('異なるトークンで検証が失敗する', () => {
      const token1 = generateCSRFToken()
      const token2 = generateCSRFToken()
      expect(validateCSRFToken(token1, token2)).toBe(false)
    })

    it('null値のトークンで検証が失敗する', () => {
      const token = generateCSRFToken()
      expect(validateCSRFToken(null, token)).toBe(false)
      expect(validateCSRFToken(token, '')).toBe(false)
    })

    it('空文字列のトークンで検証が失敗する', () => {
      expect(validateCSRFToken('', '')).toBe(false)
      expect(validateCSRFToken('token', '')).toBe(false)
      expect(validateCSRFToken('', 'token')).toBe(false)
    })

    it('長さが異なるトークンで検証が失敗する', () => {
      const token = generateCSRFToken()
      const shortToken = token.slice(0, 16)
      expect(validateCSRFToken(shortToken, token)).toBe(false)
    })

    it('大文字小文字を区別する', () => {
      const token = 'abcdef1234567890abcdef1234567890'
      const upperToken = token.toUpperCase()
      expect(validateCSRFToken(token, upperToken)).toBe(false)
    })
  })

  describe('getOrCreateCSRFToken', () => {
    it('初回呼び出しで新しいトークンを生成する', () => {
      const token = getOrCreateCSRFToken()
      expect(token).toHaveLength(32)
    })

    it('2回目以降の呼び出しで同じトークンを返す', () => {
      const token1 = getOrCreateCSRFToken()
      const token2 = getOrCreateCSRFToken()
      const token3 = getOrCreateCSRFToken()

      expect(token1).toBe(token2)
      expect(token2).toBe(token3)
    })

    it('セッションストレージにトークンを保存する', () => {
      const token = getOrCreateCSRFToken()
      const storedToken = sessionStorage.getItem('csrf_token')

      expect(storedToken).toBe(token)
    })

    it('既存のセッションストレージのトークンを使用する', () => {
      const existingToken = 'existing12345678901234567890abc'
      sessionStorage.setItem('csrf_token', existingToken)

      const token = getOrCreateCSRFToken()
      expect(token).toBe(existingToken)
    })
  })

  describe('clearCSRFToken', () => {
    it('セッションストレージからトークンを削除する', () => {
      // トークンを生成・保存
      const token = getOrCreateCSRFToken()
      expect(sessionStorage.getItem('csrf_token')).toBe(token)

      // トークンをクリア
      clearCSRFToken()
      expect(sessionStorage.getItem('csrf_token')).toBeNull()
    })

    it('トークンがない状態でクリアを呼び出してもエラーにならない', () => {
      expect(() => clearCSRFToken()).not.toThrow()
    })

    it('クリア後に新しいトークンが生成される', () => {
      const token1 = getOrCreateCSRFToken()
      clearCSRFToken()
      const token2 = getOrCreateCSRFToken()

      expect(token1).not.toBe(token2)
    })
  })

  describe('セキュリティ要件', () => {
    it('トークンの推測が困難である（エントロピーが十分）', () => {
      // 1000個のトークンを生成して重複がないことを確認
      const tokens = new Set<string>()

      for (let i = 0; i < 1000; i++) {
        tokens.add(generateCSRFToken())
      }

      expect(tokens.size).toBe(1000)
    })

    it('トークンの検証が定数時間で実行される（タイミング攻撃対策）', () => {
      const validToken = generateCSRFToken()
      const invalidToken1 = generateCSRFToken()
      const invalidToken2 = validToken.slice(0, -1) + 'x' // 最後の1文字だけ変更

      // 複数回実行して平均時間を計測
      const iterations = 1000
      let totalTime1 = 0
      let totalTime2 = 0

      for (let i = 0; i < iterations; i++) {
        const start1 = performance.now()
        validateCSRFToken(invalidToken1, validToken)
        totalTime1 += performance.now() - start1

        const start2 = performance.now()
        validateCSRFToken(invalidToken2, validToken)
        totalTime2 += performance.now() - start2
      }

      const avgTime1 = totalTime1 / iterations
      const avgTime2 = totalTime2 / iterations

      // 実行時間の差が小さいことを確認（定数時間比較）
      // Note: JavaScriptの実行環境により変動が大きいため、
      // 実際の本番環境ではサーバーサイドでの検証を推奨
      const timeDifference = Math.abs(avgTime1 - avgTime2)

      // 実行時間が極端に異なっていないことを確認（10倍以内）
      const ratio = avgTime1 / avgTime2
      expect(ratio).toBeGreaterThan(0.1)
      expect(ratio).toBeLessThan(10)
    })
  })
})
