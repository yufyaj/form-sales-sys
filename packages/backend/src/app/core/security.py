"""
セキュリティユーティリティ

パスワードハッシュ化、JWT認証など、セキュリティ関連の機能を提供します。
"""
from passlib.context import CryptContext

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
