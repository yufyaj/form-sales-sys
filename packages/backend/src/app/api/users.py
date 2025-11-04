"""
ユーザー管理APIルーター

ユーザーのCRUD操作とロール管理のエンドポイントを提供します
"""



from fastapi import APIRouter, Depends, status

from src.app.api.dependencies import (
    RoleChecker,
    get_current_active_user,
    get_user_use_cases,
)
from src.domain.entities.user_entity import UserEntity
from src.application.schemas.user import (
    PasswordChangeRequest,
    RoleAssignRequest,
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
    UserWithRolesResponse,
)
from src.application.use_cases.user_use_cases import UserUseCases

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー作成",
    description="新規ユーザーを作成します。パスワードは自動的にハッシュ化されます。管理者権限が必要です。",
)
async def create_user(
    request: UserCreateRequest,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
) -> UserResponse:
    """
    新規ユーザーを作成

    - **email**: メールアドレス（一意）
    - **full_name**: フルネーム
    - **password**: パスワード（8文字以上、英大文字・英小文字・数字を含む）
    - **organization_id**: 所属組織ID
    """
    user = await use_cases.create_user(request)
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="ユーザー取得",
    description="指定されたIDのユーザーを取得します。認証が必要です。",
)
async def get_user(
    user_id: int,
    organization_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(get_current_active_user),
) -> UserResponse:
    """
    ユーザーを取得

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID（マルチテナント対応）
    """
    user = await use_cases.get_user(user_id, organization_id)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=UserListResponse,
    summary="ユーザー一覧取得",
    description="組織に所属するユーザー一覧を取得します。",
)
async def list_users(
    organization_id: int,
    skip: int = 0,
    limit: int = 100,
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserListResponse:
    """
    組織のユーザー一覧を取得

    - **organization_id**: 組織ID
    - **skip**: スキップする件数（デフォルト: 0）
    - **limit**: 取得する最大件数（デフォルト: 100）
    """
    users, total = await use_cases.list_users(organization_id, skip, limit)
    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="ユーザー更新",
    description="ユーザー情報を更新します。",
)
async def update_user(
    user_id: int,
    organization_id: int,
    request: UserUpdateRequest,
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserResponse:
    """
    ユーザー情報を更新

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID（マルチテナント対応）
    - **request**: 更新内容（部分更新可能）
    """
    user = await use_cases.update_user(user_id, organization_id, request)
    return UserResponse.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ユーザー削除",
    description="ユーザーを論理削除します。アクティブなユーザーは削除できません。",
)
async def delete_user(
    user_id: int,
    organization_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> None:
    """
    ユーザーを論理削除

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID（マルチテナント対応）

    注意: アクティブなユーザーは削除できません。先に無効化してください。
    """
    await use_cases.delete_user(user_id, organization_id)


@router.post(
    "/{user_id}/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="パスワード変更",
    description="ユーザーのパスワードを変更します。",
)
async def change_password(
    user_id: int,
    organization_id: int,
    request: PasswordChangeRequest,
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> None:
    """
    パスワードを変更

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID
    - **request**: パスワード変更情報
    """
    await use_cases.change_password(user_id, organization_id, request)


@router.get(
    "/{user_id}/roles",
    response_model=UserWithRolesResponse,
    summary="ユーザーとロール取得",
    description="ユーザー情報と割り当てられたロール一覧を取得します。",
)
async def get_user_with_roles(
    user_id: int,
    organization_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
) -> UserWithRolesResponse:
    """
    ユーザーとロール一覧を取得

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID
    """
    user, roles = await use_cases.get_user_with_roles(user_id, organization_id)
    user_dict = UserResponse.model_validate(user).model_dump()
    user_dict["roles"] = [
        {"id": role.id, "name": role.name, "display_name": role.display_name, "description": role.description}
        for role in roles
    ]
    return UserWithRolesResponse(**user_dict)


@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ロール割り当て",
    description="ユーザーにロールを割り当てます。管理者または営業支援会社の権限が必要です。",
)
async def assign_role(
    user_id: int,
    organization_id: int,
    request: RoleAssignRequest,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
) -> None:
    """
    ユーザーにロールを割り当て

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID
    - **request**: ロール割り当て情報
    """
    await use_cases.assign_role(user_id, organization_id, request.role_id)


@router.delete(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ロール削除",
    description="ユーザーからロールを削除します。管理者または営業支援会社の権限が必要です。",
)
async def remove_role(
    user_id: int,
    organization_id: int,
    role_id: int,
    use_cases: UserUseCases = Depends(get_user_use_cases),
    current_user: UserEntity = Depends(RoleChecker(["admin", "sales_support"])),
) -> None:
    """
    ユーザーからロールを削除

    - **user_id**: ユーザーID
    - **organization_id**: 組織ID
    - **role_id**: ロールID
    """
    await use_cases.remove_role(user_id, organization_id, role_id)
