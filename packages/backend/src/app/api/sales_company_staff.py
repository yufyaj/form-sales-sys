"""
営業支援会社担当者管理APIルーター

営業支援会社担当者のCRUD操作のエンドポイントを提供します
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user, get_db
from src.application.schemas.sales_company_staff import (
    SalesCompanyStaffCreateRequest,
    SalesCompanyStaffListResponse,
    SalesCompanyStaffResponse,
    SalesCompanyStaffUpdateRequest,
)
from src.application.use_cases.sales_company_staff_use_cases import (
    SalesCompanyStaffUseCases,
)
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.sales_company_staff_repository import (
    SalesCompanyStaffRepository,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository

router = APIRouter(prefix="/sales-company-staff", tags=["sales-company-staff"])


async def get_sales_company_staff_use_cases(
    session: AsyncSession = Depends(get_db),
) -> SalesCompanyStaffUseCases:
    """
    営業支援会社担当者ユースケースの依存性注入

    Args:
        session: DBセッション

    Returns:
        SalesCompanyStaffUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    staff_repo = SalesCompanyStaffRepository(session)
    user_repo = UserRepository(session)

    # ユースケースをインスタンス化
    use_cases = SalesCompanyStaffUseCases(
        staff_repository=staff_repo,
        user_repository=user_repo,
    )

    return use_cases


@router.post(
    "",
    response_model=SalesCompanyStaffResponse,
    status_code=status.HTTP_201_CREATED,
    summary="営業支援会社担当者作成",
    description="新規営業支援会社担当者を作成します。認証が必要です。",
)
async def create_staff(
    request: SalesCompanyStaffCreateRequest,
    use_cases: SalesCompanyStaffUseCases = Depends(get_sales_company_staff_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> SalesCompanyStaffResponse:
    """
    新規営業支援会社担当者を作成

    - **user_id**: ユーザーID（対応するUserレコードのID）
    - **department**: 部署（オプション）
    - **position**: 役職（オプション）
    - **employee_number**: 社員番号（オプション）
    - **notes**: 備考（オプション）
    """
    staff = await use_cases.create_staff(request, current_user.organization_id)
    return SalesCompanyStaffResponse.model_validate(staff)


@router.get(
    "/{staff_id}",
    response_model=SalesCompanyStaffResponse,
    summary="営業支援会社担当者取得",
    description="指定されたIDの営業支援会社担当者を取得します。認証が必要です。",
)
async def get_staff(
    staff_id: int,
    use_cases: SalesCompanyStaffUseCases = Depends(get_sales_company_staff_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> SalesCompanyStaffResponse:
    """
    営業支援会社担当者を取得

    - **staff_id**: 担当者ID
    """
    staff = await use_cases.get_staff(staff_id, current_user.organization_id)
    return SalesCompanyStaffResponse.model_validate(staff)


@router.get(
    "",
    response_model=SalesCompanyStaffListResponse,
    summary="営業支援会社担当者一覧取得",
    description="組織に所属する営業支援会社担当者一覧を取得します。認証が必要です。",
)
async def list_staff(
    skip: int = 0,
    limit: int = 100,
    use_cases: SalesCompanyStaffUseCases = Depends(get_sales_company_staff_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> SalesCompanyStaffListResponse:
    """
    組織の営業支援会社担当者一覧を取得

    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    staff_list, total = await use_cases.list_staff(
        current_user.organization_id, skip, limit
    )
    return SalesCompanyStaffListResponse(
        staff=[SalesCompanyStaffResponse.model_validate(s) for s in staff_list],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{staff_id}",
    response_model=SalesCompanyStaffResponse,
    summary="営業支援会社担当者更新",
    description="営業支援会社担当者情報を更新します。認証が必要です。",
)
async def update_staff(
    staff_id: int,
    request: SalesCompanyStaffUpdateRequest,
    use_cases: SalesCompanyStaffUseCases = Depends(get_sales_company_staff_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> SalesCompanyStaffResponse:
    """
    営業支援会社担当者情報を更新

    - **staff_id**: 担当者ID
    - **request**: 更新内容（部分更新可能）
    """
    staff = await use_cases.update_staff(
        staff_id, current_user.organization_id, request
    )
    return SalesCompanyStaffResponse.model_validate(staff)


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="営業支援会社担当者削除",
    description="営業支援会社担当者を論理削除します。認証が必要です。",
)
async def delete_staff(
    staff_id: int,
    use_cases: SalesCompanyStaffUseCases = Depends(get_sales_company_staff_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> None:
    """
    営業支援会社担当者を論理削除

    - **staff_id**: 担当者ID
    """
    await use_cases.delete_staff(staff_id, current_user.organization_id)
