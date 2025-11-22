import { test, expect } from '@playwright/test'

/**
 * スクリプト管理機能のE2Eテスト
 *
 * このテストは、リストごとのスクリプト(営業台本)管理機能の動作を検証します。
 */
test.describe('スクリプト管理機能', () => {
  const projectId = 1
  const listId = 1

  test.beforeEach(async ({ page }) => {
    // スクリプト管理ページに移動
    await page.goto(`/projects/${projectId}/lists/${listId}/scripts`)
  })

  test.describe('スクリプト管理ページ', () => {
    test('スクリプト管理ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: 'スクリプト管理' })).toBeVisible()

      // 説明文を確認
      await expect(
        page.getByText('営業スクリプト(台本)の登録・管理を行います')
      ).toBeVisible()

      // リスト一覧に戻るボタンを確認
      await expect(
        page.getByRole('button', { name: 'リスト一覧に戻る' })
      ).toBeVisible()

      // スクリプト追加ボタンを確認
      await expect(
        page.getByRole('button', { name: 'スクリプト追加' })
      ).toBeVisible()
    })

    test('スクリプトについての説明が表示される', async ({ page }) => {
      // 説明カードの内容を確認
      await expect(page.getByText('スクリプトについて')).toBeVisible()
      await expect(
        page.getByText('営業トークの台本を登録できます')
      ).toBeVisible()
    })

    test('リスト一覧に戻るボタンが機能する', async ({ page }) => {
      await page.getByRole('button', { name: 'リスト一覧に戻る' }).click()

      // リスト一覧ページに戻ることを確認
      await expect(page).toHaveURL(`/projects/${projectId}/lists`)
    })
  })

  test.describe('スクリプト登録フォーム', () => {
    test.beforeEach(async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'スクリプト追加' }).click()
    })

    test('フォームが正しく表示される', async ({ page }) => {
      // フォームタイトルを確認
      await expect(page.getByText('スクリプト登録')).toBeVisible()

      // 初期状態で1つのスクリプト入力フィールドが表示される
      await expect(page.getByLabelText('件名')).toBeVisible()
      await expect(page.getByLabelText('本文')).toBeVisible()

      // ボタンを確認
      await expect(
        page.getByRole('button', { name: 'スクリプトを登録' })
      ).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'キャンセル' })
      ).toBeVisible()
    })

    test('件名と本文を入力できる', async ({ page }) => {
      const titleInput = page.getByLabelText('件名')
      const contentInput = page.getByLabelText('本文')

      await titleInput.fill('お問い合わせの件について')
      await contentInput.fill('お世話になっております。\n先日お問い合わせいただいた件についてご連絡いたします。')

      // 入力値が設定されることを確認
      await expect(titleInput).toHaveValue('お問い合わせの件について')
      await expect(contentInput).toHaveValue('お世話になっております。\n先日お問い合わせいただいた件についてご連絡いたします。')
    })

    test('件名が空の場合エラーが表示される', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: 'スクリプトを登録' })

      // 件名を空のまま送信
      await submitButton.click()

      // エラーメッセージを確認
      await expect(
        page.getByText('タイトルを入力してください')
      ).toBeVisible()
    })

    test('本文が空の場合エラーが表示される', async ({ page }) => {
      const titleInput = page.getByLabelText('件名')
      const submitButton = page.getByRole('button', { name: 'スクリプトを登録' })

      await titleInput.fill('テスト件名')
      await submitButton.click()

      // エラーメッセージを確認
      await expect(
        page.getByText('本文を入力してください')
      ).toBeVisible()
    })

    test('件名が255文字を超える場合エラーが表示される', async ({ page }) => {
      const titleInput = page.getByLabelText('件名')
      const longTitle = 'あ'.repeat(256)

      await titleInput.fill(longTitle)
      await titleInput.blur() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText('タイトルは255文字以内で入力してください')
      ).toBeVisible()
    })

    test('本文が10000文字を超える場合エラーが表示される', async ({ page }) => {
      const titleInput = page.getByLabelText('件名')
      const contentInput = page.getByLabelText('本文')
      const longContent = 'あ'.repeat(10001)

      await titleInput.fill('テスト件名')
      await contentInput.fill(longContent)
      await titleInput.click() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText('本文は10,000文字以内で入力してください')
      ).toBeVisible()
    })

    test('キャンセルボタンをクリックするとフォームが閉じる', async ({ page }) => {
      await page.getByRole('button', { name: 'キャンセル' }).click()

      // フォームが非表示になることを確認
      await expect(page.getByText('スクリプト登録')).not.toBeVisible()

      // 追加ボタンが再表示されることを確認
      await expect(
        page.getByRole('button', { name: 'スクリプト追加' })
      ).toBeVisible()
    })
  })

  test.describe('動的フィールド操作', () => {
    test.beforeEach(async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'スクリプト追加' }).click()
    })

    test('スクリプト追加ボタンでフィールドが追加される', async ({ page }) => {
      // 初期状態で1つのフィールド
      const initialFields = page.getByLabelText('件名')
      await expect(initialFields).toHaveCount(1)

      // スクリプト追加ボタンをクリック
      await page.getByRole('button', { name: 'スクリプト追加' }).click()

      // フィールドが2つになることを確認
      await expect(page.getByLabelText('件名')).toHaveCount(2)
      await expect(page.getByLabelText('本文')).toHaveCount(2)
    })

    test('削除ボタンでフィールドが削除される', async ({ page }) => {
      // フィールドを追加
      await page.getByRole('button', { name: 'スクリプト追加' }).click()
      await expect(page.getByLabelText('件名')).toHaveCount(2)

      // 削除ボタンをクリック（2つ目のフィールドの削除ボタン）
      const deleteButtons = page.getByRole('button').filter({ has: page.locator('svg') })
      await deleteButtons.last().click()

      // フィールドが1つに戻ることを確認
      await expect(page.getByLabelText('件名')).toHaveCount(1)
    })

    test('複数のスクリプトを入力できる', async ({ page }) => {
      // 2つ目のフィールドを追加
      await page.getByRole('button', { name: 'スクリプト追加' }).click()
      await expect(page.getByLabelText('件名')).toHaveCount(2)

      // 各フィールドに入力
      const titleInputs = page.getByLabelText('件名')
      const contentInputs = page.getByLabelText('本文')

      await titleInputs.nth(0).fill('お問い合わせの件')
      await contentInputs.nth(0).fill('お問い合わせありがとうございます')

      await titleInputs.nth(1).fill('資料送付の件')
      await contentInputs.nth(1).fill('資料をお送りいたします')

      // 入力値が設定されることを確認
      await expect(titleInputs.nth(0)).toHaveValue('お問い合わせの件')
      await expect(contentInputs.nth(0)).toHaveValue('お問い合わせありがとうございます')
      await expect(titleInputs.nth(1)).toHaveValue('資料送付の件')
      await expect(contentInputs.nth(1)).toHaveValue('資料をお送りいたします')
    })
  })

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正しく表示される', async ({ page }) => {
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 })

      // スクリプト管理ページが表示される
      await expect(
        page.getByRole('heading', { name: 'スクリプト管理' })
      ).toBeVisible()

      // スクリプト追加ボタンが表示される
      await expect(
        page.getByRole('button', { name: 'スクリプト追加' })
      ).toBeVisible()
    })
  })

  test.describe('アクセシビリティ', () => {
    test('適切なARIAラベルが設定されている', async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'スクリプト追加' }).click()

      // フォーム要素にラベルが設定されている
      await expect(page.getByLabelText('件名')).toBeVisible()
      await expect(page.getByLabelText('本文')).toBeVisible()
    })

    test('キーボードナビゲーションが機能する', async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'スクリプト追加' }).click()

      // Tabキーで移動できることを確認
      await page.keyboard.press('Tab')
      const titleInput = page.getByLabelText('件名')
      await expect(titleInput).toBeFocused()

      await page.keyboard.press('Tab')
      const contentInput = page.getByLabelText('本文')
      await expect(contentInput).toBeFocused()
    })
  })
})
