/**
 * ワーカー一覧テーブルコンポーネントのテスト
 *
 * TDDサイクル: Red -> Green -> Refactor
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { WorkerTable } from "@/components/features/worker/WorkerTable";
import { Worker, WorkerStatus, SkillLevel } from "@/types/worker";

// モックデータ
const mockWorkers: Worker[] = [
  {
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
  },
  {
    id: 2,
    userId: 2,
    organizationId: 1,
    status: WorkerStatus.PENDING,
    skillLevel: SkillLevel.BEGINNER,
    experienceMonths: 3,
    specialties: "BtoC営業",
    maxTasksPerDay: 5,
    availableHoursPerWeek: 20,
    completedTasksCount: 10,
    successRate: 70.0,
    averageTaskTimeMinutes: 45,
    rating: 3.5,
    notes: null,
    createdAt: "2025-11-22T11:00:00Z",
    updatedAt: "2025-11-22T11:00:00Z",
    deletedAt: null,
  },
];

describe("WorkerTable", () => {
  // Arrange-Act-Assert パターンを遵守

  describe("表示テスト", () => {
    it("ワーカー一覧が表示される", () => {
      // Arrange
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      // Assert
      expect(screen.getByRole("table")).toBeInTheDocument();
      expect(screen.getByText("BtoB営業、IT業界")).toBeInTheDocument();
      expect(screen.getByText("BtoC営業")).toBeInTheDocument();
    });

    it("ステータスバッジが正しく表示される", () => {
      // Arrange
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      // Assert
      expect(screen.getByText("稼働中")).toBeInTheDocument();
      expect(screen.getByText("承認待ち")).toBeInTheDocument();
    });

    it("スキルレベルが正しく表示される", () => {
      // Arrange
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      // Assert
      expect(screen.getByText("中級")).toBeInTheDocument();
      expect(screen.getByText("初級")).toBeInTheDocument();
    });

    it("パフォーマンス指標が表示される", () => {
      // Arrange
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      // Assert
      expect(screen.getByText("85.5%")).toBeInTheDocument();
      expect(screen.getByText("70.0%")).toBeInTheDocument();
      expect(screen.getByText("4.5")).toBeInTheDocument();
      expect(screen.getByText("3.5")).toBeInTheDocument();
    });

    it("ワーカーが0件の場合、メッセージが表示される", () => {
      // Arrange
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(<WorkerTable workers={[]} onEdit={onEdit} onDelete={onDelete} />);

      // Assert
      expect(
        screen.getByText("ワーカーが登録されていません。")
      ).toBeInTheDocument();
    });
  });

  describe("操作テスト", () => {
    it("編集ボタンをクリックするとonEdit関数が呼ばれる", async () => {
      // Arrange
      const user = userEvent.setup();
      const onEdit = jest.fn();
      const onDelete = jest.fn();

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      const editButtons = screen.getAllByRole("button", { name: "編集" });
      await user.click(editButtons[0]);

      // Assert
      await waitFor(() => {
        expect(onEdit).toHaveBeenCalledTimes(1);
        expect(onEdit).toHaveBeenCalledWith(mockWorkers[0]);
      });
    });

    it("削除ボタンをクリックすると確認ダイアログが表示される", async () => {
      // Arrange
      const user = userEvent.setup();
      const onEdit = jest.fn();
      const onDelete = jest.fn();
      window.confirm = jest.fn(() => true);

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      const deleteButtons = screen.getAllByRole("button", { name: "削除" });
      await user.click(deleteButtons[0]);

      // Assert
      await waitFor(() => {
        expect(window.confirm).toHaveBeenCalledWith(
          "このワーカーを削除してもよろしいですか？"
        );
        expect(onDelete).toHaveBeenCalledTimes(1);
        expect(onDelete).toHaveBeenCalledWith(mockWorkers[0]);
      });
    });

    it("削除確認ダイアログでキャンセルした場合、onDelete関数は呼ばれない", async () => {
      // Arrange
      const user = userEvent.setup();
      const onEdit = jest.fn();
      const onDelete = jest.fn();
      window.confirm = jest.fn(() => false);

      // Act
      render(
        <WorkerTable workers={mockWorkers} onEdit={onEdit} onDelete={onDelete} />
      );

      const deleteButtons = screen.getAllByRole("button", { name: "削除" });
      await user.click(deleteButtons[0]);

      // Assert
      await waitFor(() => {
        expect(window.confirm).toHaveBeenCalled();
        expect(onDelete).not.toHaveBeenCalled();
      });
    });
  });
});
