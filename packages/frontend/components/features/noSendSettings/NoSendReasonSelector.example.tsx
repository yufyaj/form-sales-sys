/**
 * NoSendReasonSelector React Hook Form統合例
 *
 * このファイルは実装例として提供されています。
 * 実際の使用時には、プロジェクトのニーズに合わせて調整してください。
 */

'use client'

import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import NoSendReasonSelector from './NoSendReasonSelector'
import { DEFAULT_NO_SEND_REASONS, NoSendReason } from '@/types/noSendReason'

// バリデーションスキーマ
const noSendReasonFormSchema = z.object({
  reasons: z
    .array(z.string())
    .min(1, '少なくとも1つの理由を選択してください')
    .max(10, '選択できる理由は最大10個までです'),
})

type NoSendReasonFormData = z.infer<typeof noSendReasonFormSchema>

/**
 * 送信不可理由選択フォームの実装例
 */
export default function NoSendReasonFormExample() {
  // カスタム理由を含む理由リストの例
  const reasons: NoSendReason[] = [
    ...DEFAULT_NO_SEND_REASONS,
    { id: 'custom-1', label: '社内ブラックリスト', isDefault: false },
    { id: 'custom-2', label: '競合他社', isDefault: false },
  ]

  // React Hook Formのセットアップ
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<NoSendReasonFormData>({
    resolver: zodResolver(noSendReasonFormSchema),
    defaultValues: {
      reasons: [],
    },
  })

  // フォーム送信処理
  const onSubmit = (data: NoSendReasonFormData) => {
    console.log('選択された理由:', data.reasons)
    // ここで実際のAPI呼び出しなどを行う
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">送信不可理由の設定</h2>

      <div className="mb-6">
        <Controller
          name="reasons"
          control={control}
          render={({ field }) => (
            <NoSendReasonSelector
              reasons={reasons}
              value={field.value}
              onChange={field.onChange}
              label="送信不可理由を選択してください"
              error={errors.reasons?.message}
              showSelectAll
            />
          )}
        />
      </div>

      <div className="flex gap-4">
        <button
          type="submit"
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          保存
        </button>
        <button
          type="button"
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          onClick={() => console.log('キャンセル')}
        >
          キャンセル
        </button>
      </div>
    </form>
  )
}

/**
 * 無効化状態の実装例
 */
export function NoSendReasonFormDisabledExample() {
  const {
    control,
    formState: { errors },
  } = useForm<NoSendReasonFormData>({
    resolver: zodResolver(noSendReasonFormSchema),
    defaultValues: {
      reasons: ['invalid-email', 'bounced'],
    },
  })

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">送信不可理由（無効化状態）</h2>

      <Controller
        name="reasons"
        control={control}
        render={({ field }) => (
          <NoSendReasonSelector
            reasons={DEFAULT_NO_SEND_REASONS}
            value={field.value}
            onChange={field.onChange}
            label="現在の設定（編集不可）"
            error={errors.reasons?.message}
            disabled
          />
        )}
      />
    </div>
  )
}

/**
 * 簡易的な使用例（React Hook Formなし）
 */
export function SimpleNoSendReasonExample() {
  const [selectedReasons, setSelectedReasons] = React.useState<string[]>([])

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">送信不可理由選択（簡易版）</h2>

      <NoSendReasonSelector
        reasons={DEFAULT_NO_SEND_REASONS}
        value={selectedReasons}
        onChange={setSelectedReasons}
        label="送信不可理由"
        showSelectAll
      />

      <div className="mt-6">
        <p className="text-sm text-gray-600">
          選択された理由: {selectedReasons.length}個
        </p>
        {selectedReasons.length > 0 && (
          <ul className="mt-2 text-sm text-gray-700">
            {selectedReasons.map((id) => (
              <li key={id}>• {id}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
