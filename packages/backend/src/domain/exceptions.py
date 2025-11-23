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


class SalesCompanyStaffNotFoundError(DomainException):
    """営業支援会社担当者が見つからない場合の例外"""

    def __init__(self, staff_id: int | None = None) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("Sales company staff not found")


class WorkerNotFoundError(DomainException):
    """ワーカーが見つからない場合の例外"""

    def __init__(self, worker_id: int | None = None) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("Worker not found")


class ProjectNotFoundError(ResourceNotFoundException):
    """プロジェクトが見つからない場合の例外"""

    def __init__(self, project_id: int) -> None:
        super().__init__(f"Project with id {project_id} not found")


class BusinessRuleViolationException(DomainException):
    """ビジネスルール違反の基底例外"""

    pass


class ProjectCannotBeEditedError(BusinessRuleViolationException):
    """プロジェクトが編集不可能な状態の場合の例外"""

    def __init__(self, project_id: int, reason: str = "Project is archived or deleted") -> None:
        super().__init__(f"Project {project_id} cannot be edited: {reason}")


# ========================================
# Phase3: リスト管理例外
# ========================================


class ListNotFoundError(ResourceNotFoundException):
    """リストが見つからない場合の例外"""

    def __init__(self, list_id: int) -> None:
        super().__init__(f"List with id {list_id} not found")


class ListItemNotFoundError(DomainException):
    """リスト項目が見つからない場合の例外"""

    def __init__(self, list_item_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        # 内部ログ用にはIDを保持するが、メッセージには含めない
        super().__init__("List item not found", {"list_item_id": list_item_id})


class CustomColumnSettingNotFoundError(DomainException):
    """カスタムカラム設定が見つからない場合の例外"""

    def __init__(self, custom_column_setting_id: int) -> None:
        super().__init__(f"Custom column setting with id {custom_column_setting_id} not found")


class ListItemCustomValueNotFoundError(DomainException):
    """リスト項目カスタム値が見つからない場合の例外"""

    def __init__(self, list_item_custom_value_id: int) -> None:
        super().__init__(f"List item custom value with id {list_item_custom_value_id} not found")


class ListCannotBeEditedError(BusinessRuleViolationException):
    """リストが編集不可能な状態の場合の例外"""

    def __init__(self, list_id: int, reason: str = "List is already accepted") -> None:
        super().__init__(f"List {list_id} cannot be edited: {reason}")


class ListInvalidStatusTransitionError(BusinessRuleViolationException):
    """リストステータスの遷移が不正な場合の例外"""

    def __init__(self, list_id: int, current_status: str, target_status: str) -> None:
        super().__init__(
            f"List {list_id} cannot transition from {current_status} to {target_status}",
            {"current_status": current_status, "target_status": target_status},
        )


class NgListDomainNotFoundError(DomainException):
    """NGリストドメインが見つからない場合の例外"""

    def __init__(self, ng_domain_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        # 内部ログ用にはIDを保持するが、メッセージには含めない
        super().__init__("NG list domain not found", {"ng_domain_id": ng_domain_id})


class DuplicateNgDomainError(DomainException):
    """NGドメインが既に登録されている場合の例外"""

    def __init__(self, domain_pattern: str, list_id: int) -> None:
        # セキュリティ: list_idを公開しない（IDOR攻撃の情報収集を防ぐ）
        # 内部ログ用には情報を保持するが、メッセージには含めない
        super().__init__(
            "このドメインパターンは既に登録されています",
            {"domain_pattern": domain_pattern, "list_id": list_id},
        )
class NoSendSettingNotFoundError(ResourceNotFoundException):
    """送信禁止設定が見つからない場合の例外"""

    def __init__(self, no_send_setting_id: int) -> None:
        super().__init__(f"No send setting with id {no_send_setting_id} not found")


class InvalidNoSendSettingError(ValidationException):
    """送信禁止設定の内容が不正な場合の例外"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


# ========================================
# Phase4: ワーカー割り当て例外
# ========================================


class ListItemAssignmentNotFoundError(DomainException):
    """リスト項目割り当てが見つからない場合の例外"""

    def __init__(self, assignment_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("Assignment not found", {"assignment_id": assignment_id})


class DuplicateAssignmentError(DomainException):
    """重複割り当てエラー"""

    def __init__(self, list_item_id: int, worker_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__(
            "このワーカーは既にこのリスト項目に割り当てられています",
            {"list_item_id": list_item_id, "worker_id": worker_id},
        )


class ListScriptNotFoundError(ResourceNotFoundException):
    """リストスクリプトが見つからない場合の例外"""

    def __init__(self, script_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("List script not found", {"script_id": script_id})


# ========================================
# Phase5: 作業記録例外
# ========================================


class WorkRecordNotFoundError(ResourceNotFoundException):
    """作業記録が見つからない場合の例外"""

    def __init__(self, record_id: int) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("Work record not found", {"record_id": record_id})


class CannotSendReasonNotFoundError(ResourceNotFoundException):
    """送信不可理由が見つからない場合の例外"""

    def __init__(self, reason_id: int) -> None:
        super().__init__(f"Cannot send reason with id {reason_id} not found")


# ========================================
# Phase5: ワーカー質問例外
# ========================================


class WorkerQuestionNotFoundError(DomainException):
    """ワーカー質問が見つからない場合の例外"""

    def __init__(self, question_id: int | None = None) -> None:
        # セキュリティ: IDを公開しない（IDOR攻撃の情報収集を防ぐ）
        super().__init__("Worker question not found")


class WorkerQuestionCannotBeAnsweredError(BusinessRuleViolationException):
    """質問が回答不可能な状態の場合の例外"""

    def __init__(self, question_id: int, reason: str = "Question is already answered or closed") -> None:
        super().__init__(f"Question {question_id} cannot be answered: {reason}")


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
ClientOrganizationNotFoundException = ClientOrganizationNotFoundError
ClientContactNotFoundException = ClientContactNotFoundError
