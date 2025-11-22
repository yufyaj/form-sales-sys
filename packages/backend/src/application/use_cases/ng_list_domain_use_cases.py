"""
NGリストドメイン管理ユースケース

NGリストドメインのCRUD操作とビジネスロジックを実行します。
"""

import logging

from src.application.schemas.ng_list_domain import NgListDomainCreateRequest
from src.domain.entities.ng_list_domain_entity import NgListDomainEntity
from src.domain.exceptions import (
    DuplicateNgDomainError,
    ListNotFoundError,
    NgListDomainNotFoundError,
)
from src.domain.interfaces.list_repository import IListRepository
from src.domain.interfaces.ng_list_domain_repository import INgListDomainRepository
from src.infrastructure.utils.domain_utils import (
    normalize_domain_pattern,
    is_wildcard_pattern,
    extract_domain_from_url,
)

logger = logging.getLogger(__name__)


class NgListDomainUseCases:
    """NGリストドメイン管理ユースケースクラス"""

    def __init__(
        self,
        ng_list_domain_repository: INgListDomainRepository,
        list_repository: IListRepository,
    ) -> None:
        """
        Args:
            ng_list_domain_repository: NGリストドメインリポジトリ
            list_repository: リストリポジトリ（リスト存在確認用）
        """
        self._ng_repo = ng_list_domain_repository
        self._list_repo = list_repository

    async def add_ng_domain(
        self,
        requesting_organization_id: int,
        request: NgListDomainCreateRequest,
    ) -> NgListDomainEntity:
        """
        NGドメインを追加

        Args:
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）
            request: NGドメイン登録リクエスト

        Returns:
            作成されたNGドメインエンティティ

        Raises:
            ListNotFoundError: リストが見つからない場合
            DuplicateNgDomainError: 同じドメインパターンが既に登録されている場合
        """
        try:
            # セキュリティ: リストの存在確認と権限チェック
            list_entity = await self._list_repo.find_by_id(
                list_id=request.list_id,
                requesting_organization_id=requesting_organization_id,
            )
            if list_entity is None:
                # セキュリティログ: 権限エラー
                logger.warning(
                    "Unauthorized access attempt to list",
                    extra={
                        "event": "ng_domain_unauthorized_access",
                        "organization_id": requesting_organization_id,
                        "list_id": request.list_id,
                        "action": "add_ng_domain",
                    }
                )
                raise ListNotFoundError(request.list_id)

            # ドメインパターンの正規化（バリデータで既に正規化済みだが、念のため）
            normalized_pattern = normalize_domain_pattern(request.domain)
            is_wildcard = is_wildcard_pattern(normalized_pattern)

            # NGドメインを作成
            ng_domain = await self._ng_repo.create(
                list_id=request.list_id,
                domain=request.domain,
                domain_pattern=normalized_pattern,
                is_wildcard=is_wildcard,
                memo=request.memo,
            )

            # セキュリティログ: 成功
            logger.info(
                "NG domain created successfully",
                extra={
                    "event": "ng_domain_created",
                    "organization_id": requesting_organization_id,
                    "list_id": request.list_id,
                    "domain_pattern": ng_domain.domain_pattern,
                    "is_wildcard": ng_domain.is_wildcard,
                    "ng_domain_id": ng_domain.id,
                }
            )

            return ng_domain

        except DuplicateNgDomainError as e:
            # セキュリティログ: 重複エラー
            logger.warning(
                "Duplicate NG domain attempt",
                extra={
                    "event": "ng_domain_duplicate",
                    "organization_id": requesting_organization_id,
                    "list_id": request.list_id,
                    "domain_pattern": request.domain,
                }
            )
            raise

    async def get_ng_domain(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> NgListDomainEntity:
        """
        NGドメインを取得

        Args:
            ng_domain_id: NGドメインID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Returns:
            NGドメインエンティティ

        Raises:
            NgListDomainNotFoundError: NGドメインが見つからない場合
        """
        ng_domain = await self._ng_repo.find_by_id(
            ng_domain_id=ng_domain_id,
            requesting_organization_id=requesting_organization_id,
        )
        if ng_domain is None:
            raise NgListDomainNotFoundError(ng_domain_id)

        return ng_domain

    async def list_ng_domains_by_list(
        self,
        list_id: int,
        requesting_organization_id: int,
    ) -> list[NgListDomainEntity]:
        """
        リストに属するNGドメインの一覧を取得

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Returns:
            NGドメインエンティティのリスト

        Raises:
            ListNotFoundError: リストが見つからない場合
        """
        # セキュリティ: リストの存在確認と権限チェック
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # NGドメイン一覧を取得
        ng_domains = await self._ng_repo.list_by_list_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
            include_deleted=False,
        )

        return ng_domains

    async def delete_ng_domain(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        NGドメインを論理削除

        Args:
            ng_domain_id: NGドメインID
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Raises:
            NgListDomainNotFoundError: NGドメインが見つからない場合
        """
        # 存在確認（権限チェックを含む）
        ng_domain = await self._ng_repo.find_by_id(
            ng_domain_id=ng_domain_id,
            requesting_organization_id=requesting_organization_id,
        )
        if ng_domain is None:
            # セキュリティログ: 権限エラー
            logger.warning(
                "Unauthorized access attempt to NG domain",
                extra={
                    "event": "ng_domain_unauthorized_delete",
                    "organization_id": requesting_organization_id,
                    "ng_domain_id": ng_domain_id,
                }
            )
            raise NgListDomainNotFoundError(ng_domain_id)

        # 論理削除を実行
        await self._ng_repo.delete(
            ng_domain_id=ng_domain_id,
            requesting_organization_id=requesting_organization_id,
        )

        # セキュリティログ: 削除成功
        logger.info(
            "NG domain deleted successfully",
            extra={
                "event": "ng_domain_deleted",
                "organization_id": requesting_organization_id,
                "ng_domain_id": ng_domain_id,
                "list_id": ng_domain.list_id,
                "domain_pattern": ng_domain.domain_pattern,
            }
        )

    async def check_url_is_ng(
        self,
        list_id: int,
        url: str,
        requesting_organization_id: int,
    ) -> tuple[bool, str | None, str | None]:
        """
        URLがNGリストに含まれるかチェック

        Args:
            list_id: リストID
            url: チェック対象のURL
            requesting_organization_id: リクエスト元の組織ID（マルチテナント対応）

        Returns:
            tuple[bool, str | None, str | None]:
                - NGフラグ: URLがNGリストに含まれる場合True
                - マッチしたパターン: マッチしたNGドメインパターン（NGでない場合はNone）
                - 抽出されたドメイン: URLから抽出されたドメイン（抽出失敗時はNone）

        Raises:
            ListNotFoundError: リストが見つからない場合
        """
        # セキュリティ: リストの存在確認と権限チェック
        list_entity = await self._list_repo.find_by_id(
            list_id=list_id,
            requesting_organization_id=requesting_organization_id,
        )
        if list_entity is None:
            raise ListNotFoundError(list_id)

        # URLからドメインを抽出
        extracted_domain = extract_domain_from_url(url)

        # NGチェックを実行
        is_ng, matched_pattern = await self._ng_repo.check_domain_is_ng(
            list_id=list_id,
            url=url,
            requesting_organization_id=requesting_organization_id,
        )

        return is_ng, matched_pattern, extracted_domain
