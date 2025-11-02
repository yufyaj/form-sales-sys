import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginForm from '@/components/features/auth/LoginForm'
import * as authActions from '@/lib/auth/actions'

// Next.jsのルーターをモック
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    refresh: jest.fn(),
  }),
}))

// Server Actionsをモック
jest.mock('@/lib/auth/actions', () => ({
  loginAction: jest.fn(),
}))

describe('LoginForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('メールアドレスとパスワードの入力フィールドが表示される', () => {
    render(<LoginForm />)

    expect(screen.getByLabelText(/メールアドレス/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/パスワード/i)).toBeInTheDocument()
  })

  it('ログインボタンが表示される', () => {
    render(<LoginForm />)

    expect(
      screen.getByRole('button', { name: /ログイン/i })
    ).toBeInTheDocument()
  })

  it('パスワードリセットリンクが表示される', () => {
    render(<LoginForm />)

    expect(
      screen.getByRole('link', { name: /パスワードをお忘れですか/i })
    ).toBeInTheDocument()
  })

  it('空のメールアドレスでバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const passwordInput = screen.getByLabelText(/パスワード/i)

    // メールアドレスを空のまま、パスワードだけ入力してフォーカスを外す
    await user.type(passwordInput, 'password123')
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
    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)

    await user.type(emailInput, 'invalid-email')
    await user.tab()

    await waitFor(() => {
      expect(
        screen.getByText(/有効なメールアドレスを入力してください/i)
      ).toBeInTheDocument()
    })
  })

  it('短すぎるパスワードでバリデーションエラーが表示される', async () => {
    const user = userEvent.setup()
    render(<LoginForm />)

    const passwordInput = screen.getByLabelText(/パスワード/i)

    await user.type(passwordInput, '1234567')
    await user.tab()

    await waitFor(() => {
      expect(
        screen.getByText(/パスワードは12文字以上で入力してください/i)
      ).toBeInTheDocument()
    })
  })

  it('正しい入力でログインが成功する', async () => {
    const user = userEvent.setup()
    const mockLoginAction = authActions.loginAction as jest.Mock

    mockLoginAction.mockResolvedValue({
      success: true,
      data: {
        user: { id: '1', email: 'test@example.com' },
      },
    })

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const passwordInput = screen.getByLabelText(/パスワード/i)
    const submitButton = screen.getByRole('button', { name: /ログイン/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'ValidPassword123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(mockLoginAction).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'ValidPassword123',
      })
    })
  })

  it('ログイン失敗時にエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    const mockLoginAction = authActions.loginAction as jest.Mock

    mockLoginAction.mockResolvedValue({
      success: false,
      error: '認証に失敗しました',
    })

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const passwordInput = screen.getByLabelText(/パスワード/i)
    const submitButton = screen.getByRole('button', { name: /ログイン/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'WrongPassword123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(/認証に失敗しました/i)).toBeInTheDocument()
    })
  })

  it('送信中はボタンが無効化される', async () => {
    const user = userEvent.setup()
    const mockLoginAction = authActions.loginAction as jest.Mock

    // APIレスポンスを遅延させる
    mockLoginAction.mockImplementation(
      () =>
        new Promise((resolve) =>
          setTimeout(
            () =>
              resolve({
                success: true,
                data: {
                  user: { id: '1', email: 'test@example.com' },
                },
              }),
            1000
          )
        )
    )

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const passwordInput = screen.getByLabelText(/パスワード/i)
    const submitButton = screen.getByRole('button', { name: /ログイン/i })

    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'ValidPassword123')
    await user.click(submitButton)

    // ボタンが無効化されることを確認
    await waitFor(() => {
      expect(submitButton).toBeDisabled()
    })
  })

  it('レート制限が機能する', async () => {
    const user = userEvent.setup()
    const mockLoginAction = authActions.loginAction as jest.Mock

    // 5回連続失敗させる
    mockLoginAction.mockResolvedValue({
      success: false,
      error: '認証に失敗しました',
    })

    render(<LoginForm />)

    const emailInput = screen.getByLabelText(/メールアドレス/i)
    const passwordInput = screen.getByLabelText(/パスワード/i)
    const submitButton = screen.getByRole('button', { name: /ログイン/i })

    // 5回失敗させる
    for (let i = 0; i < 5; i++) {
      await user.clear(emailInput)
      await user.clear(passwordInput)
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'WrongPassword123')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/認証に失敗しました/i)).toBeInTheDocument()
      })

      // エラーメッセージをクリア（次の試行のため）
      mockLoginAction.mockClear()
    }

    // 6回目はレート制限エラーになる
    await user.clear(emailInput)
    await user.clear(passwordInput)
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'WrongPassword123')
    await user.click(submitButton)

    await waitFor(() => {
      expect(
        screen.getByText(/試行回数が多すぎます/i)
      ).toBeInTheDocument()
    })
  })
})
