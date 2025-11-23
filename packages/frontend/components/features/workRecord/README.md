# 作業記録UIコンポーネント

Phase5要件に基づいた作業記録UIの実装です。

## 📋 概要

ワーカーが作業を完了した際に、送信済み・送信不可を記録するためのUIコンポーネント群です。

### 実装機能

- ✅ 送信済みボタン
- ✅ 送信不可ボタン
- ✅ 作業日時表示（自動記録）
- ✅ 送信制御UI（禁止時間帯の警告・ボタン無効化）

## 🗂️ ファイル構成

```
components/features/workRecord/
├── WorkRecordUI.tsx          # メインコンポーネント（統合UI）
├── WorkRecordButtons.tsx     # 送信済み・送信不可ボタン
├── WorkTimeDisplay.tsx       # 作業時間表示
└── README.md                 # このファイル

hooks/
└── useProhibitedTimeCheck.ts # 禁止時間帯チェックフック

lib/actions/
└── workRecord.ts             # 作業記録用Server Actions

types/
└── workRecord.ts             # 作業記録関連の型定義

__tests__/components/features/workRecord/
├── WorkTimeDisplay.test.tsx  # 作業時間表示のテスト
└── WorkRecordButtons.test.tsx # ボタンのテスト
```

## 🚀 使用方法

### 基本的な使用例

```tsx
import WorkRecordUI from '@/components/features/workRecord/WorkRecordUI'

function AssignmentDetailPage() {
  return (
    <WorkRecordUI
      assignmentId={1}
      listId={10}
      onRecordCreated={() => {
        // 記録完了後の処理（例: リスト再読み込み）
        console.log('作業記録が作成されました')
      }}
    />
  )
}
```

### 個別コンポーネントの使用

必要に応じて個別のコンポーネントを使用することも可能です。

#### 作業時間表示のみ

```tsx
import WorkTimeDisplay from '@/components/features/workRecord/WorkTimeDisplay'

<WorkTimeDisplay
  startedAt="2025-11-23T10:00:00Z"
  updateInterval={1000} // 1秒ごとに更新（デフォルト）
/>
```

#### ボタンのみ

```tsx
import WorkRecordButtons from '@/components/features/workRecord/WorkRecordButtons'
import { useProhibitedTimeCheck } from '@/hooks/useProhibitedTimeCheck'

function CustomUI() {
  const prohibitedCheck = useProhibitedTimeCheck(noSendSettings)

  return (
    <WorkRecordButtons
      assignmentId={1}
      prohibitedCheck={prohibitedCheck}
      startedAt="2025-11-23T10:00:00Z"
      onRecordCreated={() => {}}
    />
  )
}
```

## 🔧 カスタムフック

### useProhibitedTimeCheck

禁止時間帯を判定するカスタムフックです。

```tsx
import { useProhibitedTimeCheck } from '@/hooks/useProhibitedTimeCheck'

const prohibitedCheck = useProhibitedTimeCheck(
  noSendSettings,  // NoSendSetting[]
  60000            // チェック間隔（ミリ秒、デフォルト: 60秒）
)

// 結果
prohibitedCheck.isProhibited      // boolean: 禁止時間帯かどうか
prohibitedCheck.reasons           // string[]: 禁止理由の配列
prohibitedCheck.nextAllowedTime   // Date: 次回送信可能時刻
```

## 🔒 セキュリティ

### クライアント側

- 禁止時間帯チェックはUI表示用のみ
- 実際の送信可否はサーバー側で再検証

### サーバー側（Server Actions）

- Next.js Server ActionsによるCSRF保護
- Cookie認証トークンによる認可
- エラー情報の適切な隠蔽

## 📝 型定義

### WorkRecordStatus

```typescript
enum WorkRecordStatus {
  SENT = 'sent',           // 送信済み
  CANNOT_SEND = 'cannot_send'  // 送信不可
}
```

### ProhibitedTimeCheckResult

```typescript
interface ProhibitedTimeCheckResult {
  isProhibited: boolean      // 現在禁止時間帯かどうか
  reasons: string[]          // 禁止理由
  nextAllowedTime?: Date     // 次回許可時刻
}
```

## 🧪 テスト

### テスト実行

```bash
cd packages/frontend

# すべてのworkRecord関連テストを実行
npm test -- workRecord

# 特定のテストファイルのみ
npm test -- WorkTimeDisplay.test.tsx
npm test -- WorkRecordButtons.test.tsx
```

### テストカバレッジ

- ✅ 作業時間表示のレンダリング
- ✅ 経過時間のリアルタイム更新
- ✅ ボタンの有効/無効化
- ✅ 禁止時間帯の警告表示
- ✅ 送信済み記録の作成
- ✅ 送信不可記録の作成
- ✅ エラーハンドリング

## 🎨 スタイリング

Tailwind CSSを使用しています。カスタマイズが必要な場合は、各コンポーネントのクラス名を調整してください。

```tsx
// 例: ボタンの幅を調整
<WorkRecordButtons
  className="max-w-2xl mx-auto"
  // ...
/>
```

## 📚 関連ドキュメント

- [フロントエンド開発規約](../../../ai-docs/skills/frontend.md)
- [バックエンドAPI仕様](../../../packages/backend/README.md)
- [送信禁止設定](../noSendSettings/README.md)

## 🐛 トラブルシューティング

### 禁止時間帯が正しく判定されない

1. `noSendSettings`が正しく取得されているか確認
2. 設定の`is_enabled`が`true`になっているか確認
3. ブラウザの時刻設定が正しいか確認

### 作業記録が作成されない

1. バックエンドAPIが起動しているか確認
2. 認証トークンが有効か確認
3. ブラウザのコンソールでエラーログを確認

### テストが失敗する

1. `jest.useFakeTimers()`が正しく設定されているか確認
2. モックが正しく設定されているか確認
3. `npm test -- --clearCache`でキャッシュをクリア

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. ブラウザのコンソールログ
2. サーバー側のログ（`packages/backend/logs/`）
3. ネットワークタブでAPIリクエストの詳細

それでも解決しない場合は、開発チームにお問い合わせください。
