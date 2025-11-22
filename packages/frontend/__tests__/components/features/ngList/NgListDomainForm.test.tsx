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

  describe('動的フィールド操作', () => {
    it('ドメイン追加ボタンでフィールドが追加される', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      // 初期状態では1つのフィールド
      const initialFields = screen.getAllByLabelText('ドメイン')
      expect(initialFields).toHaveLength(1)

      // ドメイン追加
      const addButton = screen.getByRole('button', { name: /ドメイン追加/i })
      await user.click(addButton)

      // アニメーション完了を待つ
      await waitFor(() => {
        const updatedFields = screen.getAllByLabelText('ドメイン')
        expect(updatedFields).toHaveLength(2)
      })
    })

    it('削除ボタンでフィールドが削除される', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      // フィールドを追加
      const addButton = screen.getByRole('button', { name: /ドメイン追加/i })
      await user.click(addButton)

      // アニメーション完了を待つ
      await waitFor(() => {
        expect(screen.getAllByLabelText('ドメイン')).toHaveLength(2)
      })

      // 削除ボタンをクリック
      const deleteButtons = screen.getAllByRole('button', { name: '' })
      const trashButton = deleteButtons.find(
        (btn) => btn.querySelector('svg')?.getAttribute('class')?.includes('lucide')
      )
      if (trashButton) {
        await user.click(trashButton)
      }

      // フィールドが1つに戻る
      await waitFor(() => {
        expect(screen.getAllByLabelText('ドメイン')).toHaveLength(1)
      })
    })

    it('最後の1つは削除できない', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      // 初期状態では削除ボタンが表示されない
      const deleteButtons = screen.queryAllByRole('button', { name: '' })
      const trashButtons = deleteButtons.filter(
        (btn) => btn.querySelector('svg')?.getAttribute('class')?.includes('lucide')
      )
      expect(trashButtons).toHaveLength(0)
    })
  })

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

    it('メモが500文字を超える場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<NgListDomainForm listId={listId} />)

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'example.com')

      const memoInput = screen.getByLabelText('メモ（任意）')
      // 長い文字列を直接pasteで設定（typeは遅いため）
      const longMemo = 'a'.repeat(501)
      await user.click(memoInput)
      await user.paste(longMemo)
      await user.tab() // onBlur トリガー

      await waitFor(() => {
        expect(
          screen.getByText('メモは500文字以内で入力してください')
        ).toBeInTheDocument()
      })
    })
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

    it('複数ドメインを一括登録できる', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
      })

      render(
        <NgListDomainForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      // 1つ目のドメイン
      const firstDomainInput = screen.getByLabelText('ドメイン')
      await user.type(firstDomainInput, 'example.com')

      // 2つ目のドメインを追加
      const addButton = screen.getByRole('button', { name: /ドメイン追加/i })
      await user.click(addButton)

      // アニメーション完了を待つ
      await waitFor(() => {
        expect(screen.getAllByLabelText('ドメイン')).toHaveLength(2)
      })

      const domainInputs = screen.getAllByLabelText('ドメイン')
      await user.type(domainInputs[1], 'test.com')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(ngListDomainsApi.createNgListDomain).toHaveBeenCalledTimes(2)
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })

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

    it('送信中はボタンが無効化される', async () => {
      const user = userEvent.setup()
      ;(ngListDomainsApi.createNgListDomain as jest.Mock).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      render(<NgListDomainForm listId={listId} />)

      const domainInput = screen.getByLabelText('ドメイン')
      await user.type(domainInput, 'example.com')

      const submitButton = screen.getByRole('button', {
        name: /NGドメインを登録/i,
      })
      await user.click(submitButton)

      // 送信中はボタンが無効化される
      expect(submitButton).toBeDisabled()
      expect(screen.getByText('登録中...')).toBeInTheDocument()

      // 送信完了まで待機
      await waitFor(
        () => {
          expect(ngListDomainsApi.createNgListDomain).toHaveBeenCalled()
        },
        { timeout: 200 }
      )
    })
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
