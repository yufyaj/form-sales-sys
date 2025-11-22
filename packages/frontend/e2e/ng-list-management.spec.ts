import { test, expect } from '@playwright/test'

/**
 * NGリスト管理機能のE2Eテスト
 *
 * このテストは、リストごとのNG(送信禁止)ドメイン管理機能の動作を検証します。
 */
test.describe('NGリスト管理機能', () => {
  const projectId = 1
  const listId = 1

  test.beforeEach(async ({ page }) => {
    // NGリスト管理ページに移動
    await page.goto(`/projects/${projectId}/lists/${listId}/ng-domains`)
  })

  test.describe('NGリスト管理ページ', () => {
    test('NGリスト管理ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: 'NGリスト管理' })).toBeVisible()

      // 説明文を確認
      await expect(
        page.getByText('送信禁止ドメインの登録・管理を行います')
      ).toBeVisible()

      // リスト一覧に戻るボタンを確認
      await expect(
        page.getByRole('button', { name: 'リスト一覧に戻る' })
      ).toBeVisible()

      // NGドメイン追加ボタンを確認
      await expect(
        page.getByRole('button', { name: 'NGドメイン追加' })
      ).toBeVisible()
    })

    test('NGリストについての説明が表示される', async ({ page }) => {
      // 説明カードの内容を確認
      await expect(page.getByText('NGリストについて')).toBeVisible()
      await expect(
        page.getByText('NGドメインに登録されたドメインへのメール送信は自動的にブロックされます')
      ).toBeVisible()
    })

    test('リスト一覧に戻るボタンが機能する', async ({ page }) => {
      await page.getByRole('button', { name: 'リスト一覧に戻る' }).click()

      // リスト一覧ページに戻ることを確認
      await expect(page).toHaveURL(`/projects/${projectId}/lists`)
    })
  })

  test.describe('NGドメイン登録フォーム', () => {
    test.beforeEach(async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'NGドメイン追加' }).click()
    })

    test('フォームが正しく表示される', async ({ page }) => {
      // フォームタイトルを確認
      await expect(page.getByText('NGドメイン登録')).toBeVisible()

      // 初期状態で1つのドメイン入力フィールドが表示される
      await expect(page.getByLabelText('ドメイン')).toBeVisible()
      await expect(page.getByLabelText('メモ（任意）')).toBeVisible()

      // ボタンを確認
      await expect(
        page.getByRole('button', { name: 'NGドメインを登録' })
      ).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'キャンセル' })
      ).toBeVisible()
    })

    test('ドメインを入力できる', async ({ page }) => {
      const domainInput = page.getByLabelText('ドメイン')
      const memoInput = page.getByLabelText('メモ（任意）')

      await domainInput.fill('example.com')
      await memoInput.fill('テストメモ')

      // 入力値が設定されることを確認
      await expect(domainInput).toHaveValue('example.com')
      await expect(memoInput).toHaveValue('テストメモ')
    })

    test('ワイルドカードドメインを入力できる', async ({ page }) => {
      const domainInput = page.getByLabelText('ドメイン')

      await domainInput.fill('*.example.com')

      // 入力値が設定されることを確認
      await expect(domainInput).toHaveValue('*.example.com')
    })

    test('ドメインが空の場合エラーが表示される', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: 'NGドメインを登録' })

      // ドメインを空のまま送信
      await submitButton.click()

      // エラーメッセージを確認
      await expect(
        page.getByText('ドメインを入力してください')
      ).toBeVisible()
    })

    test('不正なドメイン形式でエラーが表示される', async ({ page }) => {
      const domainInput = page.getByLabelText('ドメイン')

      await domainInput.fill('invalid domain!')
      await domainInput.blur() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText(/ドメイン形式が正しくありません/i)
      ).toBeVisible()
    })

    test('メモが500文字を超える場合エラーが表示される', async ({ page }) => {
      const domainInput = page.getByLabelText('ドメイン')
      const memoInput = page.getByLabelText('メモ（任意）')
      const longMemo = 'あ'.repeat(501)

      await domainInput.fill('example.com')
      await memoInput.fill(longMemo)
      await domainInput.click() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText('メモは500文字以内で入力してください')
      ).toBeVisible()
    })

    test('キャンセルボタンをクリックするとフォームが閉じる', async ({ page }) => {
      await page.getByRole('button', { name: 'キャンセル' }).click()

      // フォームが非表示になることを確認
      await expect(page.getByText('NGドメイン登録')).not.toBeVisible()

      // 追加ボタンが再表示されることを確認
      await expect(
        page.getByRole('button', { name: 'NGドメイン追加' })
      ).toBeVisible()
    })
  })

  test.describe('動的フィールド操作', () => {
    test.beforeEach(async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'NGドメイン追加' }).click()
    })

    test('ドメイン追加ボタンでフィールドが追加される', async ({ page }) => {
      // 初期状態で1つのフィールド
      const initialFields = page.getByLabelText('ドメイン')
      await expect(initialFields).toHaveCount(1)

      // ドメイン追加ボタンをクリック
      await page.getByRole('button', { name: 'ドメイン追加' }).click()

      // フィールドが2つになることを確認
      await expect(page.getByLabelText('ドメイン')).toHaveCount(2)
    })

    test('削除ボタンでフィールドが削除される', async ({ page }) => {
      // フィールドを追加
      await page.getByRole('button', { name: 'ドメイン追加' }).click()
      await expect(page.getByLabelText('ドメイン')).toHaveCount(2)

      // 削除ボタンをクリック（2つ目のフィールドの削除ボタン）
      const deleteButtons = page.getByRole('button').filter({ has: page.locator('svg') })
      await deleteButtons.last().click()

      // フィールドが1つに戻ることを確認
      await expect(page.getByLabelText('ドメイン')).toHaveCount(1)
    })

    test('複数のドメインを入力できる', async ({ page }) => {
      // 2つ目のフィールドを追加
      await page.getByRole('button', { name: 'ドメイン追加' }).click()
      await expect(page.getByLabelText('ドメイン')).toHaveCount(2)

      // 各フィールドに入力
      const domainInputs = page.getByLabelText('ドメイン')
      await domainInputs.nth(0).fill('example.com')
      await domainInputs.nth(1).fill('test.com')

      // 入力値が設定されることを確認
      await expect(domainInputs.nth(0)).toHaveValue('example.com')
      await expect(domainInputs.nth(1)).toHaveValue('test.com')
    })
  })

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正しく表示される', async ({ page }) => {
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 })

      // NGリスト管理ページが表示される
      await expect(
        page.getByRole('heading', { name: 'NGリスト管理' })
      ).toBeVisible()

      // NGドメイン追加ボタンが表示される
      await expect(
        page.getByRole('button', { name: 'NGドメイン追加' })
      ).toBeVisible()
    })
  })

  test.describe('アクセシビリティ', () => {
    test('適切なARIAラベルが設定されている', async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'NGドメイン追加' }).click()

      // フォーム要素にラベルが設定されている
      await expect(page.getByLabelText('ドメイン')).toBeVisible()
      await expect(page.getByLabelText('メモ（任意）')).toBeVisible()
    })

    test('キーボードナビゲーションが機能する', async ({ page }) => {
      // フォームを表示
      await page.getByRole('button', { name: 'NGドメイン追加' }).click()

      // Tabキーで移動できることを確認
      await page.keyboard.press('Tab')
      const domainInput = page.getByLabelText('ドメイン')
      await expect(domainInput).toBeFocused()

      await page.keyboard.press('Tab')
      const memoInput = page.getByLabelText('メモ（任意）')
      await expect(memoInput).toBeFocused()
    })
  })
})
