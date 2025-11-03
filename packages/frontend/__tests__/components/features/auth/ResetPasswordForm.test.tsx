import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ResetPasswordForm from '@/components/features/auth/ResetPasswordForm'
import * as authActions from '@/lib/auth/actions'

// Server Actionsをモック
jest.mock('@/lib/auth/actions', () => ({
  requestPasswordResetAction: jest.fn(),
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
      const errorElement = screen.getByRole('alert')
      expect(errorElement).toHaveTextContent(/メールアドレスを入力してください/i)
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
    const mockRequestPasswordResetAction = authActions.requestPasswordResetAction as jest.Mock

    mockRequestPasswordResetAction.mockResolvedValue({
      success: true,
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
      expect(mockRequestPasswordResetAction).toHaveBeenCalledWith({
        email: 'test@example.com',
      })
    })

    await waitFor(() => {
      expect(
        screen.getByText(/パスワードリセットリンクをメールで送信しました/i)
      ).toBeInTheDocument()
    })
  })

  it('送信失敗時にエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    const mockRequestPasswordResetAction = authActions.requestPasswordResetAction as jest.Mock

    mockRequestPasswordResetAction.mockResolvedValue({
      success: false,
      error: '予期しないエラーが発生しました',
    })

    render(<ResetPasswordForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const submitButton = screen.getByRole('button', {
      name: /リセットリンクを送信/i,
    })

    await user.type(emailInput, 'notfound@example.com')
    await user.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/予期しないエラーが発生しました/i)
      ).toBeInTheDocument()
    })
  })

  it('送信中はボタンが無効化される', async () => {
    const user = userEvent.setup()
    const mockRequestPasswordResetAction = authActions.requestPasswordResetAction as jest.Mock

    // APIレスポンスを遅延させる
    mockRequestPasswordResetAction.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                success: true,
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
