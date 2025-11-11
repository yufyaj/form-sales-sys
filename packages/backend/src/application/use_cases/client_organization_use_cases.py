"""
顧客組織管理のユースケース

顧客組織のCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.client_organization import (
    ClientOrganizationCreateRequest,
    ClientOrganizationUpdateRequest,
)
from src.domain.entities.client_organization_entity import ClientOrganizationEntity
from src.domain.exceptions import (
    ClientOrganizationNotFoundException,
    OrganizationNotFoundException,
)
from src.domain.interfaces.client_organization_repository import (
    IClientOrganizationRepository,
)
from src.domain.interfaces.organization_repository import IOrganizationRepository


class ClientOrganizationUseCases:
    """顧客組織管理のユースケースクラス"""

    def __init__(
        self,
        client_org_repository: IClientOrganizationRepository,
        organization_repository: IOrganizationRepository,
    ) -> None:
        """
        Args:
            client_org_repository: 顧客組織リポジトリ
            organization_repository: 組織リポジトリ
        """
        self._client_org_repo = client_org_repository
        self._org_repo = organization_repository

    async def create_client_organization(
        self,
        request: ClientOrganizationCreateRequest,
        requesting_organization_id: int,
    ) -> ClientOrganizationEntity:
        """
        新規顧客組織を作成

        Args:
            request: 顧客組織作成リクエスト
            requesting_organization_id: リクエスト元の営業支援会社の組織ID

        Returns:
            作成された顧客組織エンティティ

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
        """
        # 組織の存在確認
        organization = await self._org_repo.find_by_id(request.organization_id)
        if organization is None:
            raise OrganizationNotFoundException(
                organization_id=str(request.organization_id)
            )

        # 組織が営業支援会社の子組織であることを確認（セキュリティチェック）
        if organization.parent_organization_id != requesting_organization_id:
            raise OrganizationNotFoundException(
                organization_id=str(request.organization_id)
            )

        # リポジトリで永続化
        created_client_org = await self._client_org_repo.create(
            organization_id=request.organization_id,
            industry=request.industry,
            employee_count=request.employee_count,
            annual_revenue=request.annual_revenue,
            established_year=request.established_year,
            website=request.website,
            sales_person=request.sales_person,
            notes=request.notes,
        )
        return created_client_org

    async def get_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
    ) -> ClientOrganizationEntity:
        """
        顧客組織を取得

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）

        Returns:
            顧客組織エンティティ

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(client_organization_id)
        return client_org

    async def list_client_organizations(
        self,
        requesting_organization_id: int,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[ClientOrganizationEntity], int]:
        """
        営業支援会社の顧客組織一覧を取得

        Args:
            requesting_organization_id: リクエスト元の営業支援会社の組織ID
            skip: スキップする件数（ページネーション用）
            limit: 取得する最大件数
            include_deleted: 削除済み顧客組織を含めるか

        Returns:
            (顧客組織リスト, 総件数)のタプル
        """
        client_orgs = await self._client_org_repo.list_by_sales_support_organization(
            sales_support_organization_id=requesting_organization_id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

        # 総件数を取得（簡易実装: limitを外して全件取得）
        # 本番環境ではcount専用のメソッドを実装することを推奨
        all_client_orgs = await self._client_org_repo.list_by_sales_support_organization(
            sales_support_organization_id=requesting_organization_id,
            skip=0,
            limit=10000,  # 大きな数値を設定
            include_deleted=include_deleted,
        )
        total = len(all_client_orgs)

        return client_orgs, total

    async def update_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
        request: ClientOrganizationUpdateRequest,
    ) -> ClientOrganizationEntity:
        """
        顧客組織情報を更新

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）
            request: 更新リクエスト

        Returns:
            更新された顧客組織エンティティ

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        # 顧客組織を取得（IDOR対策）
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(client_organization_id)

        # 部分更新: exclude_unset=Trueで設定されたフィールドのみ更新
        update_data = request.model_dump(exclude_unset=True)

        # エンティティのフィールドを更新
        for field, value in update_data.items():
            setattr(client_org, field, value)

        # リポジトリで永続化
        updated_client_org = await self._client_org_repo.update(
            client_org, requesting_organization_id
        )
        return updated_client_org

    async def delete_client_organization(
        self,
        client_organization_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        顧客組織を論理削除

        Args:
            client_organization_id: 顧客組織ID
            requesting_organization_id: リクエスト元の営業支援会社の組織ID（IDOR対策）

        Raises:
            ClientOrganizationNotFoundException: 顧客組織が見つからない場合
        """
        # 存在確認（IDOR対策）
        client_org = await self._client_org_repo.find_by_id(
            client_organization_id, requesting_organization_id
        )
        if client_org is None:
            raise ClientOrganizationNotFoundException(client_organization_id)

        # 論理削除実行
        await self._client_org_repo.soft_delete(
            client_organization_id, requesting_organization_id
        )
