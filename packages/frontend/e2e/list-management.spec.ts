import { test, expect } from '@playwright/test'

/**
 * リスト管理機能のE2Eテスト
 *
 * このテストは、プロジェクトに紐づくリスト管理機能の動作を検証します。
 * 注意: バックエンドのリストAPIが未実装のため、実際のAPIコールは失敗します。
 */
test.describe('リスト管理機能', () => {
  const projectId = 1

  test.beforeEach(async ({ page }) => {
    // リスト一覧ページに移動
    await page.goto(`/projects/${projectId}/lists`)
  })

  test.describe('リスト一覧ページ', () => {
    test('リスト一覧ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: 'リスト管理' })).toBeVisible()

      // 説明文を確認
      await expect(
        page.getByText('営業先リストの作成・管理を行います')
      ).toBeVisible()

      // プロジェクト詳細に戻るボタンを確認
      await expect(
        page.getByRole('button', { name: '← プロジェクト詳細に戻る' })
      ).toBeVisible()

      // 新規作成ボタンを確認
      await expect(
        page.getByRole('button', { name: '新規リスト作成' })
      ).toBeVisible()
    })

    test('リスト一覧テーブルのヘッダーが表示される', async ({ page }) => {
      // テーブルヘッダーを確認
      await expect(page.getByText('リスト名')).toBeVisible()
      await expect(page.getByText('説明')).toBeVisible()
      await expect(page.getByText('作成日')).toBeVisible()
      await expect(page.getByText('操作')).toBeVisible()
    })

    test('プロジェクト詳細に戻るボタンが機能する', async ({ page }) => {
      await page.getByRole('button', { name: '← プロジェクト詳細に戻る' }).click()

      // プロジェクト詳細ページに戻ることを確認
      await expect(page).toHaveURL(`/projects/${projectId}`)
    })

    test('新規リスト作成ボタンをクリックすると作成ページに遷移する', async ({
      page,
    }) => {
      await page.getByRole('button', { name: '新規リスト作成' }).click()

      // 新規作成ページに遷移することを確認
      await expect(page).toHaveURL(`/projects/${projectId}/lists/new`)
      await expect(
        page.getByRole('heading', { name: '新規リスト作成' })
      ).toBeVisible()
    })
  })

  test.describe('リスト新規作成ページ', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto(`/projects/${projectId}/lists/new`)
    })

    test('新規作成ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(
        page.getByRole('heading', { name: '新規リスト作成' })
      ).toBeVisible()

      // 説明文を確認
      await expect(
        page.getByText('新しいリストの情報を入力してください')
      ).toBeVisible()
    })

    test('フォームの全てのフィールドが表示される', async ({ page }) => {
      // リスト名フィールド
      await expect(page.getByLabelText('リスト名')).toBeVisible()

      // 説明フィールド
      await expect(page.getByLabelText('説明（任意）')).toBeVisible()

      // ボタン
      await expect(
        page.getByRole('button', { name: 'リストを作成' })
      ).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'キャンセル' })
      ).toBeVisible()
    })

    test('フォームに入力できる', async ({ page }) => {
      const nameInput = page.getByLabelText('リスト名')
      const descriptionInput = page.getByLabelText('説明（任意）')

      await nameInput.fill('新規営業先リスト')
      await descriptionInput.fill('2025年度第1四半期の新規営業先リスト')

      // 入力値が設定されることを確認
      await expect(nameInput).toHaveValue('新規営業先リスト')
      await expect(descriptionInput).toHaveValue(
        '2025年度第1四半期の新規営業先リスト'
      )
    })

    test('リスト名が空の場合エラーが表示される', async ({ page }) => {
      const submitButton = page.getByRole('button', { name: 'リストを作成' })

      // リスト名を空のまま送信
      await submitButton.click()

      // エラーメッセージを確認
      await expect(
        page.getByText('リスト名を入力してください')
      ).toBeVisible()
    })

    test('リスト名が255文字を超える場合エラーが表示される', async ({
      page,
    }) => {
      const nameInput = page.getByLabelText('リスト名')
      const longName = 'あ'.repeat(256)

      await nameInput.fill(longName)
      await page.getByLabelText('説明（任意）').click() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText('リスト名は255文字以内で入力してください')
      ).toBeVisible()
    })

    test('説明が5000文字を超える場合エラーが表示される', async ({
      page,
    }) => {
      const nameInput = page.getByLabelText('リスト名')
      const descriptionInput = page.getByLabelText('説明（任意）')
      const longDescription = 'あ'.repeat(5001)

      await nameInput.fill('テストリスト')
      await descriptionInput.fill(longDescription)
      await nameInput.click() // フォーカスを外してバリデーション発火

      // エラーメッセージを確認
      await expect(
        page.getByText('説明は5000文字以内で入力してください')
      ).toBeVisible()
    })

    test('キャンセルボタンをクリックすると前のページに戻る', async ({
      page,
    }) => {
      await page.getByRole('button', { name: 'キャンセル' }).click()

      // 一覧ページに戻ることを確認
      await expect(page).toHaveURL(`/projects/${projectId}/lists`)
    })
  })

  test.describe('リスト編集ページ', () => {
    const listId = 1

    test.beforeEach(async ({ page }) => {
      await page.goto(`/projects/${projectId}/lists/${listId}/edit`)
    })

    test('編集ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(
        page.getByRole('heading', { name: 'リスト編集' })
      ).toBeVisible()

      // 説明文を確認
      await expect(
        page.getByText('リストの情報を変更します')
      ).toBeVisible()
    })

    test('フォームの全てのフィールドが表示される', async ({ page }) => {
      // リスト名フィールド
      await expect(page.getByLabelText('リスト名')).toBeVisible()

      // 説明フィールド
      await expect(page.getByLabelText('説明（任意）')).toBeVisible()

      // ボタン
      await expect(
        page.getByRole('button', { name: 'リストを更新' })
      ).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'キャンセル' })
      ).toBeVisible()
    })

    test('フォームに入力できる', async ({ page }) => {
      const nameInput = page.getByLabelText('リスト名')
      const descriptionInput = page.getByLabelText('説明（任意）')

      // 既存の値をクリアして新しい値を入力
      await nameInput.fill('更新された営業先リスト')
      await descriptionInput.fill('更新された説明文')

      // 入力値が設定されることを確認
      await expect(nameInput).toHaveValue('更新された営業先リスト')
      await expect(descriptionInput).toHaveValue('更新された説明文')
    })

    test('リスト名が空の場合エラーが表示される', async ({ page }) => {
      const nameInput = page.getByLabelText('リスト名')
      const submitButton = page.getByRole('button', { name: 'リストを更新' })

      // リスト名を空にして送信
      await nameInput.clear()
      await submitButton.click()

      // エラーメッセージを確認
      await expect(
        page.getByText('リスト名を入力してください')
      ).toBeVisible()
    })

    test('キャンセルボタンをクリックすると前のページに戻る', async ({
      page,
    }) => {
      await page.getByRole('button', { name: 'キャンセル' }).click()

      // 一覧ページに戻ることを確認
      await expect(page).toHaveURL(`/projects/${projectId}/lists`)
    })
  })

  test.describe('リスト削除機能', () => {
    test('削除ボタンをクリックすると確認ダイアログが表示される', async ({
      page,
    }) => {
      // ダイアログのハンドラを設定
      page.on('dialog', (dialog) => {
        expect(dialog.message()).toBe('このリストを削除してもよろしいですか？')
        dialog.dismiss() // キャンセル
      })

      // 削除ボタンをクリック
      const deleteButtons = page.getByRole('button', { name: '削除' })
      if ((await deleteButtons.count()) > 0) {
        await deleteButtons.first().click()
      }
    })
  })

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正しく表示される', async ({ page }) => {
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 })

      // リスト一覧ページが表示される
      await expect(
        page.getByRole('heading', { name: 'リスト管理' })
      ).toBeVisible()

      // 新規作成ボタンが表示される
      await expect(
        page.getByRole('button', { name: '新規リスト作成' })
      ).toBeVisible()
    })
  })

  test.describe('アクセシビリティ', () => {
    test('適切なARIAラベルが設定されている', async ({ page }) => {
      await page.goto(`/projects/${projectId}/lists/new`)

      // フォーム要素にラベルが設定されている
      await expect(page.getByLabelText('リスト名')).toBeVisible()
      await expect(page.getByLabelText('説明（任意）')).toBeVisible()
    })

    test('キーボードナビゲーションが機能する', async ({ page }) => {
      await page.goto(`/projects/${projectId}/lists/new`)

      // Tabキーで移動できることを確認
      await page.keyboard.press('Tab')
      const nameInput = page.getByLabelText('リスト名')
      await expect(nameInput).toBeFocused()

      await page.keyboard.press('Tab')
      const descriptionInput = page.getByLabelText('説明（任意）')
      await expect(descriptionInput).toBeFocused()
    })
  })
})
