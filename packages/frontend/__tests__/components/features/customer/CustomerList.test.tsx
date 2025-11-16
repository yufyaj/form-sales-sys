import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CustomerList from '@/components/features/customer/CustomerList'
import type { ClientOrganization } from '@/types/customer'

// Next.jsのルーターをモック
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    refresh: jest.fn(),
  }),
}))

describe('CustomerList', () => {
  const mockCustomers: ClientOrganization[] = [
    {
      id: 1,
      organizationId: 101,
      organizationName: '株式会社テスト',
      industry: '製造業',
      employeeCount: 500,
      annualRevenue: 5000000000,
      establishedYear: 1990,
      website: 'https://test.example.com',
      salesPerson: '山田 太郎',
      notes: 'テストメモ',
      createdAt: '2025-01-01T00:00:00Z',
      updatedAt: '2025-01-01T00:00:00Z',
      deletedAt: null,
    },
    {
      id: 2,
      organizationId: 102,
      organizationName: 'サンプル株式会社',
      industry: 'IT・通信',
      employeeCount: 200,
      annualRevenue: 2000000000,
      establishedYear: 2010,
      website: 'https://sample.example.com',
      salesPerson: '佐藤 花子',
      notes: null,
      createdAt: '2025-01-02T00:00:00Z',
      updatedAt: '2025-01-02T00:00:00Z',
      deletedAt: null,
    },
    {
      id: 3,
      organizationId: 103,
      organizationName: 'デモ企業株式会社',
      industry: 'サービス業',
      employeeCount: 50,
      annualRevenue: 500000000,
      establishedYear: 2020,
      website: null,
      salesPerson: '田中 一郎',
      notes: null,
      createdAt: '2025-01-03T00:00:00Z',
      updatedAt: '2025-01-03T00:00:00Z',
      deletedAt: null,
    },
  ]

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('顧客一覧のヘッダーが表示される', () => {
    render(<CustomerList customers={mockCustomers} />)

    expect(screen.getByText('顧客一覧')).toBeInTheDocument()
    expect(screen.getByText('3件の顧客を表示中')).toBeInTheDocument()
  })

  it('全ての顧客が表示される', () => {
    render(<CustomerList customers={mockCustomers} />)

    expect(screen.getByText('株式会社テスト')).toBeInTheDocument()
    expect(screen.getByText('サンプル株式会社')).toBeInTheDocument()
    expect(screen.getByText('デモ企業株式会社')).toBeInTheDocument()
  })

  it('顧客情報が正しく表示される', () => {
    render(<CustomerList customers={mockCustomers} />)

    // 業種が表示される
    expect(screen.getByText('製造業')).toBeInTheDocument()
    expect(screen.getByText('IT・通信')).toBeInTheDocument()

    // 従業員数が表示される
    expect(screen.getByText('500名')).toBeInTheDocument()
    expect(screen.getByText('200名')).toBeInTheDocument()

    // 年商が表示される
    expect(screen.getByText('¥5,000,000,000')).toBeInTheDocument()
    expect(screen.getByText('¥2,000,000,000')).toBeInTheDocument()

    // 担当営業が表示される
    expect(screen.getByText('山田 太郎')).toBeInTheDocument()
    expect(screen.getByText('佐藤 花子')).toBeInTheDocument()
  })

  it('検索機能が動作する', async () => {
    const user = userEvent.setup()
    render(<CustomerList customers={mockCustomers} />)

    const searchInput = screen.getByPlaceholderText(
      /顧客名、業種、担当営業で検索/i
    )

    // 「テスト」で検索
    await user.type(searchInput, 'テスト')

    await waitFor(() => {
      expect(screen.getByText('株式会社テスト')).toBeInTheDocument()
      expect(screen.queryByText('サンプル株式会社')).not.toBeInTheDocument()
      expect(screen.queryByText('デモ企業株式会社')).not.toBeInTheDocument()
      expect(screen.getByText('1件の顧客を表示中')).toBeInTheDocument()
    })
  })

  it('業種で検索できる', async () => {
    const user = userEvent.setup()
    render(<CustomerList customers={mockCustomers} />)

    const searchInput = screen.getByPlaceholderText(
      /顧客名、業種、担当営業で検索/i
    )

    await user.type(searchInput, 'IT')

    await waitFor(() => {
      expect(screen.getByText('サンプル株式会社')).toBeInTheDocument()
      expect(screen.queryByText('株式会社テスト')).not.toBeInTheDocument()
      expect(screen.queryByText('デモ企業株式会社')).not.toBeInTheDocument()
    })
  })

  it('担当営業で検索できる', async () => {
    const user = userEvent.setup()
    render(<CustomerList customers={mockCustomers} />)

    const searchInput = screen.getByPlaceholderText(
      /顧客名、業種、担当営業で検索/i
    )

    await user.type(searchInput, '佐藤')

    await waitFor(() => {
      expect(screen.getByText('サンプル株式会社')).toBeInTheDocument()
      expect(screen.queryByText('株式会社テスト')).not.toBeInTheDocument()
    })
  })

  it('検索結果が0件の場合、適切なメッセージが表示される', async () => {
    const user = userEvent.setup()
    render(<CustomerList customers={mockCustomers} />)

    const searchInput = screen.getByPlaceholderText(
      /顧客名、業種、担当営業で検索/i
    )

    await user.type(searchInput, '存在しない顧客')

    await waitFor(() => {
      expect(
        screen.getByText('検索条件に一致する顧客が見つかりませんでした')
      ).toBeInTheDocument()
    })
  })

  it('顧客が0件の場合、適切なメッセージが表示される', () => {
    render(<CustomerList customers={[]} />)

    expect(screen.getByText('顧客が登録されていません')).toBeInTheDocument()
  })

  it('顧客追加ボタンが表示される', () => {
    const mockOnAddCustomer = jest.fn()
    render(
      <CustomerList customers={mockCustomers} onAddCustomer={mockOnAddCustomer} />
    )

    const addButton = screen.getByRole('button', { name: '顧客を追加' })
    expect(addButton).toBeInTheDocument()
  })

  it('顧客追加ボタンをクリックすると、onAddCustomerが呼ばれる', async () => {
    const user = userEvent.setup()
    const mockOnAddCustomer = jest.fn()
    render(
      <CustomerList customers={mockCustomers} onAddCustomer={mockOnAddCustomer} />
    )

    const addButton = screen.getByRole('button', { name: '顧客を追加' })
    await user.click(addButton)

    expect(mockOnAddCustomer).toHaveBeenCalledTimes(1)
  })

  it('顧客行をクリックすると、onCustomerClickが呼ばれる', async () => {
    const user = userEvent.setup()
    const mockOnCustomerClick = jest.fn()
    render(
      <CustomerList
        customers={mockCustomers}
        onCustomerClick={mockOnCustomerClick}
      />
    )

    const customerRow = screen.getByText('株式会社テスト').closest('tr')
    expect(customerRow).toBeInTheDocument()

    if (customerRow) {
      await user.click(customerRow)
    }

    expect(mockOnCustomerClick).toHaveBeenCalledTimes(1)
    expect(mockOnCustomerClick).toHaveBeenCalledWith(mockCustomers[0])
  })

  it('ローディング中は適切な表示がされる', () => {
    render(<CustomerList customers={[]} isLoading={true} />)

    expect(screen.getByText('読み込み中...')).toBeInTheDocument()
  })

  it('Webサイトリンクが正しく表示される', () => {
    render(<CustomerList customers={mockCustomers} />)

    const links = screen.getAllByRole('link', { name: 'リンク' })
    expect(links).toHaveLength(2) // Webサイトを持つ顧客は2件

    expect(links[0]).toHaveAttribute('href', 'https://test.example.com')
    expect(links[0]).toHaveAttribute('target', '_blank')
    expect(links[0]).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('Webサイトがない場合、"-"が表示される', () => {
    render(<CustomerList customers={[mockCustomers[2]]} />)

    // デモ企業株式会社はWebサイトがnull
    const cells = screen.getAllByRole('cell')
    const websiteCell = cells.find((cell) => cell.textContent === '-')
    expect(websiteCell).toBeInTheDocument()
  })

  it('従業員数がnullの場合、"-"が表示される', () => {
    const customerWithoutEmployeeCount: ClientOrganization = {
      ...mockCustomers[0],
      employeeCount: null,
    }

    render(<CustomerList customers={[customerWithoutEmployeeCount]} />)

    const cells = screen.getAllByRole('cell')
    // 従業員数列に"-"が表示されることを確認
    expect(screen.getAllByText('-').length).toBeGreaterThan(0)
  })

  it('年商がnullの場合、"-"が表示される', () => {
    const customerWithoutRevenue: ClientOrganization = {
      ...mockCustomers[0],
      annualRevenue: null,
    }

    render(<CustomerList customers={[customerWithoutRevenue]} />)

    const cells = screen.getAllByRole('cell')
    expect(screen.getAllByText('-').length).toBeGreaterThan(0)
  })
})
