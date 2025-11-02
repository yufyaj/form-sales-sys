"""
API依存性注入

FastAPIの依存性注入を使用して、リポジトリやユースケースを提供します
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from application.use_cases.user_use_cases import UserUseCases
from infrastructure.persistence.repositories.organization_repository import (
    OrganizationRepository,
)
from infrastructure.persistence.repositories.role_repository import RoleRepository
from infrastructure.persistence.repositories.user_repository import UserRepository


async def get_user_use_cases(
    session: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserUseCases, None]:
    """
    ユーザーユースケースの依存性注入

    Args:
        session: DBセッション

    Yields:
        UserUseCasesインスタンス
    """
    # リポジトリをインスタンス化
    user_repo = UserRepository(session)
    org_repo = OrganizationRepository(session)
    role_repo = RoleRepository(session)

    # ユースケースをインスタンス化
    use_cases = UserUseCases(
        user_repository=user_repo,
        organization_repository=org_repo,
        role_repository=role_repo,
    )

    yield use_cases
