import { render, screen, fireEvent } from '@testing-library/react'
import { usePathname } from 'next/navigation'
import Sidebar from '@/components/common/Sidebar'
import { UserRole } from '@/types/auth'

// next/navigationのモック
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

describe('Sidebar', () => {
  const mockOnCloseMobileMenu = jest.fn()

  beforeEach(() => {
    mockOnCloseMobileMenu.mockClear()
    ;(usePathname as jest.Mock).mockReturnValue('/dashboard')
  })

  describe('ナビゲーション項目の表示', () => {
    it('全ロール共通の項目が表示される', () => {
      render(<Sidebar userRole="member" />)

      expect(screen.getByText('ダッシュボード')).toBeInTheDocument()
      expect(screen.getByText('プロジェクト')).toBeInTheDocument()
      expect(screen.getByText('リスト管理')).toBeInTheDocument()
      expect(screen.getByText('設定')).toBeInTheDocument()
    })

    it('メンバーロールの場合、管理者限定項目が表示されない', () => {
      render(<Sidebar userRole="member" />)

      expect(screen.queryByText('アナリティクス')).not.toBeInTheDocument()
      expect(screen.queryByText('ユーザー管理')).not.toBeInTheDocument()
    })

    it('マネージャーロールの場合、アナリティクスが表示される', () => {
      render(<Sidebar userRole="manager" />)

      expect(screen.getByText('アナリティクス')).toBeInTheDocument()
      expect(screen.queryByText('ユーザー管理')).not.toBeInTheDocument()
    })

    it('管理者ロールの場合、すべての項目が表示される', () => {
      render(<Sidebar userRole="admin" />)

      expect(screen.getByText('ダッシュボード')).toBeInTheDocument()
      expect(screen.getByText('プロジェクト')).toBeInTheDocument()
      expect(screen.getByText('リスト管理')).toBeInTheDocument()
      expect(screen.getByText('アナリティクス')).toBeInTheDocument()
      expect(screen.getByText('ユーザー管理')).toBeInTheDocument()
      expect(screen.getByText('設定')).toBeInTheDocument()
    })

    it('ロールが指定されていない場合、すべての項目が表示されない', () => {
      render(<Sidebar />)

      // ロールがない場合は、rolesプロパティがあるすべての項目が表示されない
      expect(screen.queryByText('ダッシュボード')).not.toBeInTheDocument()
      expect(screen.queryByText('プロジェクト')).not.toBeInTheDocument()
      expect(screen.queryByText('アナリティクス')).not.toBeInTheDocument()
      expect(screen.queryByText('ユーザー管理')).not.toBeInTheDocument()
    })
  })

  describe('アクティブ状態', () => {
    it('現在のパスに対応する項目がアクティブになる', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/dashboard')
      render(<Sidebar userRole="admin" />)

      const dashboardLink = screen.getByText('ダッシュボード').closest('a')
      expect(dashboardLink).toHaveClass('bg-blue-50', 'text-blue-700')
    })

    it('サブパスでもアクティブになる', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/projects/123')
      render(<Sidebar userRole="admin" />)

      const projectLink = screen.getByText('プロジェクト').closest('a')
      expect(projectLink).toHaveClass('bg-blue-50', 'text-blue-700')
    })

    it('非アクティブな項目は通常のスタイルになる', () => {
      ;(usePathname as jest.Mock).mockReturnValue('/dashboard')
      render(<Sidebar userRole="admin" />)

      const projectLink = screen.getByText('プロジェクト').closest('a')
      expect(projectLink).toHaveClass('text-gray-700', 'hover:bg-gray-100')
      expect(projectLink).not.toHaveClass('bg-blue-50', 'text-blue-700')
    })
  })

  describe('モバイルメニュー', () => {
    it('モバイルメニューが閉じている場合、サイドバーが非表示', () => {
      const { container } = render(
        <Sidebar userRole="admin" isMobileMenuOpen={false} />
      )

      const sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('-translate-x-full')
    })

    it('モバイルメニューが開いている場合、サイドバーが表示される', () => {
      const { container } = render(
        <Sidebar userRole="admin" isMobileMenuOpen={true} />
      )

      const sidebar = container.querySelector('aside')
      expect(sidebar).toHaveClass('translate-x-0')
    })

    it('モバイルメニューが開いている場合、オーバーレイが表示される', () => {
      const { container } = render(
        <Sidebar
          userRole="admin"
          isMobileMenuOpen={true}
          onCloseMobileMenu={mockOnCloseMobileMenu}
        />
      )

      const overlay = container.querySelector('.fixed.inset-0.z-40.bg-black')
      expect(overlay).toBeInTheDocument()
    })

    it('オーバーレイをクリックするとメニューが閉じる', () => {
      const { container } = render(
        <Sidebar
          userRole="admin"
          isMobileMenuOpen={true}
          onCloseMobileMenu={mockOnCloseMobileMenu}
        />
      )

      const overlay = container.querySelector(
        '.fixed.inset-0.z-40.bg-black'
      ) as HTMLElement
      fireEvent.click(overlay)

      expect(mockOnCloseMobileMenu).toHaveBeenCalledTimes(1)
    })

    it('リンクをクリックするとメニューが閉じる', () => {
      render(
        <Sidebar
          userRole="admin"
          isMobileMenuOpen={true}
          onCloseMobileMenu={mockOnCloseMobileMenu}
        />
      )

      const dashboardLink = screen.getByText('ダッシュボード')
      fireEvent.click(dashboardLink)

      expect(mockOnCloseMobileMenu).toHaveBeenCalledTimes(1)
    })
  })

  describe('ロール表示', () => {
    it('ロールが指定されている場合、フッターにロールが表示される', () => {
      render(<Sidebar userRole="admin" />)
      expect(screen.getByText('ロール: 管理者')).toBeInTheDocument()
    })

    it('各ロールのラベルが正しく表示される', () => {
      const testCases: Array<{ role: UserRole; label: string }> = [
        { role: 'admin', label: '管理者' },
        { role: 'manager', label: 'マネージャー' },
        { role: 'member', label: 'メンバー' },
      ]

      testCases.forEach(({ role, label }) => {
        const { unmount } = render(<Sidebar userRole={role} />)
        expect(screen.getByText(`ロール: ${label}`)).toBeInTheDocument()
        unmount()
      })
    })

    it('ロールが指定されていない場合、フッターが表示されない', () => {
      render(<Sidebar />)
      expect(screen.queryByText(/ロール:/)).not.toBeInTheDocument()
    })
  })
})
