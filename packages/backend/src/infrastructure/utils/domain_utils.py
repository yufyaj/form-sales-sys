"""
ドメイン判定ユーティリティ

URLからのドメイン抽出、正規化、NGドメインマッチングなどの
ドメイン関連のユーティリティ関数を提供します。
"""
from urllib.parse import urlparse
import fnmatch


def extract_domain_from_url(url: str) -> str | None:
    """
    URLからドメインを抽出し、正規化する

    Args:
        url: URL文字列（例: "https://www.example.com/path"）

    Returns:
        正規化されたドメイン（例: "example.com"）
        無効なURLの場合はNone

    Examples:
        >>> extract_domain_from_url("https://www.example.com/path")
        "example.com"
        >>> extract_domain_from_url("http://sub.example.com:8080/")
        "sub.example.com"
        >>> extract_domain_from_url("www.example.com")
        "example.com"
    """
    if not url:
        return None

    # スキームがない場合は追加（urlparseの挙動を安定化）
    if not url.startswith(('http://', 'https://', 'ftp://')):
        url = 'https://' + url

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # ポート番号を除去
        if ':' in domain:
            domain = domain.split(':')[0]

        # www.プレフィックスを除去（正規化）
        if domain.startswith('www.'):
            domain = domain[4:]

        # 有効なドメイン形式かチェック（最低限、ドットを含むこと）
        if domain and '.' in domain:
            return domain
        else:
            return None
    except Exception:
        return None


def normalize_domain_pattern(pattern: str) -> str:
    """
    NGドメインパターンを正規化

    Args:
        pattern: ドメインパターン（例: "*.example.com", "example.com"）

    Returns:
        正規化されたパターン

    Examples:
        >>> normalize_domain_pattern("*.Example.Com")
        "*.example.com"
        >>> normalize_domain_pattern("  www.example.com  ")
        "example.com"
    """
    pattern = pattern.lower().strip()

    # www.プレフィックスを除去（一貫性のため）
    # ただし、ワイルドカードパターンの場合は除去しない
    if pattern.startswith('www.') and not pattern.startswith('*.'):
        pattern = pattern[4:]

    return pattern


def is_wildcard_pattern(pattern: str) -> bool:
    """
    ワイルドカードパターンかを判定

    Args:
        pattern: ドメインパターン

    Returns:
        ワイルドカードを含む場合True

    Examples:
        >>> is_wildcard_pattern("*.example.com")
        True
        >>> is_wildcard_pattern("example.com")
        False
    """
    return '*' in pattern


def is_domain_in_ng_list(
    domain: str,
    ng_patterns: list[str]
) -> tuple[bool, str | None]:
    """
    ドメインがNGリストに含まれるかチェック

    Args:
        domain: チェック対象のドメイン（正規化済み）
        ng_patterns: NGドメインパターンのリスト

    Returns:
        (NGフラグ, マッチしたパターン)
            - NGフラグ: NGリストに含まれる場合True
            - マッチしたパターン: マッチしたNGドメインパターン（NGでない場合はNone）

    Examples:
        >>> is_domain_in_ng_list("example.com", ["example.com"])
        (True, "example.com")
        >>> is_domain_in_ng_list("sub.example.com", ["*.example.com"])
        (True, "*.example.com")
        >>> is_domain_in_ng_list("other.com", ["example.com"])
        (False, None)
    """
    for pattern in ng_patterns:
        # ワイルドカード使用の場合
        if '*' in pattern:
            if fnmatch.fnmatch(domain, pattern):
                return (True, pattern)
        # 完全一致
        elif domain == pattern:
            return (True, pattern)
        # サブドメインマッチング（*.example.comの簡易版）
        # パターンがexample.comの場合、sub.example.comもマッチさせる
        elif domain.endswith('.' + pattern):
            return (True, pattern)

    return (False, None)
