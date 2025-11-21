"""
NGリストドメインリポジトリの実装

INgListDomainRepositoryインターフェースの具体的な実装。
SQLAlchemyを使用してデータベース操作を行います。
"""
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.domain.entities.ng_list_domain_entity import NgListDomainEntity
from src.domain.exceptions import (
    DuplicateNgDomainError,
    NgListDomainNotFoundError,
)
from src.domain.interfaces.ng_list_domain_repository import INgListDomainRepository
from src.infrastructure.persistence.models.ng_list_domain import NgListDomain
from src.infrastructure.persistence.models.list import List
from src.infrastructure.utils.domain_utils import (
    extract_domain_from_url,
    is_domain_in_ng_list,
)


class NgListDomainRepository(INgListDomainRepository):
    """
    NGリストドメインリポジトリの実装

    SQLAlchemyを使用してNGドメインの永続化を行います。
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Args:
            session: データベースセッション
        """
        self._session = session

    async def create(
        self,
        list_id: int,
        domain: str,
        domain_pattern: str,
        is_wildcard: bool = False,
        memo: str | None = None,
    ) -> NgListDomainEntity:
        """NGドメインを作成"""
        ng_domain_model = NgListDomain(
            list_id=list_id,
            domain=domain,
            domain_pattern=domain_pattern,
            is_wildcard=is_wildcard,
            memo=memo,
        )

        self._session.add(ng_domain_model)

        try:
            await self._session.flush()
            await self._session.refresh(ng_domain_model)
        except IntegrityError as e:
            # UNIQUE制約違反の場合
            if "uq_ng_list_domains_list_id_domain_pattern" in str(e):
                raise DuplicateNgDomainError(domain_pattern=domain_pattern, list_id=list_id)
            raise

        return self._to_entity(ng_domain_model)

    async def find_by_id(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> NgListDomainEntity | None:
        """IDでNGドメインを検索（マルチテナント対応・IDOR脆弱性対策）"""
        # listsテーブルを結合してorganization_idを検証
        stmt = (
            select(NgListDomain)
            .join(List, NgListDomain.list_id == List.id)
            .where(
                NgListDomain.id == ng_domain_id,
                List.organization_id == requesting_organization_id,
                NgListDomain.deleted_at.is_(None),
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        ng_domain_model = result.scalar_one_or_none()

        if ng_domain_model is None:
            return None

        return self._to_entity(ng_domain_model)

    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[NgListDomainEntity]:
        """リストIDでNGドメインの一覧を取得（マルチテナント対応・IDOR脆弱性対策）"""
        # listsテーブルを結合してorganization_idを検証
        conditions = [
            NgListDomain.list_id == list_id,
            List.organization_id == requesting_organization_id,
            List.deleted_at.is_(None),
        ]
        if not include_deleted:
            conditions.append(NgListDomain.deleted_at.is_(None))

        stmt = (
            select(NgListDomain)
            .join(List, NgListDomain.list_id == List.id)
            .where(and_(*conditions))
            .order_by(NgListDomain.created_at.desc())
        )

        result = await self._session.execute(stmt)
        ng_domains = result.scalars().all()

        return [self._to_entity(ng_domain) for ng_domain in ng_domains]

    async def delete(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> None:
        """NGドメインを論理削除（ソフトデリート）（マルチテナント対応・IDOR脆弱性対策）"""
        # listsテーブルを結合してorganization_idを検証
        stmt = (
            select(NgListDomain)
            .join(List, NgListDomain.list_id == List.id)
            .where(
                NgListDomain.id == ng_domain_id,
                List.organization_id == requesting_organization_id,
                NgListDomain.deleted_at.is_(None),
                List.deleted_at.is_(None),
            )
        )
        result = await self._session.execute(stmt)
        ng_domain_model = result.scalar_one_or_none()

        if ng_domain_model is None:
            raise NgListDomainNotFoundError(ng_domain_id)

        ng_domain_model.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def check_domain_is_ng(
        self,
        list_id: int,
        url: str,
        requesting_organization_id: int,
    ) -> tuple[bool, str | None]:
        """
        URLがNGリストに含まれるかチェック（マルチテナント対応・IDOR脆弱性対策）

        Args:
            list_id: リストID
            url: チェック対象のURL
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            tuple[bool, str | None]: (NGフラグ, マッチしたパターン)
        """
        # URLからドメインを抽出
        domain = extract_domain_from_url(url)
        if domain is None:
            # 無効なURLの場合はNGとしない
            return (False, None)

        # NGドメインパターンを取得（マルチテナント対応）
        ng_domains = await self.list_by_list_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
            include_deleted=False,
        )

        # NGパターンリストを作成
        ng_patterns = [ng_domain.domain_pattern for ng_domain in ng_domains]

        # ドメイン判定
        return is_domain_in_ng_list(domain, ng_patterns)

    def _to_entity(self, ng_domain_model: NgListDomain) -> NgListDomainEntity:
        """
        SQLAlchemyモデルをドメインエンティティに変換

        インフラストラクチャの実装詳細をドメイン層から隠蔽します。
        """
        return NgListDomainEntity(
            id=ng_domain_model.id,
            list_id=ng_domain_model.list_id,
            domain=ng_domain_model.domain,
            domain_pattern=ng_domain_model.domain_pattern,
            is_wildcard=ng_domain_model.is_wildcard,
            memo=ng_domain_model.memo,
            created_at=ng_domain_model.created_at,
            updated_at=ng_domain_model.updated_at,
            deleted_at=ng_domain_model.deleted_at,
        )
