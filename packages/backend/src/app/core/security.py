"""
セキュリティユーティリティ

パスワードハッシュ化、JWT認証など、セキュリティ関連の機能を提供します。
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.app.core.config import get_settings

# bcryptを使用したパスワードハッシュ化コンテキスト
# bcryptは推奨されるパスワードハッシュアルゴリズムで、以下の特徴があります：
# - ソルト付き（レインボーテーブル攻撃に強い）
# - 計算コストが高い（ブルートフォース攻撃に強い）
# - 時間経過とともにコストを増やせる（将来的な攻撃にも対応可能）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    パスワードをbcryptでハッシュ化します

    Args:
        password: プレーンテキストのパスワード

    Returns:
        str: bcryptでハッシュ化されたパスワード（60文字）

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> len(hashed)
        60
        >>> hashed.startswith("$2b$")
        True

    Security Notes:
        - bcryptは自動的にソルトを生成します
        - デフォルトのコストファクターは12ラウンドです
        - ハッシュ化には約0.3秒かかります（ブルートフォース攻撃対策）
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    プレーンテキストのパスワードとハッシュ化されたパスワードを比較します

    Args:
        plain_password: ユーザーが入力したプレーンテキストのパスワード
        hashed_password: データベースに保存されているハッシュ化されたパスワード

    Returns:
        bool: パスワードが一致する場合True、それ以外はFalse

    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> verify_password("my_secure_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False

    Security Notes:
        - タイミング攻撃に対して安全です（constant-time comparison）
        - 不正なハッシュ形式の場合はFalseを返します
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # ハッシュ形式が不正な場合や検証エラーの場合
        return False


def is_password_hash(value: str) -> bool:
    """
    文字列がbcryptハッシュかどうかを判定します

    Args:
        value: 判定する文字列

    Returns:
        bool: bcryptハッシュの場合True、それ以外はFalse

    Example:
        >>> is_password_hash("$2b$12$...")
        True
        >>> is_password_hash("plain_password")
        False

    Notes:
        - bcryptハッシュは"$2b$"で始まります
        - 長さは60文字です
    """
    return value.startswith("$2b$") and len(value) == 60


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWTアクセストークンを生成します

    Args:
        data: トークンに埋め込むデータ（通常はユーザーIDなど）
        expires_delta: トークンの有効期限（指定しない場合は設定値を使用）

    Returns:
        str: JWT形式のアクセストークン

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> isinstance(token, str)
        True

    Security Notes:
        - トークンには機密情報を含めないでください
        - HS256アルゴリズムを使用（対称鍵方式）
        - 有効期限を必ず設定します（デフォルト30分）
    """
    settings = get_settings()
    to_encode = data.copy()

    # 有効期限の設定
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # JWTトークンの生成
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    JWTアクセストークンをデコードします

    Args:
        token: JWT形式のアクセストークン

    Returns:
        dict | None: デコードされたペイロード、無効な場合はNone

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        'user@example.com'

    Security Notes:
        - 有効期限が切れている場合はNoneを返します
        - 署名が不正な場合はNoneを返します
        - タイミング攻撃に対して安全です
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # トークンが不正または有効期限切れ
        return None
