"""
営業支援会社担当者管理のユースケース

営業支援会社担当者のCRUD操作とビジネスロジックを実行します
"""

from src.application.schemas.sales_company_staff import (
    SalesCompanyStaffCreateRequest,
    SalesCompanyStaffUpdateRequest,
)
from src.domain.entities.sales_company_staff_entity import SalesCompanyStaffEntity
from src.domain.exceptions import (
    SalesCompanyStaffNotFoundError,
    UserNotFoundException,
)
from src.domain.interfaces.sales_company_staff_repository import (
    ISalesCompanyStaffRepository,
)
from src.domain.interfaces.user_repository import IUserRepository


class SalesCompanyStaffUseCases:
    """営業支援会社担当者管理のユースケースクラス"""

    def __init__(
        self,
        staff_repository: ISalesCompanyStaffRepository,
        user_repository: IUserRepository,
    ) -> None:
        """
        Args:
            staff_repository: 営業支援会社担当者リポジトリ
            user_repository: ユーザーリポジトリ
        """
        self._staff_repo = staff_repository
        self._user_repo = user_repository

    async def create_staff(
        self,
        request: SalesCompanyStaffCreateRequest,
        organization_id: int,
    ) -> SalesCompanyStaffEntity:
        """
        新規営業支援会社担当者を作成

        Args:
            request: 担当者作成リクエスト
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            作成された担当者エンティティ

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
        """
        # ユーザーの存在確認（マルチテナント対応）
        user = await self._user_repo.find_by_id_with_org(
            request.user_id, organization_id
        )
        if user is None:
            raise UserNotFoundException(user_id=request.user_id)

        # リポジトリで永続化
        staff = await self._staff_repo.create(
            user_id=request.user_id,
            organization_id=organization_id,
            department=request.department,
            position=request.position,
            employee_number=request.employee_number,
            notes=request.notes,
        )
        return staff

    async def get_staff(
        self,
        staff_id: int,
        organization_id: int,
    ) -> SalesCompanyStaffEntity:
        """
        営業支援会社担当者を取得

        Args:
            staff_id: 担当者ID
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            担当者エンティティ

        Raises:
            SalesCompanyStaffNotFoundError: 担当者が見つからない場合
        """
        staff = await self._staff_repo.find_by_id(staff_id, organization_id)
        if staff is None:
            raise SalesCompanyStaffNotFoundError(staff_id)
        return staff

    async def list_staff(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SalesCompanyStaffEntity], int]:
        """
        組織の担当者一覧を取得

        Args:
            organization_id: 組織ID
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (担当者リスト, 総件数)のタプル
        """
        staff_list = await self._staff_repo.list_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        # 総件数を正確に取得（ページネーション対応）
        total = await self._staff_repo.count_by_organization(
            organization_id=organization_id,
            include_deleted=False,
        )
        return staff_list, total

    async def update_staff(
        self,
        staff_id: int,
        organization_id: int,
        request: SalesCompanyStaffUpdateRequest,
    ) -> SalesCompanyStaffEntity:
        """
        営業支援会社担当者情報を更新

        Args:
            staff_id: 担当者ID
            organization_id: 組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新された担当者エンティティ

        Raises:
            SalesCompanyStaffNotFoundError: 担当者が見つからない場合
        """
        # 担当者を取得
        staff = await self._staff_repo.find_by_id(staff_id, organization_id)
        if staff is None:
            raise SalesCompanyStaffNotFoundError(staff_id)

        # フィールドを更新
        if request.department is not None:
            staff.department = request.department

        if request.position is not None:
            staff.position = request.position

        if request.employee_number is not None:
            staff.employee_number = request.employee_number

        if request.notes is not None:
            staff.notes = request.notes

        # リポジトリで永続化
        updated_staff = await self._staff_repo.update(staff, organization_id)
        return updated_staff

    async def delete_staff(
        self,
        staff_id: int,
        organization_id: int,
    ) -> None:
        """
        営業支援会社担当者を論理削除

        Args:
            staff_id: 担当者ID
            organization_id: 組織ID（マルチテナント対応）

        Raises:
            SalesCompanyStaffNotFoundError: 担当者が見つからない場合
        """
        await self._staff_repo.soft_delete(staff_id, organization_id)
