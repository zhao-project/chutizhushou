"""测试出题基础功能"""
from app.models.schemas import Question, QuestionType, Difficulty, ExamPaper
from app.exporters.word_exporter import export_word


def test_models():
    """测试数据模型"""
    q = Question(
        question_type=QuestionType.CHOICE,
        difficulty=Difficulty.MEDIUM,
        content="1 + 1 = ?",
        options=["A. 1", "B. 2", "C. 3", "D. 4"],
        answer="B",
        explanation="基本加法运算",
        knowledge_point="加法",
    )
    assert q.question_type == QuestionType.CHOICE
    assert len(q.options) == 4

    paper = ExamPaper(
        title="数学测试",
        subject="数学",
        grade="七年级",
        total_score=100,
        questions=[q],
    )
    assert paper.title == "数学测试"
    assert len(paper.questions) == 1
    print("✅ 数据模型测试通过")


def test_word_export():
    """测试 Word 导出"""
    q = Question(
        question_type=QuestionType.CHOICE,
        difficulty=Difficulty.EASY,
        content="地球是第几颗行星？",
        options=["A. 第一颗", "B. 第二颗", "C. 第三颗", "D. 第四颗"],
        answer="C",
        explanation="太阳系八大行星顺序",
        knowledge_point="天文",
    )
    q2 = Question(
        question_type=QuestionType.FILL_BLANK,
        difficulty=Difficulty.EASY,
        content="光的速度约为 ____ m/s",
        answer="3×10^8",
        knowledge_point="物理",
    )

    paper = ExamPaper(
        title="科学练习题",
        subject="科学",
        grade="六年级",
        total_score=100,
        questions=[q, q2],
    )

    docx_bytes = export_word(paper, separate_answers=True, include_answer_sheet=True)
    assert len(docx_bytes) > 1000, "导出的 Word 文件太小"
    # 验证是有效的 zip（docx 格式）
    assert docx_bytes[:2] == b"PK", "不是有效的 docx 文件"
    print("✅ Word 导出测试通过")


if __name__ == "__main__":
    test_models()
    test_word_export()
    print("\n🎉 所有测试通过！")
