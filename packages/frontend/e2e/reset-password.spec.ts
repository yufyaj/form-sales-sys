import { test, expect } from '@playwright/test'

test.describe('パスワードリセットページ', () => {
  test.beforeEach(async ({ page }) => {
    // パスワードリセットページに移動
    await page.goto('/reset-password')
  })

  test('パスワードリセットページが正しく表示される', async ({ page }) => {
    // ページタイトルを確認
    await expect(
      page.getByRole('heading', { name: 'パスワードリセット' })
    ).toBeVisible()

    // フォーム要素を確認
    await expect(page.getByLabel('メールアドレス')).toBeVisible()
    await expect(
      page.getByRole('button', { name: 'リセットリンクを送信' })
    ).toBeVisible()

    // 説明文を確認
    await expect(
      page.getByText('登録されているメールアドレスを入力してください')
    ).toBeVisible()

    // ログインページへのリンクを確認
    await expect(
      page.getByRole('link', { name: 'ログインページに戻る' })
    ).toBeVisible()
  })

  test('空のフォームでバリデーションエラーが表示される', async ({
    page,
  }) => {
    // メールアドレスにフォーカスして外す
    await page.getByLabel('メールアドレス').click()
    await page.keyboard.press('Tab')

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
    await page.keyboard.press('Tab')

    // エラーメッセージを確認
    await expect(
      page.getByText('有効なメールアドレスを入力してください')
    ).toBeVisible()
  })

  test('ログインページに戻るリンクをクリックするとログインページに遷移する', async ({
    page,
  }) => {
    // ログインページに戻るリンクをクリック
    await page.getByRole('link', { name: 'ログインページに戻る' }).click()

    // ログインページに遷移することを確認
    await expect(page).toHaveURL('/login')
    await expect(page.getByRole('heading', { name: 'ログイン' })).toBeVisible()
  })

  test('正しいメールアドレスでリセットリンク送信が成功する（モック）', async ({
    page,
  }) => {
    // APIリクエストをモック
    await page.route('**/api/auth/reset-password', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'パスワードリセットリンクをメールで送信しました。',
        }),
      })
    })

    // フォームに入力
    await page.getByLabel('メールアドレス').fill('test@example.com')

    // 送信ボタンをクリック
    await page.getByRole('button', { name: 'リセットリンクを送信' }).click()

    // 成功メッセージを確認
    await expect(
      page.getByText('パスワードリセットリンクをメールで送信しました')
    ).toBeVisible()
  })

  test('存在しないメールアドレスでエラーメッセージが表示される（モック）', async ({
    page,
  }) => {
    // APIリクエストをモック（エラーレスポンス）
    await page.route('**/api/auth/reset-password', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'メールアドレスが見つかりません',
        }),
      })
    })

    // フォームに入力
    await page.getByLabel('メールアドレス').fill('notfound@example.com')

    // 送信ボタンをクリック
    await page.getByRole('button', { name: 'リセットリンクを送信' }).click()

    // エラーメッセージを確認（セキュリティホワイトリストによる汎用メッセージ）
    await expect(
      page.getByText('予期しないエラーが発生しました')
    ).toBeVisible()
  })

  test('送信中はボタンが無効化される', async ({ page }) => {
    // APIリクエストを遅延させる
    await page.route('**/api/auth/reset-password', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'パスワードリセットリンクをメールで送信しました。',
        }),
      })
    })

    // フォームに入力
    await page.getByLabel('メールアドレス').fill('test@example.com')

    // 送信ボタンをクリック
    const submitButton = page.getByRole('button', {
      name: 'リセットリンクを送信',
    })
    await submitButton.click()

    // ボタンが無効化されることを確認
    await expect(submitButton).toBeDisabled()
  })
})
