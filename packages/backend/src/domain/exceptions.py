"""
ドメイン層のカスタム例外定義

ビジネスルール違反やエンティティの状態に関する例外を定義します。
これらの例外はアプリケーション層で送出され、プレゼンテーション層で
適切なHTTPレスポンスに変換されます。
"""

from typing import Any


class DomainException(Exception):
    """ドメイン層の基底例外クラス"""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """
        Args:
            message: エラーメッセージ
            details: エラーの詳細情報（任意）
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


# ========================================
# リソース未検出系
# ========================================


class ResourceNotFoundException(DomainException):
    """リソースが見つからない場合の例外"""

    pass


class UserNotFoundException(ResourceNotFoundException):
    """ユーザーが見つからない場合の例外"""

    def __init__(self, user_id: str | None = None, email: str | None = None) -> None:
        details = {}
        if user_id:
            details["user_id"] = user_id
        if email:
            details["email"] = email
        super().__init__("ユーザーが見つかりません", details)


class OrganizationNotFoundException(ResourceNotFoundException):
    """組織が見つからない場合の例外"""

    def __init__(self, organization_id: str) -> None:
        super().__init__(
            "組織が見つかりません",
            {"organization_id": organization_id},
        )


class RoleNotFoundException(ResourceNotFoundException):
    """ロールが見つからない場合の例外"""

    def __init__(self, role_id: str | None = None, role_name: str | None = None) -> None:
        details = {}
        if role_id:
            details["role_id"] = role_id
        if role_name:
            details["role_name"] = role_name
        super().__init__("ロールが見つかりません", details)


# ========================================
# バリデーション・ビジネスルール違反系
# ========================================


class ValidationException(DomainException):
    """バリデーションエラーの例外"""

    pass


class DuplicateResourceException(ValidationException):
    """リソースの重複エラー"""

    pass


class DuplicateEmailException(DuplicateResourceException):
    """メールアドレスの重複エラー"""

    def __init__(self, email: str) -> None:
        super().__init__(
            "このメールアドレスは既に使用されています",
            {"email": email},
        )


class InvalidCredentialsException(ValidationException):
    """認証情報が無効な場合の例外"""

    def __init__(self) -> None:
        super().__init__("メールアドレスまたはパスワードが正しくありません")


class InactiveUserException(ValidationException):
    """非アクティブなユーザーがログインしようとした場合の例外"""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            "このアカウントは無効化されています",
            {"user_id": user_id},
        )


class EmailNotVerifiedException(ValidationException):
    """メールアドレス未確認のユーザーがアクセスしようとした場合の例外"""

    def __init__(self, user_id: str, email: str) -> None:
        super().__init__(
            "メールアドレスの確認が完了していません",
            {"user_id": user_id, "email": email},
        )


# ========================================
# 権限・認可系
# ========================================


class AuthorizationException(DomainException):
    """認可エラーの基底例外"""

    pass


class InsufficientPermissionException(AuthorizationException):
    """権限不足の例外"""

    def __init__(self, required_permission: str) -> None:
        super().__init__(
            "この操作を実行する権限がありません",
            {"required_permission": required_permission},
        )


class OrganizationMismatchException(AuthorizationException):
    """組織の不一致エラー（マルチテナント違反）"""

    def __init__(
        self,
        user_organization_id: str,
        resource_organization_id: str,
    ) -> None:
        super().__init__(
            "異なる組織のリソースにアクセスできません",
            {
                "user_organization_id": user_organization_id,
                "resource_organization_id": resource_organization_id,
            },
        )


# ========================================
# ビジネスロジック系
# ========================================


class BusinessRuleViolationException(DomainException):
    """ビジネスルール違反の例外"""

    pass


class CannotDeleteActiveUserException(BusinessRuleViolationException):
    """アクティブなユーザーを削除しようとした場合の例外"""

    def __init__(self, user_id: str) -> None:
        super().__init__(
            "アクティブなユーザーは削除できません。先に無効化してください。",
            {"user_id": user_id},
        )


class CannotModifySystemRoleException(BusinessRuleViolationException):
    """システムロールを変更しようとした場合の例外"""

    def __init__(self, role_name: str) -> None:
        super().__init__(
            "システムロールは変更できません",
            {"role_name": role_name},
        )
