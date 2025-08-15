# 招标文件文档提取器

这是一个智能的招标文件分析工具，使用通义千问API自动识别和提取招标文件中要求投标人提交的所有文档、材料、证明等。

## 功能特点

- 🔍 智能识别：使用通义千问API进行自然语言理解，准确识别文档要求
- 📄 多格式支持：支持PDF格式的招标文件
- 🏷️ 自动分类：将提取的文档按资格文件、技术文件、商务文件等类别自动分类
- 📝 结构化输出：生成Markdown格式的文档清单和JSON格式的详细数据
- 🔄 去重处理：自动去除重复的文档要求
- 📍 页码定位：记录每个文档要求在原文件中的具体页码

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

在使用前，需要设置通义千问API密钥：

```bash
export QIANWEN_API_KEY='sk-fe0485c281964259b404907d483d3777'
```

## 使用方法

### 基本使用

```bash
python extract_required_documents.py
```

### 自定义配置

可以修改 `config.py` 文件来调整各种参数：

- API配置（模型、温度、最大token数等）
- PDF处理参数（批处理大小、延迟时间等）
- 文档分类规则
- 输出文件设置

## 输出文件

运行完成后，会生成以下文件：

1. **`required_documents.md`** - Markdown格式的文档清单
2. **`extracted_documents_YYYYMMDD_HHMMSS.json`** - JSON格式的详细数据

## 输出示例

### Markdown输出

```markdown
# 招标文件要求提交文档清单

> 生成时间：2024-01-15 14:30:25  
> 文档总数：15 项

## 📋 文档总览

本清单包含招标文件中明确要求投标人提交或附带的所有文档、材料、证明等。

---

## 📁 按类别分类

### 资格文件 (8 项)

**1. 营业执照复印件**
- 页码：第 5 页
- 原始要求：投标人需提供有效的营业执照复印件

**2. 质量管理体系认证证书**
- 页码：第 6 页
- 原始要求：需提供ISO9001质量管理体系认证证书
```

### JSON输出

```json
{
  "extraction_time": "2024-01-15 14:30:25",
  "total_documents": 15,
  "documents": [
    {
      "name": "营业执照复印件",
      "original_text": "投标人需提供有效的营业执照复印件",
      "category": "资格文件",
      "page": 5
    }
  ]
}
```

## 技术架构

- **PDF处理**：使用 `pdfplumber` 提取PDF文本内容
- **AI分析**：调用通义千问API进行智能文档识别
- **数据处理**：Python原生库进行数据清洗、去重、分类
- **输出生成**：生成Markdown和JSON格式的结构化数据

## 注意事项

1. **API密钥安全**：请妥善保管通义千问API密钥，不要将其提交到代码仓库
2. **API调用限制**：程序会在页面间添加延迟，避免触发API限流
3. **PDF质量**：PDF文件质量会影响文本提取效果，建议使用文本可选择的PDF文件
4. **网络连接**：需要稳定的网络连接来调用通义千问API

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查环境变量是否正确设置
   - 确认API密钥是否有效

2. **PDF读取失败**
   - 检查PDF文件是否存在
   - 确认PDF文件是否损坏

3. **API调用失败**
   - 检查网络连接
   - 确认API配额是否充足
   - 查看错误日志获取详细信息

## 许可证

本项目采用MIT许可证，详见LICENSE文件。


## 自动生成响应文件与附件

本仓库新增 `main.py` 等模块，可根据分析表与招标文件自动生成响应附件和逐条说明。

### 使用方法

```bash
export DASHSCOPE_API_KEY=sk-fe0485c281964259b404907d483d3777
export QWEN_MODEL=qwen-plus
python main.py --analysis /path/analysis.txt --tender /path/tender.pdf --repo /path/repo --out ./output
```

### 输出目录

- `attachments/`：自动生成的附件模板
- `responses/`：针对每条要求的响应文件
- `manifest.json`：生成过程的元数据
- `logs/`：关键日志

所有文本理解与生成均通过通义千问API完成，本地代码仅负责I/O与调度。

## 新增：基于需求列表构建 PDF

本项目新增 `build_pdf` 管线，可将需求列表与知识库整合成单个 PDF。示例：

```bash
python -m build_pdf --requirements examples/reqs.json --kb ./kb --out build/output.pdf


参数说明：
- `--requirements` 需求列表文件，支持 JSON/CSV/Markdown 表格
- `--kb` 知识库目录
- `--out` 输出 PDF 路径
- `--latex-template` 自定义 LaTeX 模板，可选
- `--workdir` 工作目录，默认 `./build`
- `--topk` 每条需求检索候选数量，默认 5
- `--use-llm` 是否启用 LLM 处理，默认 `true`

生成文件包括：`merged.md`、`main.tex`、`meta.json`、`logs/build.log`。
