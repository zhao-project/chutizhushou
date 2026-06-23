"""出题引擎 - 基于 LLM 自动生成题目"""

import json
import logging
from typing import List
from app.models.schemas import Question, QuestionType, Difficulty

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的出题助手，擅长根据教材内容生成高质量的练习题。

要求：
1. 题目内容必须基于提供的教材文本
2. 难度要适中，符合对应年级水平
3. 选择题的干扰项要有迷惑性但不能误导
4. 每道题都要标注对应的知识点
5. 答案要准确，解析要清晰

输出格式：严格的 JSON 数组，每个元素包含：
{
  "question_type": "choice/fill/true_false/short/essay",
  "difficulty": "easy/medium/hard",
  "content": "题干内容",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],  // 仅选择题需要
  "answer": "答案",
  "explanation": "解析",
  "knowledge_point": "知识点"
}"""


def generate_questions(
    source_text: str,
    question_types: List[QuestionType],
    question_count: int,
    difficulty: Difficulty,
    subject: str,
    grade: str = None,
    chapter: str = None,
    extra_prompt: str = None,
    client=None,
    model: str = None,
) -> List[Question]:
    """使用 LLM 生成题目"""
    import openai

    if client is None:
        client = openai.OpenAI()

    type_names = [t.value for t in question_types]
    type_desc = "、".join(type_names)

    user_prompt = f"""请根据以下{subject}教材内容，生成 {question_count} 道{type_desc}题。

{f"年级：{grade}" if grade else ""}
{f"章节：{chapter}" if chapter else ""}
难度：{difficulty.value}

教材内容：
---
{source_text[:8000]}
---

{f"额外要求：{extra_prompt}" if extra_prompt else ""}

请输出严格的 JSON 数组，不要任何额外文字。"""

    response = client.chat.completions.create(
        model=model or "gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )

    text = response.choices[0].message.content.strip()
    # 清理可能的 markdown 代码块
    if text.startswith("```"):
        text = text.split("```", 2)[-2] if "```" in text[3:] else text[3:]
        text = text.lstrip("json").strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"LLM 返回 JSON 解析失败: {e}\n原始内容: {text[:500]}")
        raise ValueError(f"题目生成失败：LLM 返回格式不正确")

    questions = []
    for item in data:
        try:
            q = Question(
                question_type=QuestionType(item["question_type"]),
                difficulty=Difficulty(item.get("difficulty", difficulty.value)),
                content=item["content"],
                options=item.get("options"),
                answer=item["answer"],
                explanation=item.get("explanation"),
                knowledge_point=item.get("knowledge_point"),
            )
            questions.append(q)
        except Exception as e:
            logger.warning(f"跳过无效题目: {e}")
            continue

    return questions
