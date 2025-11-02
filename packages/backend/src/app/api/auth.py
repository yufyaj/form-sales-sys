"""
認証APIエンドポイント

ユーザー登録、ログイン、パスワードリセットのAPIを提供します。
"""
import asyncio
import time

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.database import get_db
from src.application.schemas.auth_schemas import (
    PasswordResetRequest,
    PasswordResetRequestEmail,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from src.application.use_cases.auth_use_cases import (
    LoginUseCase,
    RegisterUserUseCase,
    ResetPasswordUseCase,
)
from src.domain.exceptions import (
    DuplicateEmailError,
    InactiveUserError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from src.infrastructure.persistence.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["認証"])

# レート制限の設定
limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    description="新規ユーザーを登録します。パスワードは自動的にハッシュ化されます。",
)
@limiter.limit("5/minute")  # 1分間に5回まで（スパム対策）
async def register(
    req: Request,
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    ユーザー登録

    新規ユーザーを登録します。
    メールアドレスは一意である必要があります。
    """
    user_repository = UserRepository(db)
    use_case = RegisterUserUseCase(user_repository)

    try:
        user = await use_case.execute(
            organization_id=request.organization_id,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone,
            avatar_url=request.avatar_url,
            description=request.description,
        )

        return UserResponse.model_validate(user)

    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="ログイン",
    description="メールアドレスとパスワードで認証し、JWTトークンを発行します。",
)
@limiter.limit("5/minute")  # 1分間に5回まで（ブルートフォース対策）
async def login(
    req: Request,
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    ログイン

    メールアドレスとパスワードで認証し、JWTアクセストークンを発行します。
    """
    user_repository = UserRepository(db)
    use_case = LoginUseCase(user_repository)

    try:
        _, access_token = await use_case.execute(
            email=request.email,
            password=request.password,
        )

        return TokenResponse(access_token=access_token, token_type="bearer")

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="ログアウト",
    description="ログアウトします。（JWT方式ではサーバー側での処理は不要、クライアント側でトークンを破棄）",
)
async def logout() -> None:
    """
    ログアウト

    JWT認証方式では、サーバー側でのセッション管理がないため、
    クライアント側でトークンを破棄するだけです。
    このエンドポイントは、APIの一貫性のために提供されています。
    """
    # JWT方式ではサーバー側での処理は不要
    # クライアント側でトークンを削除してください
    return None


@router.post(
    "/password-reset-request",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="パスワードリセット依頼",
    description="メールアドレスを指定してパスワードリセットを依頼します。",
    deprecated=True,
)
@limiter.limit("3/hour")  # 1時間に3回まで（厳格な制限）
async def request_password_reset(
    req: Request,
    request: PasswordResetRequestEmail,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    パスワードリセット依頼

    ⚠️ Phase2で安全な実装に変更予定

    セキュリティ上の理由により、Phase1では機能を無効化しています。
    Phase2にて、以下の安全な実装を追加予定：
    - CSPRNG（暗号学的に安全な乱数生成器）による32バイト以上のトークン生成
    - トークンのハッシュ化保存
    - 有効期限管理（1時間）
    - ワンタイムトークン（使用後は無効化）
    - タイミング攻撃対策
    """
    # タイミング攻撃対策：常に一定の処理時間を確保
    start_time = time.perf_counter()

    # Phase1では機能を無効化（セキュリティ上の理由）
    # Phase2でトークンベースの安全な実装を追加予定

    # タイミングを均一化するため、最低限の処理時間を確保
    elapsed = time.perf_counter() - start_time
    min_time = 0.5  # 最低500ms
    if elapsed < min_time:
        await asyncio.sleep(min_time - elapsed)

    # 常に同じレスポンスを返す（ユーザー存在の有無を漏らさない）
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset feature will be implemented in Phase 2 with secure token-based mechanism",
    )


@router.post(
    "/password-reset",
    response_model=UserResponse,
    summary="パスワードリセット",
    description="リセットトークンを使用してパスワードをリセットします。",
    deprecated=True,
)
async def reset_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    パスワードリセット

    ⚠️ Phase2で安全な実装に変更予定

    セキュリティ上の理由により、Phase1では機能を無効化しています。
    Phase2にて、以下の安全な実装を追加予定：
    - トークンのハッシュ化検証
    - 有効期限チェック
    - ワンタイムトークンの無効化
    - レート制限
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Password reset feature will be implemented in Phase 2 with secure token-based mechanism",
    )
