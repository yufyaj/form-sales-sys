'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Select } from '@/components/ui/Select'
import { Textarea } from '@/components/ui/Textarea'
import { workRecordFormSchema, type WorkRecordFormData } from '@/lib/validations/workRecord'
import { ClipboardCheck } from 'lucide-react'

/**
 * 作業記録フォームのプロパティ
 */
export interface WorkRecordFormProps {
  /**
   * 割り当てID
   */
  assignmentId: string
  /**
   * ワーカーID
   */
  workerId: number
  /**
   * 送信ハンドラー
   */
  onSubmit: (data: WorkRecordFormData) => void | Promise<void>
  /**
   * 送信中フラグ
   */
  isSubmitting?: boolean
}

/**
 * 作業記録フォームコンポーネント
 *
 * ワーカーが作業結果（送信完了 or 送信不可）を記録するためのフォームです。
 */
export function WorkRecordForm({
  assignmentId,
  workerId,
  onSubmit,
  isSubmitting = false,
}: WorkRecordFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<WorkRecordFormData>({
    resolver: zodResolver(workRecordFormSchema),
    defaultValues: {
      status: 'sent',
    },
  })

  const status = watch('status')

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ClipboardCheck className="h-5 w-5" />
          作業記録
        </CardTitle>
        <CardDescription>作業結果を記録してください</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* 作業ステータス */}
          <Select
            label="作業ステータス"
            options={[
              { value: 'sent', label: '送信完了' },
              { value: 'cannot_send', label: '送信不可' },
            ]}
            error={errors.status?.message}
            {...register('status')}
          />

          {/* 送信不可理由（送信不可の場合のみ表示） */}
          {status === 'cannot_send' && (
            <Select
              label="送信不可理由"
              placeholder="理由を選択してください"
              options={[
                { value: 1, label: '問い合わせフォームが見つからない' },
                { value: 2, label: 'フォームが機能していない' },
                { value: 3, label: '営業お断りと明記されている' },
                { value: 4, label: 'その他' },
              ]}
              error={errors.cannotSendReasonId?.message}
              {...register('cannotSendReasonId', { valueAsNumber: true })}
            />
          )}

          {/* 備考 */}
          <Textarea
            label="備考"
            placeholder="補足情報があれば入力してください"
            rows={4}
            error={errors.notes?.message}
            {...register('notes')}
          />

          {/* 送信ボタン */}
          <div className="flex justify-end">
            <Button type="submit" isLoading={isSubmitting} className="min-w-[120px]">
              記録を保存
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
