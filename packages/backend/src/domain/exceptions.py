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


class InvalidDateRangeError(ValidationException):
    """日付範囲が不正な場合の例外"""

    def __init__(self, start_date: str, end_date: str) -> None:
        super().__init__(
            f"開始日（{start_date}）は終了日（{end_date}）より前である必要があります",
            {"start_date": start_date, "end_date": end_date},
        )


class InvalidBudgetError(ValidationException):
    """予算値が不正な場合の例外"""

    def __init__(self, field_name: str, value: int) -> None:
        super().__init__(
            f"{field_name}は0以上である必要があります（現在値: {value}）",
            {"field_name": field_name, "value": value},
        )


class AuthorizationException(DomainException):
    """認可エラーの基底例外"""

    pass


class InsufficientPermissionsError(AuthorizationException):
    """権限不足エラー"""

    def __init__(
        self,
        required_permissions: list[str] | None = None,
        required_roles: list[str] | None = None,
    ) -> None:
        if required_permissions:
            super().__init__(
                f"Insufficient permissions. Required: {', '.join(required_permissions)}",
                {"required_permissions": required_permissions},
            )
        elif required_roles:
            super().__init__(
                f"Insufficient roles. Required: {', '.join(required_roles)}",
                {"required_roles": required_roles},
            )
        else:
            super().__init__("Insufficient permissions")


class PermissionNotFoundError(DomainException):
    """権限が見つからない場合の例外"""

    def __init__(
        self, permission_id: int | None = None, permission_code: str | None = None
    ) -> None:
        if permission_id:
            super().__init__(f"Permission with id {permission_id} not found")
        elif permission_code:
            super().__init__(f"Permission with code {permission_code} not found")
        else:
            super().__init__("Permission not found")


class ClientOrganizationNotFoundError(DomainException):
    """顧客組織が見つからない場合の例外"""

    def __init__(self, client_organization_id: int) -> None:
        super().__init__(f"Client organization with id {client_organization_id} not found")


class ClientContactNotFoundError(DomainException):
    """顧客担当者が見つからない場合の例外"""

    def __init__(self, client_contact_id: int) -> None:
        super().__init__(f"Client contact with id {client_contact_id} not found")


class ProjectNotFoundError(DomainException):
    """プロジェクトが見つからない場合の例外"""

    def __init__(self, project_id: int) -> None:
        super().__init__(f"Project with id {project_id} not found")


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
