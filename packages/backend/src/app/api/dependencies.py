"""
API依存性注入

FastAPIの依存性注入を使用して、リポジトリやユースケースを提供します
"""

import logging
from typing import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.app.core.security import decode_access_token
from src.application.use_cases.client_contact_use_cases import ClientContactUseCases
from src.application.use_cases.client_organization_use_cases import (
    ClientOrganizationUseCases,
)
from src.application.use_cases.user_use_cases import UserUseCases
from src.domain.entities.user_entity import UserEntity
from src.infrastructure.persistence.repositories.client_contact_repository import (
    ClientContactRepository,
)
from src.infrastructure.persistence.repositories.client_organization_repository import (
    ClientOrganizationRepository,
)
from src.infrastructure.persistence.repositories.organization_repository import (
    OrganizationRepository,
)
from src.infrastructure.persistence.repositories.role_repository import RoleRepository
from src.infrastructure.persistence.repositories.user_repository import UserRepository
from src.infrastructure.persistence.repositories.worker_repository import WorkerRepository

# ロガー設定
logger = logging.getLogger(__name__)

# HTTP Bearer認証スキーム（オプション: クッキー認証もサポート）
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    session: AsyncSession = Depends(get_db),
) -> UserEntity:
    """
    現在のユーザーを取得

    JWTトークンからユーザー情報を取得し、データベースから最新のユーザー情報を返します。
    トークンはAuthorizationヘッダーまたはauthTokenクッキーから取得します。

    Args:
        request: FastAPIリクエスト
        credentials: HTTPベアラートークン（オプション）
        session: DBセッション

    Returns:
        認証されたユーザーエンティティ

    Raises:
        HTTPException: トークンが無効、または期限切れの場合
    """
    # Authorizationヘッダーからトークンを取得
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # クッキーからトークンを取得
        token = request.cookies.get('authToken')

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # トークンをデコード
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ユーザーIDを取得（"sub"フィールドから取得）
    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # user_idを整数に変換
    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # データベースからユーザーを取得
    user_repo = UserRepository(session)
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 削除されたユーザーはアクセス不可
    if user.is_deleted():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deleted",
        )

    return user


async def get_current_active_user(
    current_user: UserEntity = Depends(get_current_user),
) -> UserEntity:
    """
    現在のアクティブユーザーを取得

    Args:
        current_user: 現在のユーザー

    Returns:
        アクティブなユーザーエンティティ

    Raises:
        HTTPException: ユーザーがアクティブでない場合
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_current_worker_id(
    current_user: UserEntity = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> int:
    """
    現在のユーザーのWorker IDを取得（IDOR対策）

    UserとWorkerの関連を検証し、ログイン中のユーザーに紐づくWorker IDのみを返します。
    これにより、他のワーカーのデータにアクセスするIDOR脆弱性を防止します。

    Args:
        current_user: 現在のアクティブユーザー
        session: DBセッション

    Returns:
        ログイン中のユーザーに紐づくWorker ID

    Raises:
        HTTPException: ユーザーがワーカーでない場合（403 Forbidden）

    セキュリティ上の注意:
        この関数は、APIエンドポイントで worker_id を扱う際に必ず使用してください。
        クエリパラメータやパスパラメータで受け取った worker_id をそのまま使用すると、
        IDOR脆弱性が発生します。
    """
    worker_repo = WorkerRepository(session)

    # UserIDからWorkerを取得
    worker = await worker_repo.find_by_user_id(
        current_user.id,
        current_user.organization_id,
    )

    if worker is None:
        # ユーザーがワーカーでない場合はアクセス拒否
        logger.warning(
            "Worker access denied: user is not a worker",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "organization_id": current_user.organization_id,
                "event_type": "worker_access_denied",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a worker",
        )

    return worker.id


class RoleChecker:
    """
    ロールベースのアクセス制御を行う依存性クラス

    指定されたロールのいずれかを持つユーザーのみアクセスを許可します。

    Example:
        @router.get("/admin")
        async def admin_only(user: UserEntity = Depends(RoleChecker(["admin"]))):
            return {"message": "Admin access granted"}
    """

    def __init__(self, allowed_roles: list[str]) -> None:
        """
        Args:
            allowed_roles: 許可するロール名のリスト（例: ["admin", "sales_support"]）
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: UserEntity = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db),
    ) -> UserEntity:
        """
        ユーザーが許可されたロールを持っているか確認

        Args:
            current_user: 現在のユーザー
            session: DBセッション

        Returns:
            認可されたユーザーエンティティ

        Raises:
            HTTPException: ユーザーが必要なロールを持っていない場合
        """
        role_repo = RoleRepository(session)

        # ユーザーが許可されたロールのいずれかを持っているか確認
        has_role = await role_repo.user_has_any_role(current_user.id, self.allowed_roles)

        if not has_role:
            # セキュリティイベントをログ記録
            logger.warning(
                "Authorization denied: insufficient roles",
                extra={
                    "user_id": current_user.id,
                    "user_email": current_user.email,
                    "required_roles": self.allowed_roles,
                    "event_type": "authorization_denied",
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient privileges",
            )

        return current_user


class PermissionChecker:
    """
    権限ベースのアクセス制御を行う依存性クラス

    指定された権限のいずれかを持つユーザーのみアクセスを許可します。

    Example:
        @router.post("/projects")
        async def create_project(
            user: UserEntity = Depends(PermissionChecker(["project:create"]))
        ):
            return {"message": "Project created"}
    """

    def __init__(self, required_permissions: list[str]) -> None:
        """
        Args:
            required_permissions: 必要な権限コードのリスト（例: ["project:create"]）
        """
        self.required_permissions = required_permissions

    async def __call__(
        self,
        current_user: UserEntity = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db),
    ) -> UserEntity:
        """
        ユーザーが必要な権限を持っているか確認

        Args:
            current_user: 現在のユーザー
            session: DBセッション

        Returns:
            認可されたユーザーエンティティ

        Raises:
            HTTPException: ユーザーが必要な権限を持っていない場合
        """
        role_repo = RoleRepository(session)

        # 各権限をチェック（いずれか1つでもあればOK）
        for permission in self.required_permissions:
            has_permission = await role_repo.user_has_permission(
                current_user.id, permission
            )
            if has_permission:
                return current_user

        # どの権限も持っていない場合はエラー
        # セキュリティイベントをログ記録
        logger.warning(
            "Authorization denied: insufficient permissions",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "required_permissions": self.required_permissions,
                "event_type": "authorization_denied",
            },
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges",
        )


async def get_user_use_cases(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserUseCases, None]:
    """
    ユーザーユースケースの依存性注入

    Args:
        session: DBセッション

    Yields:
        UserUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    user_repo = UserRepository(session)
    org_repo = OrganizationRepository(session)
    role_repo = RoleRepository(session)

    # ユースケースをインスタンス化
    use_cases = UserUseCases(
        user_repository=user_repo,
        organization_repository=org_repo,
        role_repository=role_repo,
    )

    yield use_cases


async def get_client_organization_use_cases(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ClientOrganizationUseCases, None]:
    """
    顧客組織ユースケースの依存性注入

    Args:
        session: DBセッション

    Yields:
        ClientOrganizationUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    client_org_repo = ClientOrganizationRepository(session)
    org_repo = OrganizationRepository(session)

    # ユースケースをインスタンス化
    use_cases = ClientOrganizationUseCases(
        client_org_repository=client_org_repo,
        organization_repository=org_repo,
    )

    yield use_cases


async def get_client_contact_use_cases(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ClientContactUseCases, None]:
    """
    顧客担当者ユースケースの依存性注入

    Args:
        session: DBセッション

    Yields:
        ClientContactUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    contact_repo = ClientContactRepository(session)
    client_org_repo = ClientOrganizationRepository(session)

    # ユースケースをインスタンス化
    use_cases = ClientContactUseCases(
        client_contact_repository=contact_repo,
        client_organization_repository=client_org_repo,
    )

    yield use_cases
