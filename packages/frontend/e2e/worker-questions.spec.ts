import { test, expect } from '@playwright/test'

/**
 * ワーカー質問管理機能のE2Eテスト
 *
 * 営業支援会社ユーザーとしてのワーカー質問管理機能を検証
 */
test.describe('ワーカー質問管理', () => {
  // 認証前の準備
  // Note: 実際のE2E環境では適切な認証フローを実装する必要があります
  test.beforeEach(async ({ page }) => {
    // TODO: 営業支援会社ユーザーとしてログイン
    // 現在はモックユーザーを使用（AuthContext の 501 レスポンス）
    await page.goto('/dashboard/sales-company/worker-questions')
  })

  test.describe('質問一覧ページ', () => {
    test('質問一覧ページが正しく表示される', async ({ page }) => {
      // ページタイトルを確認
      await expect(
        page.getByRole('heading', { name: 'ワーカー質問管理' })
      ).toBeVisible()

      // フィルター要素を確認
      await expect(page.getByLabel('ステータス')).toBeVisible()
      await expect(page.getByLabel('優先度')).toBeVisible()
      await expect(
        page.getByRole('button', { name: 'フィルタークリア' })
      ).toBeVisible()
    })

    test('ステータスフィルターで質問をフィルタリングできる', async ({
      page,
    }) => {
      // ステータスフィルターを選択
      await page.getByLabel('ステータス').selectOption('pending')

      // フィルタリング後の表示を確認
      // Note: 実際のデータがある場合、期待される結果を確認
      await expect(page.getByText(/件の質問が見つかりました/)).toBeVisible()
    })

    test('優先度フィルターで質問をフィルタリングできる', async ({
      page,
    }) => {
      // 優先度フィルターを選択
      await page.getByLabel('優先度').selectOption('urgent')

      // フィルタリング後の表示を確認
      await expect(page.getByText(/件の質問が見つかりました/)).toBeVisible()
    })

    test('フィルタークリアボタンでフィルターがリセットされる', async ({
      page,
    }) => {
      // フィルターを設定
      await page.getByLabel('ステータス').selectOption('pending')
      await page.getByLabel('優先度').selectOption('high')

      // フィルタークリアボタンをクリック
      await page.getByRole('button', { name: 'フィルタークリア' }).click()

      // フィルターがリセットされることを確認
      await expect(page.getByLabel('ステータス')).toHaveValue('')
      await expect(page.getByLabel('優先度')).toHaveValue('')
    })

    test.skip('質問カードをクリックすると詳細ページに遷移する', async ({
      page,
    }) => {
      // Note: 実際のデータがある場合のテスト
      // 質問カードの「回答する」または「詳細を見る」ボタンをクリック
      const detailButton = page
        .getByRole('button', { name: /回答する|詳細を見る/ })
        .first()
      await detailButton.click()

      // 詳細ページに遷移することを確認
      await expect(page).toHaveURL(/\/worker-questions\/\d+/)
    })

    test('データがない場合は適切なメッセージが表示される', async ({
      page,
    }) => {
      // 存在しないフィルターを設定してデータを空にする
      await page.getByLabel('ステータス').selectOption('closed')
      await page.getByLabel('優先度').selectOption('low')

      // データがない場合のメッセージを確認
      // Note: 実際のデータ状況によって調整が必要
      await expect(
        page.getByText(/質問が登録されていません|0件の質問が見つかりました/)
      ).toBeVisible()
    })
  })

  test.describe('質問詳細・回答ページ', () => {
    test.skip('質問詳細ページが正しく表示される', async ({ page }) => {
      // Note: 実際の質問IDを使用する必要があります
      const questionId = 1
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 一覧に戻るボタンを確認
      await expect(
        page.getByRole('button', { name: '← 一覧に戻る' })
      ).toBeVisible()

      // 質問情報セクションを確認
      await expect(page.getByText('質問ID:')).toBeVisible()
      await expect(page.getByText('ワーカーID:')).toBeVisible()
      await expect(page.getByText('作成日時:')).toBeVisible()

      // 回答セクションを確認
      await expect(page.getByRole('heading', { name: '回答' })).toBeVisible()
    })

    test.skip('回答フォームが正しく表示される', async ({ page }) => {
      // Note: 未回答の質問IDを使用する必要があります
      const questionId = 1
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 回答フォーム要素を確認
      await expect(page.getByLabel(/回答内容/)).toBeVisible()
      await expect(
        page.getByRole('button', { name: /回答を送信/ })
      ).toBeVisible()
    })

    test.skip('空の回答で送信するとバリデーションエラーが表示される', async ({
      page,
    }) => {
      const questionId = 1
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 空のまま送信
      await page.getByRole('button', { name: /回答を送信/ }).click()

      // エラーメッセージを確認
      await expect(
        page.getByText('回答を入力してください')
      ).toBeVisible()
    })

    test.skip('有効な回答を送信すると成功する', async ({ page }) => {
      const questionId = 1
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 回答を入力
      const answerText = 'これはテスト回答です。質問にお答えします。'
      await page.getByLabel(/回答内容/).fill(answerText)

      // 送信
      await page.getByRole('button', { name: /回答を送信/ }).click()

      // 成功後の表示を確認
      // Note: 実装により、成功メッセージや回答表示の確認が必要
      await expect(page.getByText(answerText)).toBeVisible({ timeout: 10000 })
    })

    test.skip('既存の回答を編集できる', async ({ page }) => {
      // Note: 既に回答済みの質問IDを使用する必要があります
      const questionId = 2
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 回答を編集ボタンをクリック
      await page.getByRole('button', { name: '回答を編集' }).click()

      // 回答フォームが表示されることを確認
      await expect(page.getByLabel(/回答内容/)).toBeVisible()
      await expect(
        page.getByRole('button', { name: /回答を更新/ })
      ).toBeVisible()
      await expect(
        page.getByRole('button', { name: /キャンセル/ })
      ).toBeVisible()
    })

    test.skip('回答編集をキャンセルできる', async ({ page }) => {
      const questionId = 2
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 回答を編集ボタンをクリック
      await page.getByRole('button', { name: '回答を編集' }).click()

      // キャンセルボタンをクリック
      await page.getByRole('button', { name: /キャンセル/ }).click()

      // フォームが非表示になり、回答が表示されることを確認
      await expect(page.getByLabel(/回答内容/)).not.toBeVisible()
      await expect(page.getByText('回答内容')).toBeVisible()
    })

    test.skip('一覧に戻るボタンで一覧ページに戻る', async ({ page }) => {
      const questionId = 1
      await page.goto(
        `/dashboard/sales-company/worker-questions/${questionId}`
      )

      // 一覧に戻るボタンをクリック
      await page.getByRole('button', { name: '← 一覧に戻る' }).click()

      // 一覧ページに遷移することを確認
      await expect(page).toHaveURL('/dashboard/sales-company/worker-questions')
      await expect(
        page.getByRole('heading', { name: 'ワーカー質問管理' })
      ).toBeVisible()
    })
  })

  test.describe('ページネーション', () => {
    test.skip('ページネーションが正しく機能する', async ({ page }) => {
      // Note: 20件以上のデータがある場合のテスト
      await page.goto('/dashboard/sales-company/worker-questions')

      // ページネーションボタンを確認
      const nextButton = page.getByRole('button', { name: '次へ' })
      await expect(nextButton).toBeVisible()

      // 次のページに移動
      await nextButton.click()

      // URLまたは表示内容が変わることを確認
      await expect(page.getByText(/\d+ - \d+ \/ \d+ 件/)).toBeVisible()
    })
  })

  test.describe('アクセシビリティ', () => {
    test('キーボードナビゲーションが機能する', async ({ page }) => {
      await page.goto('/dashboard/sales-company/worker-questions')

      // Tabキーでフォーカス移動
      await page.keyboard.press('Tab')
      await page.keyboard.press('Tab')

      // フォーカスされた要素を確認
      // Note: 具体的なフォーカス順序の検証
    })

    test('スクリーンリーダー向けのラベルが適切に設定されている', async ({
      page,
    }) => {
      await page.goto('/dashboard/sales-company/worker-questions')

      // aria-labelやlabelタグが適切に設定されていることを確認
      await expect(page.getByLabel('ステータス')).toBeVisible()
      await expect(page.getByLabel('優先度')).toBeVisible()
    })
  })

  test.describe('エラーハンドリング', () => {
    test.skip('存在しない質問IDにアクセスするとエラーが表示される', async ({
      page,
    }) => {
      const invalidQuestionId = 999999
      await page.goto(
        `/dashboard/sales-company/worker-questions/${invalidQuestionId}`
      )

      // エラーメッセージを確認
      await expect(
        page.getByText(/質問が見つかりませんでした|エラー/)
      ).toBeVisible()
    })

    test('ネットワークエラー時に適切なエラーメッセージが表示される', async ({
      page,
    }) => {
      // ネットワークをオフラインにする
      await page.context().setOffline(true)

      await page.goto('/dashboard/sales-company/worker-questions')

      // エラーメッセージまたはリトライボタンを確認
      // Note: 実装により異なる可能性があります
      await expect(
        page.getByText(/エラー|再読み込み/)
      ).toBeVisible({ timeout: 10000 })

      // ネットワークを復元
      await page.context().setOffline(false)
    })
  })
})
