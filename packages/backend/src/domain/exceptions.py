"""
ドメイン例外

ビジネスロジック違反を表現するカスタム例外を定義します。
"""


class DomainException(Exception):
    """ドメイン例外の基底クラス"""

    pass


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
        super().__init__(f"User with email {email} already exists")


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
