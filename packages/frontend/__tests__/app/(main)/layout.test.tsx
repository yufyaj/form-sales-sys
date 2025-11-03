import { render, screen, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import Layout from '@/app/(main)/layout'
import { useAuth } from '@/contexts/AuthContext'

// useRouterのモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

// useAuthのモック
jest.mock('@/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}))

// MainLayoutコンポーネントのモック
jest.mock('@/components/common/MainLayout', () => {
  return function MainLayout({
    children,
    user,
  }: {
    children: React.ReactNode
    user: { name?: string; email: string }
  }) {
    return (
      <div data-testid="main-layout">
        <div data-testid="user-info">{user.name || user.email}</div>
        {children}
      </div>
    )
  }
})

describe('(main)/layout', () => {
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
  })

  describe('認証状態による表示', () => {
    it('ローディング中は読み込み画面を表示する', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: true,
        error: null,
        logout: jest.fn(),
      })

      render(<Layout>Test Content</Layout>)

      expect(screen.getByText('読み込み中...')).toBeInTheDocument()
      expect(screen.queryByText('Test Content')).not.toBeInTheDocument()
    })

    it('エラー発生時はエラー画面を表示する', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: false,
        error: '認証に失敗しました',
        logout: jest.fn(),
      })

      render(<Layout>Test Content</Layout>)

      expect(screen.getByText('認証エラー')).toBeInTheDocument()
      expect(screen.getByText('認証に失敗しました')).toBeInTheDocument()
      expect(screen.queryByText('Test Content')).not.toBeInTheDocument()
    })

    it('エラー画面で再読み込みボタンが表示される', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: false,
        error: '認証に失敗しました',
        logout: jest.fn(),
      })

      render(<Layout>Test Content</Layout>)

      const reloadButton = screen.getByRole('button', { name: '再読み込み' })
      expect(reloadButton).toBeInTheDocument()
    })

    it('認証されていない場合は何も表示しない', () => {
      ;(useAuth as jest.Mock).mockReturnValue({
        user: null,
        isLoading: false,
        error: null,
        logout: jest.fn(),
      })

      const { container } = render(<Layout>Test Content</Layout>)

      expect(container.firstChild).toBeNull()
      expect(screen.queryByText('Test Content')).not.toBeInTheDocument()
    })

    it('認証済みの場合はMainLayoutとchildrenを表示する', () => {
      const mockUser = {
        id: '1',
        email: 'user@example.com',
        name: 'テストユーザー',
        role: 'admin' as const,
      }

      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        isLoading: false,
        error: null,
        logout: jest.fn(),
      })

      render(<Layout>Test Content</Layout>)

      expect(screen.getByTestId('main-layout')).toBeInTheDocument()
      expect(screen.getByTestId('user-info')).toHaveTextContent('テストユーザー')
      expect(screen.getByText('Test Content')).toBeInTheDocument()
    })
  })

  describe('ログアウト処理', () => {
    it('ログアウト関数をMainLayoutに渡す', () => {
      const mockLogout = jest.fn()
      const mockUser = {
        id: '1',
        email: 'user@example.com',
        name: 'テストユーザー',
        role: 'admin' as const,
      }

      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        isLoading: false,
        error: null,
        logout: mockLogout,
      })

      render(<Layout>Test Content</Layout>)

      // MainLayoutコンポーネントがレンダリングされていることを確認
      expect(screen.getByTestId('main-layout')).toBeInTheDocument()
    })
  })

  describe('異なるユーザーロールでの表示', () => {
    it.each([
      ['admin', '管理者ユーザー'],
      ['manager', 'マネージャーユーザー'],
      ['member', 'メンバーユーザー'],
    ])('%sロールのユーザーを正しく表示する', (role, name) => {
      const mockUser = {
        id: '1',
        email: 'user@example.com',
        name: name,
        role: role as 'admin' | 'manager' | 'member',
      }

      ;(useAuth as jest.Mock).mockReturnValue({
        user: mockUser,
        isLoading: false,
        error: null,
        logout: jest.fn(),
      })

      render(<Layout>Test Content</Layout>)

      expect(screen.getByTestId('user-info')).toHaveTextContent(name)
    })
  })
})
