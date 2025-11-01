# フォーム営業支援システム バックエンド

## 概要

フォーム営業支援システムのバックエンドAPIです。FastAPI + SQLAlchemy 2.0 + PostgreSQLを使用した、クリーンアーキテクチャに基づいた設計となっています。

## 技術スタック

| カテゴリ | 技術 | バージョン |
|---------|------|-----------|
| 言語 | Python | 3.11+ |
| Webフレームワーク | FastAPI | ^0.115.0 |
| ASGIサーバー | Uvicorn | ^0.32.0 |
| ORM | SQLAlchemy | ^2.0.35 |
| マイグレーション | Alembic | ^1.14.0 |
| バリデーション | Pydantic | ^2.10.0 |
| データベース | PostgreSQL | 16+ |
| DB接続 | asyncpg | ^0.30.0 |
| 認証 | python-jose | ^3.3.0 |
| パスワード | passlib[bcrypt] | ^1.7.4 |
| テスト | pytest | ^8.3.0 |
| テストDB | testcontainers | ^4.9.0 |

## ディレクトリ構成

```
packages/backend/
├── src/
│   ├── app/                    # Presentation Layer (FastAPI)
│   │   ├── api/                # APIエンドポイント
│   │   ├── core/               # 設定、DBセッション、セキュリティ
│   │   └── main.py             # FastAPIアプリケーション
│   │
│   ├── domain/                 # Domain Layer
│   │   ├── entities/           # ドメインエンティティ
│   │   └── interfaces/         # リポジトリインターフェース
│   │
│   ├── application/            # Application Layer
│   │   ├── use_cases/          # ユースケース
│   │   ├── services/           # アプリケーションサービス
│   │   └── schemas/            # DTOスキーマ
│   │
│   └── infrastructure/         # Infrastructure Layer
│       ├── persistence/
│       │   ├── models/         # SQLAlchemyモデル
│       │   └── repositories/   # リポジトリ実装
│       └── external/           # 外部サービス連携
│
├── tests/
│   ├── unit/                   # 単体テスト
│   └── integration/            # 結合テスト
│
├── alembic/                    # マイグレーション
│   └── versions/               # マイグレーションファイル
│
├── pyproject.toml              # Poetry設定
├── alembic.ini                 # Alembic設定
└── .env.example                # 環境変数サンプル
```

## Phase 1: データベーススキーマ設計

### 実装済みテーブル

#### 1. organizations（組織テーブル）
- 営業支援会社と顧客企業の両方を管理
- マルチテナント対応の基盤となるテーブル
- 親子関係をサポート（顧客企業 → 営業支援会社）

**カラム:**
- `id`: 主キー
- `name`: 組織名
- `type`: 組織タイプ（sales_support/client）
- `parent_organization_id`: 親組織ID（顧客企業の場合）
- `email`, `phone`, `address`, `description`: オプション情報
- `created_at`, `updated_at`, `deleted_at`: タイムスタンプ

#### 2. users（ユーザーテーブル）
- 全ロール（営業支援会社、顧客、ワーカー）共通のユーザー情報
- 認証情報を含む
- organization_idによるマルチテナント分離

**カラム:**
- `id`: 主キー
- `organization_id`: 所属組織ID（外部キー）
- `email`: メールアドレス（ログインID、一意）
- `hashed_password`: ハッシュ化パスワード
- `full_name`: 氏名
- `phone`, `avatar_url`, `description`: オプション情報
- `is_active`, `is_email_verified`: アカウント状態
- `created_at`, `updated_at`, `deleted_at`: タイムスタンプ

#### 3. roles（ロールテーブル）
- システム全体のロール定義
- 基本ロール: sales_support（営業支援会社）、client（顧客）、worker（ワーカー）

**カラム:**
- `id`: 主キー
- `name`: ロール名（一意）
- `display_name`: 表示名
- `description`: 説明
- `created_at`, `updated_at`: タイムスタンプ

#### 4. permissions（権限テーブル）
- リソースとアクションの組み合わせで権限を定義
- 例: project:create, list:read, worker:update

**カラム:**
- `id`: 主キー
- `resource`: リソース名（例: project, list, worker）
- `action`: アクション名（例: create, read, update, delete）
- `description`: 説明
- `created_at`, `updated_at`: タイムスタンプ

#### 5. user_roles（ユーザー・ロール中間テーブル）
- ユーザーとロールの多対多リレーション

**カラム:**
- `id`: 主キー
- `user_id`: ユーザーID（外部キー）
- `role_id`: ロールID（外部キー）
- `created_at`, `updated_at`: タイムスタンプ

#### 6. role_permissions（ロール・権限中間テーブル）
- ロールと権限の多対多リレーション

**カラム:**
- `id`: 主キー
- `role_id`: ロールID（外部キー）
- `permission_id`: 権限ID（外部キー）
- `created_at`, `updated_at`: タイムスタンプ

### マルチテナント設計

**テナントID列方式**を採用しています：

- すべてのデータは`organization_id`によって分離
- 営業支援会社と顧客企業間のクロス分析が可能
- 実装・運用がシンプル
- PostgreSQL Row Level Security (RLS)で安全性確保可能

### SQLAlchemy 2.0の型ヒント

最新のSQLAlchemy 2.0の型ヒント機能を使用しています：

```python
from sqlalchemy.orm import Mapped, mapped_column

class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))

    # リレーションシップも型ヒント付き
    organization: Mapped["Organization"] = relationship(...)
```

## セットアップ

### 前提条件

- Python 3.11以上
- Poetry
- Docker（テスト実行時にPostgreSQLコンテナを使用）

### インストール

```bash
cd packages/backend

# 依存関係のインストール
poetry install

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してデータベース接続情報などを設定
```

### データベースマイグレーション

```bash
# マイグレーションの実行
poetry run alembic upgrade head

# マイグレーションの作成（モデル変更時）
poetry run alembic revision --autogenerate -m "変更内容"

# マイグレーションのロールバック
poetry run alembic downgrade -1
```

## テスト実行

```bash
# すべてのテストを実行
poetry run pytest

# カバレッジ付きでテスト実行
poetry run pytest --cov=src --cov-report=html

# 特定のテストファイルのみ実行
poetry run pytest tests/integration/persistence/test_models.py

# テストの詳細表示
poetry run pytest -v
```

### テスト戦略

- **testcontainers**を使用して実際のPostgreSQLコンテナでテスト
- 各テストは独立したトランザクション内で実行され、自動的にロールバック
- TDDサイクル（Red → Green → Refactor）を厳守

## 開発規約

詳細は[ai-docs/skills/backend.md](../../ai-docs/skills/backend.md)を参照してください。

### 主な規約

- **TDD（テスト駆動開発）**: 必ずテストを先に書く
- **クリーンアーキテクチャ**: 依存関係の方向を厳守
- **型ヒント**: Python 3.10+の型ヒントを積極的に使用
- **コメント**: 日本語で「なぜ」を説明
- **命名規則**: snake_case（変数・関数）、PascalCase（クラス）

## セキュリティ

- パスワードは必ずpasslib + bcryptでハッシュ化
- SQLインジェクション対策: ORMによるパラメータ化クエリ
- 入力バリデーション: Pydanticモデルで厳格に検証
- 環境変数: .envで管理し、リポジトリにコミットしない
- HTTPS: 本番環境では必須

## 次のステップ

Phase 1完了後は、以下の順序で実装を進めます：

1. **認証機能の実装** (Phase 1.2)
   - ユーザー登録API
   - ログインAPI（JWT認証）
   - パスワードリセット機能

2. **ユーザー管理API** (Phase 1.3)
   - ユーザーCRUD API
   - ロール管理
   - 組織管理

3. **認可機能の実装** (Phase 1.4)
   - ロールベースアクセス制御（RBAC）
   - ミドルウェア実装

## ライセンス

MIT License
