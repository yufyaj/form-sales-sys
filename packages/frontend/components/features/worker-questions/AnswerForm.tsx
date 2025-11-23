/**
 * 回答フォームコンポーネント
 *
 * React Hook FormとZodを使用したバリデーション付きフォーム
 */

"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { WorkerQuestion } from "@/types/workerQuestion";
import { addAnswerToWorkerQuestion } from "@/lib/workerQuestionApi";
import { Button } from "@/components/ui/Button";

/**
 * 回答フォームのバリデーションスキーマ
 */
const answerSchema = z.object({
  answer: z
    .string()
    .min(1, "回答を入力してください")
    .max(5000, "回答は5000文字以内で入力してください"),
});

type AnswerFormData = z.infer<typeof answerSchema>;

interface AnswerFormProps {
  questionId: number;
  existingAnswer?: string | null;
  onSuccess: (updatedQuestion: WorkerQuestion) => void;
  onCancel?: () => void;
}

export default function AnswerForm({
  questionId,
  existingAnswer,
  onSuccess,
  onCancel,
}: AnswerFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AnswerFormData>({
    resolver: zodResolver(answerSchema),
    defaultValues: {
      answer: existingAnswer || "",
    },
  });

  /**
   * フォーム送信処理
   */
  const onSubmit = async (data: AnswerFormData) => {
    try {
      setIsSubmitting(true);
      setError(null);

      const updatedQuestion = await addAnswerToWorkerQuestion(questionId, {
        answer: data.answer,
      });

      onSuccess(updatedQuestion);
    } catch (err) {
      setError(err instanceof Error ? err.message : "回答の送信に失敗しました");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* エラー表示 */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">エラー</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 回答入力エリア */}
      <div>
        <label
          htmlFor="answer"
          className="block text-sm font-medium text-gray-700"
        >
          回答内容 <span className="text-red-500">*</span>
        </label>
        <textarea
          id="answer"
          rows={10}
          {...register("answer")}
          className={`mt-1 block w-full rounded-md shadow-sm sm:text-sm ${
            errors.answer
              ? "border-red-300 focus:border-red-500 focus:ring-red-500"
              : "border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          }`}
          placeholder="ワーカーへの回答を入力してください..."
          aria-describedby={errors.answer ? "answer-error" : undefined}
          disabled={isSubmitting}
        />
        {errors.answer && (
          <p id="answer-error" className="mt-2 text-sm text-red-600">
            {errors.answer.message}
          </p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          回答はワーカーに表示されます。丁寧で分かりやすい回答を心がけてください。
        </p>
      </div>

      {/* アクションボタン */}
      <div className="flex gap-3">
        <Button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 sm:flex-none"
        >
          {isSubmitting ? (
            <>
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></span>
              送信中...
            </>
          ) : existingAnswer ? (
            "回答を更新"
          ) : (
            "回答を送信"
          )}
        </Button>
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            キャンセル
          </Button>
        )}
      </div>
    </form>
  );
}
