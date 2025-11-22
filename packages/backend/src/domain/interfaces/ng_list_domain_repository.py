"""
NGリストドメインリポジトリインターフェース

ドメイン層で定義するNGリストドメインリポジトリの抽象インターフェース。
依存性逆転の原則（DIP）により、Infrastructure層がこのインターフェースを実装します。
"""
from abc import ABC, abstractmethod

from src.domain.entities.ng_list_domain_entity import NgListDomainEntity


class INgListDomainRepository(ABC):
    """
    NGリストドメインリポジトリインターフェース

    リストごとのNG（送信禁止）ドメインの永続化操作を定義します。
    """

    @abstractmethod
    async def create(
        self,
        list_id: int,
        domain: str,
        domain_pattern: str,
        is_wildcard: bool = False,
        memo: str | None = None,
    ) -> NgListDomainEntity:
        """
        NGドメインを作成

        Args:
            list_id: リストID
            domain: 元のドメインパターン（ユーザー入力）
            domain_pattern: 正規化されたドメインパターン（比較用）
            is_wildcard: ワイルドカード使用フラグ
            memo: メモ（任意）

        Returns:
            NgListDomainEntity: 作成されたNGドメインエンティティ
        """
        pass

    @abstractmethod
    async def find_by_id(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> NgListDomainEntity | None:
        """
        IDでNGドメインを検索（マルチテナント対応）

        Args:
            ng_domain_id: NGドメインID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            NgListDomainEntity | None: 見つかった場合はNGドメインエンティティ、見つからない場合はNone

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
            listsテーブルを結合してorganization_idを検証します。
        """
        pass

    @abstractmethod
    async def list_by_list_id(
        self,
        list_id: int,
        requesting_organization_id: int,
        include_deleted: bool = False,
    ) -> list[NgListDomainEntity]:
        """
        リストIDでNGドメインの一覧を取得（マルチテナント対応）

        Args:
            list_id: リストID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）
            include_deleted: 削除済みNGドメインを含めるか

        Returns:
            list[NgListDomainEntity]: NGドメインエンティティのリスト

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
            listsテーブルを結合してorganization_idを検証します。
        """
        pass

    @abstractmethod
    async def delete(
        self,
        ng_domain_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        NGドメインを論理削除（ソフトデリート）（マルチテナント対応）

        Args:
            ng_domain_id: NGドメインID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Raises:
            NgListDomainNotFoundError: NGドメインが見つからない場合、
                                      またはrequesting_organization_idと一致しない場合

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass

    @abstractmethod
    async def check_domain_is_ng(
        self,
        list_id: int,
        url: str,
        requesting_organization_id: int,
    ) -> tuple[bool, str | None]:
        """
        URLがNGリストに含まれるかチェック（マルチテナント対応）

        Args:
            list_id: リストID
            url: チェック対象のURL
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（テナント分離用）

        Returns:
            tuple[bool, str | None]: (NGフラグ, マッチしたパターン)
                - NGフラグ: URLがNGリストに含まれる場合True
                - マッチしたパターン: マッチしたNGドメインパターン（NGでない場合はNone）

        Note:
            IDOR（Insecure Direct Object Reference）脆弱性対策として、
            requesting_organization_idで必ずテナント分離を行います。
        """
        pass
