@echo off
chcp 65001 >nul
title 招标文件文档提取器

echo 🔧 招标文件文档提取器
echo ========================

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查依赖包
echo 📦 检查依赖包...
python -c "import pdfplumber, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 缺少依赖包，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 检查API密钥
if "%QIANWEN_API_KEY%"=="" (
    echo ❌ 错误：未设置通义千问API密钥
    echo.
    echo 请按以下步骤设置：
    echo 1. 获取通义千问API密钥：https://dashscope.aliyun.com/
    echo 2. 设置环境变量：
    echo    set QIANWEN_API_KEY=your_api_key_here
    echo 3. 或者将密钥添加到系统环境变量中
    echo.
    echo 设置完成后，重新运行此脚本
    pause
    exit /b 1
)

REM 检查PDF文件
if not exist "03.招标文件.pdf" (
    echo ❌ 错误：未找到招标文件PDF
    echo 请确保 '03.招标文件.pdf' 文件存在于当前目录
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🚀 启动文档提取器...

REM 运行主程序
python extract_required_documents.py

REM 检查运行结果
if %errorlevel% equ 0 (
    echo.
    echo 🎉 文档提取完成！
    echo 📁 输出文件：
    echo   - required_documents.md (文档清单)
    echo   - extracted_documents_*.json (详细数据)
) else (
    echo.
    echo ❌ 文档提取失败，请检查错误信息
)

pause

