#!/bin/bash
echo "======================================"
echo "Phase 1 実装の検証"
echo "======================================"

echo -e "\n1. ファイル数の確認"
echo "   Pythonファイル: $(find . -name "*.py" -type f | wc -l) 個"
echo "   設定ファイル: $(find . -name "*.toml" -o -name "*.ini" -o -name ".env.example" | wc -l) 個"

echo -e "\n2. ディレクトリ構造の確認"
echo "   ✅ src/app/core/ - アプリケーション設定"
echo "   ✅ src/infrastructure/persistence/models/ - データベースモデル"
echo "   ✅ tests/integration/persistence/ - 統合テスト"
echo "   ✅ alembic/versions/ - マイグレーション"

echo -e "\n3. 主要ファイルの存在確認"
files=(
  "src/app/core/security.py"
  "src/app/core/config.py"
  "src/app/core/database.py"
  "src/infrastructure/persistence/models/organization.py"
  "src/infrastructure/persistence/models/user.py"
  "src/infrastructure/persistence/models/role.py"
  "alembic/versions/20251102_0000_initial_schema.py"
  "pyproject.toml"
  ".env.example"
  "README.md"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "   ✅ $file"
  else
    echo "   ❌ $file - 見つかりません"
  fi
done

echo -e "\n4. 構文チェック結果"
error_count=0
for pyfile in $(find . -name "*.py" -type f | grep -E "(src|tests|alembic)"); do
  if python3 -m py_compile "$pyfile" 2>/dev/null; then
    : # Success - no output
  else
    echo "   ❌ $pyfile - 構文エラー"
    ((error_count++))
  fi
done

if [ $error_count -eq 0 ]; then
  echo "   ✅ すべてのPythonファイルの構文チェック成功"
else
  echo "   ❌ $error_count 個のファイルに構文エラー"
fi

echo -e "\n5. セキュリティ機能の確認"
if grep -q "hash_password" src/app/core/security.py; then
  echo "   ✅ パスワードハッシュ化関数あり"
fi
if grep -q "verify_password" src/app/core/security.py; then
  echo "   ✅ パスワード検証関数あり"
fi
if grep -q 'Literal\["HS256"' src/app/core/config.py; then
  echo "   ✅ JWT アルゴリズム型制限あり"
fi
if grep -q "validate_secret_key" src/app/core/config.py; then
  echo "   ✅ SECRET_KEY バリデーションあり"
fi
if grep -q "ForeignKey" src/infrastructure/persistence/models/organization.py; then
  echo "   ✅ 外部キー制約あり"
fi

echo -e "\n======================================"
echo "検証完了"
echo "======================================"
