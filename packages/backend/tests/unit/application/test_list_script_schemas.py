"""
スクリプトスキーマのテスト

入力バリデーション、NULL文字・制御文字のチェックをテストします。
"""
import pytest
from pydantic import ValidationError

from src.application.schemas.list_script import (
    ListScriptCreate,
    ListScriptUpdate,
)


class TestListScriptCreate:
    """ListScriptCreateスキーマのテスト"""

    def test_valid_script_creation(self) -> None:
        """正常なスクリプト作成リクエストが検証を通過すること"""
        # Arrange & Act
        schema = ListScriptCreate(
            list_id=1,
            title="テストスクリプト",
            content="テスト内容です。",
        )

        # Assert
        assert schema.list_id == 1
        assert schema.title == "テストスクリプト"
        assert schema.content == "テスト内容です。"

    def test_trim_whitespace(self) -> None:
        """前後の空白が除去されること"""
        # Arrange & Act
        schema = ListScriptCreate(
            list_id=1,
            title="  タイトル  ",
            content="  内容  ",
        )

        # Assert
        assert schema.title == "タイトル"
        assert schema.content == "内容"

    def test_reject_null_character_in_title(self) -> None:
        """タイトルにNULL文字が含まれる場合、バリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="タイトル\x00悪意のある文字",
                content="正常な内容",
            )

        # エラーメッセージを確認
        errors = exc_info.value.errors()
        assert any("NULL文字は使用できません" in str(error) for error in errors)

    def test_reject_null_character_in_content(self) -> None:
        """本文にNULL文字が含まれる場合、バリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="正常なタイトル",
                content="内容\x00悪意のある文字",
            )

        errors = exc_info.value.errors()
        assert any("NULL文字は使用できません" in str(error) for error in errors)

    def test_reject_control_characters(self) -> None:
        """危険な制御文字が含まれる場合、バリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="タイトル\x01制御文字",
                content="正常な内容",
            )

        errors = exc_info.value.errors()
        assert any("制御文字は使用できません" in str(error) for error in errors)

    def test_allow_newline_and_tab(self) -> None:
        """改行とタブは許可されること"""
        # Arrange & Act
        schema = ListScriptCreate(
            list_id=1,
            title="タイトル",
            content="こんにちは。\n本日はよろしくお願いします。\t敬具",
        )

        # Assert
        assert "\n" in schema.content
        assert "\t" in schema.content

    def test_reject_empty_title(self) -> None:
        """空のタイトルはバリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="",
                content="正常な内容",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)

    def test_reject_empty_content(self) -> None:
        """空の本文はバリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="正常なタイトル",
                content="",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_short" for error in errors)

    def test_reject_title_too_long(self) -> None:
        """256文字以上のタイトルはバリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="あ" * 256,
                content="正常な内容",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_reject_content_too_long(self) -> None:
        """100001文字以上の本文はバリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=1,
                title="正常なタイトル",
                content="あ" * 100001,
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_too_long" for error in errors)

    def test_reject_invalid_list_id(self) -> None:
        """0以下のlist_idはバリデーションエラーとなること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptCreate(
                list_id=0,
                title="正常なタイトル",
                content="正常な内容",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "greater_than" for error in errors)


class TestListScriptUpdate:
    """ListScriptUpdateスキーマのテスト"""

    def test_partial_update_title_only(self) -> None:
        """タイトルのみの部分更新が可能なこと"""
        # Arrange & Act
        schema = ListScriptUpdate(title="新しいタイトル")

        # Assert
        assert schema.title == "新しいタイトル"
        assert schema.content is None

    def test_partial_update_content_only(self) -> None:
        """本文のみの部分更新が可能なこと"""
        # Arrange & Act
        schema = ListScriptUpdate(content="新しい内容")

        # Assert
        assert schema.title is None
        assert schema.content == "新しい内容"

    def test_reject_null_character_in_update(self) -> None:
        """更新時もNULL文字が拒否されること"""
        # Arrange & Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ListScriptUpdate(title="タイトル\x00悪意")

        errors = exc_info.value.errors()
        assert any("NULL文字は使用できません" in str(error) for error in errors)

    def test_allow_none_values(self) -> None:
        """Noneが許可されること（部分更新のため）"""
        # Arrange & Act
        schema = ListScriptUpdate()

        # Assert
        assert schema.title is None
        assert schema.content is None
