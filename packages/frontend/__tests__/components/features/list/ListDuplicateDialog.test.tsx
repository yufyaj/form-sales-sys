import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ListDuplicateDialog from '@/components/features/list/ListDuplicateDialog'

describe('ListDuplicateDialog', () => {
  const defaultProps = {
    open: true,
    onOpenChange: jest.fn(),
    originalListName: 'テストリスト',
    onDuplicate: jest.fn(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('ダイアログのレンダリング', () => {
    it('ダイアログが開いている場合、全ての要素が表示される', () => {
      render(<ListDuplicateDialog {...defaultProps} />)

      expect(screen.getByText('リストを複製')).toBeInTheDocument()
      expect(
        screen.getByText('「テストリスト」を複製します。新しいリスト名を入力してください。')
      ).toBeInTheDocument()
      expect(screen.getByLabelText('新しいリスト名')).toBeInTheDocument()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeInTheDocument()
      expect(screen.getByRole('button', { name: '複製' })).toBeInTheDocument()
    })

    it('ダイアログが閉じている場合、何も表示されない', () => {
      render(<ListDuplicateDialog {...defaultProps} open={false} />)

      expect(screen.queryByText('リストを複製')).not.toBeInTheDocument()
    })

    it('デフォルトで「{元のリスト名}のコピー」が入力されている', () => {
      render(<ListDuplicateDialog {...defaultProps} />)

      const input = screen.getByLabelText('新しいリスト名')
      expect(input).toHaveValue('テストリストのコピー')
    })
  })

  describe('バリデーション', () => {
    it('リスト名が空の場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<ListDuplicateDialog {...defaultProps} />)

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リスト名を入力してください')
        ).toBeInTheDocument()
      })

      expect(defaultProps.onDuplicate).not.toHaveBeenCalled()
    })

    it('リスト名が空白のみの場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<ListDuplicateDialog {...defaultProps} />)

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '   ')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リスト名を入力してください')
        ).toBeInTheDocument()
      })

      expect(defaultProps.onDuplicate).not.toHaveBeenCalled()
    })

    it('リスト名が255文字を超える場合、エラーが表示される', async () => {
      const user = userEvent.setup()
      render(<ListDuplicateDialog {...defaultProps} />)

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      const longName = 'あ'.repeat(256)
      await user.type(input, longName)

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リスト名は255文字以内で入力してください')
        ).toBeInTheDocument()
      })

      expect(defaultProps.onDuplicate).not.toHaveBeenCalled()
    })
  })

  describe('複製機能', () => {
    it('正しい入力で複製が実行される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockResolvedValue(undefined)

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalledWith('新しいリスト名')
      })

      // 成功後、ダイアログが閉じられる
      expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false)
    })

    it('複製中はボタンが無効化される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      // 送信中はボタンが無効化される
      expect(submitButton).toBeDisabled()
      expect(
        screen.getByRole('button', { name: 'キャンセル' })
      ).toBeDisabled()
      expect(input).toBeDisabled()

      // 送信完了まで待機
      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalled()
      })
    })

    it('複製失敗時にエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest
        .fn()
        .mockRejectedValue(new Error('Network Error'))
      const mockOnOpenChange = jest.fn()

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
          onOpenChange={mockOnOpenChange}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('ネットワークエラーが発生しました')).toBeInTheDocument()
      })

      // エラー時はダイアログは閉じない（falseで呼ばれていない）
      expect(mockOnOpenChange).not.toHaveBeenCalledWith(false)
    })

    it('エラーがError型でない場合、デフォルトエラーメッセージが表示される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockRejectedValue('Unknown error')

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リストの複製に失敗しました')
        ).toBeInTheDocument()
      })
    })
  })

  describe('キャンセル機能', () => {
    it('キャンセルボタンクリックでonOpenChangeが呼ばれる', async () => {
      const user = userEvent.setup()
      render(<ListDuplicateDialog {...defaultProps} />)

      const cancelButton = screen.getByRole('button', { name: 'キャンセル' })
      await user.click(cancelButton)

      expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false)
    })

    it('閉じるアイコンクリックでonOpenChangeが呼ばれる', async () => {
      const user = userEvent.setup()
      render(<ListDuplicateDialog {...defaultProps} />)

      const closeButton = screen.getByRole('button', { name: 'ダイアログを閉じる' })
      await user.click(closeButton)

      expect(defaultProps.onOpenChange).toHaveBeenCalledWith(false)
    })
  })

  describe('状態管理', () => {
    it('ダイアログが再度開かれた時、前回の入力がリセットされる', async () => {
      const user = userEvent.setup()
      const { rerender } = render(
        <ListDuplicateDialog {...defaultProps} open={false} />
      )

      // ダイアログを開く
      rerender(<ListDuplicateDialog {...defaultProps} open={true} />)

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, 'カスタム名')

      // ダイアログを閉じる
      rerender(<ListDuplicateDialog {...defaultProps} open={false} />)

      // 再度開く
      rerender(<ListDuplicateDialog {...defaultProps} open={true} />)

      // デフォルト値に戻っている
      expect(screen.getByLabelText('新しいリスト名')).toHaveValue(
        'テストリストのコピー'
      )
    })

    it('ダイアログが閉じられた時、エラー状態がリセットされる', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest
        .fn()
        .mockRejectedValue(new Error('Network Error'))

      const { rerender } = render(
        <ListDuplicateDialog
          {...defaultProps}
          open={true}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      // エラーが表示される
      await waitFor(() => {
        expect(screen.getByText('ネットワークエラーが発生しました')).toBeInTheDocument()
      })

      // ダイアログを閉じる
      rerender(
        <ListDuplicateDialog
          {...defaultProps}
          open={false}
          onDuplicate={mockOnDuplicate}
        />
      )

      // 再度開く
      rerender(
        <ListDuplicateDialog
          {...defaultProps}
          open={true}
          onDuplicate={mockOnDuplicate}
        />
      )

      // エラーが消えている
      expect(screen.queryByText('ネットワークエラーが発生しました')).not.toBeInTheDocument()
    })
  })

  describe('セキュリティテスト', () => {
    it('制御文字を含む入力が適切に処理される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockResolvedValue(undefined)

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      // 制御文字を含む文字列を入力
      await user.type(input, 'Test\x00\x01\x1F\x7FList')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      // 制御文字が除去されて送信されることを確認
      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalledWith('TestList')
      })
    })

    it('255文字ちょうどの入力が許可される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockResolvedValue(undefined)

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const exactLength = 'あ'.repeat(255)
      const input = screen.getByLabelText('新しいリスト名')

      await user.clear(input)
      await user.type(input, exactLength)

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalledWith(exactLength)
      })

      expect(screen.queryByText(/255文字以内/)).not.toBeInTheDocument()
    })

    it('254文字の入力が許可される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockResolvedValue(undefined)

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const validLength = 'あ'.repeat(254)
      const input = screen.getByLabelText('新しいリスト名')

      await user.clear(input)
      await user.type(input, validLength)

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalledWith(validLength)
      })

      expect(screen.queryByText(/255文字以内/)).not.toBeInTheDocument()
    })

    it('前後の空白がトリミングされる', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest.fn().mockResolvedValue(undefined)

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '  テストリスト  ')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnDuplicate).toHaveBeenCalledWith('テストリスト')
      })
    })

    it('既知のエラーメッセージが適切にマッピングされる', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest
        .fn()
        .mockRejectedValue(new Error('List name already exists'))

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('このリスト名は既に使用されています')
        ).toBeInTheDocument()
      })
    })

    it('未知のエラーメッセージがデフォルトメッセージに変換される', async () => {
      const user = userEvent.setup()
      const mockOnDuplicate = jest
        .fn()
        .mockRejectedValue(new Error('Unknown database error'))

      render(
        <ListDuplicateDialog
          {...defaultProps}
          onDuplicate={mockOnDuplicate}
        />
      )

      const input = screen.getByLabelText('新しいリスト名')
      await user.clear(input)
      await user.type(input, '新しいリスト名')

      const submitButton = screen.getByRole('button', { name: '複製' })
      await user.click(submitButton)

      await waitFor(() => {
        expect(
          screen.getByText('リストの複製に失敗しました')
        ).toBeInTheDocument()
      })

      // 元のエラーメッセージが表示されないことを確認（情報漏洩防止）
      expect(
        screen.queryByText('Unknown database error')
      ).not.toBeInTheDocument()
    })
  })
})
