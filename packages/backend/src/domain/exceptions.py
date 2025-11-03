"""
ドメイン例外

ビジネスロジック違反を表現するカスタム例外を定義します。
"""

from typing import Any


class DomainException(Exception):
    """ドメイン例外の基底クラス"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class UserNotFoundError(DomainException):
    """ユーザーが見つからない場合の例外"""

    def __init__(self, user_id: int | None = None, email: str | None = None) -> None:
        if user_id:
            super().__init__(f"User with id {user_id} not found")
        elif email:
            super().__init__(f"User with email {email} not found")
        else:
            super().__init__("User not found")


class DuplicateEmailError(DomainException):
    """メールアドレスが既に存在する場合の例外"""

    def __init__(self, email: str) -> None:
        super().__init__(f"このメールアドレスは既に使用されています", {"email": email})


class InvalidCredentialsError(DomainException):
    """認証情報が無効な場合の例外"""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class InactiveUserError(DomainException):
    """ユーザーが無効化されている場合の例外"""

    def __init__(self) -> None:
        super().__init__("User account is inactive")


class InvalidTokenError(DomainException):
    """トークンが無効な場合の例外"""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message)


class OrganizationNotFoundError(DomainException):
    """組織が見つからない場合の例外"""

    def __init__(self, organization_id: int) -> None:
        super().__init__(f"Organization with id {organization_id} not found")


class RoleNotFoundError(DomainException):
    """ロールが見つからない場合の例外"""

    def __init__(self, role_id: int | None = None, role_name: str | None = None) -> None:
        if role_id:
            super().__init__(f"Role with id {role_id} not found")
        elif role_name:
            super().__init__(f"Role with name {role_name} not found")
        else:
            super().__init__("Role not found")


# ========================================
# カテゴリ別の基底例外クラス
# ========================================


class ResourceNotFoundException(DomainException):
    """リソースが見つからない場合の基底例外"""

    pass


class ValidationException(DomainException):
    """バリデーションエラーの基底例外"""

    pass


class AuthorizationException(DomainException):
    """認可エラーの基底例外"""

    pass


class BusinessRuleViolationException(DomainException):
    """ビジネスルール違反の基底例外"""

    pass


# ========================================
# ユーザー管理APIとの互換性のためのエイリアス
# ========================================

# ユーザー管理APIでは Exception サフィックスを使用しているため、エイリアスを定義
UserNotFoundException = UserNotFoundError
DuplicateEmailException = DuplicateEmailError
InvalidCredentialsException = InvalidCredentialsError
InactiveUserException = InactiveUserError
OrganizationNotFoundException = OrganizationNotFoundError
RoleNotFoundException = RoleNotFoundError
