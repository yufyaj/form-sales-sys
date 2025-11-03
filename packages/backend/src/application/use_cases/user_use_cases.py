"""
ユーザー管理のユースケース

ユーザーのCRUD操作とビジネスロジックを実行します
"""



from src.app.core.security import hash_password, verify_password
from src.application.schemas.user import (
    PasswordChangeRequest,
    UserCreateRequest,
    UserUpdateRequest,
)
from src.domain.exceptions import (
    DuplicateEmailException,
    InvalidCredentialsException,
    OrganizationNotFoundException,
    UserNotFoundException,
)
from src.domain.interfaces.organization_repository import IOrganizationRepository
from src.domain.interfaces.role_repository import IRoleRepository
from src.domain.interfaces.user_repository import IUserRepository
from src.infrastructure.persistence.models.user import User


class UserUseCases:
    """ユーザー管理のユースケースクラス"""

    def __init__(
        self,
        user_repository: IUserRepository,
        organization_repository: IOrganizationRepository,
        role_repository: IRoleRepository,
    ) -> None:
        """
        Args:
            user_repository: ユーザーリポジトリ
            organization_repository: 組織リポジトリ
            role_repository: ロールリポジトリ
        """
        self._user_repo = user_repository
        self._org_repo = organization_repository
        self._role_repo = role_repository

    async def create_user(self, request: UserCreateRequest) -> User:
        """
        新規ユーザーを作成

        Args:
            request: ユーザー作成リクエスト

        Returns:
            作成されたユーザー

        Raises:
            OrganizationNotFoundException: 組織が見つからない場合
            DuplicateEmailException: メールアドレスが重複している場合
        """
        # 組織の存在確認
        organization = await self._org_repo.find_by_id(request.organization_id)
        if organization is None:
            raise OrganizationNotFoundException(organization_id=str(request.organization_id))

        # メールアドレスの重複チェック
        if await self._user_repo.exists_by_email(request.email, request.organization_id):
            raise DuplicateEmailException(email=request.email)

        # パスワードをハッシュ化
        hashed_password = hash_password(request.password)

        # ユーザーエンティティを作成
        user = User(
            email=request.email,
            full_name=request.full_name,
            hashed_password=hashed_password,
            organization_id=request.organization_id,
            is_active=True,  # デフォルトでアクティブ
            is_email_verified=False,  # メール未確認
        )

        # リポジトリで永続化
        created_user = await self._user_repo.create(user)
        return created_user

    async def get_user(self, user_id: int, organization_id: int) -> User:
        """
        ユーザーを取得

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（マルチテナント対応）

        Returns:
            ユーザー

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
        """
        user = await self._user_repo.find_by_id(user_id, organization_id)
        if user is None:
            raise UserNotFoundException(user_id=str(user_id))
        return user

    async def list_users(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[User], int]:
        """
        組織のユーザー一覧を取得

        Args:
            organization_id: 組織ID
            skip: スキップする件数
            limit: 取得する最大件数

        Returns:
            (ユーザーリスト, 総件数)のタプル
        """
        users = await self._user_repo.list_by_organization(
            organization_id=organization_id,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )
        total = await self._user_repo.count_by_organization(
            organization_id=organization_id,
            include_deleted=False,
        )
        return list(users), total

    async def update_user(
        self,
        user_id: int,
        organization_id: int,
        request: UserUpdateRequest,
    ) -> User:
        """
        ユーザー情報を更新

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（マルチテナント対応）
            request: 更新リクエスト

        Returns:
            更新されたユーザー

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            DuplicateEmailException: メールアドレスが重複している場合
        """
        # ユーザーを取得
        user = await self._user_repo.find_by_id(user_id, organization_id)
        if user is None:
            raise UserNotFoundException(user_id=str(user_id))

        # メールアドレスの変更をチェック
        if request.email is not None and request.email != user.email:
            if await self._user_repo.exists_by_email(request.email, organization_id):
                raise DuplicateEmailException(email=request.email)
            user.email = request.email
            user.is_email_verified = False  # メールアドレス変更時は再確認が必要

        # その他のフィールドを更新
        if request.full_name is not None:
            user.full_name = request.full_name

        if request.is_active is not None:
            user.is_active = request.is_active

        if request.is_email_verified is not None:
            user.is_email_verified = request.is_email_verified

        # リポジトリで永続化
        updated_user = await self._user_repo.update(user)
        return updated_user

    async def delete_user(self, user_id: int, organization_id: int) -> None:
        """
        ユーザーを論理削除

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（マルチテナント対応）

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            CannotDeleteActiveUserException: アクティブなユーザーを削除しようとした場合
        """
        await self._user_repo.soft_delete(user_id, organization_id)

    async def change_password(
        self,
        user_id: int,
        organization_id: int,
        request: PasswordChangeRequest,
    ) -> None:
        """
        パスワードを変更

        Args:
            user_id: ユーザーID
            organization_id: 組織ID
            request: パスワード変更リクエスト

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            InvalidCredentialsException: 現在のパスワードが正しくない場合
        """
        # ユーザーを取得
        user = await self._user_repo.find_by_id(user_id, organization_id)
        if user is None:
            raise UserNotFoundException(user_id=str(user_id))

        # 現在のパスワードを確認
        if not verify_password(request.current_password, user.hashed_password):
            raise InvalidCredentialsException()

        # 新しいパスワードをハッシュ化して設定
        user.hashed_password = hash_password(request.new_password)

        # リポジトリで永続化
        await self._user_repo.update(user)

    async def assign_role(
        self,
        user_id: int,
        organization_id: int,
        role_id: int,
    ) -> None:
        """
        ユーザーにロールを割り当て

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（マルチテナント対応）
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        # ユーザーの存在確認（マルチテナント対応）
        user = await self._user_repo.find_by_id(user_id, organization_id)
        if user is None:
            raise UserNotFoundException(user_id=str(user_id))

        # ロールを割り当て
        await self._role_repo.assign_role_to_user(user_id, role_id)

    async def remove_role(
        self,
        user_id: int,
        organization_id: int,
        role_id: int,
    ) -> None:
        """
        ユーザーからロールを削除

        Args:
            user_id: ユーザーID
            organization_id: 組織ID（マルチテナント対応）
            role_id: ロールID

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
            RoleNotFoundException: ロールが見つからない場合
        """
        # ユーザーの存在確認（マルチテナント対応）
        user = await self._user_repo.find_by_id(user_id, organization_id)
        if user is None:
            raise UserNotFoundException(user_id=str(user_id))

        # ロールを削除
        await self._role_repo.remove_role_from_user(user_id, role_id)

    async def get_user_with_roles(self, user_id: int, organization_id: int) -> tuple[User, list]:
        """
        ユーザーとそのロール一覧を取得

        Args:
            user_id: ユーザーID
            organization_id: 組織ID

        Returns:
            (ユーザー, ロールリスト)のタプル

        Raises:
            UserNotFoundException: ユーザーが見つからない場合
        """
        # ユーザーを取得
        user = await self.get_user(user_id, organization_id)

        # ロール一覧を取得
        roles = await self._role_repo.get_user_roles(user_id)

        return user, list(roles)
