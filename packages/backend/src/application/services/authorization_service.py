"""
認可サービス

組織リソースへのアクセス権限チェックを一元管理します。
"""
from src.domain.exceptions import InsufficientPermissionsError


class AuthorizationService:
    """
    認可サービス

    マルチテナント環境でのリソースアクセス権限を検証します。
    """

    def check_organization_access(
        self,
        resource_organization_id: int,
        requesting_organization_id: int,
    ) -> None:
        """
        組織リソースへのアクセス権限をチェック

        Args:
            resource_organization_id: リソースが属する組織ID
            requesting_organization_id: リクエスト元の組織ID

        Raises:
            InsufficientPermissionsError: アクセス権限がない場合
        """
        if resource_organization_id != requesting_organization_id:
            raise InsufficientPermissionsError()
