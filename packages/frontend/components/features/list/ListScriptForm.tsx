'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Card } from '@/components/ui/Card'
import {
  listScriptFormSchema,
  type ListScriptFormData,
} from '@/lib/validations/listScript'
import { createListScript } from '@/lib/api/listScripts'
import { ApiError } from '@/lib/api-client'
import { transitions } from '@/lib/motion'

interface ListScriptFormProps {
  listId: number
  onSuccess?: () => void
  onCancel?: () => void
}

/**
 * スクリプト登録・編集フォームコンポーネント
 *
 * useFieldArrayを使用した動的なスクリプト入力フィールド管理
 */
export function ListScriptForm({
  listId,
  onSuccess,
  onCancel,
}: ListScriptFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ListScriptFormData>({
    resolver: zodResolver(listScriptFormSchema),
    mode: 'onBlur',
    defaultValues: {
      scripts: [{ title: '', content: '' }],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'scripts',
  })

  /**
   * フォーム送信ハンドラ
   */
  const onSubmit = async (data: ListScriptFormData) => {
    setIsSubmitting(true)
    setError(null)

    try {
      // 各スクリプトを順次登録
      for (const scriptData of data.scripts) {
        await createListScript({
          listId,
          title: scriptData.title,
          content: scriptData.content,
        })
      }

      // 成功時のコールバック
      onSuccess?.()
    } catch (err) {
      // セキュリティのため、開発者用のログのみ詳細エラーを記録
      console.error('スクリプト登録エラー:', err)

      // ユーザー向けには安全なメッセージのみ表示
      let userMessage = 'スクリプトの登録に失敗しました。もう一度お試しください。'

      // ApiErrorの場合は、ステータスコードに応じて適切なメッセージを設定
      if (err instanceof ApiError) {
        if (err.status === 400) {
          userMessage = '入力内容に誤りがあります。入力内容をご確認ください。'
        } else if (err.status === 409) {
          userMessage = 'このスクリプトは既に登録されています。'
        } else if (err.status === 422) {
          userMessage = '入力値の検証に失敗しました。入力内容をご確認ください。'
        } else if (err.status >= 500) {
          userMessage = 'サーバーエラーが発生しました。しばらくしてから再度お試しください。'
        } else if (err.status === 0) {
          userMessage = 'ネットワークエラーが発生しました。インターネット接続をご確認ください。'
        }
      }

      setError(userMessage)
    } finally {
      setIsSubmitting(false)
    }
  }

  /**
   * スクリプトフィールドを追加
   */
  const handleAddScript = () => {
    append({ title: '', content: '' })
  }

  /**
   * スクリプトフィールドを削除
   */
  const handleRemoveScript = (index: number) => {
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
      {errors.scripts?.root && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-md bg-destructive/10 p-4 text-sm text-destructive"
          role="alert"
        >
          {errors.scripts.root.message}
        </motion.div>
      )}

      {/* スクリプト入力フィールド一覧 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">スクリプト</h3>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleAddScript}
            disabled={isSubmitting}
          >
            <Plus className="h-4 w-4" />
            スクリプト追加
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
                  {/* 件名入力 */}
                  <div className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        {...register(`scripts.${index}.title`)}
                        label="件名"
                        placeholder="例: お問い合わせの件について"
                        error={errors.scripts?.[index]?.title?.message}
                        disabled={isSubmitting}
                        autoComplete="off"
                        maxLength={255}
                      />
                    </div>

                    {/* 削除ボタン */}
                    {fields.length > 1 && (
                      <div className="flex items-end pb-2">
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          onClick={() => handleRemoveScript(index)}
                          disabled={isSubmitting}
                          className="text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>

                  {/* 本文入力 */}
                  <Textarea
                    {...register(`scripts.${index}.content`)}
                    label="本文"
                    placeholder="例: お世話になっております。&#10;先日お問い合わせいただいた件についてご連絡いたします。"
                    error={errors.scripts?.[index]?.content?.message}
                    disabled={isSubmitting}
                    rows={8}
                    maxLength={10000}
                  />
                  <p className="mt-1 text-xs text-muted-foreground">
                    改行やタブも使用できます（最大10,000文字）
                  </p>
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
          {isSubmitting ? '登録中...' : 'スクリプトを登録'}
        </Button>
      </div>
    </form>
  )
}
