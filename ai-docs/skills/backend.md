# フォーム営業支援システム バックエンド開発規約

## 1. 概要

本ドキュメントは、フォーム営業支援システムのバックエンド開発におけるディレクトリ構成（クリーンアーキテクチャ）、コーディング規約、テスト戦略を定義するものです。

### 1.1. 基本原則

* **TDD (テスト駆動開発) サイクル（厳守）:**
    1.  **Red**: 失敗するテストを先に書く。
    2.  **Green**: テストを通す最小限の実装を行う。
    3.  **Refactor**: 実装をクリーンにし、可読性と保守性を向上させる。
* **クリーンアーキテクチャ**: 依存関係の方向（外側から内側へ）を厳守し、ビジネスロジック（ドメイン）をインフラストラクチャから分離します。
* **可読性優先**: 常に読みやすく、理解しやすいコードを目指します。
* **KISS原則 (Keep It Simple, Stupid)**: シンプルな設計を維持します。
* **DRY原則 (Don't Repeat Yourself)**: 重複するコードを排除します。
* **SOLID原則**: 特に単一責任の原則 (SRP) と依存性逆転の原則 (DIP) を重視します。**各関数・クラス・モジュールのスコープは常に最小限に保ち、一つのことだけを行うように設計します。**

### 1.2. セキュリティ基本要件

* **パスワード**: `passlib` などのライブラリを使用し、必ずハッシュ化して保存します。
* **SQLインジェクション**: SQLAlchemyなどのORMを使用し、クエリは常にパラメータ化します。生のSQL文字列の連結は厳禁です。
* **ユーザー入力**: FastAPIのPydanticモデルで、API境界にて厳格にバリデーションします。
* **機密情報**: `.env` ファイルで管理し、リポジトリにはコミットしません。
* **通信**: 本番環境では常時HTTPSを使用します。

### 1.3. コメント規約

* **言語**: 日本語で記述します。
* **内容**: 「何を」ではなく、「なぜ」その実装が必要なのか（ビジネスロジックの背景、技術的決定の理由）を説明します。
* **型ヒント**: Python 3.10+ の型ヒントを積極的に使用し、コメントでの型記述（`# type: ...`）は避けます。
* **TODO**: `# TODO: [担当者名 or 空欄] 説明` の形式で記述します。

## 2. バックエンド (Python + FastAPI)

### 2.1. ディレクトリ構成 (`packages/backend/`)

クリーンアーキテクチャの原則に基づいた構成です。

```

packages/backend/
├── src/
│   ├── app/                 \# FastAPIアプリ, ルーター (4. Presentation)
│   │   ├── api/             \# APIエンドポイント (ルーター)
│   │   ├── core/            \# 設定, DBセッション, セキュリティ
│   │   └── main.py          \# FastAPIアプリケーションインスタンス
│   │
│   ├── domain/              \# 1. Domain Layer ( Entities / Interfaces )
│   │   ├── entities/        \# コアなビジネスモデル (Pydantic or Dataclasses)
│   │   └── interfaces/      \# 抽象リポジトリ (例: IProjectRepository)
│   │
│   ├── application/         \# 2. Application Layer ( Use Cases )
│   │   ├── use\_cases/       \# ユースケース実装 (例: CreateProjectUseCase)
│   │   ├── services/        \# アプリケーションサービス (ドメインロジックの調整)
│   │   └── schemas/         \# API送受信用DTO (Pydanticモデル)
│   │
│   └── infrastructure/      \# 3. Infrastructure Layer ( Frameworks / DB )
│       ├── persistence/     \# DB永続化の実装
│       │   ├── models/        \# SQLAlchemy DBモデル (テーブル定義)
│       │   └── repositories/  \# リポジトリインターフェースの実装
│       └── external/        \# 外部サービス (メール送信など)
│
├── tests/                   \# Pytestディレクトリ
│   ├── unit/                \# 単体テスト (依存関係はモック)
│   │   ├── domain/
│   │   └── application/
│   └── integration/         \# 結合テスト (DB含む)
│       ├── api/             \# API E2Eテスト
│       └── persistence/     \# DBリポジトリテスト
│
├── .env                     \# 環境変数 (Git管理外)
├── poetry.lock              \# (or requirements.txt)
└── pyproject.toml           \# (or setup.cfg)

```

### 2.2. コーディング規約 (Backend)

* **変数・関数・メソッド**: `snake_case` (例: `get_project_list`)
* **クラス**: `PascalCase` (例: `ProjectRepository`)
* **定数**: `UPPER_SNAKE_CASE` (例: `MAX_LIST_ITEMS`)
* **ファイル名**: `snake_case.py`
* **フォーマッタ**: `Black` の使用を推奨します。
* **リンター**: `Ruff` または `Flake8` の使用を推奨します。

### 2.3. テスト戦略 (Backend)

#### 単体テスト (Pytest)

* **配置**: `tests/unit/` 配下に、`src/` に対応する構造で配置します。
* **命名**: `test_*.py` ファイル、`test_...` 関数。
* **TDDサイクル**:
    1.  **Red**: ユースケースやドメインロジックの仕様に基づき、失敗するテスト（例: `test_create_project_success`）を記述します。`Infrastructure` 層はモックします。
    2.  **Green**: テストが通る最小限のロジックを `Application` 層や `Domain` 層に実装します。
    3.  **Refactor**: リファクタリングします。
* **パターン**: Arrange-Act-Assert (AAA) パターンを遵守します。

#### 結合テスト (Pytest + PostgreSQL)

* **配置**: `tests/integration/`
* **データベース**:
    * **インメモリPostgreSQL**: `testing.postgresql` ライブラリなどを利用し、各テスト実行時に独立した一時的なPostgreSQLデータベースをメモリ上（または一時ディレクトリ）に構築します。
    * **フィクスチャ**: Pytestのフィクスチャ（`pytest.fixture`）を使用し、テスト用のDBセッションや初期データをセットアップします。
* **TDDサイクル**:
    1.  **Red**: APIエンドポイントやDBリポジトリの仕様に基づき、失敗するテスト（例: `test_project_repository_create_and_get`）を、**実際のDB（インメモリ）** を使って記述します。
    2.  **Green**: `Infrastructure` 層（リポジトリ実装）や `Presentation` 層（APIルーター）を実装し、テストを通します。
    3.  **Refactor**: リファクタリングします。

## 3. エラーハンドリング (Backend)

* **例外処理**:
    * `Domain` 層、`Application` 層では、ビジネスルール違反（例: `ProjectNotFoundException`）としてカスタム例外を送出します。
    * `Presentation` 層（APIルーター）では、**個別のエンドポイントでの `try...except` を極力避け**、FastAPIの**グローバル例外ハンドラ（`@app.exception_handler`）** を使用してカスタム例外（`ProjectNotFoundException` など）を一元的にキャッチします。これにより、ビジネスロジックの例外を適切なHTTPエラーレスポンス（例: 404）に変換する処理を集約し、コードの重複を排除します。
    * **やむを得ず `try...except` を使用する場合、そのスコープ（ブロック）は例外が発生しうる箇所のみを囲むよう最小限に留め**、正常系のロジックとエラー処理を明確に分離します。

* **ログ**: 重要な処理の境界やエラー発生時には、十分なコンテキスト情報（例: ユーザーID、リクエストID）を含むログを出力します。