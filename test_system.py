import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print('=' * 60)
print('系统集成验证测试')
print('=' * 60)

# 1. 数据模型验证
print('\n[1/6] 验证数据模型...')
from models.kaoyan_model import KaoyanMaterial
from models.note_model import GeneratedNote

test_kaoyan = KaoyanMaterial(
    id='TEST001', title='测试资料', subject='数学一',
    year=2026, material_type='历年真题', description='测试描述',
    file_path='test.zip', file_size='100MB', file_format='PDF',
    download_count=100, rating=4.5, tags=['数学一', '真题']
)
assert test_kaoyan.id == 'TEST001'
assert test_kaoyan.subject == '数学一'
print('   ✅ 数据模型正常')

# 2. 数据加载验证
print('\n[2/6] 验证数据加载...')
from utils.data_loader import DataLoader
loader = DataLoader()

kaoyan_data = loader.load('kaoyan')
office_data = loader.load('office')
english_data = loader.load('english')
notes_data = loader.load('notes')

k_count = len(kaoyan_data.get('materials', []))
o_count = len(office_data.get('templates', []))
e_count = len(english_data.get('resources', []))
n_count = len(notes_data.get('notes', []))

print(f'   ✅ 考研资料: {k_count} 条')
print(f'   ✅ 办公模板: {o_count} 条')
print(f'   ✅ 英语资源: {e_count} 条')
print(f'   ✅ 笔记记录: {n_count} 条')

# 3. DataFrame转换
print('\n[3/6] 验证DataFrame转换...')
df = loader.load_as_dataframe('kaoyan', 'materials')
print(f'   ✅ DataFrame: {df.shape}')
assert not df.empty, "DataFrame为空"

# 4. 模板引擎
print('\n[4/6] 验证模板引擎...')
from utils.template_engine import TemplateEngine
engine = TemplateEngine()
templates = engine.get_available_templates()
print(f'   ✅ 可用模板: {templates}')
assert len(templates) > 0, "无可用模板"

# 5. 内容生成服务
print('\n[5/6] 验证内容生成服务...')
from services.content_generator import ContentGeneratorService
generator = ContentGeneratorService()

note = generator.generate_xiaohongshu_note(source_content=test_kaoyan.__dict__, style='ganhuo', tone='qinjie')
assert isinstance(note, list) and len(note) > 0, "生成结果为空"
assert note[0].get('title', '') != '', "标题为空"
assert note[0].get('body', '') != '', "内容为空"
print(f'   ✅ 笔记生成成功')
print(f'      标题: {note[0]["title"][:50]}...')

# 6. 导出服务
print('\n[6/6] 验证导出功能...')
from services.exporter import ExporterService
exporter = ExporterService()

md_path = exporter.export_note_to_markdown(note[0])
assert md_path and isinstance(md_path, str), "Markdown导出失败"
print(f'   ✅ Markdown导出正常: {md_path}')

batch_result = exporter.export_notes_batch(note, format='text')
assert batch_result, "批量导出失败"
print(f'   ✅ 批量导出正常')

# 统计信息
stats = loader.get_statistics('kaoyan')
print(f'\n   📊 统计信息: 总数={stats["total_count"]}, 版本={stats["version"]}')

print('\n' + '=' * 60)
print('🎉 所有系统集成测试通过！')
print('=' * 60)

total = k_count + o_count + e_count + n_count
print(f'\n📈 数据量统计:')
print(f'   📚 考研资料: {k_count} 条记录')
print(f'   📝 办公模板: {o_count} 条记录')
print(f'   📖 英语资源: {e_count} 条记录')
print(f'   ✍️ 笔记记录: {n_count} 条记录')
print(f'   ─────────────────────')
print(f'   📊 总计: {total} 条记录')
