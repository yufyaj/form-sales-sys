import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SalesCompanyDashboard from '@/components/features/dashboard/SalesCompanyDashboard'

// Next.jsのuseRouterをモック
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
  }),
}))

describe('SalesCompanyDashboard', () => {
  // Arrange-Act-Assert パターンに従う

  it('コンポーネントが正しくレンダリングされる', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert - データ読み込み後のコンテンツが表示される
    await waitFor(() => {
      expect(screen.getByText('プロジェクト一覧')).toBeInTheDocument()
    })
  })

  it('ページタイトルとヘッダーが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('プロジェクト一覧')).toBeInTheDocument()
      expect(screen.getByText('進行中のプロジェクトと統計情報')).toBeInTheDocument()
    })
  })

  it('統計カードが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('総プロジェクト数')).toBeInTheDocument()
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
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('プロジェクト名')).toBeInTheDocument()
      expect(screen.getByText('ステータス')).toBeInTheDocument()
      expect(screen.getByText('進捗')).toBeInTheDocument()
      expect(screen.getByText('リスト数')).toBeInTheDocument()
      expect(screen.getByText('送信数')).toBeInTheDocument()
    })
  })

  it('モックデータのプロジェクトが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('A社フォーム営業プロジェクト')).toBeInTheDocument()
      expect(screen.getByText('B社リード獲得キャンペーン')).toBeInTheDocument()
      expect(screen.getByText('C社市場調査プロジェクト')).toBeInTheDocument()
    })
  })

  it('顧客名が表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('A株式会社')).toBeInTheDocument()
      expect(screen.getByText('B株式会社')).toBeInTheDocument()
      expect(screen.getByText('C株式会社')).toBeInTheDocument()
    })
  })

  it('ステータスバッジが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      const activeStatuses = screen.getAllByText('進行中')
      // "進行中" は統計カードとテーブルの両方に表示される
      expect(activeStatuses.length).toBeGreaterThan(0)
      const completedStatuses = screen.getAllByText('完了')
      expect(completedStatuses.length).toBeGreaterThan(0)
    })
  })

  it('進捗バーが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('65%')).toBeInTheDocument()
      expect(screen.getByText('40%')).toBeInTheDocument()
      expect(screen.getByText('100%')).toBeInTheDocument()
    })
  })

  it('新規プロジェクトボタンが表示される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      expect(screen.getByText('新規プロジェクト')).toBeInTheDocument()
    })
  })

  it('新規プロジェクトボタンをクリックするとコンソールログが出力される', async () => {
    // Arrange
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation()
    const user = userEvent.setup()
    render(<SalesCompanyDashboard />)

    await waitFor(() => {
      expect(screen.getByText('新規プロジェクト')).toBeInTheDocument()
    })

    // Act
    const button = screen.getByText('新規プロジェクト')
    await user.click(button)

    // Assert
    expect(consoleSpy).toHaveBeenCalledWith('プロジェクト作成')

    consoleSpy.mockRestore()
  })

  it('統計情報が正しく計算される', async () => {
    // Arrange & Act
    render(<SalesCompanyDashboard />)

    // Assert
    await waitFor(() => {
      // モックデータには3つのプロジェクトがある
      expect(screen.getByText('3')).toBeInTheDocument() // 総プロジェクト数

      // 進行中のプロジェクトは2つ
      const activeCount = screen.getAllByText('2')
      expect(activeCount.length).toBeGreaterThan(0)

      // 完了したプロジェクトは1つ
      const completedCount = screen.getAllByText('1')
      expect(completedCount.length).toBeGreaterThan(0)

      // 総送信数は1250 + 680 + 450 = 2,380
      expect(screen.getByText('2,380')).toBeInTheDocument()
    })
  })
})
