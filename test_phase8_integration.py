import sys, io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, '.')

print('='*70)
print('🔄 Phase 8 系统集成测试 - 真实数据源接入')
print('='*70)

tests_passed = 0
tests_total = 0

# Test 1: 工具函数
tests_total += 1
print('\n[1/7] 爬虫工具函数...')
try:
    from crawlers.utils.user_agents import UserAgentPool
    from crawlers.utils.rate_limiter import RateLimiter
    
    ua_pool = UserAgentPool()
    assert ua_pool.pool_size >= 10
    limiter = RateLimiter(min_delay=0.1, max_delay=0.2)
    
    print('   ✅ UserAgentPool & RateLimiter 正常')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')

# Test 2: BaseCrawler
tests_total += 1
print('\n[2/7] BaseCrawler...')
try:
    from crawlers.base_crawler import BaseCrawler, BlockedError, CrawlerError
    print('   ✅ BaseCrawler 导入正常 (含异常类)')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')

# Test 3: DataPipeline
tests_total += 1
print('\n[3/7] DataPipeline...')
try:
    from crawlers.pipelines import DataPipeline
    pipeline = DataPipeline('kaoyan')
    
    test_data = [
        {'title': '测试资料A'},
        {'title': '测试资料B'},
        {'title': '测试资料A'},
        {'title': ''},
    ]
    
    result = pipeline.process(test_data)
    assert result['metadata']['total_count'] == 2
    assert result['metadata']['version'] == '2.0.0'
    
    print(f'   ✅ Pipeline: 4条输入 → {result["metadata"]["total_count"]}条输出')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')
    import traceback
    traceback.print_exc()

# Test 4: KaoyanCrawler
tests_total += 1
print('\n[4/7] KaoyanCrawler (考研帮)...')
try:
    from crawlers.kaoyan_crawler import KaoyanCrawler
    crawler = KaoyanCrawler()
    
    data = crawler.run_and_save()
    assert data['metadata']['total_count'] > 0
    assert 'materials' in data
    
    materials = data['materials']
    sample = materials[0]
    required_fields = ['id', 'title', 'subject', 'material_type', 'source']
    for field in required_fields:
        assert field in sample, f"缺少字段: {field}"
    
    print(f'   ✅ 考研资料采集: {data["metadata"]["total_count"]}条')
    print(f'      示例: {sample["title"][:45]}...')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')
    import traceback
    traceback.print_exc()

# Test 5: ZhihuCrawler
tests_total += 1
print('\n[5/7] ZhihuCrawler (知乎)...')
try:
    from crawlers.zhihu_crawler import ZhihuCrawler
    zhihu = ZhihuCrawler()
    
    english_data = zhihu.run_and_save()
    assert english_data['metadata']['total_count'] > 0
    assert 'resources' in english_data
    
    resources = english_data['resources']
    sample = resources[0]
    assert all(k in sample for k in ['id', 'title', 'category_name', 'difficulty', 'priority'])
    
    print(f'   ✅ 英语资料采集: {english_data["metadata"]["total_count"]}条')
    print(f'      示例: {sample["title"][:45]}... [{sample["priority"]}]')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')
    import traceback
    traceback.print_exc()

# Test 6: CanvaCrawler
tests_total += 1
print('\n[6/7] CanvaCrawler (办公模板)...')
try:
    from crawlers.canva_crawler import CanvaCrawler
    canva = CanvaCrawler()
    
    office_data = canva.run_and_save()
    assert office_data['metadata']['total_count'] > 0
    assert 'templates' in office_data
    
    templates = office_data['templates']
    sample = templates[0]
    assert all(k in sample for k in ['id', 'title', 'category', 'difficulty', 'rating'])
    
    print(f'   ✅ 办公模板采集: {office_data["metadata"]["total_count"]}条')
    print(f'      示例: {sample["title"][:45]}... [⭐{sample["rating"]}]')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')
    import traceback
    traceback.print_exc()

# Test 7: 数据加载验证
tests_total += 1
print('\n[7/7] 数据持久化验证...')
try:
    from utils.data_loader import DataLoader
    loader = DataLoader()
    
    kaoyan = loader.load('kaoyan')
    english = loader.load('english')
    office = loader.load('office')
    
    k_count = len(kaoyan.get('materials', []))
    e_count = len(english.get('resources', []))
    o_count = len(office.get('templates', []))
    
    assert k_count > 0, "考研数据为空"
    assert e_count > 0, "英语数据为空"
    assert o_count > 0, "办公模板为空"
    
    total_new = k_count + e_count + o_count
    print(f'   ✅ 数据可正常加载:')
    print(f'      📚 考研资料: {k_count}条')
    print(f'      📖 英语资源: {e_count}条')
    print(f'      📝 办公模板: {o_count}条')
    print(f'      ──────────────')
    print(f'      📊 新增总计: {total_new}条')
    tests_passed += 1
except Exception as e:
    print(f'   ❌ 失败: {e}')
    import traceback
    traceback.print_exc()

# 结果汇总
print('\n' + '='*70)
print(f'📊 测试结果: {tests_passed}/{tests_total} 通过')

if tests_passed == tests_total:
    print('🎉 Phase 8 全部测试通过！真实数据源接入成功！')
    print('='*70)
else:
    print(f'⚠️ 存在 {tests_total - tests_passed} 个问题')
    print('='*70)
