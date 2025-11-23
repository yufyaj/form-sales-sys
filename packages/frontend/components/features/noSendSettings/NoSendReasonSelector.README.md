# NoSendReasonSelector コンポーネント

送信不可理由を複数選択できるチェックボックス形式のUIコンポーネントです。

## 機能

- ✅ チェックボックス形式の複数選択UI
- ✅ デフォルト理由とカスタム理由の区別表示
- ✅ 全選択/全解除機能
- ✅ React Hook Form統合対応
- ✅ Zodバリデーション対応
- ✅ アクセシビリティ対応（ARIA属性）
- ✅ 無効化状態のサポート
- ✅ エラーメッセージ表示

## インストール

このコンポーネントは既にプロジェクトに含まれています。

## 基本的な使い方

```tsx
import NoSendReasonSelector from '@/components/features/noSendSettings/NoSendReasonSelector'
import { DEFAULT_NO_SEND_REASONS } from '@/types/noSendReason'

function MyComponent() {
  const [selectedReasons, setSelectedReasons] = useState<string[]>([])

  return (
    <NoSendReasonSelector
      reasons={DEFAULT_NO_SEND_REASONS}
      value={selectedReasons}
      onChange={setSelectedReasons}
      label="送信不可理由を選択"
      showSelectAll
    />
  )
}
```

## React Hook Formとの統合

```tsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import NoSendReasonSelector from '@/components/features/noSendSettings/NoSendReasonSelector'
import { DEFAULT_NO_SEND_REASONS } from '@/types/noSendReason'

const schema = z.object({
  reasons: z.array(z.string()).min(1, '少なくとも1つ選択してください'),
})

function MyForm() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { reasons: [] },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="reasons"
        control={control}
        render={({ field }) => (
          <NoSendReasonSelector
            reasons={DEFAULT_NO_SEND_REASONS}
            value={field.value}
            onChange={field.onChange}
            error={errors.reasons?.message}
            showSelectAll
          />
        )}
      />
    </form>
  )
}
```

## カスタム理由の追加

```tsx
import { DEFAULT_NO_SEND_REASONS, NoSendReason } from '@/types/noSendReason'

const customReasons: NoSendReason[] = [
  ...DEFAULT_NO_SEND_REASONS,
  { id: 'custom-1', label: '社内ブラックリスト', isDefault: false },
  { id: 'custom-2', label: '競合他社', isDefault: false },
]

<NoSendReasonSelector
  reasons={customReasons}
  value={selectedReasons}
  onChange={setSelectedReasons}
/>
```

## Props

| プロパティ | 型 | 必須 | デフォルト | 説明 |
|----------|------|------|-----------|------|
| `reasons` | `NoSendReason[]` | ✅ | - | 表示する理由のリスト |
| `value` | `string[]` | ✅ | - | 選択されている理由のIDリスト |
| `onChange` | `(value: string[]) => void` | ✅ | - | 選択状態変更時のコールバック |
| `label` | `string` | ❌ | - | コンポーネントのラベル |
| `error` | `string` | ❌ | - | エラーメッセージ |
| `disabled` | `boolean` | ❌ | `false` | 無効化状態 |
| `showSelectAll` | `boolean` | ❌ | `false` | 全選択/全解除ボタンの表示 |

## 型定義

### NoSendReason

```typescript
interface NoSendReason {
  id: string        // 理由の一意識別子
  label: string     // 表示ラベル
  isDefault: boolean // デフォルト理由かどうか
}
```

### デフォルト理由

以下の5つのデフォルト理由が用意されています：

1. メールアドレスが無効
2. バウンス履歴あり
3. 配信停止済み
4. 重複データ
5. スパム報告履歴

## テスト

```bash
# 単体テストの実行
npx jest __tests__/components/features/noSendSettings/NoSendReasonSelector.test.tsx

# 全てのnoSendSettings関連テストの実行
npx jest __tests__/components/features/noSendSettings/
```

## アクセシビリティ

- `role="checkbox"` による適切なロール設定
- `checked` 属性による選択状態の明示
- `disabled` 属性による無効化状態の明示
- `role="alert"` によるエラーメッセージの読み上げ
- フォーカス管理とキーボード操作のサポート

## スタイリング

Tailwind CSSを使用しています。カスタマイズする場合は、`cn`ユーティリティを使用してクラスを追加できます。

## 実装例

詳細な実装例は `NoSendReasonSelector.example.tsx` を参照してください。

## ファイル構成

```
packages/frontend/
├── types/
│   └── noSendReason.ts                    # 型定義
├── components/features/noSendSettings/
│   ├── NoSendReasonSelector.tsx           # コンポーネント本体
│   ├── NoSendReasonSelector.example.tsx   # 使用例
│   └── NoSendReasonSelector.README.md     # このファイル
└── __tests__/components/features/noSendSettings/
    └── NoSendReasonSelector.test.tsx      # テストコード
```

## 関連コンポーネント

- `DayOfWeekSelector` - 曜日選択コンポーネント
- `TimeRangeInput` - 時間範囲入力コンポーネント
- `DateInput` - 日付入力コンポーネント

## ライセンス

このコンポーネントはプロジェクトのライセンスに従います。
