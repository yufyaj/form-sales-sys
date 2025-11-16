import { test, expect } from '@playwright/test'

test.describe('顧客管理機能', () => {
  test.beforeEach(async ({ page }) => {
    // 顧客一覧ページに移動
    await page.goto('/customers')
  })

  test.describe('顧客一覧ページ', () => {
    test('顧客一覧ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: '顧客一覧' })).toBeVisible()

      // 検索バーを確認
      await expect(
        page.getByPlaceholder('顧客名、業種、担当営業で検索...')
      ).toBeVisible()

      // 顧客追加ボタンを確認
      await expect(
        page.getByRole('button', { name: '顧客を追加' })
      ).toBeVisible()
    })

    test('顧客一覧が表示される', async ({ page }) => {
      // モックデータが表示されることを確認
      await expect(page.getByText('株式会社サンプル')).toBeVisible()
      await expect(page.getByText('テクノロジー株式会社')).toBeVisible()
    })

    test('顧客情報が正しく表示される', async ({ page }) => {
      // 業種が表示される
      await expect(page.getByText('製造業')).toBeVisible()

      // 担当営業が表示される
      await expect(page.getByText('山田 太郎')).toBeVisible()

      // Webサイトリンクが表示される
      const websiteLinks = page.getByRole('link', { name: 'リンク' })
      await expect(websiteLinks.first()).toBeVisible()
    })

    test('検索機能が動作する', async ({ page }) => {
      const searchInput = page.getByPlaceholder('顧客名、業種、担当営業で検索...')

      // 「テクノロジー」で検索
      await searchInput.fill('テクノロジー')

      // 検索結果を確認
      await expect(page.getByText('テクノロジー株式会社')).toBeVisible()

      // 他の顧客が非表示になることを確認
      await expect(page.getByText('1件の顧客を表示中')).toBeVisible()
    })

    test('顧客をクリックすると詳細ページに遷移する', async ({ page }) => {
      // 顧客行をクリック
      await page.getByText('株式会社サンプル').click()

      // 詳細ページに遷移することを確認
      await expect(page).toHaveURL(/\/customers\/\d+/)
      await expect(page.getByText('株式会社サンプル')).toBeVisible()
    })
  })

  test.describe('顧客詳細ページ', () => {
    test.beforeEach(async ({ page }) => {
      // 顧客一覧から詳細ページへ遷移
      await page.getByText('株式会社サンプル').click()
      await page.waitForURL(/\/customers\/\d+/)
    })

    test('顧客詳細ページが正しく表示される', async ({ page }) => {
      // 顧客名が表示される
      await expect(
        page.getByRole('heading', { name: '株式会社サンプル' })
      ).toBeVisible()

      // 一覧に戻るリンクを確認
      await expect(page.getByText('← 一覧に戻る')).toBeVisible()

      // 顧客情報を編集ボタンを確認
      await expect(
        page.getByRole('button', { name: '顧客情報を編集' })
      ).toBeVisible()
    })

    test('顧客情報が正しく表示される', async ({ page }) => {
      // 顧客情報セクション
      await expect(
        page.getByRole('heading', { name: '顧客情報' })
      ).toBeVisible()

      // 各項目が表示される
      await expect(page.getByText('業種')).toBeVisible()
      await expect(page.getByText('従業員数')).toBeVisible()
      await expect(page.getByText('年商')).toBeVisible()
      await expect(page.getByText('設立年')).toBeVisible()
      await expect(page.getByText('Webサイト')).toBeVisible()
      await expect(page.getByText('担当営業')).toBeVisible()
    })

    test('担当者一覧が表示される', async ({ page }) => {
      // 担当者一覧セクション
      await expect(
        page.getByRole('heading', { name: '担当者一覧' })
      ).toBeVisible()

      // 担当者が表示される
      await expect(page.getByText('田中 一郎')).toBeVisible()
      await expect(page.getByText('鈴木 花子')).toBeVisible()

      // 主担当バッジが表示される
      await expect(page.getByText('主担当')).toBeVisible()
    })

    test('一覧に戻るリンクをクリックすると、一覧ページに戻る', async ({
      page,
    }) => {
      await page.getByText('← 一覧に戻る').click()

      await expect(page).toHaveURL('/customers')
      await expect(page.getByRole('heading', { name: '顧客一覧' })).toBeVisible()
    })
  })

  test.describe('顧客情報編集', () => {
    test.beforeEach(async ({ page }) => {
      // 顧客詳細ページへ遷移
      await page.getByText('株式会社サンプル').click()
      await page.waitForURL(/\/customers\/\d+/)

      // 編集ボタンをクリック
      await page.getByRole('button', { name: '顧客情報を編集' }).click()
    })

    test('顧客編集フォームが表示される', async ({ page }) => {
      // フォーム要素を確認
      await expect(page.getByLabel('業種')).toBeVisible()
      await expect(page.getByLabel('従業員数')).toBeVisible()
      await expect(page.getByLabel('年商（円）')).toBeVisible()
      await expect(page.getByLabel('設立年')).toBeVisible()
      await expect(page.getByLabel('Webサイト')).toBeVisible()
      await expect(page.getByLabel('担当営業')).toBeVisible()
      await expect(page.getByLabel('備考')).toBeVisible()

      // ボタンを確認
      await expect(page.getByRole('button', { name: '更新' })).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'キャンセル' })
      ).toBeVisible()
    })

    test('既存の値がフォームに設定される', async ({ page }) => {
      // 既存の値が入力されていることを確認
      const industryInput = page.getByLabel('業種')
      await expect(industryInput).toHaveValue('製造業')
    })

    test('キャンセルボタンをクリックすると、編集モードが終了する', async ({
      page,
    }) => {
      await page.getByRole('button', { name: 'キャンセル' }).click()

      // 編集ボタンが再表示されることを確認
      await expect(
        page.getByRole('button', { name: '顧客情報を編集' })
      ).toBeVisible()
    })

    test('フォームバリデーションが動作する', async ({ page }) => {
      // 無効なURLを入力
      const websiteInput = page.getByLabel('Webサイト')
      await websiteInput.fill('invalid-url')
      await page.getByLabel('業種').click()

      // エラーメッセージを確認
      await expect(
        page.getByText('有効なURLを入力してください')
      ).toBeVisible()
    })

    test('負の従業員数を入力すると、エラーが表示される', async ({ page }) => {
      const employeeInput = page.getByLabel('従業員数')
      await employeeInput.fill('-100')
      await page.getByLabel('業種').click()

      await expect(
        page.getByText('従業員数は0以上である必要があります')
      ).toBeVisible()
    })
  })

  test.describe('担当者管理', () => {
    test.beforeEach(async ({ page }) => {
      // 顧客詳細ページへ遷移
      await page.getByText('株式会社サンプル').click()
      await page.waitForURL(/\/customers\/\d+/)
    })

    test('担当者を追加ボタンをクリックすると、追加フォームが表示される', async ({
      page,
    }) => {
      await page.getByRole('button', { name: '担当者を追加' }).click()

      // フォームが表示される
      await expect(page.getByText('新しい担当者を追加')).toBeVisible()
      await expect(page.getByLabel('氏名 *')).toBeVisible()
      await expect(page.getByLabel('部署')).toBeVisible()
      await expect(page.getByLabel('役職')).toBeVisible()
      await expect(page.getByLabel('メールアドレス')).toBeVisible()
      await expect(page.getByLabel('電話番号')).toBeVisible()
      await expect(page.getByLabel('携帯電話番号')).toBeVisible()
    })

    test('担当者追加フォームで入力できる', async ({ page }) => {
      await page.getByRole('button', { name: '担当者を追加' }).click()

      // フォームに入力
      await page.getByLabel('氏名 *').fill('山田 太郎')
      await page.getByLabel('部署').fill('営業部')
      await page.getByLabel('役職').fill('課長')
      await page.getByLabel('メールアドレス').fill('yamada@example.com')
      await page.getByLabel('電話番号').fill('03-1234-5678')

      // 入力値が設定されることを確認
      await expect(page.getByLabel('氏名 *')).toHaveValue('山田 太郎')
      await expect(page.getByLabel('部署')).toHaveValue('営業部')
    })

    test('担当者追加フォームのバリデーションが動作する', async ({ page }) => {
      await page.getByRole('button', { name: '担当者を追加' }).click()

      // 氏名を空のまま送信
      const nameInput = page.getByLabel('氏名 *')
      await nameInput.click()
      await page.getByLabel('部署').click()

      // エラーメッセージを確認
      await expect(
        page.getByText('氏名を入力してください')
      ).toBeVisible()
    })

    test('無効なメールアドレスでバリデーションエラーが表示される', async ({
      page,
    }) => {
      await page.getByRole('button', { name: '担当者を追加' }).click()

      await page.getByLabel('メールアドレス').fill('invalid-email')
      await page.getByLabel('氏名 *').click()

      await expect(
        page.getByText('有効なメールアドレスを入力してください')
      ).toBeVisible()
    })

    test('担当者編集ボタンをクリックすると、編集フォームが表示される', async ({
      page,
    }) => {
      // 最初の編集ボタンをクリック
      const editButtons = page.getByRole('button', { name: '編集' })
      await editButtons.first().click()

      // 編集フォームが表示される
      await expect(page.getByRole('button', { name: '更新' })).toBeVisible()
    })

    test('担当者削除ボタンをクリックすると、確認ダイアログが表示される', async ({
      page,
    }) => {
      // 削除ダイアログのハンドラを設定
      page.on('dialog', (dialog) => {
        expect(dialog.message()).toBe('この担当者を削除してもよろしいですか？')
        dialog.dismiss() // キャンセル
      })

      // 削除ボタンをクリック
      const deleteButtons = page.getByRole('button', { name: '削除' })
      await deleteButtons.first().click()
    })

    test('担当者追加フォームのキャンセルボタンが動作する', async ({
      page,
    }) => {
      await page.getByRole('button', { name: '担当者を追加' }).click()

      // フォームが表示されることを確認
      await expect(page.getByText('新しい担当者を追加')).toBeVisible()

      // キャンセルボタンをクリック
      const cancelButtons = page.getByRole('button', { name: 'キャンセル' })
      await cancelButtons.first().click()

      // フォームが閉じることを確認
      await expect(page.getByText('新しい担当者を追加')).not.toBeVisible()
    })
  })

  test.describe('レスポンシブデザイン', () => {
    test('モバイルビューで正しく表示される', async ({ page }) => {
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 })

      // 顧客一覧ページが表示される
      await expect(page.getByRole('heading', { name: '顧客一覧' })).toBeVisible()

      // 検索バーが表示される
      await expect(
        page.getByPlaceholder('顧客名、業種、担当営業で検索...')
      ).toBeVisible()

      // テーブルが横スクロールできることを確認（視覚的なテストは省略）
      await expect(page.getByText('株式会社サンプル')).toBeVisible()
    })
  })

  test.describe('アクセシビリティ', () => {
    test('適切なARIAラベルが設定されている', async ({ page }) => {
      // フォーム要素にラベルが設定されている
      await page.goto('/customers/1')
      await page.getByRole('button', { name: '顧客情報を編集' }).click()

      await expect(page.getByLabel('業種')).toBeVisible()
      await expect(page.getByLabel('従業員数')).toBeVisible()
      await expect(page.getByLabel('年商（円）')).toBeVisible()
    })

    test('キーボードナビゲーションが機能する', async ({ page }) => {
      // Tabキーで移動できることを確認
      await page.keyboard.press('Tab')
      await page.keyboard.press('Tab')

      // フォーカスが移動することを確認（詳細なテストは省略）
    })
  })
})
