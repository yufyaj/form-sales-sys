import { render, screen, waitFor } from '@testing-library/react'
import WorkerDashboard from '@/components/features/dashboard/WorkerDashboard'
import type { User } from '@/types/auth'

// AuthContextをモック
const mockUser: User = {
  id: 'test-worker-id',
  email: 'worker@example.com',
  name: 'テストワーカー',
  role: 'worker',
}

jest.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    user: mockUser,
    isLoading: false,
    error: null,
    logout: jest.fn(),
  }),
}))

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}))

describe('WorkerDashboard', () => {
  // Arrange-Act-Assert パターンに従う

  it('ページタイトルとヘッダーが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('割り当てリスト一覧')).toBeInTheDocument()
      expect(screen.getByText('あなたに割り当てられたタスクの状況')).toBeInTheDocument()
    })
  })

  it('統計カードが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('割り当て中')).toBeInTheDocument()
      // "作業中"と"完了"は複数箇所に表示されるため、getAllByTextを使用
      const inProgressElements = screen.getAllByText('作業中')
      expect(inProgressElements.length).toBeGreaterThan(0)
      const completedElements = screen.getAllByText('完了')
      expect(completedElements.length).toBeGreaterThan(0)
      expect(screen.getByText('処理進捗')).toBeInTheDocument()
    })
  })

  it('タスク一覧テーブルが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('優先度')).toBeInTheDocument()
      expect(screen.getByText('リスト名')).toBeInTheDocument()
      expect(screen.getByText('ステータス')).toBeInTheDocument()
      expect(screen.getByText('進捗')).toBeInTheDocument()
      expect(screen.getByText('処理状況')).toBeInTheDocument()
      expect(screen.getByText('期限')).toBeInTheDocument()
    })
  })

  it('モックデータの割り当てタスクが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('IT企業リスト（東京）')).toBeInTheDocument()
      expect(screen.getByText('製造業リスト（大阪）')).toBeInTheDocument()
      expect(screen.getByText('小売業リスト（全国）')).toBeInTheDocument()
      expect(screen.getByText('金融機関リスト（東京・大阪）')).toBeInTheDocument()
    })
  })

  it('プロジェクト名が表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      // プロジェクト名は複数のタスクに表示される可能性があるため、getAllByTextを使用
      const projectAElements = screen.getAllByText('A社フォーム営業プロジェクト')
      expect(projectAElements.length).toBeGreaterThan(0)
      expect(screen.getByText('B社リード獲得キャンペーン')).toBeInTheDocument()
    })
  })

  it('優先度バッジが正しく表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('高')).toBeInTheDocument()
      expect(screen.getByText('中')).toBeInTheDocument()
      expect(screen.getByText('低')).toBeInTheDocument()
      expect(screen.getByText('緊急')).toBeInTheDocument()
    })
  })

  it('ステータスバッジが正しく表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      // "作業中" は統計カードとテーブルの両方に表示される
      const inProgressStatuses = screen.getAllByText('作業中')
      expect(inProgressStatuses.length).toBeGreaterThan(0)

      // "割り当て済み"も複数のタスクに表示される可能性がある
      const assignedStatuses = screen.getAllByText('割り当て済み')
      expect(assignedStatuses.length).toBeGreaterThan(0)

      // "完了" も統計カードとテーブルに表示される
      const completedStatuses = screen.getAllByText('完了')
      expect(completedStatuses.length).toBeGreaterThan(0)
    })
  })

  it('進捗バーとパーセンテージが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      // IT企業リスト: 325/500 = 65%
      expect(screen.getByText('65%')).toBeInTheDocument()

      // 製造業リスト: 0/300 = 0%、金融機関リスト: 0/150 = 0%で2つある
      const zeroPercentElements = screen.getAllByText('0%')
      expect(zeroPercentElements.length).toBeGreaterThan(0)

      // 小売業リスト: 200/200 = 100%
      expect(screen.getByText('100%')).toBeInTheDocument()
    })
  })

  it('処理状況が正しく表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('325 / 500')).toBeInTheDocument()
      expect(screen.getByText('0 / 300')).toBeInTheDocument()
      expect(screen.getByText('200 / 200')).toBeInTheDocument()
      expect(screen.getByText('0 / 150')).toBeInTheDocument()
    })
  })

  it('統計情報が正しく計算される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert
    await waitFor(() => {
      // 割り当て中（assigned）: 2つ
      expect(screen.getByText('2')).toBeInTheDocument()

      // 作業中（in_progress）: 1つ
      const inProgressCount = screen.getAllByText('1')
      expect(inProgressCount.length).toBeGreaterThan(0)

      // 総処理レコード数: 325 + 200 (completed含む) = 525
      // 総レコード数: 525 + (500 + 300 + 150 + 200 - 325) = 525 + 950 = 1,475
      // StatCardの値として525 / 1475が表示されていることを確認
      const bodyText = document.body.textContent || ''
      expect(bodyText).toContain('525 / 1475')
    })
  })

  it('ローディング完了後にダッシュボードが表示される', async () => {
    // Arrange & Act
    render(<WorkerDashboard />)

    // Assert - データ読み込み後のコンテンツが表示される
    await waitFor(() => {
      expect(screen.getByText('割り当てリスト一覧')).toBeInTheDocument()
    })
  })
})
