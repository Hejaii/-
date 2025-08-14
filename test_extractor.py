#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本 - 验证文档提取器的基本功能
"""

import os
import sys
from extract_required_documents import DocumentExtractor

def test_pdf_extraction():
    """测试PDF文本提取功能"""
    print("🧪 测试PDF文本提取功能...")
    
    # 检查PDF文件是否存在
    pdf_path = "03.招标文件.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return False
    
    # 创建提取器
    extractor = DocumentExtractor()
    
    try:
        # 测试PDF文本提取
        pages_data = extractor.extract_text_from_pdf(pdf_path)
        
        if not pages_data:
            print("❌ PDF文本提取失败")
            return False
        
        print(f"✅ PDF文本提取成功，共 {len(pages_data)} 页")
        
        # 显示前几页的基本信息
        for i, page in enumerate(pages_data[:3]):
            print(f"  第 {page['page']} 页: {page['content_length']} 字符")
        
        if len(pages_data) > 3:
            print(f"  ... 还有 {len(pages_data) - 3} 页")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_configuration():
    """测试配置文件加载"""
    print("\n🧪 测试配置文件...")
    
    try:
        from config import QIANWEN_CONFIG, PDF_CONFIG, DOCUMENT_CATEGORIES
        
        print("✅ 配置文件加载成功")
        print(f"  - API基础URL: {QIANWEN_CONFIG['api_base_url']}")
        print(f"  - 模型: {QIANWEN_CONFIG['model']}")
        print(f"  - 输入文件: {PDF_CONFIG['input_file']}")
        print(f"  - 文档类别: {list(DOCUMENT_CATEGORIES.keys())}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 配置文件导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包安装"""
    print("\n🧪 测试依赖包...")
    
    required_packages = [
        "pdfplumber",
        "requests",
        "PyMuPDF"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️ 缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🔧 招标文件文档提取器 - 功能测试")
    print("=" * 50)
    
    tests = [
        ("依赖包检查", test_dependencies),
        ("配置文件测试", test_configuration),
        ("PDF提取测试", test_pdf_extraction),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！可以开始使用文档提取器")
        print("\n📝 下一步:")
        print("1. 设置通义千问API密钥: export QIANWEN_API_KEY='sk-fe0485c281964259b404907d483d3777'")
        print("2. 运行主程序: python extract_required_documents.py")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

