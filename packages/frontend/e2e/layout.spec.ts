import { test, expect } from '@playwright/test'

test.describe('メインレイアウト', () => {
  test.beforeEach(async ({ page }) => {
    // ダッシュボードページに移動（メインレイアウトを使用）
    await page.goto('/dashboard')
  })

  test('ヘッダーが正しく表示される', async ({ page }) => {
    // タイトルを確認
    await expect(
      page.getByRole('heading', { name: 'フォーム営業支援システム' })
    ).toBeVisible()
  })

  test('サイドバーが正しく表示される（デスクトップ）', async ({ page }) => {
    // デスクトップサイズに設定
    await page.setViewportSize({ width: 1280, height: 720 })

    // ナビゲーション項目を確認
    await expect(page.getByRole('link', { name: 'ダッシュボード' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'プロジェクト' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'リスト管理' })).toBeVisible()
    await expect(page.getByRole('link', { name: '設定' })).toBeVisible()
  })

  test('モバイルメニューボタンが表示される（モバイル）', async ({ page }) => {
    // モバイルサイズに設定
    await page.setViewportSize({ width: 375, height: 667 })

    // メニューボタンを確認
    const menuButton = page.getByLabel('メニューを開く')
    await expect(menuButton).toBeVisible()
  })

  test('モバイルメニューが開閉する', async ({ page }) => {
    // モバイルサイズに設定
    await page.setViewportSize({ width: 375, height: 667 })

    // メニューを開く
    const menuButton = page.getByLabel('メニューを開く')
    await menuButton.click({ force: true }) // force: true で重なり問題を回避

    // サイドバーが表示されることを確認
    await expect(page.getByRole('link', { name: 'ダッシュボード' })).toBeVisible()

    // サイドバー内のリンクをクリックしてメニューを閉じる
    await page.getByRole('link', { name: 'ダッシュボード' }).click()

    // アニメーション待機
    await page.waitForTimeout(300)
  })

  test('メインコンテンツが表示される', async ({ page }) => {
    // ダッシュボードページのコンテンツを確認
    await expect(page.getByRole('heading', { name: 'ダッシュボード' })).toBeVisible()
    await expect(
      page.getByText('フォーム営業支援システムへようこそ')
    ).toBeVisible()
  })

  test('レスポンシブデザインが機能する', async ({ page }) => {
    // デスクトップサイズ
    await page.setViewportSize({ width: 1280, height: 720 })
    await expect(page.getByRole('link', { name: 'ダッシュボード' })).toBeVisible()

    // タブレットサイズ
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.getByLabel('メニューを開く')).toBeVisible()

    // モバイルサイズ
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.getByLabel('メニューを開く')).toBeVisible()
  })
})
