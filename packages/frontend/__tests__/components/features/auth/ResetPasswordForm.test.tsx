import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ResetPasswordForm from '@/components/features/auth/ResetPasswordForm'
import { apiClient } from '@/lib/api'

// APIクライアントをモック
jest.mock('@/lib/api', () => ({
  apiClient: {
    requestPasswordReset: jest.fn(),
  },
}))

describe('ResetPasswordForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('メールアドレスの入力フィールドが表示される', () => {
    render(<ResetPasswordForm />)

    expect(screen.getByLabelText(/メールアドレス/i)).toBeInTheDocument()
  })

  it('送信ボタンが表示される', () => {
    render(<ResetPasswordForm />)

    expect(
      screen.getByRole('button', { name: /リセットリンクを送信/i })
    ).toBeInTheDocument()
  })

  it('ログインページへのリンクが表示される', () => {
    render(<ResetPasswordForm />)

    expect(
      screen.getByRole('link', { name: /ログインページに戻る/i })
    ).toBeInTheDocument()
  })

  it('説明文が表示される', () => {
    render(<ResetPasswordForm />)

    expect(
      screen.getByText(/登録されているメールアドレスを入力してください/i)
    ).toBeInTheDocument()
  })

  it('空のメールアドレスでバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)

    await user.click(emailInput)
    await user.tab()

    await waitFor(() => {
      expect(
        screen.getByText(/メールアドレスを入力してください/i)
      ).toBeInTheDocument()
    })
  })

  it('無効なメールアドレス形式でバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)

    await user.type(emailInput, 'invalid-email')
    await user.tab()

    await waitFor(() => {
      expect(
        screen.getByText(/有効なメールアドレスを入力してください/i)
      ).toBeInTheDocument()
    })
  })

  it('正しい入力でリセットリンク送信が成功する', async () => {
    const user = userEvent.setup()
    const mockRequestPasswordReset = apiClient.requestPasswordReset as jest.Mock

    mockRequestPasswordReset.mockResolvedValue({
      message: 'パスワードリセットリンクをメールで送信しました。',
    })

    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const submitButton = screen.getByRole('button', {
      name: /リセットリンクを送信/i,
    })

    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockRequestPasswordReset).toHaveBeenCalledWith('test@example.com')
    })

    await waitFor(() => {
      expect(
        screen.getByText(/パスワードリセットリンクをメールで送信しました/i)
      ).toBeInTheDocument()
    })
  })

  it('送信失敗時にエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    const mockRequestPasswordReset = apiClient.requestPasswordReset as jest.Mock

    mockRequestPasswordReset.mockRejectedValue(
      new Error('メールアドレスが見つかりません')
    )

    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const submitButton = screen.getByRole('button', {
      name: /リセットリンクを送信/i,
    })

    await user.type(emailInput, 'notfound@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/メールアドレスが見つかりません/i)
      ).toBeInTheDocument()
    })
  })

  it('送信中はボタンが無効化される', async () => {
    const user = userEvent.setup()
    const mockRequestPasswordReset = apiClient.requestPasswordReset as jest.Mock

    // APIレスポンスを遅延させる
    mockRequestPasswordReset.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                message: 'パスワードリセットリンクをメールで送信しました。',
              }),
            1000
          )
        )
    )

    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const submitButton = screen.getByRole('button', {
      name: /リセットリンクを送信/i,
    })

    await user.type(emailInput, 'test@example.com')
    await user.click(submitButton)

    // ボタンが無効化されることを確認
    expect(submitButton).toBeDisabled()
  })
})
