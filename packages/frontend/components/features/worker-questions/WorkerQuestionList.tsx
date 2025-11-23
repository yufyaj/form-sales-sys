/**
 * ワーカー質問一覧コンポーネント
 *
 * ワーカーからの質問を一覧表示し、フィルタリング・回答機能を提供
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  WorkerQuestion,
  QuestionStatus,
  QuestionPriority,
  QuestionStatusLabel,
  QuestionPriorityLabel,
  QuestionStatusColor,
  QuestionPriorityColor,
} from "@/types/workerQuestion";
import { fetchWorkerQuestions } from "@/lib/workerQuestionApi";
import { Button } from "@/components/ui/Button";
import Badge from "@/components/ui/Badge";

/**
 * 質問フィルター
 */
interface QuestionFilters {
  status?: QuestionStatus;
  priority?: QuestionPriority;
}

export default function WorkerQuestionList() {
  const router = useRouter();
  const [questions, setQuestions] = useState<WorkerQuestion[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<QuestionFilters>({});
  const [currentPage, setCurrentPage] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const ITEMS_PER_PAGE = 20;

  /**
   * 質問一覧を取得
   */
  const loadQuestions = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetchWorkerQuestions({
        status: filters.status,
        priority: filters.priority,
        skip: currentPage * ITEMS_PER_PAGE,
        limit: ITEMS_PER_PAGE,
      });

      setQuestions(response.questions);
      setTotalCount(response.total);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "質問の取得に失敗しました"
      );
    } finally {
      setIsLoading(false);
    }
  };

  // 初回読み込みとフィルター変更時に質問を取得
  useEffect(() => {
    loadQuestions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, currentPage]);

  /**
   * 質問詳細ページへ遷移
   */
  const handleViewQuestion = (questionId: number) => {
    router.push(
      `/dashboard/sales-company/worker-questions/${questionId}`
    );
  };

  /**
   * ステータスフィルター変更
   */
  const handleStatusFilterChange = (status: QuestionStatus | undefined) => {
    setFilters({ ...filters, status });
    setCurrentPage(0); // ページをリセット
  };

  /**
   * 優先度フィルター変更
   */
  const handlePriorityFilterChange = (
    priority: QuestionPriority | undefined
  ) => {
    setFilters({ ...filters, priority });
    setCurrentPage(0); // ページをリセット
  };

  /**
   * フィルタークリア
   */
  const handleClearFilters = () => {
    setFilters({});
    setCurrentPage(0);
  };

  /**
   * 日時フォーマット
   */
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("ja-JP", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // ローディング表示
  if (isLoading && questions.length === 0) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-600"></div>
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    );
  }

  // エラー表示
  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">エラー</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
            <div className="mt-4">
              <Button onClick={loadQuestions} variant="outline" size="sm">
                再読み込み
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const totalPages = Math.ceil(totalCount / ITEMS_PER_PAGE);

  return (
    <div className="space-y-6">
      {/* フィルター */}
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ステータス
            </label>
            <select
              value={filters.status || ""}
              onChange={(e) =>
                handleStatusFilterChange(
                  e.target.value ? (e.target.value as QuestionStatus) : undefined
                )
              }
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">全て</option>
              {Object.entries(QuestionStatusLabel).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              優先度
            </label>
            <select
              value={filters.priority || ""}
              onChange={(e) =>
                handlePriorityFilterChange(
                  e.target.value
                    ? (e.target.value as QuestionPriority)
                    : undefined
                )
              }
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">全て</option>
              {Object.entries(QuestionPriorityLabel).map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <Button onClick={handleClearFilters} variant="outline" size="sm">
              フィルタークリア
            </Button>
          </div>
        </div>

        <div className="mt-4 text-sm text-gray-600">
          {totalCount}件の質問が見つかりました
        </div>
      </div>

      {/* 質問一覧 */}
      {questions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">質問が登録されていません。</p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {questions.map((question) => (
              <li key={question.id}>
                <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            QuestionStatusColor[question.status]
                          }`}
                        >
                          {QuestionStatusLabel[question.status]}
                        </span>
                        <span
                          className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                            QuestionPriorityColor[question.priority]
                          }`}
                        >
                          {QuestionPriorityLabel[question.priority]}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {question.title}
                      </p>
                      <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                        {question.content}
                      </p>
                      <div className="mt-2 flex items-center text-xs text-gray-500">
                        <span>
                          ワーカーID: {question.workerId}
                        </span>
                        <span className="mx-2">•</span>
                        <span>{formatDate(question.createdAt)}</span>
                        {question.answeredAt && (
                          <>
                            <span className="mx-2">•</span>
                            <span>回答日時: {formatDate(question.answeredAt)}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <Button
                        onClick={() => handleViewQuestion(question.id)}
                        variant="outline"
                        size="sm"
                      >
                        {question.answer ? "詳細を見る" : "回答する"}
                      </Button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ページネーション */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between bg-white px-4 py-3 sm:px-6 rounded-lg shadow">
          <div className="flex flex-1 justify-between sm:hidden">
            <Button
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 0}
              variant="outline"
              size="sm"
            >
              前へ
            </Button>
            <Button
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage >= totalPages - 1}
              variant="outline"
              size="sm"
            >
              次へ
            </Button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                <span className="font-medium">{currentPage * ITEMS_PER_PAGE + 1}</span>
                {" - "}
                <span className="font-medium">
                  {Math.min((currentPage + 1) * ITEMS_PER_PAGE, totalCount)}
                </span>
                {" / "}
                <span className="font-medium">{totalCount}</span>
                {" 件"}
              </p>
            </div>
            <div>
              <nav className="inline-flex -space-x-px rounded-md shadow-sm">
                <Button
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 0}
                  variant="outline"
                  size="sm"
                  className="rounded-l-md"
                >
                  前へ
                </Button>
                <Button
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage >= totalPages - 1}
                  variant="outline"
                  size="sm"
                  className="rounded-r-md"
                >
                  次へ
                </Button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
