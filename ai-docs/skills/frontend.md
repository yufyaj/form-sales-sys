# フォーム営業支援システム フロントエンド開発規約

## 1. 概要

本ドキュメントは、フォーム営業支援システムのフロントエンド開発におけるディレクトリ構成、コーディング規約、テスト戦略を定義するものです。

### 1.1. 基本原則

* **TDD (テスト駆動開発) サイクル（厳守）:**

  1. **Red**: 失敗するテストを先に書く。

  2. **Green**: テストを通す最小限の実装を行う。

  3. **Refactor**: 実装をクリーンにし、可読性と保守性を向上させる。

* **可読性優先**: 常に読みやすく、理解しやすいコードを目指します。

* **KISS原則 (Keep It Simple, Stupid)**: シンプルな設計を維持します。

* **DRY原則 (Don't Repeat Yourself)**: 重複するコードを排除します。

* **SOLID原則**: 特に単一責任の原則 (Single Responsibility Principle) を重視します。

### 1.2. セキュリティ基本要件

* **ユーザー入力**: フロントエンド側でも必ずバリデーションを実施します。

* **機密情報**: `.env.local` ファイルで管理し、絶対にハードコーディングしません。

* **通信**: 本番環境では常時HTTPSを使用します。

### 1.3. コメント規約

* **言語**: 日本語で記述します。

* **内容**: 「何を」しているか（コードが示すこと）ではなく、「なぜ」その実装が必要なのかを説明します。

* **必須箇所**: 複雑なロジック、ワークアラウンド（回避策）には必ずコメントを残します。

* **TODO**: `# TODO: [担当者名 or 空欄] 説明（例: # TODO: ページGpaginationの実装）` の形式で記述します。

## 2. フロントエンド (TypeScript + Next.js 16 / App Router)

### 2.1. ディレクトリ構成 (`packages/frontend/`)

Next.js 16のApp Routerを前提とした構成です。

```

packages/frontend/
├── e2e/                     \# Playwright E2Eテスト
│   └── ...                  \# (テストシナリオファイル \*.spec.ts)
│
├── src/
│   ├── app/                 \# Next.js App Router (ルーティング)
│   │   ├── (auth)/            \# 認証関連ページ（ログイン前）
│   │   │   └── login/
│   │   │       └── ...
│   │   ├── (main)/            \# 認証後メインレイアウト
│   │   │   ├── dashboard/     \# ダッシュボード
│   │   │   │   └── ...
│   │   │   ├── projects/      \# プロジェクト関連
│   │   │   │   └── [projectId]/
│   │   │   │       ├── lists/
│   │   │   │       │   └── [listId]/
│   │   │   │       │       └── ...
│   │   │   │       ├── analytics/
│   │   │   │       │   └── ...
│   │   │   │       └── ...
│   │   │   └── settings/      \# 設定ページ
│   │   │       └── ...
│   │   ├── api/                 \# API Routes (BFF用)
│   │   │   └── ...
│   │   └── ...                \# (グローバルレイアウト、ページなど)
│   │
│   ├── components/            \# 共通コンポーネント
│   │   ├── ui/                \# UI部品（Button, Input, Cardなど）
│   │   ├── common/            \# 共通レイアウト部品（Header, Sidebar）
│   │   └── features/            \# 特定機能ドメインのコンポーネント
│   │       ├── project/
│   │       └── list/
│   │
│   ├── contexts/              \# グローバルステート管理 (React Context)
│   │
│   ├── hooks/                 \# カスタムフック
│   │
│   ├── lib/                   \# ライブラリ、ユーティリティ
│   │   ├── api.ts             \# (バックエンドAPIクライアント)
│   │   └── utils.ts           \# (汎用ヘルパー関数)
│   │
│   ├── types/                 \# グローバルな型定義
│   │
│   └── **tests**/             \# 単体・結合テスト (Jest / RTL)
│       ├── components/
│       │   └── features/
│       │       └── project/
│       └── hooks/
│
├── .env.local               \# 環境変数 (Git管理外)
├── next.config.mjs          \# Next.js設定
└── tsconfig.json            \# TypeScript設定

```

### 2.2. コーディング規約 (Frontend)

* **変数・関数**: `camelCase` (例: `fetchProjects`, `isLoading`)

* **コンポーネント**: `PascalCase` (例: `ProjectCard`)

* **定数**: `UPPER_SNAKE_CASE` (例: `API_BASE_URL`)

* **ファイル名**:

  * コンポーネント (React): `PascalCase.tsx`

  * その他 (フック、型定義など): `camelCase.ts`

* **コンポーネント実装**:

  * 原則としてFunctional ComponentとHooksを使用します。

  * 状態管理は `useState`, `useReducer` を基本とし、広範囲な状態共有が必要な場合のみ `Context` や `Zustand` などを検討します。

* **スタイリング**: Tailwind CSSを優先的に使用します。

### 2.3. テスト戦略 (Frontend)

#### 単体テスト (Jest + React Testing Library)

* **配置**: `src/__tests__/` 配下に、`src/` と同じディレクトリ構造で配置します。

  * **命名**: `*.test.tsx` または `*.test.ts`

  * **TDDサイクル**:

    1. コンポーネントの仕様に基づき、失敗するテスト（例: 特定のテキストが表示されるか、ボタンクリックで関数が呼ばれるか）を記述します。

    2. テストが通る最小限のコンポーネント実装を行います。

    3. リファクタリングします。

  * **パターン**: Arrange-Act-Assert (AAA) パターンを遵守します。

  * **セレクター**: `getByRole`, `getByLabelText` など、ユーザー操作に近いセレクターを優先します。

#### E2Eテスト (Playwright)

* **配置**: `packages/frontend/e2e/`

* **命名**: `*.spec.ts`

* **TDDサイクル**:

  1. ユーザーストーリー（要件）に基づき、失敗するE2Eテストシナリオ（例: ログインフォームに入力し、ダッシュボードに遷移する）を記述します。

  2. テストが通るように、必要なページ、コンポーネント、API接続を（TDDサイクルに従い）実装します。

  3. リファクタリングします。

* **セレクター優先順位**:

  1. `getByRole()`: アクセシビリティ属性（推奨）

  2. `getByLabel()`: フォーム要素

  3. `getByText()`: 表示テキスト

  4. `getByTestId()`: 上記で特定できない場合の最終手段

* **ベストプラクティス**:

  * 各テストは独立させ、`test.beforeEach()` でログイン処理など共通セットアップを行います。

  * Page Object Model (POM) パターンを導入し、セレクターと操作をページごとにカプセル化することを推奨します。

## 3. エラーハンドリング (Frontend)

## 3. エラーハンドリング (Frontend)

* `fetch` ラッパーでレスポンスステータスをチェックし、エラー時は例外をスローします。

* Reactコンポーネントでは Error Boundary を適切に配置し、クラッシュを防ぎます。

* フォーム送信時などは、ユーザーに分かりやすいエラーメッセージを表示します。