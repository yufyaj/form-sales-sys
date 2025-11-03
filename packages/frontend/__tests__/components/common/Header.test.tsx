import { render, screen, fireEvent } from '@testing-library/react'
import Header from '@/components/common/Header'
import { User } from '@/types/auth'

describe('Header', () => {
  const mockUser: User = {
    id: '1',
    email: 'test@example.com',
    name: 'テストユーザー',
    role: 'admin',
  }

  const mockOnLogout = jest.fn()

  beforeEach(() => {
    mockOnLogout.mockClear()
  })

  describe('表示', () => {
    it('タイトルが表示される', () => {
      render(<Header />)
      expect(screen.getByText('フォーム営業支援システム')).toBeInTheDocument()
    })

    it('ユーザー情報がない場合、ユーザーメニューが表示されない', () => {
      render(<Header />)
      expect(screen.queryByLabelText('ユーザーメニュー')).not.toBeInTheDocument()
    })

    it('ユーザー情報がある場合、ユーザーメニューが表示される', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)
      expect(screen.getByLabelText('ユーザーメニュー')).toBeInTheDocument()
    })

    it('ユーザー名が表示される', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)
      expect(screen.getByText('テストユーザー')).toBeInTheDocument()
    })

    it('名前がない場合、メールアドレスが表示される', () => {
      const userWithoutName = { ...mockUser, name: undefined }
      render(<Header user={userWithoutName} onLogout={mockOnLogout} />)
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })
  })

  describe('ドロップダウンメニュー', () => {
    it('初期状態ではドロップダウンメニューが閉じている', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)
      expect(screen.queryByText('ログアウト')).not.toBeInTheDocument()
    })

    it('ユーザーメニューをクリックするとドロップダウンが開く', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)

      const menuButton = screen.getByLabelText('ユーザーメニュー')
      fireEvent.click(menuButton)

      expect(screen.getByText('ログアウト')).toBeInTheDocument()
    })

    it('ドロップダウン内にユーザー情報が表示される', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)

      const menuButton = screen.getByLabelText('ユーザーメニュー')
      fireEvent.click(menuButton)

      // ドロップダウン内のユーザー情報を確認（複数箇所に表示される場合があるため、getAllByTextを使用）
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
      expect(screen.getAllByText('テストユーザー').length).toBeGreaterThan(0)
      expect(screen.getByText('ロール: 管理者')).toBeInTheDocument()
    })

    it('ロールが各種表示される', () => {
      const testCases = [
        { role: 'admin' as const, label: '管理者' },
        { role: 'manager' as const, label: 'マネージャー' },
        { role: 'member' as const, label: 'メンバー' },
      ]

      testCases.forEach(({ role, label }) => {
        const { unmount } = render(
          <Header user={{ ...mockUser, role }} onLogout={mockOnLogout} />
        )

        const menuButton = screen.getByLabelText('ユーザーメニュー')
        fireEvent.click(menuButton)

        expect(screen.getByText(`ロール: ${label}`)).toBeInTheDocument()

        unmount()
      })
    })
  })

  describe('ログアウト', () => {
    it('ログアウトボタンをクリックするとonLogoutが呼ばれる', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)

      // ドロップダウンを開く
      const menuButton = screen.getByLabelText('ユーザーメニュー')
      fireEvent.click(menuButton)

      // ログアウトボタンをクリック
      const logoutButton = screen.getByText('ログアウト')
      fireEvent.click(logoutButton)

      expect(mockOnLogout).toHaveBeenCalledTimes(1)
    })

    it('ログアウト後、ドロップダウンが閉じる', () => {
      render(<Header user={mockUser} onLogout={mockOnLogout} />)

      // ドロップダウンを開く
      const menuButton = screen.getByLabelText('ユーザーメニュー')
      fireEvent.click(menuButton)

      // ログアウトボタンをクリック
      const logoutButton = screen.getByText('ログアウト')
      fireEvent.click(logoutButton)

      // ドロップダウンが閉じていることを確認
      expect(screen.queryByText('ログアウト')).not.toBeInTheDocument()
    })
  })
})
