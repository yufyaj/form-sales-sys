# FastAPI + SQLAlchemy 2.0 + Pydantic v2 ベストプラクティス調査レポート

**調査実施日**: 2025年11月22日
**対象プロジェクト**: フォーム営業支援システム バックエンドAPI
**技術スタック**:
- Python: 3.11+ (実行環境: 3.12.11)
- FastAPI: 0.115.14
- SQLAlchemy: 2.0.44
- Pydantic: 2.12.3

---

## 目次

1. [調査概要](#調査概要)
2. [FastAPI 非同期CRUD APIエンドポイント](#1-fastapi-非同期crud-apiエンドポイント)
3. [SQLAlchemy 2.0 非同期セッション管理とリポジトリパターン](#2-sqlalchemy-20-非同期セッション管理とリポジトリパターン)
4. [Pydantic v2 モデルバリデーションとDTO設計](#3-pydantic-v2-モデルバリデーションとdto設計)
5. [クリーンアーキテクチャの実装](#4-クリーンアーキテクチャの実装)
6. [論理削除(Soft Delete)の実装パターン](#5-論理削除soft-deleteの実装パターン)
7. [エンティティとDTOの変換ベストプラクティス](#6-エンティティとdtoの変換ベストプラクティス)
8. [実装推奨事項まとめ](#実装推奨事項まとめ)

---

## 調査概要

本レポートは、2025年11月時点の最新公式ドキュメントとコミュニティベストプラクティスに基づき、FastAPI、SQLAlchemy 2.0、Pydantic v2を使用したRESTful APIの実装方針を調査したものです。

### 調査情報源

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 公式ドキュメント](https://docs.sqlalchemy.org/en/20/)
- [Pydantic 公式ドキュメント](https://docs.pydantic.dev/latest/)
- GitHub公式ディスカッション、最新のコミュニティ記事（2024-2025年）

---

## 1. FastAPI 非同期CRUD APIエンドポイント

### 1.1 async/awaitの使い分け原則

**非同期ルート（`async def`）を使用すべき場合:**
- サードパーティライブラリが `await` をサポートしている
- データベース、外部API、ファイルシステムとの通信が必要
- I/O待機が多い処理

**同期ルート（`def`）を使用すべき場合:**
- ライブラリが `await` 非対応
- ブロッキングI/O操作を含む処理

**重要な公式見解:**
> "If you are using a third party library that communicates with something (a database, an API, the file system, etc.) and doesn't have support for using `await`, then declare your path operation functions with normal `def`."

FastAPIは両方のアプローチを自動最適化します。同期関数は外部スレッドプールで実行されるため、サーバーをブロックしません。

### 1.2 依存性注入（Dependency Injection）のベストプラクティス

#### Dependencies with Yieldパターン

**公式推奨パターン:**

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッション依存性（クリーンアップ付き）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**重要な動作:**
- `yield`より前のコードは、レスポンス生成**前**に実行
- `yield`より後のコードは、レスポンス送信**後**に実行
- `finally`ブロックは例外の有無に関わらず実行される

#### エラーハンドリング

**公式ドキュメントの警告:**
> "If you catch an exception in a dependency with `yield`, unless you are raising another `HTTPException` or similar, you should re-raise the original exception."

カスタム例外をHTTPExceptionに変換する例:

```python
async def get_user_session():
    try:
        yield session
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 型アノテーションの推奨パターン

```python
from typing import Annotated

AsyncDatabaseDependency = Annotated[AsyncSession, Depends(get_db)]

@router.get("/items/")
async def list_items(db: AsyncDatabaseDependency):
    # dbセッションを使用
    pass
```

### 1.3 CRUDエンドポイントの実装パターン

```python
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/items", tags=["items"])

# CREATE
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: AsyncDatabaseDependency,
    current_user: CurrentUserDependency,
) -> ItemResponse:
    use_case = CreateItemUseCase(item_repository)
    entity = await use_case.execute(item_data, current_user.id)
    return ItemResponse.model_validate(entity)

# READ
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: AsyncDatabaseDependency,
    current_user: CurrentUserDependency,
) -> ItemResponse:
    use_case = GetItemUseCase(item_repository)
    entity = await use_case.execute(item_id, current_user.id)
    return ItemResponse.model_validate(entity)

# UPDATE
@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: AsyncDatabaseDependency,
    current_user: CurrentUserDependency,
) -> ItemResponse:
    use_case = UpdateItemUseCase(item_repository)
    entity = await use_case.execute(item_id, item_data, current_user.id)
    return ItemResponse.model_validate(entity)

# DELETE
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncDatabaseDependency,
    current_user: CurrentUserDependency,
) -> None:
    use_case = DeleteItemUseCase(item_repository)
    await use_case.execute(item_id, current_user.id)
```

**ポイント:**
- ステータスコードを明示（201 Created, 204 No Content等）
- `response_model`でレスポンス形式を保証
- 依存性注入でセッション、認証情報を受け取る
- ユースケース層に処理を委譲

---

## 2. SQLAlchemy 2.0 非同期セッション管理とリポジトリパターン

### 2.1 AsyncSessionの基本設定

**必須設定: `expire_on_commit=False`**

公式ドキュメントの重要な指摘:
> "Using async, you cannot lazy load expired attributes after a commit like you would in case of sync code. The default behavior of a SQLAlchemy Session is to expire the attributes of objects in the session after a commit."

**推奨設定:**

```python
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

# エンジン作成
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# セッションファクトリ作成（expire_on_commit=Falseが重要）
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 非同期では必須
    autoflush=False,
    autocommit=False,
)
```

**なぜ`expire_on_commit=False`が必要か:**
- デフォルトではcommit後に属性がexpireされる
- expired属性へのアクセス時、DBから再取得が試みられる
- 非同期環境では「予期しない場所でのI/O」エラーが発生
- `False`にすることで、commit後も属性アクセスが可能

**トレードオフ:**
- 古いデータを扱う可能性が増加
- 必要に応じて`session.refresh()`で明示的に再取得

### 2.2 リポジトリパターンの実装

#### インターフェース定義（Domain層）

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.item_entity import ItemEntity

class IItemRepository(ABC):
    """アイテムリポジトリのインターフェース"""

    @abstractmethod
    async def create(self, entity: ItemEntity) -> ItemEntity:
        """アイテムを作成"""
        pass

    @abstractmethod
    async def find_by_id(self, item_id: int) -> Optional[ItemEntity]:
        """IDでアイテムを取得"""
        pass

    @abstractmethod
    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ItemEntity]:
        """アイテム一覧を取得"""
        pass

    @abstractmethod
    async def update(self, entity: ItemEntity) -> ItemEntity:
        """アイテムを更新"""
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> None:
        """アイテムを削除"""
        pass
```

#### リポジトリ実装（Infrastructure層）

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from domain.interfaces.item_repository import IItemRepository
from domain.entities.item_entity import ItemEntity
from infrastructure.persistence.models.item import ItemModel

class ItemRepository(IItemRepository):
    """アイテムリポジトリの実装"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, entity: ItemEntity) -> ItemEntity:
        """アイテムを作成"""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def find_by_id(self, item_id: int) -> Optional[ItemEntity]:
        """IDでアイテムを取得"""
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ItemEntity]:
        """アイテム一覧を取得"""
        stmt = select(ItemModel).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(m) for m in models]

    async def update(self, entity: ItemEntity) -> ItemEntity:
        """アイテムを更新"""
        stmt = select(ItemModel).where(ItemModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        # エンティティの値でモデルを更新
        model.name = entity.name
        model.description = entity.description
        # ... 他のフィールド

        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, item_id: int) -> None:
        """アイテムを削除"""
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()
        await self._session.delete(model)
        await self._session.flush()

    def _model_to_entity(self, model: ItemModel) -> ItemEntity:
        """モデルをエンティティに変換"""
        return ItemEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: ItemEntity) -> ItemModel:
        """エンティティをモデルに変換"""
        return ItemModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )
```

### 2.3 並行タスク処理での注意点

**公式ドキュメントの警告:**
> "AsyncSession is not safe for use in multiple, concurrent tasks."

**複数タスクを並行実行する場合:**

```python
# ❌ 間違った例
async def process_items():
    async with AsyncSessionLocal() as session:
        # 同じセッションを複数タスクで共有するのはNG
        await asyncio.gather(
            task1(session),
            task2(session),
        )

# ✅ 正しい例
async def process_items():
    # 各タスクに個別のセッションを作成
    await asyncio.gather(
        task1_with_own_session(),
        task2_with_own_session(),
    )

async def task1_with_own_session():
    async with AsyncSessionLocal() as session:
        # このタスク専用のセッション
        pass
```

### 2.4 暗黙的なI/O防止戦略

**問題:**
- 遅延ロード（lazy loading）が非同期環境で問題を起こす

**解決策:**

1. **eager loadingを使用**

```python
from sqlalchemy.orm import selectinload

stmt = (
    select(ItemModel)
    .options(selectinload(ItemModel.tags))  # 関連データを事前ロード
    .where(ItemModel.id == item_id)
)
```

2. **リレーションシップで`lazy="raise"`を設定**

```python
class ItemModel(Base):
    __tablename__ = "items"

    tags = relationship(
        "TagModel",
        lazy="raise",  # 遅延ロードを禁止
        back_populates="item",
    )
```

---

## 3. Pydantic v2 モデルバリデーションとDTO設計

### 3.1 ConfigDictの推奨設定

**基本的なベースDTOクラス:**

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class BaseDTO(BaseModel):
    """全DTOの基底クラス（統一的な設定）"""

    model_config = ConfigDict(
        from_attributes=True,      # ORM変換を有効化（旧orm_mode）
        populate_by_name=True,      # snake_caseとaliasの両方を許可
        str_strip_whitespace=True,  # 文字列の前後空白を自動削除
        extra="forbid",             # 未定義フィールドでエラー（fail fast）
        validate_assignment=True,   # 代入時も検証
    )
```

**各設定の意味:**

- **`from_attributes=True`**: SQLAlchemyモデル等のオブジェクト属性から変換可能に
- **`populate_by_name=True`**: フィールド名とaliasの両方で入力可能
- **`str_strip_whitespace=True`**: 文字列の前後空白を自動削除
- **`extra="forbid"`**: 定義されていないフィールドがあるとエラー（早期発見）
- **`validate_assignment=True`**: オブジェクト作成後の代入時も検証実行

### 3.2 DTOの分類と命名規則

```python
# 1. 作成用DTO（IDなし、必須フィールドのみ）
class ItemCreate(BaseDTO):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# 2. 更新用DTO（全フィールドOptional）
class ItemUpdate(BaseDTO):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

# 3. レスポンス用DTO（IDあり、タイムスタンプあり）
class ItemResponse(BaseDTO):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

# 4. 一覧用DTO（リストとページネーション情報）
class ItemListResponse(BaseDTO):
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int
```

### 3.3 バリデーションメソッド

**Pydantic v2の検証メソッド:**

```python
# 1. 辞書またはオブジェクトから検証
item = ItemResponse.model_validate(item_entity)

# 2. JSON文字列から検証（高速）
item = ItemResponse.model_validate_json(json_string)

# 3. 検証なしで構築（信頼済みデータ）
item = ItemResponse.model_construct(id=1, name="test")
```

**パフォーマンスの重要な指摘:**
> "`model_validate_json()`は内部で検証を行うため、`json.loads()`してから`model_validate()`するより効率的"

### 3.4 ORMオブジェクトからの変換

**from_orm → model_validate への移行**

```python
# Pydantic v1（非推奨）
item_response = ItemResponse.from_orm(item_model)

# Pydantic v2（推奨）
item_response = ItemResponse.model_validate(item_model)
```

**FastAPIでの自動変換:**

```python
@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncDatabaseDependency):
    model = await get_item_from_db(db, item_id)
    # FastAPIが自動的にmodel_validate()を呼び出し、JSONに変換
    return model
```

### 3.5 カスタムバリデーション

```python
from pydantic import field_validator, model_validator

class ItemCreate(BaseDTO):
    name: str
    category: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """名前は空白のみ不可"""
        if not v.strip():
            raise ValueError('名前は空白のみにできません')
        return v.strip()

    @model_validator(mode='after')
    def validate_category_name_combination(self) -> 'ItemCreate':
        """カテゴリと名前の組み合わせを検証"""
        if self.category == 'special' and 'special' not in self.name.lower():
            raise ValueError('specialカテゴリの名前には"special"を含める必要があります')
        return self
```

---

## 4. クリーンアーキテクチャの実装

### 4.1 層の責務と依存関係の方向

```
┌─────────────────────────────────────────────────────┐
│  Presentation Layer (app/api/)                      │
│  - FastAPIルーター、エンドポイント                    │
│  - HTTPリクエスト/レスポンスの処理                    │
└──────────────────┬──────────────────────────────────┘
                   │ 依存
                   ↓
┌─────────────────────────────────────────────────────┐
│  Application Layer (application/)                   │
│  - ユースケース（ビジネスロジックの調整）              │
│  - アプリケーションサービス                           │
│  - DTO（schemas/）                                   │
└──────────────────┬──────────────────────────────────┘
                   │ 依存
                   ↓
┌─────────────────────────────────────────────────────┐
│  Domain Layer (domain/)                             │
│  - エンティティ（ビジネスルール）                      │
│  - インターフェース（抽象リポジトリ）                  │
│  - ドメイン例外                                       │
└──────────────────┬──────────────────────────────────┘
                   ↑ 実装
                   │
┌─────────────────────────────────────────────────────┐
│  Infrastructure Layer (infrastructure/)             │
│  - リポジトリ実装                                     │
│  - SQLAlchemyモデル                                  │
│  - 外部サービス連携                                   │
└─────────────────────────────────────────────────────┘
```

**重要な原則:**
- **依存関係は常に外側から内側へ**
- ドメイン層はインフラストラクチャ層を知らない
- ビジネスロジックはフレームワークから独立

### 4.2 ドメイン層の実装

#### エンティティ（domain/entities/）

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ItemEntity:
    """アイテムエンティティ（ビジネスモデル）"""

    id: Optional[int]
    name: str
    description: Optional[str]
    category: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate_name(self) -> None:
        """名前のビジネスルール検証"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("名前は必須です")
        if len(self.name) > 100:
            raise ValueError("名前は100文字以内にしてください")

    def can_be_deleted(self) -> bool:
        """削除可能かどうかのビジネスルール"""
        # 例: 作成から24時間以内のみ削除可能
        if not self.created_at:
            return False
        elapsed = datetime.now() - self.created_at
        return elapsed.total_seconds() < 86400
```

**ポイント:**
- `dataclass`または`BaseModel`を使用（フレームワーク非依存）
- ビジネスルールをメソッドとして実装
- SQLAlchemyやFastAPIのimportは禁止

#### インターフェース（domain/interfaces/）

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.item_entity import ItemEntity

class IItemRepository(ABC):
    """アイテムリポジトリのインターフェース（抽象化）"""

    @abstractmethod
    async def create(self, entity: ItemEntity) -> ItemEntity:
        pass

    @abstractmethod
    async def find_by_id(self, item_id: int) -> Optional[ItemEntity]:
        pass

    @abstractmethod
    async def update(self, entity: ItemEntity) -> ItemEntity:
        pass

    @abstractmethod
    async def delete(self, item_id: int) -> None:
        pass
```

### 4.3 アプリケーション層の実装

#### ユースケース（application/use_cases/）

```python
from domain.interfaces.item_repository import IItemRepository
from domain.entities.item_entity import ItemEntity
from domain.exceptions import ItemNotFoundException, ValidationException

class CreateItemUseCase:
    """アイテム作成ユースケース"""

    def __init__(self, item_repository: IItemRepository):
        self._repository = item_repository

    async def execute(self, name: str, description: str, user_id: int) -> ItemEntity:
        """アイテムを作成する

        Args:
            name: アイテム名
            description: 説明
            user_id: 作成者ID

        Returns:
            作成されたアイテムエンティティ

        Raises:
            ValidationException: 検証エラー
        """
        # エンティティ作成
        entity = ItemEntity(
            id=None,
            name=name,
            description=description,
            category="default",
        )

        # ビジネスルール検証
        try:
            entity.validate_name()
        except ValueError as e:
            raise ValidationException(str(e))

        # リポジトリで永続化
        created_entity = await self._repository.create(entity)

        return created_entity
```

**ポイント:**
- インターフェースに依存（実装には依存しない）
- ビジネスロジックの調整役
- トランザクション管理は上位層（Presentation層）で実施

### 4.4 インフラストラクチャ層の実装

#### SQLAlchemyモデル（infrastructure/persistence/models/）

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from infrastructure.persistence.models.base import Base

class ItemModel(Base):
    """アイテムテーブルモデル"""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="default")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

### 4.5 プレゼンテーション層の実装

#### ルーター（app/api/items.py）

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from application.schemas.item import ItemCreate, ItemResponse
from application.use_cases.item_use_cases import CreateItemUseCase
from infrastructure.persistence.repositories.item_repository import ItemRepository
from domain.entities.user_entity import UserEntity

router = APIRouter(prefix="/api/items", tags=["items"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserEntity = Depends(get_current_user),
) -> ItemResponse:
    """アイテムを作成"""
    # リポジトリとユースケースのインスタンス化
    repository = ItemRepository(db)
    use_case = CreateItemUseCase(repository)

    # ユースケース実行
    entity = await use_case.execute(
        name=item_data.name,
        description=item_data.description,
        user_id=current_user.id,
    )

    # エンティティをDTOに変換
    return ItemResponse.model_validate(entity)
```

---

## 5. 論理削除(Soft Delete)の実装パターン

### 5.1 SQLAlchemy 2.0での推奨実装

**do_orm_execute() + with_loader_criteria() パターン**

公式ドキュメント:
> "The soft delete pattern in SQLAlchemy is provided by the `do_orm_execute()` event in conjunction with the `with_loader_criteria()` ORM option."

#### Mixinクラスの作成

```python
from sqlalchemy import Column, Boolean
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class SoftDeleteMixin:
    """論理削除用Mixin"""

    is_deleted = Column(Boolean, nullable=False, server_default="0", default=False)
```

#### イベントリスナーの設定

```python
from sqlalchemy import event
from sqlalchemy.orm import Session, ORMExecuteState, with_loader_criteria

def setup_soft_delete_filter(session_factory):
    """論理削除フィルタをセッションに設定"""

    @event.listens_for(session_factory, "do_orm_execute")
    def _add_soft_delete_filtering(execute_state: ORMExecuteState):
        """全SELECTに論理削除フィルタを自動追加"""

        # オプションでフィルタをスキップできるようにする
        skip_filter = execute_state.execution_options.get("include_deleted", False)

        if execute_state.is_select and not skip_filter:
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    SoftDeleteMixin,
                    lambda cls: cls.is_deleted.is_(False),
                    include_aliases=True,
                )
            )

# セッションファクトリに適用
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
setup_soft_delete_filter(AsyncSessionLocal)
```

#### モデルでの使用

```python
from infrastructure.persistence.models.base import Base
from infrastructure.persistence.models.soft_delete_mixin import SoftDeleteMixin

class ItemModel(Base, SoftDeleteMixin):
    """論理削除対応アイテムモデル"""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    # ...
```

#### リポジトリでの削除実装

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ItemRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def soft_delete(self, item_id: int) -> None:
        """論理削除"""
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        model.is_deleted = True
        await self._session.flush()

    async def find_with_deleted(self, item_id: int) -> Optional[ItemModel]:
        """削除済みを含めて検索"""
        stmt = (
            select(ItemModel)
            .where(ItemModel.id == item_id)
            .execution_options(include_deleted=True)  # フィルタをスキップ
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def restore(self, item_id: int) -> None:
        """削除を取り消し"""
        stmt = (
            select(ItemModel)
            .where(ItemModel.id == item_id)
            .execution_options(include_deleted=True)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        model.is_deleted = False
        await self._session.flush()
```

### 5.2 タイムスタンプ型の論理削除

**`is_deleted`の代わりに`deleted_at`を使用するパターン:**

```python
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class SoftDeleteTimestampMixin:
    """タイムスタンプ型論理削除Mixin"""

    deleted_at = Column(DateTime(timezone=True), nullable=True, default=None)

# イベントリスナー
@event.listens_for(session_factory, "do_orm_execute")
def _add_soft_delete_filtering(execute_state: ORMExecuteState):
    skip_filter = execute_state.execution_options.get("include_deleted", False)

    if execute_state.is_select and not skip_filter:
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteTimestampMixin,
                lambda cls: cls.deleted_at.is_(None),  # NULLのみ取得
                include_aliases=True,
            )
        )
```

**メリット:**
- 削除日時が記録される
- 削除されたかどうかの判定が明確（NULL判定）
- 削除履歴の追跡が容易

---

## 6. エンティティとDTOの変換ベストプラクティス

### 6.1 変換の方向性と責務

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   DTO        │ ──────> │   Entity     │ ──────> │  ORM Model   │
│ (Pydantic)   │ <────── │ (Domain)     │ <────── │ (SQLAlchemy) │
└──────────────┘         └──────────────┘         └──────────────┘
 Presentation層          Domain層               Infrastructure層
```

**責務の分担:**
- **Presentation層**: DTOとエンティティ間の変換
- **Infrastructure層**: エンティティとORMモデル間の変換
- **Domain層**: 変換に関与しない（純粋なビジネスロジック）

### 6.2 DTO → エンティティの変換パターン

#### パターン1: 明示的な変換メソッド

```python
# DTO定義（application/schemas/item.py）
from pydantic import BaseModel
from domain.entities.item_entity import ItemEntity

class ItemCreate(BaseModel):
    name: str
    description: Optional[str]
    category: str

    def to_entity(self) -> ItemEntity:
        """DTOをエンティティに変換"""
        return ItemEntity(
            id=None,
            name=self.name,
            description=self.description,
            category=self.category,
        )

# 使用例
@router.post("/")
async def create_item(item_data: ItemCreate):
    entity = item_data.to_entity()
    # ...
```

#### パターン2: ファクトリメソッド

```python
# エンティティ定義（domain/entities/item_entity.py）
@dataclass
class ItemEntity:
    id: Optional[int]
    name: str
    description: Optional[str]

    @classmethod
    def from_create_dto(cls, dto: 'ItemCreate') -> 'ItemEntity':
        """作成DTOからエンティティを生成"""
        return cls(
            id=None,
            name=dto.name,
            description=dto.description,
        )

# 使用例
entity = ItemEntity.from_create_dto(item_data)
```

#### パターン3: マッパークラス（複雑な変換向け）

```python
# application/mappers/item_mapper.py
class ItemMapper:
    """アイテム変換用マッパー"""

    @staticmethod
    def create_dto_to_entity(dto: ItemCreate) -> ItemEntity:
        """作成DTOをエンティティに変換"""
        return ItemEntity(
            id=None,
            name=dto.name.strip(),
            description=dto.description.strip() if dto.description else None,
            category=dto.category,
        )

    @staticmethod
    def entity_to_response_dto(entity: ItemEntity) -> ItemResponse:
        """エンティティをレスポンスDTOに変換"""
        return ItemResponse(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

# 使用例
entity = ItemMapper.create_dto_to_entity(item_data)
response = ItemMapper.entity_to_response_dto(entity)
```

### 6.3 エンティティ → DTOの変換パターン

#### Pydantic v2のmodel_validateを活用

```python
from pydantic import BaseModel, ConfigDict
from domain.entities.item_entity import ItemEntity

class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

# 変換（from_attributesにより自動マッピング）
entity = ItemEntity(id=1, name="test", ...)
response = ItemResponse.model_validate(entity)
```

**ポイント:**
- `from_attributes=True`で属性名が一致していれば自動変換
- フィールド名が異なる場合は`Field(alias=...)`を使用

#### フィールド名が異なる場合

```python
from pydantic import Field

class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    item_id: int = Field(alias="id")  # エンティティのidをitem_idとして公開
    item_name: str = Field(alias="name")

# 変換
response = ItemResponse.model_validate(entity)
# response.item_id == entity.id
```

### 6.4 ORMモデル ↔ エンティティの変換

#### リポジトリ内での変換

```python
class ItemRepository:
    def _model_to_entity(self, model: ItemModel) -> ItemEntity:
        """ORMモデルをエンティティに変換"""
        return ItemEntity(
            id=model.id,
            name=model.name,
            description=model.description,
            category=model.category,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: ItemEntity) -> ItemModel:
        """エンティティをORMモデルに変換（新規作成用）"""
        return ItemModel(
            name=entity.name,
            description=entity.description,
            category=entity.category,
        )

    def _update_model_from_entity(
        self,
        model: ItemModel,
        entity: ItemEntity,
    ) -> None:
        """エンティティの値でORMモデルを更新"""
        model.name = entity.name
        model.description = entity.description
        model.category = entity.category
```

### 6.5 変換時のベストプラクティス

#### 1. 変換ロジックの配置

```python
# ✅ 推奨: 各層の境界で変換
# Presentation層（ルーター）
@router.post("/")
async def create_item(item_data: ItemCreate):
    entity = item_data.to_entity()  # DTO → エンティティ
    created_entity = await use_case.execute(entity)
    return ItemResponse.model_validate(created_entity)  # エンティティ → DTO

# Infrastructure層（リポジトリ）
async def create(self, entity: ItemEntity) -> ItemEntity:
    model = self._entity_to_model(entity)  # エンティティ → モデル
    # ... DB処理
    return self._model_to_entity(model)  # モデル → エンティティ
```

#### 2. 複雑な変換はマッパークラスに集約

```python
# ❌ 避けるべき: ルーター内で複雑な変換
@router.post("/")
async def create_item(item_data: ItemCreate):
    entity = ItemEntity(
        id=None,
        name=item_data.name.strip().upper(),
        description=process_description(item_data.description),
        tags=[Tag(name=t) for t in item_data.tag_names],
        # ... 複雑な変換ロジック
    )

# ✅ 推奨: マッパークラスで変換
@router.post("/")
async def create_item(item_data: ItemCreate):
    entity = ItemMapper.create_dto_to_entity(item_data)
```

#### 3. バリデーションの実施タイミング

```python
# DTOレベルでのバリデーション（型、形式）
class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    @field_validator('name')
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('名前は空白のみにできません')
        return v

# エンティティレベルでのバリデーション（ビジネスルール）
@dataclass
class ItemEntity:
    name: str
    category: str

    def validate_business_rules(self) -> None:
        """ビジネスルール検証"""
        if self.category == 'premium' and len(self.name) < 10:
            raise ValueError('プレミアムカテゴリの名前は10文字以上必要です')
```

---

## 実装推奨事項まとめ

### ✅ 必ず実施すべき事項

#### 1. SQLAlchemy 2.0 非同期設定

```python
# async_sessionmakerでexpire_on_commit=Falseを必ず設定
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # 必須
    autoflush=False,
    autocommit=False,
)
```

#### 2. FastAPI依存性注入

```python
# Dependencies with yieldパターンでセッション管理
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

#### 3. Pydantic v2設定

```python
# 統一的なConfigDictを基底クラスで設定
class BaseDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        extra="forbid",
    )
```

#### 4. クリーンアーキテクチャの遵守

- ドメイン層でインターフェース定義
- インフラストラクチャ層で実装
- 依存関係は常に外→内

#### 5. 論理削除の実装

```python
# do_orm_execute + with_loader_criteriaパターンを使用
@event.listens_for(session_factory, "do_orm_execute")
def _add_soft_delete_filtering(execute_state: ORMExecuteState):
    if execute_state.is_select and not execute_state.execution_options.get("include_deleted"):
        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                SoftDeleteMixin,
                lambda cls: cls.is_deleted.is_(False),
                include_aliases=True,
            )
        )
```

### ⚠️ 避けるべき事項

1. **AsyncSessionの複数タスク間共有** → 各タスクに個別セッション
2. **expire_on_commit=Trueのまま使用** → Falseに設定
3. **遅延ロードの使用** → eager loading（selectinload）を使用
4. **ドメイン層でフレームワーク依存** → 純粋なPythonクラスのみ
5. **ルーター内での複雑なビジネスロジック** → ユースケース層に移動

### 📊 パフォーマンス最適化

1. **JSON検証は`model_validate_json()`を使用**
   - `json.loads()` + `model_validate()`より高速

2. **N+1問題の回避**
   ```python
   # selectinloadで関連データを事前ロード
   stmt = select(ItemModel).options(selectinload(ItemModel.tags))
   ```

3. **データベース接続プール設定**
   ```python
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_pre_ping=True,
   )
   ```

### 🔒 セキュリティ考慮事項

1. **DTOで`extra="forbid"`を設定** → 未知のフィールドを拒否
2. **Pydanticバリデーションでサニタイゼーション**
3. **SQLインジェクション対策** → SQLAlchemyのパラメータ化クエリのみ使用
4. **機密情報の扱い** → `.env`で管理、リポジトリにコミットしない

---

## 参考リソース

### 公式ドキュメント

- [FastAPI - Concurrency and async / await](https://fastapi.tiangolo.com/async/)
- [FastAPI - Dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [SQLAlchemy 2.0 - Asynchronous I/O (asyncio)](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLAlchemy 2.0 - Session Basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Pydantic - Models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic - Configuration](https://docs.pydantic.dev/latest/api/config/)

### コミュニティリソース

- [GitHub: ivan-borovets/fastapi-clean-example](https://github.com/ivan-borovets/fastapi-clean-example)
- [Patterns and Practices for using SQLAlchemy 2.0 with FastAPI](https://chaoticengineer.hashnode.dev/fastapi-sqlalchemy)
- [SQLAlchemy Soft Delete Discussion](https://github.com/sqlalchemy/sqlalchemy/discussions/10517)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

**調査実施者**: Claude (Anthropic)
**最終更新**: 2025年11月22日
