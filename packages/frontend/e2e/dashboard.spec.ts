import { test, expect } from '@playwright/test'

/**
 * ダッシュボード機能のE2Eテスト
 * ユーザーストーリーに基づいたシナリオテストを実施
 */

test.describe('ダッシュボード', () => {
  // 各テスト前にログイン状態をセットアップ
  test.beforeEach(async ({ page }) => {
    // TODO: 実際の認証実装後に、ログイン処理を追加
    // 現在はモックユーザーを使用しているため、直接ダッシュボードへアクセス
    await page.goto('http://localhost:3000')
  })

  test.describe('営業支援会社ダッシュボード', () => {
    test.beforeEach(async ({ page, context }) => {
      // 営業支援会社ユーザーとしてログイン（モック）
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '1',
            email: 'sales@example.com',
            name: '営業担当者',
            role: 'sales_company',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])
      await page.goto('http://localhost:3000/dashboard')
    })

    test('営業支援会社ダッシュボードが表示される', async ({ page }) => {
      // リダイレクト後のURLを確認
      await expect(page).toHaveURL(/\/dashboard\/sales-company/)

      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: 'プロジェクト一覧' })).toBeVisible()

      // 統計カードを確認
      await expect(page.getByText('総プロジェクト数')).toBeVisible()
      await expect(page.getByText('進行中')).toBeVisible()
      await expect(page.getByText('完了')).toBeVisible()
      await expect(page.getByText('総送信数')).toBeVisible()
    })

    test('プロジェクト一覧が表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/sales-company')

      // テーブルヘッダーを確認
      await expect(page.getByRole('columnheader', { name: 'プロジェクト名' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'ステータス' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: '進捗' })).toBeVisible()

      // モックデータのプロジェクトを確認
      await expect(page.getByText('A社フォーム営業プロジェクト')).toBeVisible()
      await expect(page.getByText('A株式会社')).toBeVisible()
    })

    test('新規プロジェクトボタンが表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/sales-company')

      const newProjectButton = page.getByRole('button', { name: '新規プロジェクト' })
      await expect(newProjectButton).toBeVisible()
      await expect(newProjectButton).toBeEnabled()
    })

    test('プロジェクト行をクリックすると詳細ページに遷移する（準備）', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/sales-company')

      // プロジェクト名をクリック
      const projectRow = page.getByText('A社フォーム営業プロジェクト').locator('..')
      await projectRow.click()

      // TODO: プロジェクト詳細ページ実装後に、遷移先のURLを検証
      // await expect(page).toHaveURL(/\/dashboard\/sales-company\/projects\/1/)
    })
  })

  test.describe('顧客ダッシュボード', () => {
    test.beforeEach(async ({ page, context }) => {
      // 顧客ユーザーとしてログイン（モック）
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '2',
            email: 'customer@example.com',
            name: '顧客担当者',
            role: 'customer',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])
      await page.goto('http://localhost:3000/dashboard')
    })

    test('顧客ダッシュボードが表示される', async ({ page }) => {
      // リダイレクト後のURLを確認
      await expect(page).toHaveURL(/\/dashboard\/customer/)

      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: '依頼プロジェクト一覧' })).toBeVisible()

      // 統計カードを確認
      await expect(page.getByText('依頼中プロジェクト')).toBeVisible()
    })

    test('依頼プロジェクト一覧が表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/customer')

      // テーブルヘッダーを確認
      await expect(page.getByRole('columnheader', { name: 'プロジェクト名' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'ステータス' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: '作成日' })).toBeVisible()

      // モックデータのプロジェクトを確認
      await expect(page.getByText('新規顧客獲得キャンペーン')).toBeVisible()
    })

    test('進捗バーが表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/customer')

      // 進捗パーセンテージを確認
      await expect(page.getByText('65%')).toBeVisible()
      await expect(page.getByText('40%')).toBeVisible()
    })
  })

  test.describe('ワーカーダッシュボード', () => {
    test.beforeEach(async ({ page, context }) => {
      // ワーカーユーザーとしてログイン（モック）
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '3',
            email: 'worker@example.com',
            name: 'ワーカー',
            role: 'worker',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])
      await page.goto('http://localhost:3000/dashboard')
    })

    test('ワーカーダッシュボードが表示される', async ({ page }) => {
      // リダイレクト後のURLを確認
      await expect(page).toHaveURL(/\/dashboard\/worker/)

      // ページタイトルを確認
      await expect(page.getByRole('heading', { name: '割り当てリスト一覧' })).toBeVisible()

      // 統計カードを確認
      await expect(page.getByText('割り当て中')).toBeVisible()
      await expect(page.getByText('作業中')).toBeVisible()
      await expect(page.getByText('処理進捗')).toBeVisible()
    })

    test('割り当てタスク一覧が表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/worker')

      // テーブルヘッダーを確認
      await expect(page.getByRole('columnheader', { name: '優先度' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'リスト名' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: '処理状況' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: '期限' })).toBeVisible()

      // モックデータのタスクを確認
      await expect(page.getByText('IT企業リスト（東京）')).toBeVisible()
    })

    test('優先度バッジが表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/worker')

      // 優先度を確認
      await expect(page.getByText('高')).toBeVisible()
      await expect(page.getByText('中')).toBeVisible()
      await expect(page.getByText('低')).toBeVisible()
      await expect(page.getByText('緊急')).toBeVisible()
    })

    test('処理状況が表示される', async ({ page }) => {
      await page.goto('http://localhost:3000/dashboard/worker')

      // 処理状況を確認
      await expect(page.getByText('325 / 500')).toBeVisible()
      await expect(page.getByText('0 / 300')).toBeVisible()
    })
  })

  test.describe('ロール別リダイレクト', () => {
    test('営業支援会社ユーザーは営業支援会社ダッシュボードにリダイレクトされる', async ({
      page,
      context,
    }) => {
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '1',
            email: 'sales@example.com',
            role: 'sales_company',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])

      await page.goto('http://localhost:3000/dashboard')
      await expect(page).toHaveURL(/\/dashboard\/sales-company/)
    })

    test('顧客ユーザーは顧客ダッシュボードにリダイレクトされる', async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '2',
            email: 'customer@example.com',
            role: 'customer',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])

      await page.goto('http://localhost:3000/dashboard')
      await expect(page).toHaveURL(/\/dashboard\/customer/)
    })

    test('ワーカーユーザーはワーカーダッシュボードにリダイレクトされる', async ({
      page,
      context,
    }) => {
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '3',
            email: 'worker@example.com',
            role: 'worker',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])

      await page.goto('http://localhost:3000/dashboard')
      await expect(page).toHaveURL(/\/dashboard\/worker/)
    })
  })

  test.describe('レスポンシブデザイン', () => {
    test('モバイル表示でも正しくレンダリングされる', async ({ page, context }) => {
      // 営業支援会社ユーザーとしてログイン
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '1',
            email: 'sales@example.com',
            role: 'sales_company',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])

      // モバイルビューポートを設定
      await page.setViewportSize({ width: 375, height: 667 })
      await page.goto('http://localhost:3000/dashboard/sales-company')

      // ページが表示されることを確認
      await expect(page.getByRole('heading', { name: 'プロジェクト一覧' })).toBeVisible()
      await expect(page.getByText('総プロジェクト数')).toBeVisible()
    })

    test('タブレット表示でも正しくレンダリングされる', async ({ page, context }) => {
      await context.addCookies([
        {
          name: 'user',
          value: JSON.stringify({
            id: '1',
            email: 'sales@example.com',
            role: 'sales_company',
          }),
          domain: 'localhost',
          path: '/',
        },
      ])

      // タブレットビューポートを設定
      await page.setViewportSize({ width: 768, height: 1024 })
      await page.goto('http://localhost:3000/dashboard/sales-company')

      // ページが表示されることを確認
      await expect(page.getByRole('heading', { name: 'プロジェクト一覧' })).toBeVisible()
    })
  })
})
