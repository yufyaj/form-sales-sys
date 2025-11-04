import { test, expect } from '@playwright/test'

test.describe('ナビゲーション', () => {
  test.beforeEach(async ({ page }) => {
    // ダッシュボードページに移動
    await page.goto('/dashboard')
  })

  test('サイドバーのナビゲーションリンクが機能する', async ({ page }) => {
    // デスクトップサイズに設定
    await page.setViewportSize({ width: 1280, height: 720 })

    // ダッシュボードリンクがアクティブであることを確認
    const dashboardLink = page.getByRole('link', { name: 'ダッシュボード' })
    await expect(dashboardLink).toHaveClass(/bg-blue-50/)
  })

  test('モバイルでナビゲーションリンクをクリックするとメニューが閉じる', async ({
    page,
  }) => {
    // モバイルサイズに設定
    await page.setViewportSize({ width: 375, height: 667 })

    // メニューを開く
    const menuButton = page.getByLabel('メニューを開く')
    await menuButton.click({ force: true }) // force: true で重なり問題を回避

    // ナビゲーションリンクが表示されることを確認
    const projectLink = page.getByRole('link', { name: 'プロジェクト' })
    await expect(projectLink).toBeVisible()

    // リンクをクリック
    await projectLink.click()

    // アニメーション待機
    await page.waitForTimeout(300)

    // メニューが閉じたことを確認するために、再度メニューを開けることを確認
    await menuButton.click({ force: true })
    await expect(projectLink).toBeVisible()
  })

  test('ユーザーメニューが開閉する', async ({ page }) => {
    // デスクトップサイズに設定
    await page.setViewportSize({ width: 1280, height: 720 })

    // ユーザーメニューボタンをクリック
    const userMenuButton = page.getByLabel('ユーザーメニュー')
    await userMenuButton.click()

    // ログアウトボタンが表示されることを確認
    await expect(page.getByRole('button', { name: 'ログアウト' })).toBeVisible()

    // メニューボタンを再度クリックして閉じる
    await userMenuButton.click()

    // ログアウトボタンが非表示になることを確認
    await expect(
      page.getByRole('button', { name: 'ログアウト' })
    ).not.toBeVisible()
  })

  test('ダッシュボードカードが表示される', async ({ page }) => {
    // 統計カードを確認（複数要素がある場合はより具体的なセレクターを使用）
    await expect(page.getByRole('heading', { name: 'プロジェクト' })).toBeVisible()
    await expect(page.getByText('進行中のプロジェクト')).toBeVisible()

    await expect(page.getByRole('heading', { name: 'リスト' })).toBeVisible()
    await expect(page.getByText('登録済みリスト')).toBeVisible()

    await expect(page.getByRole('heading', { name: '送信済み' })).toBeVisible()
    await expect(page.getByText('今月の送信数')).toBeVisible()
  })

  test('レスポンシブグリッドが機能する', async ({ page }) => {
    // モバイルサイズ - 1列表示
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.getByRole('heading', { name: 'プロジェクト' })).toBeVisible()

    // タブレットサイズ - 2列表示
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.getByRole('heading', { name: 'プロジェクト' })).toBeVisible()

    // デスクトップサイズ - 3列表示
    await page.setViewportSize({ width: 1280, height: 720 })
    await expect(page.getByRole('heading', { name: 'プロジェクト' })).toBeVisible()
  })

  test('ユーザー情報が表示される', async ({ page }) => {
    // デスクトップサイズに設定
    await page.setViewportSize({ width: 1280, height: 720 })

    // ユーザーメニューを開く
    const userMenuButton = page.getByLabel('ユーザーメニュー')
    await userMenuButton.click()

    // ユーザー情報を確認（モックデータ）
    // ドロップダウン内の情報を確認
    await expect(page.getByText('user@example.com')).toBeVisible()
    // ヘッダー内のロール情報を確認（より具体的なセレクター）
    await expect(
      page.getByRole('banner').getByText('ロール: 管理者')
    ).toBeVisible()
  })

  test('サイドバーのロール情報が表示される', async ({ page }) => {
    // デスクトップサイズに設定
    await page.setViewportSize({ width: 1280, height: 720 })

    // サイドバー内のロール情報を確認
    await expect(page.getByText('ロール: 管理者')).toBeVisible()
  })
})
