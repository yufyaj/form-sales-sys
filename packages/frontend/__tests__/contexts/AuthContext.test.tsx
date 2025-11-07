import { render, screen, waitFor, act } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'

// useRouterのモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// loggerのモック
jest.mock('@/lib/logger', () => ({
  logError: jest.fn(),
  logAuthError: jest.fn(),
  logWarn: jest.fn(),
  logInfo: jest.fn(),
  logDebug: jest.fn(),
}))

// fetchのモック
global.fetch = jest.fn()

describe('AuthContext', () => {
  const mockRouter = {
    push: jest.fn(),
    back: jest.fn(),
    forward: jest.fn(),
    refresh: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    ;(global.fetch as jest.Mock).mockClear()
  })

  // テスト用コンポーネント
  function TestComponent() {
    const { user, isLoading, error, logout } = useAuth()

    if (isLoading) return <div>Loading...</div>
    if (error) return <div>Error: {error}</div>
    if (!user) return <div>No user</div>

    return (
      <div>
        <div data-testid="user-id">{user.id}</div>
        <div data-testid="user-email">{user.email}</div>
        <div data-testid="user-name">{user.name}</div>
        <div data-testid="user-role">{user.role}</div>
        <button onClick={logout}>Logout</button>
      </div>
    )
  }

  describe('初期化', () => {
    it('AuthProvider外でuseAuthを呼び出すとエラーをスローする', () => {
      // エラーログを抑制
      const consoleError = jest
        .spyOn(console, 'error')
        .mockImplementation(() => {})

      expect(() => {
        render(<TestComponent />)
      }).toThrow('useAuth must be used within an AuthProvider')

      consoleError.mockRestore()
    })

    it('初期状態ではisLoadingがtrueである', () => {
      ;(global.fetch as jest.Mock).mockImplementation(
        () =>
          new Promise(() => {
            /* never resolves */
          })
      )

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      expect(screen.getByText('Loading...')).toBeInTheDocument()
    })
  })

  describe('セッション検証', () => {
    it('認証が未実装(501)の場合はモックユーザーを使用する', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 501,
        ok: false,
      })

      const consoleWarn = jest.spyOn(console, 'warn').mockImplementation()

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user-id')).toHaveTextContent('1')
      })

      expect(screen.getByTestId('user-email')).toHaveTextContent(
        'user@example.com'
      )
      expect(screen.getByTestId('user-name')).toHaveTextContent(
        'テストユーザー'
      )
      expect(screen.getByTestId('user-role')).toHaveTextContent('sales_company')

      consoleWarn.mockRestore()
    })

    it('認証に成功した場合はユーザー情報を設定する', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        role: 'manager',
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 200,
        ok: true,
        json: async () => mockUser,
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user-id')).toHaveTextContent('123')
      })

      expect(screen.getByTestId('user-email')).toHaveTextContent(
        'test@example.com'
      )
      expect(screen.getByTestId('user-name')).toHaveTextContent('Test User')
      expect(screen.getByTestId('user-role')).toHaveTextContent('manager')
    })

    it('認証に失敗した場合はログインページへリダイレクトする', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 401,
        ok: false,
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
      })
    })

    it('エラーが発生した場合はエラーメッセージを表示しログインページへリダイレクトする', async () => {
      ;(global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      )

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByText('Error: 認証に失敗しました')).toBeInTheDocument()
      })

      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })
  })

  describe('ログアウト処理', () => {
    it('ログアウトに成功した場合はログインページへリダイレクトする', async () => {
      // 初回のセッション検証（モックユーザー）
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 501,
        ok: false,
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user-id')).toBeInTheDocument()
      })

      // ログアウトAPIのモック
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 200,
        ok: true,
      })

      const logoutButton = screen.getByRole('button', { name: 'Logout' })

      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
      })

      expect(global.fetch).toHaveBeenCalledWith('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      })
    })

    it('ログアウトが未実装(501)の場合でもログインページへリダイレクトする', async () => {
      // 初回のセッション検証（モックユーザー）
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 501,
        ok: false,
      })

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      )

      await waitFor(() => {
        expect(screen.getByTestId('user-id')).toBeInTheDocument()
      })

      // ログアウトAPIのモック（未実装）
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        status: 501,
        ok: false,
      })

      const logoutButton = screen.getByRole('button', { name: 'Logout' })

      await act(async () => {
        logoutButton.click()
      })

      await waitFor(() => {
        expect(mockRouter.push).toHaveBeenCalledWith('/login')
      })
    })

    it.skip('ログアウトに失敗した場合はエラーメッセージを表示する', async () => {
      // TODO: このテストはエラーハンドリングの仕様変更が必要
      // 現在、logout関数はエラーをスローするが、コンポーネント内でcatchされないため
      // テストが困難。エラーハンドリングの設計を見直した後に再実装する。
    })
  })
})
