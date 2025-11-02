# フォーム営業支援システム - フロントエンド

Next.js 16 + TypeScript + Tailwind CSSを使用したフロントエンドアプリケーション

## 技術スタック

- **フレームワーク**: Next.js 16 (App Router)
- **言語**: TypeScript
- **スタイリング**: Tailwind CSS
- **フォーム管理**: React Hook Form + Zod
- **認証**: NextAuth.js v5
- **テスト**:
  - 単体テスト: Jest + React Testing Library
  - E2Eテスト: Playwright

## セットアップ

### 1. 依存関係のインストール

```bash
npm install
```

### 2. 環境変数の設定

`.env.local`ファイルを作成し、以下の環境変数を設定してください：

```bash
cp .env.local.example .env.local
```

```.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

アプリケーションは [http://localhost:3000](http://localhost:3000) で起動します。

## 利用可能なスクリプト

- `npm run dev` - 開発サーバーの起動
- `npm run build` - プロダクションビルド
- `npm start` - プロダクションサーバーの起動
- `npm run lint` - ESLintによるコードチェック
- `npm test` - 単体テストの実行
- `npm run test:watch` - 単体テストのウォッチモード
- `npm run test:e2e` - E2Eテストの実行

## ディレクトリ構造

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # 認証関連ページ（ログイン前）
│   │   ├── login/
│   │   └── reset-password/
│   ├── api/               # API Routes
│   └── layout.tsx         # ルートレイアウト
├── components/            # Reactコンポーネント
│   ├── ui/               # UI部品（Button, Input, Card等）
│   └── features/         # 機能別コンポーネント
│       └── auth/         # 認証関連コンポーネント
├── lib/                   # ライブラリ・ユーティリティ
│   ├── api.ts            # APIクライアント
│   ├── utils.ts          # 汎用ヘルパー関数
│   └── validations/      # バリデーションスキーマ
├── types/                 # TypeScript型定義
├── __tests__/            # 単体テスト
└── e2e/                   # E2Eテスト
```

## 実装済み機能

### Phase 1: ログイン画面

- ✅ ログインフォーム
  - メールアドレス入力
  - パスワード入力
  - クライアントサイドバリデーション（Zod）
  - エラー表示

- ✅ パスワードリセット画面
  - メールアドレス入力
  - リセットリンク送信機能
  - 成功/エラーメッセージ表示

## テスト

### 単体テスト

```bash
npm test
```

- LoginFormコンポーネントのテスト
- ResetPasswordFormコンポーネントのテスト
- バリデーションロジックのテスト

### E2Eテスト

```bash
npm run test:e2e
```

- ログインフローのE2Eテスト
- パスワードリセットフローのE2Eテスト
- フォームバリデーションのテスト

## コーディング規約

- **変数・関数**: `camelCase`
- **コンポーネント**: `PascalCase`
- **定数**: `UPPER_SNAKE_CASE`
- **ファイル名**: コンポーネントは`PascalCase.tsx`、その他は`camelCase.ts`

## TDD開発フロー

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通す最小限の実装を行う
3. **Refactor**: 実装をクリーンにし、可読性と保守性を向上させる

## セキュリティ

- ユーザー入力は必ずバリデーションを実施
- 機密情報は`.env.local`で管理
- 本番環境では常時HTTPS使用
- 認証トークンはhttpOnlyクッキーで管理（推奨）

## ライセンス

ISC
