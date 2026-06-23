"""出题助手 - FastAPI 入口"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import Response
from app.models.schemas import GenerateRequest, ExamPaper, ExportRequest, ExportFormat, Question
from app.parsers.document_parser import parse_document
from app.generators.question_generator import generate_questions
from app.exporters.word_exporter import export_word

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="出题助手",
    description="备课减负型出题助手 —— 丢进去教材，自动出配套练习题",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "出题助手 API v0.1.0", "docs": "/docs"}


@app.post("/api/generate", response_model=ExamPaper)
async def generate(body: GenerateRequest):
    """根据文本内容出题"""
    if not body.source_text or not body.source_text.strip():
        raise HTTPException(status_code=400, detail="source_text 不能为空")

    logger.info(f"出题请求: subject={body.subject}, count={body.question_count}, types={[t.value for t in body.question_types]}")

    try:
        questions = generate_questions(
            source_text=body.source_text,
            question_types=body.question_types,
            question_count=body.question_count,
            difficulty=body.difficulty,
            subject=body.subject,
            grade=body.grade,
            chapter=body.chapter,
            extra_prompt=body.extra_prompt,
        )
    except Exception as e:
        logger.error(f"出题失败: {e}")
        raise HTTPException(status_code=500, detail=f"出题失败: {str(e)}")

    title = f"{body.subject}"
    if body.grade:
        title += f" - {body.grade}"
    if body.chapter:
        title += f" - {body.chapter}"
    title += " 练习题"

    paper = ExamPaper(
        title=title,
        subject=body.subject,
        grade=body.grade,
        chapter=body.chapter,
        questions=questions,
    )
    return paper


@app.post("/api/generate/upload")
async def generate_from_file(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: str = Form(default=None),
    chapter: str = Form(default=None),
    question_types: str = Form(default="choice,fill"),
    question_count: int = Form(default=10),
    difficulty: str = Form(default="medium"),
    extra_prompt: str = Form(default=None),
):
    """上传文档文件（Word/PDF/PPTX），解析后出题"""
    allowed = {".docx", ".pdf", ".pptx", ".ppt"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}，支持: {allowed}")

    # 保存临时文件
    tmp_path = f"/tmp/upload_{file.filename}"
    content = await file.read()
    with open(tmp_path, "wb") as f:
        f.write(content)

    try:
        source_text = parse_document(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文档解析失败: {str(e)}")
    finally:
        os.remove(tmp_path)

    from app.models.schemas import QuestionType, Difficulty

    type_list = []
    for t in question_types.split(","):
        t = t.strip()
        try:
            type_list.append(QuestionType(t))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效题型: {t}")

    try:
        diff = Difficulty(difficulty)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"无效难度: {difficulty}")

    try:
        questions = generate_questions(
            source_text=source_text,
            question_types=type_list,
            question_count=question_count,
            difficulty=diff,
            subject=subject,
            grade=grade,
            chapter=chapter,
            extra_prompt=extra_prompt,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"出题失败: {str(e)}")

    title = f"{subject}"
    if grade:
        title += f" - {grade}"
    if chapter:
        title += f" - {chapter}"
    title += " 练习题"

    return ExamPaper(
        title=title,
        subject=subject,
        grade=grade,
        chapter=chapter,
        questions=questions,
    )


@app.post("/api/export")
async def export(body: ExportRequest):
    """导出试卷为 Word"""
    try:
        docx_bytes = export_word(
            paper=body.paper,
            separate_answers=body.separate_answers,
            include_answer_sheet=body.include_answer_sheet,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

    filename = f"{body.paper.title}.docx".replace(" ", "_")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
