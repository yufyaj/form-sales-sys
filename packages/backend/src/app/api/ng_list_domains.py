"""
NGリストドメイン管理APIルーター

NGリストドメインのCRUD操作とチェック機能のエンドポイントを提供します。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.dependencies import get_current_active_user
from src.app.core.database import get_db
from src.application.schemas.ng_list_domain import (
    NgListDomainCheckRequest,
    NgListDomainCheckResponse,
    NgListDomainCreateRequest,
    NgListDomainListResponse,
    NgListDomainResponse,
)
from src.application.use_cases.ng_list_domain_use_cases import NgListDomainUseCases
from src.domain.entities.ng_list_domain_entity import NgListDomainEntity
from src.domain.entities.user_entity import UserEntity
from src.domain.interfaces.list_repository import IListRepository
from src.domain.interfaces.ng_list_domain_repository import INgListDomainRepository
from src.infrastructure.persistence.repositories.list_repository import ListRepository
from src.infrastructure.persistence.repositories.ng_list_domain_repository import (
    NgListDomainRepository,
)

router = APIRouter(prefix="/ng-list-domains", tags=["ng-list-domains"])


async def get_ng_list_domain_use_cases(
    session: AsyncSession = Depends(get_db),
) -> NgListDomainUseCases:
    """
    NGリストドメインユースケースの依存性注入

    Args:
        session: データベースセッション

    Returns:
        NgListDomainUseCases: NGリストドメインユースケースインスタンス
    """
    ng_list_domain_repo: INgListDomainRepository = NgListDomainRepository(session)
    list_repo: IListRepository = ListRepository(session)
    return NgListDomainUseCases(
        ng_list_domain_repository=ng_list_domain_repo,
        list_repository=list_repo,
    )


@router.post(
    "",
    response_model=NgListDomainResponse,
    status_code=status.HTTP_201_CREATED,
    summary="NGドメイン追加",
    description="リストにNGドメインを追加します。認証が必要です。",
)
async def create_ng_domain(
    request: NgListDomainCreateRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NgListDomainUseCases = Depends(get_ng_list_domain_use_cases),
) -> NgListDomainResponse:
    """
    NGドメインを追加

    - **list_id**: リストID
    - **domain**: NGドメインパターン（例: "example.com", "*.example.com"）
    - **memo**: メモ（任意）
    """
    ng_domain_entity = await use_cases.add_ng_domain(
        requesting_organization_id=current_user.organization_id,
        request=request,
    )
    return _to_response(ng_domain_entity)


@router.get(
    "/{ng_domain_id}",
    response_model=NgListDomainResponse,
    summary="NGドメイン取得",
    description="IDでNGドメインを取得します。認証が必要です。",
)
async def get_ng_domain(
    ng_domain_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NgListDomainUseCases = Depends(get_ng_list_domain_use_cases),
) -> NgListDomainResponse:
    """
    NGドメインを取得

    - **ng_domain_id**: NGドメインID
    """
    ng_domain_entity = await use_cases.get_ng_domain(
        ng_domain_id=ng_domain_id,
        requesting_organization_id=current_user.organization_id,
    )
    return _to_response(ng_domain_entity)


@router.get(
    "",
    response_model=NgListDomainListResponse,
    summary="NGドメイン一覧取得",
    description="リストに属するNGドメインの一覧を取得します。認証が必要です。",
)
async def list_ng_domains(
    list_id: Annotated[int, Query(gt=0, description="リストID")],
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NgListDomainUseCases = Depends(get_ng_list_domain_use_cases),
) -> NgListDomainListResponse:
    """
    リストに属するNGドメインの一覧を取得

    - **list_id**: リストID
    """
    ng_domains = await use_cases.list_ng_domains_by_list(
        list_id=list_id,
        requesting_organization_id=current_user.organization_id,
    )

    return NgListDomainListResponse(
        ng_domains=[_to_response(ng_domain) for ng_domain in ng_domains],
        total=len(ng_domains),
    )


@router.delete(
    "/{ng_domain_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="NGドメイン削除",
    description="NGドメインを論理削除します。認証が必要です。",
)
async def delete_ng_domain(
    ng_domain_id: int,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NgListDomainUseCases = Depends(get_ng_list_domain_use_cases),
) -> None:
    """
    NGドメインを論理削除

    - **ng_domain_id**: NGドメインID
    """
    await use_cases.delete_ng_domain(
        ng_domain_id=ng_domain_id,
        requesting_organization_id=current_user.organization_id,
    )


@router.post(
    "/check",
    response_model=NgListDomainCheckResponse,
    summary="URLのNGチェック",
    description="URLがNGリストに含まれるかチェックします。認証が必要です。",
)
async def check_url_is_ng(
    request: NgListDomainCheckRequest,
    current_user: UserEntity = Depends(get_current_active_user),
    use_cases: NgListDomainUseCases = Depends(get_ng_list_domain_use_cases),
) -> NgListDomainCheckResponse:
    """
    URLがNGリストに含まれるかチェック

    - **list_id**: リストID
    - **url**: チェック対象のURL（例: "https://www.example.com/form"）

    Returns:
        - **is_ng**: NGリストに含まれる場合True
        - **matched_pattern**: マッチしたNGドメインパターン（NGの場合のみ）
        - **extracted_domain**: URLから抽出されたドメイン
    """
    is_ng, matched_pattern, extracted_domain = await use_cases.check_url_is_ng(
        list_id=request.list_id,
        url=request.url,
        requesting_organization_id=current_user.organization_id,
    )

    return NgListDomainCheckResponse(
        is_ng=is_ng,
        matched_pattern=matched_pattern,
        extracted_domain=extracted_domain,
    )


def _to_response(ng_domain_entity: NgListDomainEntity) -> NgListDomainResponse:
    """
    NgListDomainEntityをNgListDomainResponseに変換

    Args:
        ng_domain_entity: NGドメインエンティティ

    Returns:
        NgListDomainResponse: NGドメインレスポンス
    """
    return NgListDomainResponse(
        id=ng_domain_entity.id,
        list_id=ng_domain_entity.list_id,
        domain=ng_domain_entity.domain,
        domain_pattern=ng_domain_entity.domain_pattern,
        is_wildcard=ng_domain_entity.is_wildcard,
        memo=ng_domain_entity.memo,
        created_at=ng_domain_entity.created_at,
        updated_at=ng_domain_entity.updated_at,
        deleted_at=ng_domain_entity.deleted_at,
    )
