import { render, screen, fireEvent } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import MainLayout from '@/components/common/MainLayout'
import { User } from '@/types/auth'

// next/navigationのモック
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('MainLayout', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'テストユーザー',
    role: 'admin',
  }

  const mockOnLogout = jest.fn()

  beforeEach(() => {
    mockOnLogout.mockClear()
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard')
  })

  describe('レイアウト構成', () => {
    it('Header、Sidebar、メインコンテンツが表示される', () => {
      render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      // Header
      expect(screen.getByText('フォーム営業支援システム')).toBeInTheDocument()

      // Sidebar
      expect(screen.getByText('ダッシュボード')).toBeInTheDocument()

      // メインコンテンツ
      expect(screen.getByText('テストコンテンツ')).toBeInTheDocument()
    })

    it('Headerにユーザー情報が渡される', () => {
      render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      expect(screen.getByText('テストユーザー')).toBeInTheDocument()
    })

    it('Sidebarにユーザーロールが渡される', () => {
      render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      // 管理者のみ表示される項目を確認
      expect(screen.getByText('ユーザー管理')).toBeInTheDocument()
    })
  })

  describe('モバイルメニューボタン', () => {
    it('モバイルメニューボタンが表示される', () => {
      render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      expect(screen.getByLabelText('メニューを開く')).toBeInTheDocument()
    })

    it('初期状態ではモバイルメニューが閉じている', () => {
      const { container } = render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      const sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('-translate-x-full')
    })

    it('モバイルメニューボタンをクリックするとメニューが開く', () => {
      const { container } = render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      const menuButton = screen.getByLabelText('メニューを開く')
      fireEvent.click(menuButton)

      const sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('translate-x-0')
    })

    it('メニューを開いた後、もう一度ボタンをクリックするとメニューが閉じる', () => {
      const { container } = render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      const menuButton = screen.getByLabelText('メニューを開く')

      // 開く
      fireEvent.click(menuButton)
      let sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('translate-x-0')

      // 閉じる
      fireEvent.click(menuButton)
      sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('-translate-x-full')
    })
  })

  describe('ユーザー情報なし', () => {
    it('ユーザー情報がなくてもレイアウトが表示される', () => {
      render(
        <MainLayout>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      expect(screen.getByText('フォーム営業支援システム')).toBeInTheDocument()
      expect(screen.getByText('テストコンテンツ')).toBeInTheDocument()
    })
  })

  describe('ログアウト', () => {
    it('Headerのログアウトボタンからログアウトできる', () => {
      render(
        <MainLayout user={mockUser} onLogout={mockOnLogout}>
          <div>テストコンテンツ</div>
        </MainLayout>
      )

      // ユーザーメニューを開く
      const userMenuButton = screen.getByLabelText('ユーザーメニュー')
      fireEvent.click(userMenuButton)

      // ログアウトボタンをクリック
      const logoutButton = screen.getByText('ログアウト')
      fireEvent.click(logoutButton)

      expect(mockOnLogout).toHaveBeenCalledTimes(1)
    })
  })
})
