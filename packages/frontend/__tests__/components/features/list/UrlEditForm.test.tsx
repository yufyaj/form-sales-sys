import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UrlEditForm from '@/components/features/list/UrlEditForm'

describe('UrlEditForm', () => {
  const defaultProps = {
    listId: 1,
    projectId: 1,
    defaultUrl: '',
    onSubmit: jest.fn().mockResolvedValue(undefined),
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  describe('レンダリング', () => {
    it('フォームが正しくレンダリングされる', () => {
      render(<UrlEditForm {...defaultProps} />)

      expect(screen.getByLabelText('URL')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /URLを更新/ })).toBeInTheDocument()
    })

    it('デフォルト値が正しく表示される', () => {
      render(<UrlEditForm {...defaultProps} defaultUrl="https://example.com" />)

      const input = screen.getByLabelText('URL') as HTMLInputElement
      expect(input.value).toBe('https://example.com')
    })
  })

  describe('バリデーション', () => {
    it('空のURLで送信できる（オプショナル）', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /URLを更新/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({ url: '' })
      })
    })

    it('有効なHTTPSのURLで送信できる', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const input = screen.getByLabelText('URL')
      const submitButton = screen.getByRole('button', { name: /URLを更新/ })

      await user.type(input, 'https://example.com')
      await user.click(submitButton)

      await waitFor(() => {
        expect(mockOnSubmit).toHaveBeenCalledWith({ url: 'https://example.com' })
      })
    })

    it('無効なURLでバリデーションエラーを表示', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const input = screen.getByLabelText('URL')
      await user.type(input, 'invalid-url')
      await user.tab() // onBlurトリガー

      expect(
        await screen.findByText('有効なURLを入力してください')
      ).toBeInTheDocument()
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })

    it('HTTPのURLでバリデーションエラーを表示（HTTPSのみ許可）', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn()

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const input = screen.getByLabelText('URL')
      await user.type(input, 'http://example.com')
      await user.tab() // onBlurトリガー

      expect(
        await screen.findByText('HTTPSのURLを入力してください')
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

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /URLを更新/ })

      // ボタンをクリックして送信開始
      user.click(submitButton)

      // 送信中の状態を確認
      await waitFor(() => {
        expect(screen.getByText('更新中...')).toBeInTheDocument()
      })

      // Promise を解決して送信完了
      resolveSubmit!()
    })

    it('送信完了後にボタンが再度有効化される', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest.fn().mockResolvedValue(undefined)

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const submitButton = screen.getByRole('button', { name: /URLを更新/ })
      await user.click(submitButton)

      await waitFor(() => {
        expect(submitButton).not.toBeDisabled()
      })
    })

    it('送信エラー時にエラーメッセージを表示', async () => {
      const user = userEvent.setup()
      const mockOnSubmit = jest
        .fn()
        .mockRejectedValue(new Error('URLの更新に失敗しました'))

      render(<UrlEditForm {...defaultProps} onSubmit={mockOnSubmit} />)

      const input = screen.getByLabelText('URL')
      const submitButton = screen.getByRole('button', { name: /URLを更新/ })

      // 有効なURLを入力してバリデーションを通過
      await user.type(input, 'https://example.com')
      await user.click(submitButton)

      expect(
        await screen.findByText('URLの更新に失敗しました')
      ).toBeInTheDocument()
    })
  })

  describe('アクセシビリティ', () => {
    it('エラー時にaria-invalidが設定される', async () => {
      const user = userEvent.setup()

      render(<UrlEditForm {...defaultProps} />)

      const input = screen.getByLabelText('URL')
      await user.type(input, 'invalid-url')
      await user.tab()

      await waitFor(() => {
        expect(input).toHaveAttribute('aria-invalid', 'true')
      })
    })

    it('エラーメッセージにrole="alert"が設定される', async () => {
      const user = userEvent.setup()

      render(<UrlEditForm {...defaultProps} />)

      const input = screen.getByLabelText('URL')
      await user.type(input, 'invalid-url')
      await user.tab()

      const errorMessage = await screen.findByText('有効なURLを入力してください')
      expect(errorMessage).toHaveAttribute('role', 'alert')
    })
  })
})
