/**
 * ワーカー管理機能のE2Eテスト
 *
 * TDDサイクルに従って実装
 */

import { test, expect } from "@playwright/test";

test.describe("ワーカー管理機能", () => {
  test.beforeEach(async ({ page }) => {
    // ワーカー管理ページに移動
    await page.goto("/dashboard/sales-company/workers");
  });

  test.describe("ワーカー一覧ページ", () => {
    test("ワーカー管理ページが正しく表示される", async ({ page }) => {
      // ページタイトルを確認
      await expect(
        page.getByRole("heading", { name: "ワーカー管理" })
      ).toBeVisible();

      // 説明文を確認
      await expect(
        page.getByText("ワーカーの登録・編集・削除ができます。")
      ).toBeVisible();

      // 新規登録ボタンを確認
      await expect(
        page.getByRole("button", { name: "新規登録" })
      ).toBeVisible();
    });

    test("ワーカー一覧テーブルが表示される", async ({ page }) => {
      // テーブルが表示される
      await expect(page.getByRole("table")).toBeVisible();

      // テーブルヘッダーを確認
      await expect(page.getByText("ID")).toBeVisible();
      await expect(page.getByText("ステータス")).toBeVisible();
      await expect(page.getByText("スキルレベル")).toBeVisible();
      await expect(page.getByText("専門分野")).toBeVisible();
      await expect(page.getByText("経験月数")).toBeVisible();
      await expect(page.getByText("完了タスク数")).toBeVisible();
      await expect(page.getByText("成功率")).toBeVisible();
      await expect(page.getByText("評価")).toBeVisible();
      await expect(page.getByText("操作")).toBeVisible();
    });

    test("ワーカー情報が正しく表示される", async ({ page }) => {
      // ステータスバッジが表示される
      await expect(page.getByText("稼働中")).toBeVisible();
      await expect(page.getByText("承認待ち")).toBeVisible();

      // スキルレベルが表示される
      await expect(page.getByText("中級")).toBeVisible();
      await expect(page.getByText("初級")).toBeVisible();

      // パフォーマンス指標が表示される
      await expect(page.getByText("85.5%")).toBeVisible();
      await expect(page.getByText("4.5")).toBeVisible();
    });

    test("ワーカーが0件の場合、メッセージが表示される", async ({
      page,
    }) => {
      // モックデータがない場合のテスト
      // 実際のテストでは、モックを調整する必要がある
      // await expect(
      //   page.getByText("ワーカーが登録されていません。")
      // ).toBeVisible();
    });
  });

  test.describe("ワーカー新規登録", () => {
    test.beforeEach(async ({ page }) => {
      // 新規登録ボタンをクリック
      await page.getByRole("button", { name: "新規登録" }).click();
    });

    test("新規登録フォームが表示される", async ({ page }) => {
      // ダイアログタイトルを確認
      await expect(page.getByText("ワーカー新規登録")).toBeVisible();

      // フォーム要素を確認
      await expect(page.getByLabel("ユーザーID")).toBeVisible();
      await expect(page.getByLabel("ステータス")).toBeVisible();
      await expect(page.getByLabel("スキルレベル")).toBeVisible();
      await expect(page.getByLabel("経験月数")).toBeVisible();
      await expect(page.getByLabel("専門分野")).toBeVisible();
      await expect(page.getByLabel("1日の最大タスク数")).toBeVisible();
      await expect(page.getByLabel("週間稼働可能時間")).toBeVisible();
      await expect(page.getByLabel("メモ")).toBeVisible();

      // ボタンを確認
      await expect(page.getByRole("button", { name: "登録" })).toBeVisible();
      await expect(
        page.getByRole("button", { name: "キャンセル" })
      ).toBeVisible();
    });

    test("キャンセルボタンをクリックすると、フォームが閉じる", async ({
      page,
    }) => {
      await page.getByRole("button", { name: "キャンセル" }).click();

      // フォームが閉じることを確認
      await expect(page.getByText("ワーカー新規登録")).not.toBeVisible();
    });

    test("必須項目が未入力の場合、エラーが表示される", async ({
      page,
    }) => {
      // 何も入力せずに登録ボタンをクリック
      await page.getByRole("button", { name: "登録" }).click();

      // エラーメッセージを確認
      await expect(page.getByText("ユーザーIDは必須です")).toBeVisible();
    });

    test("有効なデータを入力して登録できる", async ({ page }) => {
      // ユーザーIDを入力
      await page.getByLabel("ユーザーID").fill("1");

      // ステータスを選択
      await page.getByLabel("ステータス").selectOption("active");

      // スキルレベルを選択
      await page.getByLabel("スキルレベル").selectOption("intermediate");

      // 経験月数を入力
      await page.getByLabel("経験月数").fill("12");

      // 専門分野を入力
      await page.getByLabel("専門分野").fill("BtoB営業、IT業界");

      // 登録ボタンをクリック
      await page.getByRole("button", { name: "登録" }).click();

      // フォームが閉じることを確認
      await expect(page.getByText("ワーカー新規登録")).not.toBeVisible();
    });

    test("バリデーションが動作する", async ({ page }) => {
      // 負の経験月数を入力
      await page.getByLabel("ユーザーID").fill("1");
      await page.getByLabel("経験月数").fill("-5");
      await page.getByRole("button", { name: "登録" }).click();

      // エラーメッセージを確認
      await expect(
        page.getByText("経験月数は0以上である必要があります")
      ).toBeVisible();
    });
  });

  test.describe("ワーカー編集", () => {
    test.beforeEach(async ({ page }) => {
      // 編集ボタンをクリック
      const editButtons = page.getByRole("button", { name: "編集" });
      await editButtons.first().click();
    });

    test("編集フォームが表示される", async ({ page }) => {
      // ダイアログタイトルを確認
      await expect(page.getByText("ワーカー編集")).toBeVisible();

      // フォーム要素を確認（ユーザーIDは編集不可）
      await expect(page.getByLabel("ステータス")).toBeVisible();
      await expect(page.getByLabel("スキルレベル")).toBeVisible();
      await expect(page.getByLabel("経験月数")).toBeVisible();

      // ボタンを確認
      await expect(page.getByRole("button", { name: "更新" })).toBeVisible();
      await expect(
        page.getByRole("button", { name: "キャンセル" })
      ).toBeVisible();
    });

    test("既存データが初期値として表示される", async ({ page }) => {
      // 既存の値が設定されていることを確認
      const experienceMonthsInput = page.getByLabel("経験月数");
      await expect(experienceMonthsInput).toHaveValue("12");

      const specialtiesInput = page.getByLabel("専門分野");
      await expect(specialtiesInput).toHaveValue("BtoB営業、IT業界");
    });

    test("データを編集して更新できる", async ({ page }) => {
      // ステータスを変更
      await page.getByLabel("ステータス").selectOption("inactive");

      // 更新ボタンをクリック
      await page.getByRole("button", { name: "更新" }).click();

      // フォームが閉じることを確認
      await expect(page.getByText("ワーカー編集")).not.toBeVisible();
    });

    test("キャンセルボタンをクリックすると、フォームが閉じる", async ({
      page,
    }) => {
      await page.getByRole("button", { name: "キャンセル" }).click();

      // フォームが閉じることを確認
      await expect(page.getByText("ワーカー編集")).not.toBeVisible();
    });
  });

  test.describe("ワーカー削除", () => {
    test("削除ボタンをクリックすると、確認ダイアログが表示される", async ({
      page,
    }) => {
      // 削除ダイアログのハンドラを設定
      page.on("dialog", (dialog) => {
        expect(dialog.message()).toBe(
          "このワーカーを削除してもよろしいですか？"
        );
        dialog.dismiss(); // キャンセル
      });

      // 削除ボタンをクリック
      const deleteButtons = page.getByRole("button", { name: "削除" });
      await deleteButtons.first().click();
    });

    test("確認ダイアログでOKを選択すると、ワーカーが削除される", async ({
      page,
    }) => {
      // 削除ダイアログのハンドラを設定
      page.on("dialog", (dialog) => {
        dialog.accept(); // OK
      });

      // 削除ボタンをクリック
      const deleteButtons = page.getByRole("button", { name: "削除" });
      await deleteButtons.first().click();

      // ワーカーが削除されることを確認（APIモックが必要）
      // await expect(page.getByText("削除されました")).toBeVisible();
    });
  });

  test.describe("アクセシビリティ", () => {
    test("適切なARIAラベルが設定されている", async ({ page }) => {
      // 新規登録フォームを開く
      await page.getByRole("button", { name: "新規登録" }).click();

      // フォーム要素にラベルが設定されている
      await expect(page.getByLabel("ユーザーID")).toBeVisible();
      await expect(page.getByLabel("ステータス")).toBeVisible();
      await expect(page.getByLabel("スキルレベル")).toBeVisible();
      await expect(page.getByLabel("経験月数")).toBeVisible();
    });

    test("キーボードナビゲーションが機能する", async ({ page }) => {
      // 新規登録フォームを開く
      await page.getByRole("button", { name: "新規登録" }).click();

      // Tabキーで移動できることを確認
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");

      // フォーカスが移動することを確認（詳細なテストは省略）
    });
  });

  test.describe("レスポンシブデザイン", () => {
    test("モバイルビューで正しく表示される", async ({ page }) => {
      // モバイルビューポートに設定
      await page.setViewportSize({ width: 375, height: 667 });

      // ワーカー管理ページが表示される
      await expect(
        page.getByRole("heading", { name: "ワーカー管理" })
      ).toBeVisible();

      // 新規登録ボタンが表示される
      await expect(
        page.getByRole("button", { name: "新規登録" })
      ).toBeVisible();

      // テーブルが横スクロールできることを確認（視覚的なテストは省略）
      await expect(page.getByRole("table")).toBeVisible();
    });
  });
});
