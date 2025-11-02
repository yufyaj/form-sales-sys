"""
認証関連のユースケース

ユーザー登録、ログイン、パスワードリセットなどのビジネスロジックを実装します。
"""
from src.app.core.security import create_access_token, hash_password, verify_password
from src.domain.entities.user_entity import UserEntity
from src.domain.exceptions import DuplicateEmailError, InactiveUserError, InvalidCredentialsError
from src.domain.interfaces.user_repository import IUserRepository


class RegisterUserUseCase:
    """
    ユーザー登録ユースケース

    新規ユーザーを登録します。
    パスワードのハッシュ化やバリデーションを行います。
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        """
        Args:
            user_repository: ユーザーリポジトリ
        """
        self._user_repository = user_repository

    async def execute(
        self,
        organization_id: int,
        email: str,
        password: str,
        full_name: str,
        phone: str | None = None,
        avatar_url: str | None = None,
        description: str | None = None,
    ) -> UserEntity:
        """
        ユーザーを登録

        Args:
            organization_id: 所属組織ID
            email: メールアドレス
            password: プレーンテキストのパスワード
            full_name: 氏名
            phone: 電話番号（オプション）
            avatar_url: プロフィール画像URL（オプション）
            description: 備考（オプション）

        Returns:
            UserEntity: 作成されたユーザーエンティティ

        Raises:
            DuplicateEmailError: メールアドレスが既に存在する場合
        """
        # パスワードをハッシュ化
        hashed_password = hash_password(password)

        # ユーザーを作成
        user = await self._user_repository.create(
            organization_id=organization_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            phone=phone,
            avatar_url=avatar_url,
            description=description,
        )

        return user


class LoginUseCase:
    """
    ログインユースケース

    メールアドレスとパスワードで認証し、JWTトークンを発行します。
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        """
        Args:
            user_repository: ユーザーリポジトリ
        """
        self._user_repository = user_repository

    async def execute(self, email: str, password: str) -> tuple[UserEntity, str]:
        """
        ログイン認証を実行

        Args:
            email: メールアドレス
            password: パスワード

        Returns:
            tuple[UserEntity, str]: (ユーザーエンティティ, アクセストークン)

        Raises:
            InvalidCredentialsError: 認証情報が無効な場合
            InactiveUserError: ユーザーが無効化されている場合
        """
        # ユーザーを検索
        user = await self._user_repository.find_by_email(email)
        if user is None:
            raise InvalidCredentialsError()

        # パスワードを検証
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        # ユーザーがアクティブか確認
        if not user.can_login():
            raise InactiveUserError()

        # JWTトークンを生成
        # セキュリティ：最小限の情報のみをトークンに含める
        # JWTは署名されているが暗号化されていないため、ペイロードは誰でも読める
        # 必要に応じて、認証が必要なエンドポイントでユーザー情報をDBから取得
        access_token = create_access_token(
            data={
                "sub": str(user.id),  # ユーザーID（subject）
                "type": "access",  # トークンタイプの明示
            }
        )

        return user, access_token


class ResetPasswordUseCase:
    """
    パスワードリセットユースケース

    ユーザーIDを指定してパスワードをリセットします。
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        """
        Args:
            user_repository: ユーザーリポジトリ
        """
        self._user_repository = user_repository

    async def execute(self, user_id: int, new_password: str) -> UserEntity:
        """
        パスワードをリセット

        Args:
            user_id: ユーザーID
            new_password: 新しいパスワード

        Returns:
            UserEntity: 更新されたユーザーエンティティ

        Raises:
            UserNotFoundError: ユーザーが見つからない場合
        """
        # パスワードをハッシュ化
        hashed_password = hash_password(new_password)

        # パスワードを更新
        user = await self._user_repository.update_password(user_id, hashed_password)

        return user
