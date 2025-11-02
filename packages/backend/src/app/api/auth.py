"""
認証APIエンドポイント

ユーザー登録、ログイン、パスワードリセットのAPIを提供します。
"""
from fastapi import APIRouter, Depends, HTTPException, status
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


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    description="新規ユーザーを登録します。パスワードは自動的にハッシュ化されます。",
)
async def register(
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
async def login(
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
)
async def request_password_reset(
    request: PasswordResetRequestEmail,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    パスワードリセット依頼

    メールアドレスを指定してパスワードリセットを依頼します。
    本来はメール送信などの処理が必要ですが、Phase1では簡易実装とします。
    """
    user_repository = UserRepository(db)

    try:
        user = await user_repository.find_by_email(request.email)
        if user is None:
            # セキュリティ上、ユーザーが存在するかどうかを返さない
            return None

        # TODO: メール送信処理を実装
        # - リセットトークンを生成
        # - トークンをデータベースに保存（有効期限付き）
        # - リセット用URLをメールで送信

        return None

    except Exception:
        # セキュリティ上、エラー情報を返さない
        return None


@router.post(
    "/password-reset",
    response_model=UserResponse,
    summary="パスワードリセット",
    description="リセットトークンを使用してパスワードをリセットします。",
)
async def reset_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    パスワードリセット

    リセットトークンを使用してパスワードをリセットします。
    Phase1では簡易実装として、トークン=ユーザーIDとします。
    """
    user_repository = UserRepository(db)
    use_case = ResetPasswordUseCase(user_repository)

    try:
        # Phase1: トークン=ユーザーIDとして簡易実装
        # 本来はトークンの検証とユーザーIDの取得が必要
        user_id = int(request.token)

        user = await use_case.execute(
            user_id=user_id,
            new_password=request.new_password,
        )

        return UserResponse.model_validate(user)

    except (UserNotFoundError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired reset token",
        )
