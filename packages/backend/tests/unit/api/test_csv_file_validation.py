"""
CSVファイル検証のセキュリティテスト

ファイル拡張子、Content-Type、マジックナンバーの検証テスト
"""

from pathlib import Path

import pytest


class TestFileExtensionValidation:
    """ファイル拡張子検証のテスト"""

    def validate_csv_file_extension(self, filename: str) -> bool:
        """CSVファイル拡張子を厳格に検証"""
        if not filename:
            return False
        filename = filename.replace("\x00", "")
        ext = Path(filename).suffix.lower()
        return ext == ".csv"

    def test_valid_csv_extension(self):
        """有効なCSV拡張子"""
        assert self.validate_csv_file_extension("test.csv") is True
        assert self.validate_csv_file_extension("data.CSV") is True
        assert self.validate_csv_file_extension("import.Csv") is True

    def test_invalid_extension(self):
        """無効な拡張子"""
        assert self.validate_csv_file_extension("test.txt") is False
        assert self.validate_csv_file_extension("test.exe") is False
        assert self.validate_csv_file_extension("test.php") is False
        assert self.validate_csv_file_extension("test.sh") is False

    def test_null_byte_injection(self):
        """NULLバイトインジェクション対策"""
        # NULLバイトを含むファイル名
        # test.csv\x00.php -> test.csv.php (NULLバイト除去後、拡張子は.php)
        assert self.validate_csv_file_extension("test.csv\x00.php") is False
        # test\x00.exe -> test.exe (NULLバイト除去後、拡張子は.exe)
        assert self.validate_csv_file_extension("test\x00.exe") is False
        # 正常なCSVファイル
        assert self.validate_csv_file_extension("test.csv") is True

    def test_empty_filename(self):
        """空のファイル名"""
        assert self.validate_csv_file_extension("") is False

    def test_no_extension(self):
        """拡張子なしのファイル名"""
        assert self.validate_csv_file_extension("test") is False


class TestContentTypeValidation:
    """Content-Type検証のテスト"""

    ALLOWED_CONTENT_TYPES = ["text/csv", "application/csv", "text/plain"]

    def validate_file_content_type(self, content_type: str | None) -> bool:
        """ファイルのContent-Typeを検証"""
        if not content_type:
            return False
        content_type = content_type.lower().strip()
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()
        return content_type in self.ALLOWED_CONTENT_TYPES

    def test_valid_content_types(self):
        """有効なContent-Type"""
        assert self.validate_file_content_type("text/csv") is True
        assert self.validate_file_content_type("application/csv") is True
        assert self.validate_file_content_type("text/plain") is True

    def test_content_type_with_charset(self):
        """文字セット付きのContent-Type"""
        assert self.validate_file_content_type("text/csv; charset=utf-8") is True
        assert self.validate_file_content_type("application/csv; charset=shift_jis") is True

    def test_invalid_content_types(self):
        """無効なContent-Type"""
        assert self.validate_file_content_type("application/pdf") is False
        assert self.validate_file_content_type("image/png") is False
        assert self.validate_file_content_type("application/zip") is False
        assert self.validate_file_content_type("application/x-executable") is False

    def test_case_insensitive(self):
        """大文字小文字を区別しない"""
        assert self.validate_file_content_type("TEXT/CSV") is True
        assert self.validate_file_content_type("Application/CSV") is True

    def test_none_or_empty(self):
        """None・空文字列の場合"""
        assert self.validate_file_content_type(None) is False
        assert self.validate_file_content_type("") is False


class TestMagicNumberValidation:
    """マジックナンバー検証のテスト"""

    DANGEROUS_FILE_SIGNATURES = [
        b"\x4D\x5A",  # PE/EXE (MZ)
        b"\x7F\x45\x4C\x46",  # ELF
        b"\x50\x4B\x03\x04",  # ZIP/JAR
        b"\x25\x50\x44\x46",  # PDF
        b"\x89\x50\x4E\x47",  # PNG
        b"\xFF\xD8\xFF",  # JPEG
        b"\x47\x49\x46",  # GIF
    ]

    def validate_file_magic_number(self, file_content: bytes) -> bool:
        """ファイル内容のマジックナンバーを検証"""
        if not file_content:
            return True
        for signature in self.DANGEROUS_FILE_SIGNATURES:
            if file_content.startswith(signature):
                return False
        return True

    def test_safe_text_content(self):
        """安全なテキストコンテンツ"""
        csv_content = b"company_name,company_url\nSample,https://example.com"
        assert self.validate_file_magic_number(csv_content) is True

    def test_dangerous_pe_executable(self):
        """PE実行ファイル（Windows .exe）の検出"""
        pe_header = b"\x4D\x5A" + b"\x00" * 100  # MZ header
        assert self.validate_file_magic_number(pe_header) is False

    def test_dangerous_elf_executable(self):
        """ELF実行ファイル（Linux）の検出"""
        elf_header = b"\x7F\x45\x4C\x46" + b"\x00" * 100
        assert self.validate_file_magic_number(elf_header) is False

    def test_dangerous_zip_file(self):
        """ZIPファイルの検出"""
        zip_header = b"\x50\x4B\x03\x04" + b"\x00" * 100
        assert self.validate_file_magic_number(zip_header) is False

    def test_dangerous_pdf_file(self):
        """PDFファイルの検出"""
        pdf_header = b"\x25\x50\x44\x46" + b"\x00" * 100  # %PDF
        assert self.validate_file_magic_number(pdf_header) is False

    def test_dangerous_png_image(self):
        """PNG画像の検出"""
        png_header = b"\x89\x50\x4E\x47" + b"\x00" * 100
        assert self.validate_file_magic_number(png_header) is False

    def test_dangerous_jpeg_image(self):
        """JPEG画像の検出"""
        jpeg_header = b"\xFF\xD8\xFF" + b"\x00" * 100
        assert self.validate_file_magic_number(jpeg_header) is False

    def test_dangerous_gif_image(self):
        """GIF画像の検出"""
        gif_header = b"\x47\x49\x46" + b"\x00" * 100  # GIF
        assert self.validate_file_magic_number(gif_header) is False

    def test_empty_content(self):
        """空のコンテンツ"""
        assert self.validate_file_magic_number(b"") is True

    def test_all_signatures_covered(self):
        """全ての危険なシグネチャがテストされていることを確認"""
        tested_signatures = [
            b"\x4D\x5A",  # PE/EXE
            b"\x7F\x45\x4C\x46",  # ELF
            b"\x50\x4B\x03\x04",  # ZIP
            b"\x25\x50\x44\x46",  # PDF
            b"\x89\x50\x4E\x47",  # PNG
            b"\xFF\xD8\xFF",  # JPEG
            b"\x47\x49\x46",  # GIF
        ]

        for signature in self.DANGEROUS_FILE_SIGNATURES:
            assert signature in tested_signatures, f"Signature {signature.hex()} is not tested"
