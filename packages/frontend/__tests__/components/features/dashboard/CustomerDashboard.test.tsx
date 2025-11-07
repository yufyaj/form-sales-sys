import { render, screen, waitFor } from '@testing-library/react'
import CustomerDashboard from '@/components/features/dashboard/CustomerDashboard'
import type { User } from '@/types/auth'

// AuthContextをモック
const mockUser: User = {
  id: 'test-user-id',
  email: 'customer@example.com',
  name: 'テスト顧客',
  role: 'customer',
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

describe('CustomerDashboard', () => {
  // Arrange-Act-Assert パターンに従う

  it('ページタイトルとヘッダーが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('依頼プロジェクト一覧')).toBeInTheDocument()
      expect(screen.getByText('あなたが依頼したプロジェクトの進捗状況')).toBeInTheDocument()
    })
  })

  it('統計カードが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('依頼中プロジェクト')).toBeInTheDocument()
      // "進行中"と"完了"は複数箇所に表示されるため、getAllByTextを使用
      const inProgressElements = screen.getAllByText('進行中')
      expect(inProgressElements.length).toBeGreaterThan(0)
      const completedElements = screen.getAllByText('完了')
      expect(completedElements.length).toBeGreaterThan(0)
      expect(screen.getByText('総送信数')).toBeInTheDocument()
    })
  })

  it('プロジェクト一覧テーブルが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('プロジェクト名')).toBeInTheDocument()
      expect(screen.getByText('ステータス')).toBeInTheDocument()
      expect(screen.getByText('進捗')).toBeInTheDocument()
      expect(screen.getByText('送信数')).toBeInTheDocument()
      expect(screen.getByText('作成日')).toBeInTheDocument()
    })
  })

  it('モックデータのプロジェクトが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('新規顧客獲得キャンペーン')).toBeInTheDocument()
      expect(screen.getByText('製品プロモーションプロジェクト')).toBeInTheDocument()
      expect(screen.getByText('市場調査プロジェクト')).toBeInTheDocument()
    })
  })

  it('プロジェクトの説明が表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('春季の新規顧客獲得のためのフォーム営業')).toBeInTheDocument()
      expect(screen.getByText('新製品のプロモーション向けリード獲得')).toBeInTheDocument()
    })
  })

  it('進捗バーとパーセンテージが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('65%')).toBeInTheDocument()
      expect(screen.getByText('40%')).toBeInTheDocument()
      expect(screen.getByText('100%')).toBeInTheDocument()
    })
  })

  it('送信数がカンマ区切りで表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('1,250')).toBeInTheDocument()
      expect(screen.getByText('680')).toBeInTheDocument()
      expect(screen.getByText('450')).toBeInTheDocument()
    })
  })

  it('統計情報が正しく計算される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert
    await waitFor(() => {
      // モックデータには3つのプロジェクトがある
      expect(screen.getByText('3')).toBeInTheDocument()

      // 総送信数は1250 + 680 + 450 = 2,380
      expect(screen.getByText('2,380')).toBeInTheDocument()
    })
  })

  it('ローディング完了後にダッシュボードが表示される', async () => {
    // Arrange & Act
    render(<CustomerDashboard />)

    // Assert - データ読み込み後のコンテンツが表示される
    await waitFor(() => {
      expect(screen.getByText('依頼プロジェクト一覧')).toBeInTheDocument()
    })
  })
})
