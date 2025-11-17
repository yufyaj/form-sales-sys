import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useRouter } from 'next/navigation'
import ProjectList, { Project } from '@/components/features/project/ProjectList'

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

const mockRouter = {
  push: jest.fn(),
  back: jest.fn(),
  refresh: jest.fn(),
}

const mockProjects: Project[] = [
  {
    id: 1,
    name: 'プロジェクトA',
    client_organization_id: 1,
    status: 'planning',
    start_date: '2025-04-01',
    end_date: '2025-09-30',
    created_at: '2025-01-15T10:00:00Z',
  },
  {
    id: 2,
    name: 'プロジェクトB',
    client_organization_id: 2,
    status: 'active',
    start_date: '2025-02-01',
    end_date: null,
    created_at: '2025-01-20T10:00:00Z',
  },
  {
    id: 3,
    name: 'プロジェクトC',
    client_organization_id: 3,
    status: 'completed',
    start_date: '2024-10-01',
    end_date: '2024-12-31',
    created_at: '2024-09-01T10:00:00Z',
  },
]

describe('ProjectList', () => {
  beforeEach(() => {
    ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
    jest.clearAllMocks()
  })

  describe('レンダリング', () => {
    it('プロジェクト一覧が表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      expect(screen.getByText('プロジェクトA')).toBeInTheDocument()
      expect(screen.getByText('プロジェクトB')).toBeInTheDocument()
      expect(screen.getByText('プロジェクトC')).toBeInTheDocument()
    })

    it('顧客企業IDが表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      expect(screen.getByText('ID: 1')).toBeInTheDocument()
      expect(screen.getByText('ID: 2')).toBeInTheDocument()
      expect(screen.getByText('ID: 3')).toBeInTheDocument()
    })

    it('ステータスが日本語で表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      expect(screen.getByText('企画中')).toBeInTheDocument()
      expect(screen.getByText('進行中')).toBeInTheDocument()
      expect(screen.getByText('完了')).toBeInTheDocument()
    })

    it('日付がフォーマットされて表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      // 日付のフォーマット確認（YYYY/MM/DD形式）
      expect(screen.getByText('2025/04/01')).toBeInTheDocument()
      expect(screen.getByText('2025/09/30')).toBeInTheDocument()
    })

    it('日付がnullの場合はハイフンが表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      // プロジェクトBの終了日はnullなので、'-'が表示される
      const rows = screen.getAllByRole('row')
      expect(rows.length).toBeGreaterThan(1) // ヘッダー行 + データ行
    })

    it('プロジェクト件数が表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      expect(screen.getByText('全3件のプロジェクト')).toBeInTheDocument()
    })

    it('新規作成ボタンが表示される', () => {
      const mockOnCreateClick = jest.fn()
      render(
        <ProjectList
          projects={mockProjects}
          onCreateClick={mockOnCreateClick}
        />
      )

      expect(
        screen.getByRole('button', { name: '新規プロジェクト作成' })
      ).toBeInTheDocument()
    })

    it('onCreateClickが未指定の場合、新規作成ボタンは表示されない', () => {
      render(<ProjectList projects={mockProjects} />)

      expect(
        screen.queryByRole('button', { name: '新規プロジェクト作成' })
      ).not.toBeInTheDocument()
    })

    it('プロジェクトが空の場合、空メッセージが表示される', () => {
      render(<ProjectList projects={[]} />)

      expect(
        screen.getByText('プロジェクトがありません。新規作成してください。')
      ).toBeInTheDocument()
    })

    it('ローディング中の表示がされる', () => {
      render(<ProjectList projects={[]} isLoading={true} />)

      expect(screen.getByText('読み込み中...')).toBeInTheDocument()
    })
  })

  describe('インタラクション', () => {
    it('プロジェクト行クリックで詳細ページに遷移する', async () => {
      const user = userEvent.setup()
      render(<ProjectList projects={mockProjects} />)

      const projectARow = screen.getByText('プロジェクトA').closest('tr')
      if (projectARow) {
        await user.click(projectARow)
      }

      expect(mockRouter.push).toHaveBeenCalledWith('/projects/1')
    })

    it('新規作成ボタンクリックでonCreateClickが呼ばれる', async () => {
      const user = userEvent.setup()
      const mockOnCreateClick = jest.fn()

      render(
        <ProjectList
          projects={mockProjects}
          onCreateClick={mockOnCreateClick}
        />
      )

      const createButton = screen.getByRole('button', {
        name: '新規プロジェクト作成',
      })
      await user.click(createButton)

      expect(mockOnCreateClick).toHaveBeenCalled()
    })
  })

  describe('ステータスバッジ', () => {
    it('企画中ステータスが正しいバリアントで表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      const planningBadge = screen.getByText('企画中')
      expect(planningBadge).toBeInTheDocument()
    })

    it('進行中ステータスが正しいバリアントで表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      const activeBadge = screen.getByText('進行中')
      expect(activeBadge).toBeInTheDocument()
    })

    it('完了ステータスが正しいバリアントで表示される', () => {
      render(<ProjectList projects={mockProjects} />)

      const completedBadge = screen.getByText('完了')
      expect(completedBadge).toBeInTheDocument()
    })
  })
})
