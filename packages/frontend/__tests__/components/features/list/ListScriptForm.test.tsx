import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ListScriptForm } from '@/components/features/list/ListScriptForm'
import * as listScriptsApi from '@/lib/api/listScripts'

// APIモジュールをモック
jest.mock('@/lib/api/listScripts')

describe('ListScriptForm', () => {
  const listId = 1
  const mockOnSuccess = jest.fn()
  const mockOnCancel = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('フォームのレンダリング', () => {
    it('初期状態で1つのスクリプト入力フィールドが表示される', () => {
      render(<ListScriptForm listId={listId} />)

      expect(screen.getByLabelText('件名')).toBeInTheDocument()
      expect(screen.getByLabelText('本文')).toBeInTheDocument()
    })

    it('スクリプト追加ボタンが表示される', () => {
      render(<ListScriptForm listId={listId} />)

      expect(
        screen.getByRole('button', { name: /スクリプト追加/i })
      ).toBeInTheDocument()
    })

    it('登録ボタンが表示される', () => {
      render(<ListScriptForm listId={listId} />)

      expect(
        screen.getByRole('button', { name: /スクリプトを登録/i })
      ).toBeInTheDocument()
    })

    it('onCancelが指定されている場合、キャンセルボタンが表示される', () => {
      render(
        <ListScriptForm
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
    it('件名が空の場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<ListScriptForm listId={listId} />)

      const submitButton = screen.getByRole('button', {
        name: /スクリプトを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('タイトルを入力してください')
        ).toBeInTheDocument()
      })
    })

    it('本文が空の場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<ListScriptForm listId={listId} />)

      const titleInput = screen.getByLabelText('件名')
      await user.type(titleInput, 'テスト件名')

      const submitButton = screen.getByRole('button', {
        name: /スクリプトを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('本文を入力してください')
        ).toBeInTheDocument()
      })
    })

    it('件名が255文字を超える場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<ListScriptForm listId={listId} />)

      const titleInput = screen.getByLabelText('件名')
      // 256文字の入力
      const longTitle = 'あ'.repeat(256)
      await user.type(titleInput, longTitle)
      await user.tab() // onBlur トリガー

      await waitFor(() => {
        expect(
          screen.getByText('タイトルは255文字以内で入力してください')
        ).toBeInTheDocument()
      })
    })

    it('本文が10000文字を超える場合エラーが表示される', async () => {
      const user = userEvent.setup()

      render(<ListScriptForm listId={listId} />)

      const contentInput = screen.getByLabelText('本文')
      // 10001文字の入力
      const longContent = 'あ'.repeat(10001)
      await user.type(contentInput, longContent)
      await user.tab() // onBlur トリガー

      await waitFor(() => {
        expect(
          screen.getByText('本文は10,000文字以内で入力してください')
        ).toBeInTheDocument()
      })
    })

    it('正しい入力はバリデーションを通過する', async () => {
      const user = userEvent.setup()
      ;(listScriptsApi.createListScript as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
        title: 'テスト件名',
        content: 'テスト本文',
      })

      render(
        <ListScriptForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      const titleInput = screen.getByLabelText('件名')
      await user.type(titleInput, 'テスト件名')

      const contentInput = screen.getByLabelText('本文')
      await user.type(contentInput, 'テスト本文')

      const submitButton = screen.getByRole('button', {
        name: /スクリプトを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(listScriptsApi.createListScript).toHaveBeenCalled()
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })
  })

  describe('フォーム送信', () => {
    it('正しい入力でフォームが送信される', async () => {
      const user = userEvent.setup()
      ;(listScriptsApi.createListScript as jest.Mock).mockResolvedValue({
        id: 1,
        listId,
        title: 'テスト件名',
        content: 'テスト本文\n改行も含む',
      })

      render(
        <ListScriptForm
          listId={listId}
          onSuccess={mockOnSuccess}
        />
      )

      const titleInput = screen.getByLabelText('件名')
      await user.type(titleInput, 'テスト件名')

      const contentInput = screen.getByLabelText('本文')
      await user.type(contentInput, 'テスト本文{Enter}改行も含む')

      const submitButton = screen.getByRole('button', {
        name: /スクリプトを登録/i,
      })
      await user.click(submitButton)

      await waitFor(() => {
        expect(listScriptsApi.createListScript).toHaveBeenCalledWith(
          expect.objectContaining({
            listId,
            title: 'テスト件名',
          })
        )
        expect(mockOnSuccess).toHaveBeenCalled()
      })
    })

    // 複数スクリプト一括登録のテストはE2Eテストで実施

    it('送信エラー時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      ;(listScriptsApi.createListScript as jest.Mock).mockRejectedValue(
        new Error('Server error')
      )

      render(<ListScriptForm listId={listId} />)

      const titleInput = screen.getByLabelText('件名')
      await user.type(titleInput, 'テスト件名')

      const contentInput = screen.getByLabelText('本文')
      await user.type(contentInput, 'テスト本文')

      const submitButton = screen.getByRole('button', {
        name: /スクリプトを登録/i,
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
        <ListScriptForm
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
