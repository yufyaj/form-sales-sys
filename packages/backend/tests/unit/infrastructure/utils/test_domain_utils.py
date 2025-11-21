"""
ドメイン判定ユーティリティの単体テスト

TDDサイクルに従って、ドメイン抽出・正規化・マッチングロジックをテストします。
"""

import pytest

from src.infrastructure.utils.domain_utils import (
    extract_domain_from_url,
    normalize_domain_pattern,
    is_wildcard_pattern,
    is_domain_in_ng_list,
)


class TestExtractDomainFromUrl:
    """URLからドメインを抽出する関数のテスト"""

    def test_extract_domain_from_https_url(self) -> None:
        """HTTPS URLからドメインを抽出"""
        result = extract_domain_from_url("https://www.example.com/path")
        assert result == "example.com"

    def test_extract_domain_from_http_url(self) -> None:
        """HTTP URLからドメインを抽出"""
        result = extract_domain_from_url("http://www.example.com/path")
        assert result == "example.com"

    def test_extract_domain_without_www(self) -> None:
        """wwwなしのURLからドメインを抽出"""
        result = extract_domain_from_url("https://example.com/path")
        assert result == "example.com"

    def test_extract_domain_with_subdomain(self) -> None:
        """サブドメインを含むURLからドメインを抽出"""
        result = extract_domain_from_url("https://sub.example.com/path")
        assert result == "sub.example.com"

    def test_extract_domain_with_port(self) -> None:
        """ポート番号を含むURLからドメインを抽出"""
        result = extract_domain_from_url("http://example.com:8080/path")
        assert result == "example.com"

    def test_extract_domain_without_scheme(self) -> None:
        """スキームなしのURLからドメインを抽出"""
        result = extract_domain_from_url("www.example.com")
        assert result == "example.com"

    def test_extract_domain_from_empty_string(self) -> None:
        """空文字列の場合はNoneを返す"""
        result = extract_domain_from_url("")
        assert result is None

    def test_extract_domain_from_invalid_url(self) -> None:
        """無効なURLの場合はNoneを返す"""
        result = extract_domain_from_url("not-a-valid-url")
        assert result is None

    def test_extract_domain_case_insensitive(self) -> None:
        """大文字小文字を正規化"""
        result = extract_domain_from_url("https://WWW.EXAMPLE.COM/path")
        assert result == "example.com"


class TestNormalizeDomainPattern:
    """ドメインパターンを正規化する関数のテスト"""

    def test_normalize_lowercase(self) -> None:
        """小文字に正規化"""
        result = normalize_domain_pattern("EXAMPLE.COM")
        assert result == "example.com"

    def test_normalize_remove_www(self) -> None:
        """www.プレフィックスを除去"""
        result = normalize_domain_pattern("www.example.com")
        assert result == "example.com"

    def test_normalize_strip_whitespace(self) -> None:
        """前後の空白を除去"""
        result = normalize_domain_pattern("  example.com  ")
        assert result == "example.com"

    def test_normalize_wildcard_pattern(self) -> None:
        """ワイルドカードパターンは正規化"""
        result = normalize_domain_pattern("*.EXAMPLE.COM")
        assert result == "*.example.com"

    def test_normalize_combined(self) -> None:
        """複合的な正規化"""
        result = normalize_domain_pattern("  WWW.EXAMPLE.COM  ")
        assert result == "example.com"


class TestIsWildcardPattern:
    """ワイルドカードパターンかを判定する関数のテスト"""

    def test_is_wildcard_pattern_true(self) -> None:
        """ワイルドカードを含むパターン"""
        assert is_wildcard_pattern("*.example.com") is True

    def test_is_wildcard_pattern_false(self) -> None:
        """ワイルドカードを含まないパターン"""
        assert is_wildcard_pattern("example.com") is False


class TestIsDomainInNgList:
    """ドメインがNGリストに含まれるかチェックする関数のテスト"""

    def test_exact_match(self) -> None:
        """完全一致でマッチ"""
        ng_patterns = ["example.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("example.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "example.com"

    def test_wildcard_match(self) -> None:
        """ワイルドカードパターンでマッチ"""
        ng_patterns = ["*.example.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("sub.example.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "*.example.com"

    def test_subdomain_match(self) -> None:
        """サブドメインマッチ（*.example.comの簡易版）"""
        ng_patterns = ["example.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("sub.example.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "example.com"

    def test_no_match(self) -> None:
        """マッチしない場合"""
        ng_patterns = ["example.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("other.com", ng_patterns)
        assert is_ng is False
        assert matched_pattern is None

    def test_multiple_patterns_first_match(self) -> None:
        """複数パターンで最初のマッチ"""
        ng_patterns = ["example.com", "test.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("example.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "example.com"

    def test_multiple_patterns_second_match(self) -> None:
        """複数パターンで2番目のマッチ"""
        ng_patterns = ["example.com", "test.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("test.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "test.com"

    def test_empty_ng_list(self) -> None:
        """NGリストが空の場合"""
        ng_patterns: list[str] = []
        is_ng, matched_pattern = is_domain_in_ng_list("example.com", ng_patterns)
        assert is_ng is False
        assert matched_pattern is None

    def test_complex_wildcard(self) -> None:
        """複雑なワイルドカードパターン"""
        ng_patterns = ["*.sub.example.com"]
        is_ng, matched_pattern = is_domain_in_ng_list("test.sub.example.com", ng_patterns)
        assert is_ng is True
        assert matched_pattern == "*.sub.example.com"
