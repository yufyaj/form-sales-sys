"""
グローバル例外ハンドラー

ドメイン層の例外を適切なHTTPレスポンスに変換します
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from domain.exceptions import (
    AuthorizationException,
    BusinessRuleViolationException,
    DomainException,
    ResourceNotFoundException,
    ValidationException,
)


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    ドメイン例外のグローバルハンドラー

    ドメイン層の例外を適切なHTTPステータスコードとメッセージに変換します。

    Args:
        request: FastAPIリクエスト
        exc: ドメイン例外

    Returns:
        JSONレスポンス
    """
    # 例外の種類に応じてHTTPステータスコードを決定
    if isinstance(exc, ResourceNotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationException):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuthorizationException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, BusinessRuleViolationException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    else:
        # その他のドメイン例外は400 Bad Request
        status_code = status.HTTP_400_BAD_REQUEST

    # エラーレスポンスを構築
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__,
            }
        },
    )
