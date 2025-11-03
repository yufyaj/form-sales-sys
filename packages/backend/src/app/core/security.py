"""
セキュリティユーティリティ

パスワードハッシュ化、JWT認証など、セキュリティ関連の機能を提供します。
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()

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


# JWT認証関連の定数
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # アクセストークンの有効期限（30分）


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWTアクセストークンを生成します

    Args:
        data: トークンに含めるペイロードデータ（通常はuser_id, organization_id, emailなど）
        expires_delta: トークンの有効期限（指定しない場合はデフォルト30分）

    Returns:
        str: JWT形式のアクセストークン

    Example:
        >>> token_data = {"sub": 1, "organization_id": 1, "email": "user@example.com"}
        >>> token = create_access_token(token_data)
        >>> len(token) > 100  # JWTは通常100文字以上
        True

    Security Notes:
        - HS256アルゴリズムを使用（対称鍵暗号）
        - SECRET_KEYは環境変数から取得（絶対にハードコードしない）
        - トークンには機密情報を含めない（暗号化ではなく署名のみ）
        - 短い有効期限で定期的な再認証を促す
    """
    to_encode = data.copy()

    # 有効期限を設定
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # JWTトークンを生成
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    JWTアクセストークンをデコードして検証します

    Args:
        token: 検証するJWTトークン

    Returns:
        dict | None: デコードされたペイロード、検証失敗の場合はNone

    Example:
        >>> token = create_access_token({"sub": 1, "email": "user@example.com"})
        >>> payload = decode_access_token(token)
        >>> payload["sub"]
        1

    Security Notes:
        - トークンの署名を検証（改ざん検知）
        - 有効期限を検証（期限切れトークンを拒否）
        - JWTErrorをキャッチしてNoneを返す（例外を外部に漏らさない）
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        # トークンが無効（署名不正、期限切れ、形式不正など）
        return None
