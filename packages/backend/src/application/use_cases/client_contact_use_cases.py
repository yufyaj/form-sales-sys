"""
顧客担当者管理のユースケース

顧客担当者のCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.client_contact import (
    ClientContactCreateRequest,
    ClientContactUpdateRequest,
)
from src.domain.entities.client_contact_entity import ClientContactEntity
from src.domain.exceptions import (
    ClientContactNotFoundException,
    ClientOrganizationNotFoundException,
)
from src.domain.interfaces.client_contact_repository import IClientContactRepository
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)


class ClientContactUseCases:
    """顧客担当者管理のユースケースクラス"""

    def __init__(
        self,
        client_contact_repository: IClientContactRepository,
        client_organization_repository: IClientOrganizationRepository,
    ) -> None:
        """
        Args:
            client_contact_repository: 顧客担当者リポジトリ
            client_organization_repository: 顧客組織リポジトリ
        """
        self._contact_repo = client_contact_repository
        self._client_org_repo = client_organization_repository

    async def create_client_contact(
        self,
        request: ClientContactCreateRequest,
        requesting_organization_id: int,
    ) -> ClientContactEntity:
        """
        新規顧客担当者を作成

        Args:
            request: 顧客担当者作成リクエスト
            requesting_organization_id: リクエスト元の営業支援会社の組織ID

        Returns:
            作成された顧客担当者エンティティ

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        # 顧客組織の存在確認（IDOR対策）
        client_org = await self._client_org_repo.find_by_id(
            request.client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(request.client_organization_id)

        # リポジトリで永続化
        created_contact = await self._contact_repo.create(
            client_organization_id=request.client_organization_id,
            full_name=request.full_name,
            department=request.department,
            position=request.position,
            email=request.email,
            phone=request.phone,
            mobile=request.mobile,
            is_primary=request.is_primary,
            notes=request.notes,
        )
        return created_contact

    async def get_client_contact(
        self,
        client_contact_id: int,
        requesting_organization_id: int,
    ) -> ClientContactEntity:
        """
        顧客担当者を取得

        Args:
            client_contact_id: 顧客担当者ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）

        Returns:
            顧客担当者エンティティ

        Raises:
            ClientContactNotFoundException: 顧客担当者が見つからない場合
        """
        contact = await self._contact_repo.find_by_id(
            client_contact_id, requesting_organization_id
        )
        if contact is None:
            raise ClientContactNotFoundException(client_contact_id)
        return contact

    async def list_client_contacts_by_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[ClientContactEntity], int]:
        """
        顧客組織の担当者一覧を取得

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み担当者を含めるか

        Returns:
            (顧客担当者リスト, 総件数)のタプル

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        # 顧客組織の存在確認（IDOR対策）
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(client_organization_id)

        # 担当者一覧を取得
        contacts = await self._contact_repo.list_by_client_organization(
            client_organization_id=client_organization_id,
            requesting_organization_id=requesting_organization_id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

        # 総件数を取得（簡易実装: limitを外して全件取得）
        # 本番環境ではcount専用のメソッドを実装することを推奨
        all_contacts = await self._contact_repo.list_by_client_organization(
            client_organization_id=client_organization_id,
            requesting_organization_id=requesting_organization_id,
            skip=0,
            limit=10000,  # 大きな数値を設定
            include_deleted=include_deleted,
        )
        total = len(all_contacts)

        return contacts, total

    async def update_client_contact(
        self,
        client_contact_id: int,
        requesting_organization_id: int,
        request: ClientContactUpdateRequest,
    ) -> ClientContactEntity:
        """
        顧客担当者情報を更新

        Args:
            client_contact_id: 顧客担当者ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）
            request: 更新リクエスト

        Returns:
            更新された顧客担当者エンティティ

        Raises:
            ClientContactNotFoundException: 顧客担当者が見つからない場合
        """
        # 顧客担当者を取得（IDOR対策）
        contact = await self._contact_repo.find_by_id(
            client_contact_id, requesting_organization_id
        )
        if contact is None:
            raise ClientContactNotFoundException(client_contact_id)

        # 部分更新: exclude_unset=Trueで設定されたフィールドのみ更新
        update_data = request.model_dump(exclude_unset=True)

        # エンティティのフィールドを更新
        for field, value in update_data.items():
            setattr(contact, field, value)

        # リポジトリで永続化
        updated_contact = await self._contact_repo.update(
            contact, requesting_organization_id
        )
        return updated_contact

    async def delete_client_contact(
        self,
        client_contact_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        顧客担当者を論理削除

        Args:
            client_contact_id: 顧客担当者ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）

        Raises:
            ClientContactNotFoundException: 顧客担当者が見つからない場合
        """
        # 存在確認（IDOR対策）
        contact = await self._contact_repo.find_by_id(
            client_contact_id, requesting_organization_id
        )
        if contact is None:
            raise ClientContactNotFoundException(client_contact_id)

        # 論理削除実行
        await self._contact_repo.soft_delete(
            client_contact_id, requesting_organization_id
        )

    async def get_primary_contact(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
    ) -> ClientContactEntity | None:
        """
        顧客組織の主担当者を取得

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）

        Returns:
            主担当者エンティティ（見つからない場合はNone）

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        # 顧客組織の存在確認（IDOR対策）
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(client_organization_id)

        # 主担当者を取得
        primary_contact = await self._contact_repo.find_primary_contact(
            client_organization_id, requesting_organization_id
        )
        return primary_contact
