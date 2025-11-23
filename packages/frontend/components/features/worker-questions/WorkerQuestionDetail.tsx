/**
 * ワーカー質問詳細コンポーネント
 *
 * 質問の詳細情報を表示し、回答フォームを提供
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  WorkerQuestion,
  QuestionStatusLabel,
  QuestionPriorityLabel,
  QuestionStatusColor,
  QuestionPriorityColor,
} from "@/types/workerQuestion";
import { maskWorkerId, formatDateTime } from "@/lib/formatters";
import { Button } from "@/components/ui/Button";
import AnswerForm from "./AnswerForm";

interface WorkerQuestionDetailProps {
  question: WorkerQuestion;
  onUpdate: (updatedQuestion: WorkerQuestion) => void;
}

export default function WorkerQuestionDetail({
  question,
  onUpdate,
}: WorkerQuestionDetailProps) {
  const router = useRouter();
  const [showAnswerForm, setShowAnswerForm] = useState(!question.answer);

  /**
   * 回答送信成功時のコールバック
   */
  const handleAnswerSuccess = (updatedQuestion: WorkerQuestion) => {
    onUpdate(updatedQuestion);
    setShowAnswerForm(false);
  };

  /**
   * 一覧に戻る
   */
  const handleBack = () => {
    router.push("/dashboard/sales-company/worker-questions");
  };

  return (
    <div className="space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <Button onClick={handleBack} variant="outline" size="sm">
          ← 一覧に戻る
        </Button>
        <div className="flex gap-2">
          <span
            className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
              QuestionStatusColor[question.status]
            }`}
          >
            {QuestionStatusLabel[question.status]}
          </span>
          <span
            className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${
              QuestionPriorityColor[question.priority]
            }`}
          >
            {QuestionPriorityLabel[question.priority]}
          </span>
        </div>
      </div>

      {/* 質問詳細 */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {question.title}
          </h2>
          <div className="mt-2 flex flex-wrap gap-4 text-sm text-gray-500">
            <div>
              <span className="font-medium">質問ID:</span> {question.id}
            </div>
            <div>
              <span className="font-medium">ワーカー:</span>{" "}
              {maskWorkerId(question.workerId)}
            </div>
            <div>
              <span className="font-medium">作成日時:</span>{" "}
              {formatDateTime(question.createdAt)}
            </div>
          </div>
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <dt className="text-sm font-medium text-gray-500">質問内容</dt>
              <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
                {question.content}
              </dd>
            </div>

            {question.tags && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">タグ</dt>
                <dd className="mt-1 text-sm text-gray-900">{question.tags}</dd>
              </div>
            )}

            {question.clientOrganizationId && (
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  顧客組織ID
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {question.clientOrganizationId}
                </dd>
              </div>
            )}

            {question.internalNotes && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">
                  内部メモ
                </dt>
                <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap bg-yellow-50 p-3 rounded">
                  {question.internalNotes}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* 回答セクション */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">回答</h3>
          {question.answer && !showAnswerForm && (
            <Button
              onClick={() => setShowAnswerForm(true)}
              variant="outline"
              size="sm"
            >
              回答を編集
            </Button>
          )}
        </div>
        <div className="border-t border-gray-200 px-4 py-5 sm:px-6">
          {question.answer && !showAnswerForm ? (
            <div className="space-y-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">回答内容</dt>
                <dd className="mt-1 text-sm text-gray-900 whitespace-pre-wrap bg-green-50 p-4 rounded">
                  {question.answer}
                </dd>
              </div>
              {question.answeredAt && (
                <div className="flex gap-4 text-sm text-gray-500">
                  <div>
                    <span className="font-medium">回答日時:</span>{" "}
                    {formatDateTime(question.answeredAt)}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <AnswerForm
              questionId={question.id}
              existingAnswer={question.answer}
              onSuccess={handleAnswerSuccess}
              onCancel={
                question.answer ? () => setShowAnswerForm(false) : undefined
              }
            />
          )}
        </div>
      </div>
    </div>
  );
}
