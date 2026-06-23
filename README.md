# 出题助手 - 备课减负型

> 老师的出题外包 —— 丢进去教材/课件/PPT，自动出配套练习题

## 功能

- 📄 **多格式输入**：支持 Word (.docx)、PDF、PPT 课件
- 🤖 **智能出题**：对接 LLM 自动生成高质量题目
- 📝 **多题型支持**：选择题、填空题、判断题、简答题、论述题
- 📊 **分级难度**：easy / medium / hard
- 📤 **Word 导出**：自动生成排版好的试卷（.docx）
  - 答案分离（试卷 + 答案分开）
  - 选择题答题卡
  - 标注知识点
- 🔌 **REST API**：可接入 Web 前端或其他系统

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 3. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. 访问 API 文档
open http://localhost:8000/docs
```

## API 接口

### POST /api/generate

JSON 出题：

```json
{
  "source_text": "教材内容...",
  "subject": "数学",
  "grade": "七年级",
  "chapter": "第三章 一元一次方程",
  "question_types": ["choice", "fill"],
  "question_count": 10,
  "difficulty": "medium"
}
```

### POST /api/generate/upload

文件出题（multipart/form-data）：

```
POST /api/generate/upload
Content-Type: multipart/form-data

file: (word/pdf/pptx file)
subject: 数学
question_count: 10
...
```

### POST /api/export

导出 Word 试卷：

```json
{
  "paper": { ... },
  "format": "docx",
  "separate_answers": true,
  "include_answer_sheet": true
}
```

## 项目结构

```
chutizhushou/
├── main.py                  # FastAPI 入口
├── requirements.txt         # Python 依赖
├── .env.example             # 配置模板
├── app/
│   ├── models/
│   │   └── schemas.py       # 数据模型
│   ├── parsers/
│   │   └── document_parser.py  # 文档解析器
│   ├── generators/
│   │   └── question_generator.py  # LLM 出题引擎
│   └── exporters/
│       └── word_exporter.py    # Word 导出器
└── tests/
```

## License

AGPL-3.0
