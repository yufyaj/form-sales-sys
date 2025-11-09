import { test, expect } from '@playwright/test'

test.describe('ログインページ', () => {
  test.beforeEach(async ({ page }) => {
    // ログインページに移動
    await page.goto('/login')
  })

  test('ログインページが正しく表示される', async ({ page }) => {
    // ページタイトルを確認
    await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible()

    // フォーム要素を確認
    await expect(page.getByLabel('メールアドレス')).toBeVisible()
    await expect(page.getByLabel('パスワード')).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'ログイン' })
    ).toBeVisible()

    // パスワードリセットリンクを確認
    await expect(
      page.getByRole('link', { name: 'パスワードをお忘れですか？' })
    ).toBeVisible()
  })

  test('空のフォームでバリデーションエラーが表示される', async ({
    page,
  }) => {
    // メールアドレスにフォーカスして外す
    await page.getByLabel('メールアドレス').click()
    await page.getByLabel('パスワード').click()

    // エラーメッセージを確認
    await expect(
      page.getByText('メールアドレスを入力してください')
    ).toBeVisible()
  })

  test('無効なメールアドレスでバリデーションエラーが表示される', async ({
    page,
  }) => {
    // 無効なメールアドレスを入力
    await page.getByLabel('メールアドレス').fill('invalid-email')
    await page.getByLabel('パスワード').click()

    // エラーメッセージを確認
    await expect(
      page.getByText('有効なメールアドレスを入力してください')
    ).toBeVisible()
  })

  test('短いパスワードでバリデーションエラーが表示される', async ({
    page,
  }) => {
    // 短いパスワードを入力
    await page.getByLabel('パスワード').fill('Short1')
    await page.getByLabel('メールアドレス').click()

    // エラーメッセージを確認
    await expect(
      page.getByText('パスワードは12文字以上で入力してください')
    ).toBeVisible()
  })

  test('複雑性要件を満たさないパスワードでバリデーションエラーが表示される', async ({
    page,
  }) => {
    // 複雑性要件を満たさないパスワードを入力（小文字のみ）
    await page.getByLabel('パスワード').fill('onlylowercase')
    await page.getByLabel('メールアドレス').click()

    // エラーメッセージを確認
    await expect(
      page.getByText('パスワードは大文字、小文字、数字を含む必要があります')
    ).toBeVisible()
  })

  test('パスワードリセットリンクをクリックするとパスワードリセットページに遷移する', async ({
    page,
  }) => {
    // パスワードリセットリンクをクリック
    await page.getByRole('link', { name: 'パスワードをお忘れですか？' }).click()

    // パスワードリセットページに遷移することを確認
    await expect(page).toHaveURL('/reset-password')
    await expect(
      page.getByRole('heading', { name: 'パスワードリセット' })
    ).toBeVisible()
  })

  // Note: Server Actionsを使用しているため、page.routeでのモックは機能しません
  // 統合テストでは実際のバックエンドAPIが必要です
  test.skip('正しい認証情報でログインが成功する（モック）', async ({ page }) => {
    // APIリクエストをモック
    await page.route('**/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: {
            id: '1',
            email: 'test@example.com',
            name: 'Test User',
          },
          token: 'mock-token',
        }),
      })
    })

    // フォームに入力（複雑性要件を満たすパスワード）
    await page.getByLabel('メールアドレス').fill('test@example.com')
    await page.getByLabel('パスワード').fill('ValidPassword123')

    // ログインボタンをクリック
    await page.getByRole('button', { name: 'ログイン' }).click()

    // ダッシュボードページに遷移することを確認
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 })
  })

  // Note: Server Actionsを使用しているため、page.routeでのモックは機能しません
  // 統合テストでは実際のバックエンドAPIが必要です
  test.skip('誤った認証情報でエラーメッセージが表示される（モック）', async ({
    page,
  }) => {
    // APIリクエストをモック（エラーレスポンス）
    await page.route('**/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'メールアドレスまたはパスワードが正しくありません',
        }),
      })
    })

    // フォームに入力（複雑性要件を満たすが誤ったパスワード）
    await page.getByLabel('メールアドレス').fill('test@example.com')
    await page.getByLabel('パスワード').fill('WrongPassword123')

    // ログインボタンをクリック
    await page.getByRole('button', { name: 'ログイン' }).click()

    // エラーメッセージを確認
    await expect(
      page.getByText('予期しないエラーが発生しました')
    ).toBeVisible()
  })

  // Note: Server Actionsを使用しているため、page.routeでのモックは機能しません
  // 統合テストでは実際のバックエンドAPIが必要です
  test.skip('送信中はボタンが無効化される', async ({ page }) => {
    // APIリクエストを遅延させる
    await page.route('**/auth/login', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user: { id: '1', email: 'test@example.com' },
          token: 'mock-token',
        }),
      })
    })

    // フォームに入力（複雑性要件を満たすパスワード）
    await page.getByLabel('メールアドレス').fill('test@example.com')
    await page.getByLabel('パスワード').fill('ValidPassword123')

    // ログインボタンをクリック
    const loginButton = page.getByRole('button', { name: 'ログイン' })
    await loginButton.click()

    // ボタンが無効化されることを確認
    await expect(loginButton).toBeDisabled()
  })
})
