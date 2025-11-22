/**
 * ワーカーフォームコンポーネントのテスト
 *
 * TDDサイクル: Red -> Green -> Refactor
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WorkerForm } from "@/components/features/worker/WorkerForm";
import { Worker, WorkerStatus, SkillLevel } from "@/types/worker";

// モック: 既存ワーカーデータ（編集モード用）
const mockWorker: Worker = {
  id: 1,
  userId: 1,
  organizationId: 1,
  status: WorkerStatus.ACTIVE,
  skillLevel: SkillLevel.INTERMEDIATE,
  experienceMonths: 12,
  specialties: "BtoB営業、IT業界",
  maxTasksPerDay: 10,
  availableHoursPerWeek: 40,
  completedTasksCount: 50,
  successRate: 85.5,
  averageTaskTimeMinutes: 30,
  rating: 4.5,
  notes: "優秀なワーカー",
  createdAt: "2025-11-22T10:00:00Z",
  updatedAt: "2025-11-22T10:00:00Z",
  deletedAt: null,
};

describe("WorkerForm", () => {
  describe("新規作成モード", () => {
    it("フォームが表示される", () => {
      // Arrange
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      // Assert
      expect(screen.getByRole("form")).toBeInTheDocument();
      expect(screen.getByLabelText("ユーザーID")).toBeInTheDocument();
      expect(screen.getByLabelText("ステータス")).toBeInTheDocument();
      expect(screen.getByLabelText("スキルレベル")).toBeInTheDocument();
      expect(screen.getByLabelText("経験月数")).toBeInTheDocument();
      expect(screen.getByLabelText("専門分野")).toBeInTheDocument();
      expect(screen.getByLabelText("1日の最大タスク数")).toBeInTheDocument();
      expect(
        screen.getByLabelText("週間稼働可能時間")
      ).toBeInTheDocument();
      expect(screen.getByLabelText("メモ")).toBeInTheDocument();
    });

    it("必須項目が未入力の場合、送信できない", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      const submitButton = screen.getByRole("button", { name: "登録" });
      await user.click(submitButton);

      // Assert
      await waitFor(() => {
        // Zodのデフォルトエラーメッセージを確認
        expect(
          screen.getByText(/Invalid input/)
        ).toBeInTheDocument();
      });
      expect(onSubmit).not.toHaveBeenCalled();
    });

    it("有効なデータを入力して送信できる", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      // ユーザーIDを入力
      const userIdInput = screen.getByLabelText("ユーザーID");
      await user.type(userIdInput, "1");

      // ステータスを選択
      const statusSelect = screen.getByLabelText("ステータス");
      await user.selectOptions(statusSelect, WorkerStatus.ACTIVE);

      // スキルレベルを選択
      const skillLevelSelect = screen.getByLabelText("スキルレベル");
      await user.selectOptions(skillLevelSelect, SkillLevel.INTERMEDIATE);

      // 経験月数を入力
      const experienceMonthsInput = screen.getByLabelText("経験月数");
      await user.type(experienceMonthsInput, "12");

      // 専門分野を入力
      const specialtiesInput = screen.getByLabelText("専門分野");
      await user.type(specialtiesInput, "BtoB営業、IT業界");

      // 送信
      const submitButton = screen.getByRole("button", { name: "登録" });
      await user.click(submitButton);

      // Assert
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledTimes(1);
        expect(onSubmit).toHaveBeenCalledWith({
          userId: 1,
          status: WorkerStatus.ACTIVE,
          skillLevel: SkillLevel.INTERMEDIATE,
          experienceMonths: 12,
          specialties: "BtoB営業、IT業界",
          maxTasksPerDay: null,
          availableHoursPerWeek: null,
          notes: null,
        });
      });
    });

    it("キャンセルボタンをクリックするとonCancel関数が呼ばれる", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      const cancelButton = screen.getByRole("button", { name: "キャンセル" });
      await user.click(cancelButton);

      // Assert
      expect(onCancel).toHaveBeenCalledTimes(1);
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });

  describe("編集モード", () => {
    it("既存データが初期値として表示される", () => {
      // Arrange
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(
        <WorkerForm
          worker={mockWorker}
          onSubmit={onSubmit}
          onCancel={onCancel}
        />
      );

      // Assert
      expect(screen.getByDisplayValue("12")).toBeInTheDocument(); // 経験月数
      expect(
        screen.getByDisplayValue("BtoB営業、IT業界")
      ).toBeInTheDocument(); // 専門分野
      expect(screen.getByDisplayValue("10")).toBeInTheDocument(); // 最大タスク数
      expect(screen.getByDisplayValue("40")).toBeInTheDocument(); // 週間稼働時間
      expect(
        screen.getByDisplayValue("優秀なワーカー")
      ).toBeInTheDocument(); // メモ
    });

    it("編集した内容を送信できる", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(
        <WorkerForm
          worker={mockWorker}
          onSubmit={onSubmit}
          onCancel={onCancel}
        />
      );

      // ステータスを変更
      const statusSelect = screen.getByLabelText("ステータス");
      await user.selectOptions(statusSelect, WorkerStatus.INACTIVE);

      // 送信
      const submitButton = screen.getByRole("button", { name: "更新" });
      await user.click(submitButton);

      // Assert
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledTimes(1);
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            status: WorkerStatus.INACTIVE,
          })
        );
      });
    });
  });

  describe("バリデーション", () => {
    it("ユーザーIDが数値でない場合、エラーが表示される", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      const userIdInput = screen.getByLabelText("ユーザーID");
      await user.type(userIdInput, "abc");

      const submitButton = screen.getByRole("button", { name: "登録" });
      await user.click(submitButton);

      // Assert
      await waitFor(() => {
        // Zodのデフォルトエラーメッセージを確認
        expect(
          screen.getByText(/Invalid input/)
        ).toBeInTheDocument();
      });
      expect(onSubmit).not.toHaveBeenCalled();
    });

    it("経験月数が負の数の場合、エラーが表示される", async () => {
      // Arrange
      const user = userEvent.setup();
      const onSubmit = jest.fn();
      const onCancel = jest.fn();

      // Act
      render(<WorkerForm onSubmit={onSubmit} onCancel={onCancel} />);

      const userIdInput = screen.getByLabelText("ユーザーID");
      await user.type(userIdInput, "1");

      const experienceMonthsInput = screen.getByLabelText("経験月数");
      await user.type(experienceMonthsInput, "-5");

      const submitButton = screen.getByRole("button", { name: "登録" });
      await user.click(submitButton);

      // Assert
      await waitFor(() => {
        expect(
          screen.getByText("経験月数は0以上である必要があります")
        ).toBeInTheDocument();
      });
      expect(onSubmit).not.toHaveBeenCalled();
    });
  });
});
