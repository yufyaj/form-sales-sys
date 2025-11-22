/**
 * ワーカーフォームコンポーネント
 *
 * React Hook Form + Zod によるバリデーション
 */

"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Worker,
  WorkerStatus,
  SkillLevel,
  WorkerStatusLabel,
  SkillLevelLabel,
  WorkerCreateRequest,
  WorkerUpdateRequest,
} from "@/types/worker";
import { Button } from "@/components/ui/Button";

// Zodスキーマ定義
const workerFormSchema = z.object({
  userId: z
    .number({
      required_error: "ユーザーIDは必須です",
      invalid_type_error: "ユーザーIDは数値である必要があります",
    })
    .int("ユーザーIDは整数である必要があります")
    .positive("ユーザーIDは正の数である必要があります"),
  status: z.nativeEnum(WorkerStatus, {
    required_error: "ステータスは必須です",
  }),
  skillLevel: z.nativeEnum(SkillLevel).nullable().optional(),
  experienceMonths: z
    .number({
      invalid_type_error: "経験月数は数値である必要があります",
    })
    .int("経験月数は整数である必要があります")
    .min(0, "経験月数は0以上である必要があります")
    .nullable()
    .optional(),
  specialties: z.string().max(500, "専門分野は500文字以内である必要があります").nullable().optional(),
  maxTasksPerDay: z
    .number({
      invalid_type_error: "1日の最大タスク数は数値である必要があります",
    })
    .int("1日の最大タスク数は整数である必要があります")
    .min(0, "1日の最大タスク数は0以上である必要があります")
    .nullable()
    .optional(),
  availableHoursPerWeek: z
    .number({
      invalid_type_error: "週間稼働可能時間は数値である必要があります",
    })
    .int("週間稼働可能時間は整数である必要があります")
    .min(0, "週間稼働可能時間は0以上である必要があります")
    .nullable()
    .optional(),
  notes: z.string().max(1000, "メモは1000文字以内である必要があります").nullable().optional(),
});

// 更新用スキーマ（userIdが不要）
const workerUpdateFormSchema = workerFormSchema.omit({ userId: true });

type WorkerFormData = z.infer<typeof workerFormSchema>;
type WorkerUpdateFormData = z.infer<typeof workerUpdateFormSchema>;

interface WorkerFormProps {
  worker?: Worker;
  onSubmit: (data: WorkerCreateRequest | WorkerUpdateRequest) => void;
  onCancel: () => void;
}

export function WorkerForm({ worker, onSubmit, onCancel }: WorkerFormProps) {
  const isEditMode = !!worker;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<WorkerFormData | WorkerUpdateFormData>({
    resolver: zodResolver(isEditMode ? workerUpdateFormSchema : workerFormSchema),
    defaultValues: isEditMode
      ? {
          status: worker.status,
          skillLevel: worker.skillLevel,
          experienceMonths: worker.experienceMonths,
          specialties: worker.specialties,
          maxTasksPerDay: worker.maxTasksPerDay,
          availableHoursPerWeek: worker.availableHoursPerWeek,
          notes: worker.notes,
        }
      : {
          status: WorkerStatus.PENDING,
          skillLevel: null,
          experienceMonths: null,
          specialties: null,
          maxTasksPerDay: null,
          availableHoursPerWeek: null,
          notes: null,
        },
  });

  const onSubmitHandler = (data: WorkerFormData | WorkerUpdateFormData) => {
    // 空文字列をnullに変換
    const processedData = {
      ...data,
      specialties: data.specialties || null,
      notes: data.notes || null,
      experienceMonths: data.experienceMonths || null,
      maxTasksPerDay: data.maxTasksPerDay || null,
      availableHoursPerWeek: data.availableHoursPerWeek || null,
    };

    onSubmit(processedData as WorkerCreateRequest | WorkerUpdateRequest);
  };

  return (
    <form
      role="form"
      onSubmit={handleSubmit(onSubmitHandler)}
      className="space-y-6"
    >
      {/* ユーザーID（新規作成時のみ） */}
      {!isEditMode && (
        <div>
          <label
            htmlFor="userId"
            className="block text-sm font-medium text-gray-700"
          >
            ユーザーID
          </label>
          <input
            id="userId"
            type="number"
            {...register("userId", { valueAsNumber: true })}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
          {errors.userId && (
            <p className="mt-1 text-sm text-red-600">{errors.userId.message}</p>
          )}
        </div>
      )}

      {/* ステータス */}
      <div>
        <label
          htmlFor="status"
          className="block text-sm font-medium text-gray-700"
        >
          ステータス
        </label>
        <select
          id="status"
          {...register("status")}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          {Object.entries(WorkerStatusLabel).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        {errors.status && (
          <p className="mt-1 text-sm text-red-600">{errors.status.message}</p>
        )}
      </div>

      {/* スキルレベル */}
      <div>
        <label
          htmlFor="skillLevel"
          className="block text-sm font-medium text-gray-700"
        >
          スキルレベル
        </label>
        <select
          id="skillLevel"
          {...register("skillLevel")}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        >
          <option value="">選択してください</option>
          {Object.entries(SkillLevelLabel).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        {errors.skillLevel && (
          <p className="mt-1 text-sm text-red-600">
            {errors.skillLevel.message}
          </p>
        )}
      </div>

      {/* 経験月数 */}
      <div>
        <label
          htmlFor="experienceMonths"
          className="block text-sm font-medium text-gray-700"
        >
          経験月数
        </label>
        <input
          id="experienceMonths"
          type="number"
          {...register("experienceMonths", { valueAsNumber: true })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.experienceMonths && (
          <p className="mt-1 text-sm text-red-600">
            {errors.experienceMonths.message}
          </p>
        )}
      </div>

      {/* 専門分野 */}
      <div>
        <label
          htmlFor="specialties"
          className="block text-sm font-medium text-gray-700"
        >
          専門分野
        </label>
        <textarea
          id="specialties"
          {...register("specialties")}
          rows={3}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.specialties && (
          <p className="mt-1 text-sm text-red-600">
            {errors.specialties.message}
          </p>
        )}
      </div>

      {/* 1日の最大タスク数 */}
      <div>
        <label
          htmlFor="maxTasksPerDay"
          className="block text-sm font-medium text-gray-700"
        >
          1日の最大タスク数
        </label>
        <input
          id="maxTasksPerDay"
          type="number"
          {...register("maxTasksPerDay", { valueAsNumber: true })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.maxTasksPerDay && (
          <p className="mt-1 text-sm text-red-600">
            {errors.maxTasksPerDay.message}
          </p>
        )}
      </div>

      {/* 週間稼働可能時間 */}
      <div>
        <label
          htmlFor="availableHoursPerWeek"
          className="block text-sm font-medium text-gray-700"
        >
          週間稼働可能時間
        </label>
        <input
          id="availableHoursPerWeek"
          type="number"
          {...register("availableHoursPerWeek", { valueAsNumber: true })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.availableHoursPerWeek && (
          <p className="mt-1 text-sm text-red-600">
            {errors.availableHoursPerWeek.message}
          </p>
        )}
      </div>

      {/* メモ */}
      <div>
        <label
          htmlFor="notes"
          className="block text-sm font-medium text-gray-700"
        >
          メモ
        </label>
        <textarea
          id="notes"
          {...register("notes")}
          rows={4}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
        />
        {errors.notes && (
          <p className="mt-1 text-sm text-red-600">{errors.notes.message}</p>
        )}
      </div>

      {/* ボタン */}
      <div className="flex justify-end space-x-3">
        <Button type="button" variant="outline" onClick={onCancel}>
          キャンセル
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting
            ? "送信中..."
            : isEditMode
            ? "更新"
            : "登録"}
        </Button>
      </div>
    </form>
  );
}
