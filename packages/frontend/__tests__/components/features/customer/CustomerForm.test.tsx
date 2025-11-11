import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CustomerForm from '@/components/features/customer/CustomerForm'
import type { ClientOrganization } from '@/types/customer'

describe('CustomerForm', () => {
  const mockCustomer: ClientOrganization = {
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
  }

  const mockOnSubmit = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('新規作成モード', () => {
    it('全ての入力フィールドが表示される', () => {
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      expect(screen.getByLabelText('業種')).toBeInTheDocument()
      expect(screen.getByLabelText('従業員数')).toBeInTheDocument()
      expect(screen.getByLabelText('年商（円）')).toBeInTheDocument()
      expect(screen.getByLabelText('設立年')).toBeInTheDocument()
      expect(screen.getByLabelText('Webサイト')).toBeInTheDocument()
      expect(screen.getByLabelText('担当営業')).toBeInTheDocument()
      expect(screen.getByLabelText('備考')).toBeInTheDocument()
    })

    it('登録ボタンとキャンセルボタンが表示される', () => {
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      expect(screen.getByRole('button', { name: '登録' })).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
    })

    it('キャンセルボタンをクリックすると、onCancelが呼ばれる', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalledTimes(1)
    })
  })

  describe('編集モード', () => {
    it('顧客名が読み取り専用で表示される', () => {
      render(
        <CustomerForm
          customer={mockCustomer}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      )

      expect(screen.getByText('顧客名')).toBeInTheDocument()
      expect(screen.getByText('株式会社テスト')).toBeInTheDocument()
    })

    it('既存の値がフォームに設定される', () => {
      render(
        <CustomerForm
          customer={mockCustomer}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      )

      const industryInput = screen.getByLabelText('業種') as HTMLInputElement
      const employeeInput = screen.getByLabelText(
        '従業員数'
      ) as HTMLInputElement
      const revenueInput = screen.getByLabelText(
        '年商（円）'
      ) as HTMLInputElement
      const yearInput = screen.getByLabelText('設立年') as HTMLInputElement
      const websiteInput = screen.getByLabelText('Webサイト') as HTMLInputElement
      const salesPersonInput = screen.getByLabelText(
        '担当営業'
      ) as HTMLInputElement
      const notesInput = screen.getByLabelText('備考') as HTMLTextAreaElement

      expect(industryInput.value).toBe('製造業')
      expect(employeeInput.value).toBe('500')
      expect(revenueInput.value).toBe('5000000000')
      expect(yearInput.value).toBe('1990')
      expect(websiteInput.value).toBe('https://test.example.com')
      expect(salesPersonInput.value).toBe('山田 太郎')
      expect(notesInput.value).toBe('テストメモ')
    })

    it('更新ボタンが表示される', () => {
      render(
        <CustomerForm
          customer={mockCustomer}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      )

      expect(screen.getByRole('button', { name: '更新' })).toBeInTheDocument()
    })
  })

  describe('バリデーション', () => {
    it('従業員数に負の数を入力すると、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const employeeInput = screen.getByLabelText('従業員数')

      await user.type(employeeInput, '-100')
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/従業員数は0以上である必要があります/i)
        ).toBeInTheDocument()
      })
    })

    it('年商に負の数を入力すると、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const revenueInput = screen.getByLabelText('年商（円）')

      await user.type(revenueInput, '-1000')
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/年商は0以上である必要があります/i)
        ).toBeInTheDocument()
      })
    })

    it('設立年に1800年以前を入力すると、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const yearInput = screen.getByLabelText('設立年')

      await user.type(yearInput, '1799')
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/設立年は1800年以降である必要があります/i)
        ).toBeInTheDocument()
      })
    })

    it('設立年に未来の年を入力すると、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const yearInput = screen.getByLabelText('設立年')
      const nextYear = new Date().getFullYear() + 1

      await user.type(yearInput, nextYear.toString())
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/設立年は未来の年を指定できません/i)
        ).toBeInTheDocument()
      })
    })

    it('無効なURL形式を入力すると、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      const websiteInput = screen.getByLabelText('Webサイト')

      await user.type(websiteInput, 'invalid-url')
      await user.tab()

      await waitFor(() => {
        expect(
          screen.getByText(/有効なURLを入力してください/i)
        ).toBeInTheDocument()
      })
    })
  })

  describe('フォーム送信', () => {
    it('正しい入力で送信すると、onSubmitが呼ばれる', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockResolvedValue(undefined)

      render(<CustomerForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />)

      await user.type(screen.getByLabelText('業種'), 'IT・通信')
      await user.type(screen.getByLabelText('従業員数'), '100')
      await user.type(screen.getByLabelText('年商（円）'), '1000000000')
      await user.type(screen.getByLabelText('設立年'), '2020')
      await user.type(
        screen.getByLabelText('Webサイト'),
        'https://example.com'
      )
      await user.type(screen.getByLabelText('担当営業'), '佐藤 花子')
      await user.type(screen.getByLabelText('備考'), 'テスト備考')

      const submitButton = screen.getByRole('button', { name: '登録' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1)
        expect(mockOnSubmit).toHaveBeenCalledWith({
          industry: 'IT・通信',
          employeeCount: 100,
          annualRevenue: 1000000000,
          establishedYear: 2020,
          website: 'https://example.com',
          salesPerson: '佐藤 花子',
          notes: 'テスト備考',
        })
      })
    })

    it('isLoadingがtrueの場合、ボタンが無効化される', () => {
      render(
        <CustomerForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={true}
        />
      )

      const submitButton = screen.getByRole('button', { name: '登録中...' })
      expect(submitButton).toBeDisabled()
      expect(screen.getByRole('button', { name: 'キャンセル' })).toBeDisabled()
    })

    it('編集モードで送信すると、更新データが送信される', async () => {
      const user = userEvent.setup()
      mockOnSubmit.mockResolvedValue(undefined)

      render(
        <CustomerForm
          customer={mockCustomer}
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
        />
      )

      const industryInput = screen.getByLabelText('業種')
      await user.clear(industryInput)
      await user.type(industryInput, 'サービス業')

      const submitButton = screen.getByRole('button', { name: '更新' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledTimes(1)
        expect(mockOnSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            industry: 'サービス業',
          })
        )
      })
    })
  })

  describe('ローディング状態', () => {
    it('ローディング中は全てのボタンが無効化される', () => {
      render(
        <CustomerForm
          onSubmit={mockOnSubmit}
          onCancel={mockOnCancel}
          isLoading={true}
        />
      )

      expect(screen.getByRole('button', { name: '登録中...' })).toBeDisabled()
      expect(screen.getByRole('button', { name: 'キャンセル' })).toBeDisabled()
    })
  })
})
