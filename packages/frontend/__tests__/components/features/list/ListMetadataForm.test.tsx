import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ListMetadataForm from '@/components/features/list/ListMetadataForm'

describe('ListMetadataForm', () => {
  const defaultProps = {
    listId: 1,
    projectId: 1,
    defaultValues: {},
    onSubmit: jest.fn().mockResolvedValue(undefined),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('レンダリング', () => {
    it('フォームが正しくレンダリングされる', () => {
      render(<ListMetadataForm {...defaultProps} />)

      expect(screen.getByLabelText('URL')).toBeInTheDocument()
      expect(screen.getByLabelText('説明')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /更新/ })).toBeInTheDocument()
    })

    it('デフォルト値が正しく表示される', () => {
      render(
        <ListMetadataForm
          {...defaultProps}
          defaultValues={{
            url: 'https://example.com',
            description: 'テスト説明',
          }}
        />
      )

      const urlInput = screen.getByLabelText('URL') as HTMLInputElement
      const descriptionInput = screen.getByLabelText('説明') as HTMLTextAreaElement

      expect(urlInput.value).toBe('https://example.com')
      expect(descriptionInput.value).toBe('テスト説明')
    })
  })

  describe('バリデーション', () => {
    it('URLと説明の両方を更新できる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const urlInput = screen.getByLabelText('URL')
      const descriptionInput = screen.getByLabelText('説明')
      const submitButton = screen.getByRole('button', { name: /更新/ })

      await user.type(urlInput, 'https://example.com')
      await user.type(descriptionInput, 'テスト説明文')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          url: 'https://example.com',
          description: 'テスト説明文',
        })
      })
    })

    it('URLのみ更新できる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const urlInput = screen.getByLabelText('URL')
      const submitButton = screen.getByRole('button', { name: /更新/ })

      await user.type(urlInput, 'https://example.com')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          url: 'https://example.com',
          description: '',
        })
      })
    })

    it('説明のみ更新できる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const descriptionInput = screen.getByLabelText('説明')
      const submitButton = screen.getByRole('button', { name: /更新/ })

      await user.type(descriptionInput, 'テスト説明文')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          url: '',
          description: 'テスト説明文',
        })
      })
    })

    it('無効なURLでバリデーションエラーを表示', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const urlInput = screen.getByLabelText('URL')
      await user.type(urlInput, 'invalid-url')
      await user.tab()

      expect(
        await screen.findByText('有効なURLを入力してください')
      ).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('HTTPのURLでバリデーションエラーを表示', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const urlInput = screen.getByLabelText('URL')
      await user.type(urlInput, 'http://example.com')
      await user.tab()

      expect(
        await screen.findByText('HTTPSのURLを入力してください')
      ).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('説明が5000文字を超えた場合にバリデーションエラーを表示', async () => {
      const mockOnSubmit = jest.fn()
      const longText = 'あ'.repeat(5001)

      render(
        <ListMetadataForm
          {...defaultProps}
          defaultValues={{ description: longText }}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: /更新/ })

      // フォームを送信してバリデーションエラーを確認
      await userEvent.click(submitButton)

      expect(
        await screen.findByText('説明は5000文字以内で入力してください')
      ).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  describe('送信処理', () => {
    it('送信中はボタンが無効化される', async () => {
      const user = userEvent.setup()
      let resolveSubmit: () => void
      const submitPromise = new Promise<void>((resolve) => {
        resolveSubmit = resolve
      })
      const mockOnSubmit = jest.fn(() => submitPromise)

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /更新/ })

      user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText('更新中...')).toBeInTheDocument()
      })

      resolveSubmit!()
    })

    it('送信エラー時にエラーメッセージを表示', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest
        .fn()
        .mockRejectedValue(new Error('情報の更新に失敗しました'))

      render(<ListMetadataForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /更新/ })

      // 空のフォームでも送信可能なので、そのまま送信
      await user.click(submitButton)

      expect(
        await screen.findByText('情報の更新に失敗しました')
      ).toBeInTheDocument()
    })
  })

  describe('XSS対策', () => {
    it('説明から制御文字が除去される', async () => {
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)
      const textWithControlChars = 'テスト\x00説明\x1F文'

      render(
        <ListMetadataForm
          {...defaultProps}
          defaultValues={{ description: textWithControlChars }}
          onSubmit={mockOnSubmit}
        />
      )

      const submitButton = screen.getByRole('button', { name: /更新/ })

      await userEvent.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({
          url: '',
          description: 'テスト説明文', // 制御文字が除去される
        })
      })
    })
  })
})
