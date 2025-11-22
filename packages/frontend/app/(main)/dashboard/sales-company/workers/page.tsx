/**
 * ワーカー管理ページ
 *
 * 営業支援会社のワーカー一覧表示と管理機能を提供
 */

"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";
import { useRouter } from "next/navigation";
import { WorkerTable } from "@/components/features/worker/WorkerTable";
import { WorkerForm } from "@/components/features/worker/WorkerForm";
import { Button } from "@/components/ui/Button";
import {
  fetchWorkers,
  createWorker,
  updateWorker,
  deleteWorker,
} from "@/lib/workerApi";
import type {
  Worker,
  WorkerCreateRequest,
  WorkerUpdateRequest,
} from "@/types/worker";

/**
 * ダイアログモード
 */
type DialogMode = "create" | "edit" | null;

export default function WorkersPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [dialogMode, setDialogMode] = useState<DialogMode>(null);
  const [selectedWorker, setSelectedWorker] = useState<Worker | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ワーカー一覧を取得
  const {
    data: workersData,
    isLoading: workersLoading,
    error: workersError,
  } = useQuery({
    queryKey: ["workers"],
    queryFn: () => fetchWorkers(),
    enabled: !authLoading && !!user,
  });

  // ワーカー作成ミューテーション
  const createMutation = useMutation({
    mutationFn: createWorker,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workers"] });
      setDialogMode(null);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // ワーカー更新ミューテーション
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: WorkerUpdateRequest }) =>
      updateWorker(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workers"] });
      setDialogMode(null);
      setSelectedWorker(null);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // ワーカー削除ミューテーション
  const deleteMutation = useMutation({
    mutationFn: deleteWorker,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workers"] });
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
    },
  });

  // ハンドラー関数
  const handleCreate = () => {
    setDialogMode("create");
    setSelectedWorker(null);
    setError(null);
  };

  const handleEdit = (worker: Worker) => {
    setDialogMode("edit");
    setSelectedWorker(worker);
    setError(null);
  };

  const handleDelete = (worker: Worker) => {
    deleteMutation.mutate(worker.id);
  };

  const handleSubmit = (
    data: WorkerCreateRequest | WorkerUpdateRequest
  ) => {
    if (dialogMode === "create") {
      createMutation.mutate(data as WorkerCreateRequest);
    } else if (dialogMode === "edit" && selectedWorker) {
      updateMutation.mutate({
        id: selectedWorker.id,
        data: data as WorkerUpdateRequest,
      });
    }
  };

  const handleCancel = () => {
    setDialogMode(null);
    setSelectedWorker(null);
    setError(null);
  };

  // ローディング中
  if (authLoading || workersLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラー
  if (workersError) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <p className="text-sm text-red-800">
          ワーカー情報の取得に失敗しました: {workersError.message}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ワーカー管理</h1>
          <p className="mt-1 text-sm text-gray-600">
            ワーカーの登録・編集・削除ができます。
          </p>
        </div>
        <Button onClick={handleCreate}>新規登録</Button>
      </div>

      {/* エラーメッセージ */}
      {error && (
        <div className="rounded-md bg-red-50 p-4" role="alert">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* ワーカー一覧テーブル */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <WorkerTable
          workers={workersData?.workers || []}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </div>

      {/* フォームダイアログ */}
      {dialogMode && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              {dialogMode === "create" ? "ワーカー新規登録" : "ワーカー編集"}
            </h2>
            <WorkerForm
              worker={selectedWorker || undefined}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
            />
          </div>
        </div>
      )}
    </div>
  );
}
