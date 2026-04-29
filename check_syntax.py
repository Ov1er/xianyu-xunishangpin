import sys
import io
import py_compile
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print('=' * 70)
print('🔍 全面语法检查 - 所有页面文件')
print('=' * 70)

pages_dir = Path('pages')
page_files = list(pages_dir.glob('*.py'))
page_files = [f for f in page_files if not f.name.startswith('__')]

errors_found = []
success_count = 0

for page_file in sorted(page_files):
    print(f'\n📄 检查: {page_file.name}')
    try:
        py_compile.compile(str(page_file), doraise=True)
        print(f'   ✅ 语法正确')
        success_count += 1
    except py_compile.PyCompileError as e:
        print(f'   ❌ 语法错误:')
        print(f'      {e}')
        errors_found.append((page_file.name, str(e)))
    except Exception as e:
        print(f'   ⚠️ 其他错误: {type(e).__name__}: {e}')
        errors_found.append((page_file.name, f'{type(e).__name__}: {e}'))

print('\n' + '=' * 70)
if errors_found:
    print(f'❌ 发现 {len(errors_found)} 个错误:')
    for filename, error in errors_found:
        print(f'\n  📁 {filename}')
        print(f'     {error}')
else:
    print(f'✅ 全部 {success_count} 个文件语法检查通过！')

print('=' * 70)
sys.exit(1 if errors_found else 0)
