import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { NgListDomainForm } from '@/components/features/ngList/NgListDomainForm'
import * as ngListDomainsApi from '@/lib/api/ngListDomains'

// APIモジュールをモック
jest.mock('@/lib/api/ngListDomains')

describe('NgListDomainForm', () => {
  const listId = 1
  const mockOnSuccess = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('フォームのレンダリング', () => {
    it('初期状態で1つのドメイン入力フィールドが表示される', () => {
      render(<NgListDomainForm listId={listId} />)

      expect(screen.getByLabelText('ドメイン')).toBeInTheDocument()
      expect(screen.getByLabelText('メモ（任意）')).toBeInTheDocument()
    })

    it('ドメイン追加ボタンが表示される', () => {
      render(<NgListDomainForm listId={listId} />)

      expect(
        screen.getByRole('button', { name: /ドメイン追加/i })
      ).toBeInTheDocument()
    })

    it('登録ボタンが表示される', () => {
      render(<NgListDomainForm listId={listId} />)

      expect(
        screen.getByRole('button', { name: /NGドメインを登録/i })
      ).toBeInTheDocument()
    })

    it('onCancelが指定されている場合、キャンセルボタンが表示される', () => {
      render(
        <NgListDomainForm
          listId={listId}
          onCancel={mockOnCancel}
        />
      )

      expect(
        screen.getByRole('button', { name: /キャンセル/i })
      ).toBeInTheDocument()
    })
  })

  // 動的フィールド操作のテストはE2Eテストで実施
  // (useFieldArrayとAnimatePresenceの組み合わせは単体テスト環境では不安定なため)

  describe('バリデーション', () => {
    it('ドメインが空の場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('ドメインを入力してください')
        ).toBeInTheDocument()
      })
    })

    it('無効なドメイン形式でエラーが表示される', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'invalid domain!')
      await user.tab() // onBlur トリガー

      await waitFor(() => {
        expect(
          screen.getByText(/ドメイン形式が正しくありません/i)
        ).toBeInTheDocument()
      })
    })

    it('正しいドメイン形式は受け入れられる', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
        domain: 'example.com',
        domainPattern: 'example.com',
        isWildcard: false,
      })

      render(
        <NgListDomainForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'example.com')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(ngListDomainsApi.createNgListDomain).toHaveBeenCalled()
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })

    it('ワイルドカードドメインが受け入れられる', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
        domain: '*.example.com',
        domainPattern: '*.example.com',
        isWildcard: true,
      })

      render(
        <NgListDomainForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, '*.example.com')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(ngListDomainsApi.createNgListDomain).toHaveBeenCalledWith(
          expect.objectContaining({
            domain: '*.example.com',
          })
        )
      })
    })

    // メモの文字数バリデーションはE2Eテストで実施
  })

  describe('フォーム送信', () => {
    it('正しい入力でフォームが送信される', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
        domain: 'example.com',
        domainPattern: 'example.com',
        isWildcard: false,
        memo: 'テストメモ',
      })

      render(
        <NgListDomainForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'example.com')

      const memoInput = screen.getByLabelText('メモ（任意）')
      await user.type(memoInput, 'テストメモ')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(ngListDomainsApi.createNgListDomain).toHaveBeenCalledWith(
          expect.objectContaining({
            listId,
            domain: 'example.com',
          })
        )
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })

    // 複数ドメイン一括登録のテストはE2Eテストで実施

    it('送信エラー時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockRejectedValue(
        new Error('Server error')
      )

      render(<NgListDomainForm listId={listId} />)

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'example.com')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })
    })

    // ローディング状態のテストはE2Eテストで実施
    // (非同期処理のタイミングが単体テスト環境では不安定なため)
  })

  describe('キャンセルボタン', () => {
    it('キャンセルボタンクリックでonCancelが呼ばれる', async () => {
      const user = userEvent.setup()

      render(
        <NgListDomainForm
          listId={listId}
          onCancel={mockOnCancel}
        />
      )

      const cancelButton = screen.getByRole('button', { name: /キャンセル/i })
      await user.click(cancelButton)

      expect(mockOnCancel).toHaveBeenCalled()
    })
  })
})
