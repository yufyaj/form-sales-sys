/**
 * ワーカー一覧テーブルコンポーネント
 *
 * TDDサイクルに従って実装
 */

"use client";

import { Worker, WorkerStatusLabel, SkillLevelLabel } from "@/types/worker";
import Badge from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

interface WorkerTableProps {
  workers: Worker[];
  onEdit: (worker: Worker) => void;
  onDelete: (worker: Worker) => void;
}

/**
 * ワーカーステータスに応じたバッジバリアントを返す
 */
function getStatusBadgeVariant(
  status: Worker["status"]
): "success" | "warning" | "default" {
  switch (status) {
    case "active":
      return "success";
    case "pending":
      return "warning";
    default:
      return "default";
  }
}

export function WorkerTable({ workers, onEdit, onDelete }: WorkerTableProps) {
  const handleDelete = (worker: Worker) => {
    if (!confirm("このワーカーを削除してもよろしいですか？")) {
      return;
    }
    onDelete(worker);
  };

  if (workers.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">ワーカーが登録されていません。</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              ID
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              ステータス
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              スキルレベル
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              専門分野
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              経験月数
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              完了タスク数
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              成功率
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              評価
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
            >
              操作
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {workers.map((worker) => (
            <tr key={worker.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <Badge variant={getStatusBadgeVariant(worker.status)}>
                  {WorkerStatusLabel[worker.status]}
                </Badge>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.skillLevel ? SkillLevelLabel[worker.skillLevel] : "-"}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.specialties || "-"}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.experienceMonths !== null
                  ? `${worker.experienceMonths}ヶ月`
                  : "-"}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.completedTasksCount}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.successRate !== null
                  ? `${worker.successRate.toFixed(1)}%`
                  : "-"}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {worker.rating !== null ? worker.rating.toFixed(1) : "-"}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onEdit(worker)}
                >
                  編集
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleDelete(worker)}
                >
                  削除
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
