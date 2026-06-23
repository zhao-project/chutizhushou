"""数据模型定义"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class QuestionType(str, Enum):
    CHOICE = "choice"        # 选择题
    FILL_BLANK = "fill"      # 填空题
    TRUE_FALSE = "true_false" # 判断题
    SHORT_ANSWER = "short"   # 简答题
    ESSAY = "essay"          # 论述题


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(BaseModel):
    """单道题目"""
    question_type: QuestionType
    difficulty: Difficulty
    content: str                          # 题干
    options: Optional[List[str]] = None   # 选择题选项
    answer: str                           # 答案
    explanation: Optional[str] = None     # 解析
    source_ref: Optional[str] = None      # 来源标注（如教材页码）
    knowledge_point: Optional[str] = None # 知识点


class ExamPaper(BaseModel):
    """试卷"""
    title: str                            # 试卷标题
    subject: str                          # 科目
    grade: Optional[str] = None           # 年级
    chapter: Optional[str] = None         # 章节
    total_score: int = 100                # 总分
    duration_min: int = 90               # 考试时长(分钟)
    questions: List[Question]             # 题目列表


class GenerateRequest(BaseModel):
    """出题请求"""
    source_text: Optional[str] = None     # 直接输入的文本内容
    subject: str                          # 科目
    grade: Optional[str] = None           # 年级
    chapter: Optional[str] = None         # 章节
    question_types: List[QuestionType] = [QuestionType.CHOICE, QuestionType.FILL_BLANK]
    question_count: int = Field(default=10, ge=1, le=100)
    difficulty: Difficulty = Difficulty.MEDIUM
    extra_prompt: Optional[str] = None    # 额外要求


class ExportFormat(str, Enum):
    WORD = "docx"
    PDF = "pdf"


class ExportRequest(BaseModel):
    """导出请求"""
    paper: ExamPaper
    format: ExportFormat = ExportFormat.WORD
    separate_answers: bool = True         # 答案分离
    include_answer_sheet: bool = False    # 含答题卡
