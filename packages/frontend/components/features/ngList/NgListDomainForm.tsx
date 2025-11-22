'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card } from '@/components/ui/Card'
import {
  ngListDomainFormSchema,
  type NgListDomainFormData,
} from '@/lib/validations/ngListDomain'
import { createNgListDomain } from '@/lib/api/ngListDomains'
import { transitions } from '@/lib/motion'

interface NgListDomainFormProps {
  listId: number
  onSuccess?: () => void
  onCancel?: () => void
}

/**
 * NGリストドメイン登録・編集フォームコンポーネント
 *
 * useFieldArrayを使用した動的なドメイン入力フィールド管理
 */
export function NgListDomainForm({
  listId,
  onSuccess,
  onCancel,
}: NgListDomainFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<NgListDomainFormData>({
    resolver: zodResolver(ngListDomainFormSchema),
    mode: 'onBlur',
    defaultValues: {
      domains: [{ domain: '', memo: '' }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'domains',
  })

  /**
   * フォーム送信ハンドラ
   */
  const onSubmit = async (data: NgListDomainFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      // 各ドメインを順次登録
      for (const domainData of data.domains) {
        await createNgListDomain({
          listId,
          domain: domainData.domain,
          memo: domainData.memo || null,
        })
      }

      // 成功時のコールバック
      onSuccess?.()
    } catch (err) {
      console.error('NGドメイン登録エラー:', err)
      setError(
        err instanceof Error
          ? err.message
          : 'NGドメインの登録に失敗しました。もう一度お試しください。'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * ドメインフィールドを追加
   */
  const handleAddDomain = () => {
    append({ domain: '', memo: '' })
  }

  /**
   * ドメインフィールドを削除
   */
  const handleRemoveDomain = (index: number) => {
    if (fields.length > 1) {
      remove(index)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* グローバルエラー表示 */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-md bg-destructive/10 p-4 text-sm text-destructive"
          role="alert"
        >
          {error}
        </motion.div>
      )}

      {/* フォームレベルのエラー（重複チェックなど） */}
      {errors.domains?.root && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-md bg-destructive/10 p-4 text-sm text-destructive"
          role="alert"
        >
          {errors.domains.root.message}
        </motion.div>
      )}

      {/* ドメイン入力フィールド一覧 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">NGドメイン</h3>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddDomain}
            disabled={isSubmitting}
          >
            <Plus className="h-4 w-4" />
            ドメイン追加
          </Button>
        </div>

        <AnimatePresence mode="popLayout">
          {fields.map((field, index) => (
            <motion.div
              key={field.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={transitions.fast}
              layout
            >
              <Card className="p-4">
                <div className="space-y-4">
                  {/* ドメイン入力 */}
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        {...register(`domains.${index}.domain`)}
                        label="ドメイン"
                        placeholder="例: example.com, *.example.com"
                        error={errors.domains?.[index]?.domain?.message}
                        disabled={isSubmitting}
                        autoComplete="off"
                      />
                      <p className="mt-1 text-xs text-muted-foreground">
                        ワイルドカード対応: *.example.com
                      </p>
                    </div>

                    {/* 削除ボタン */}
                    {fields.length > 1 && (
                      <div className="flex items-end pb-2">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemoveDomain(index)}
                          disabled={isSubmitting}
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* メモ入力 */}
                  <Input
                    {...register(`domains.${index}.memo`)}
                    label="メモ（任意）"
                    placeholder="例: 競合他社のため送信禁止"
                    error={errors.domains?.[index]?.memo?.message}
                    disabled={isSubmitting}
                    maxLength={500}
                  />
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* アクションボタン */}
      <div className="flex justify-end gap-3">
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
        <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting}>
          {isSubmitting ? '登録中...' : 'NGドメインを登録'}
        </Button>
      </div>
    </form>
  )
}
