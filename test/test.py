"""
LangGraph + LangChain v1 기반
뷰티 인플루언서 인사이트 파이프라인 (노드 단위 디버깅용)

노드 구조 (Studio에서 그대로 보임):
- plan_questions
- research
- synthesize
- research에서 pending 질문 있으면 자기 자신으로 루프, 없으면 synthesize로 이동

모든 LLM은 init_chat_model("gpt5-mini") 사용.
"""

import json
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.agents.middleware import SummarizationMiddleware, PIIMiddleware
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------
# 0. 공통 설정
# ---------------------------------------------------------

MODEL_NAME = "gpt5-mini"  # 실제 쓰는 모델 이름에 맞게 수정


def get_llm():
    return init_chat_model(MODEL_NAME)


def get_tavily_tool():
    return TavilySearch(
        max_results=8,
        search_depth="advanced",
        include_answer=True,
        include_raw_content=True,
    )


# ---------------------------------------------------------
# 1. Pydantic 모델 (structured output)
# ---------------------------------------------------------

class SearchQuestion(BaseModel):
    category: str = Field(..., description="질문 카테고리 (성분 트렌드, 제형 등)")
    question: str = Field(..., description="실제 Tavily 검색에 쓸 자연어 질문")
    priority: int = Field(1, ge=1, le=3)


class QuestionPlan(BaseModel):
    questions: List[SearchQuestion] = Field(default_factory=list)


class ProductConcept(BaseModel):
    name: str
    summary: str
    hero_ingredients: List[str] = Field(default_factory=list)
    target_skin: str
    price_positioning: str
    content_hooks: List[str] = Field(default_factory=list)


class StrategyReport(BaseModel):
    overview: str
    trend_summary: str
    fit_analysis: str
    product_concepts: List[ProductConcept] = Field(default_factory=list)
    content_ideas: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


# ---------------------------------------------------------
# 2. LangChain 에이전트들 (노드 안에서 호출)
# ---------------------------------------------------------

# 2-1. Question Planner

def build_question_planner_agent():
    return create_agent(
        model=get_llm(),
        tools=[],
        system_prompt=(
            "너는 뷰티 브랜드 전략 컨설턴트이자 화장품 R&D 기획자다. "
            "인플루언서 인사이트를 바탕으로 웹 리서치를 위한 질문 리스트를 설계한다.\n\n"
            "규칙:\n"
            "- 질문은 모두 뷰티/스킨케어/메이크업 관련이어야 한다.\n"
            "- 각 질문은 한 가지 포인트에만 집중하고, 짧고 명확하게 작성한다.\n"
            "- category 예시: 성분 트렌드, 제형/텍스처, 타깃 피부 고민, 가격/포지셔닝, "
            "브랜드/콘셉트 방향, 콘텐츠 포맷 등.\n"
            "- priority 1~3 중에서, 인사이트 강화에 중요할수록 1에 가깝게 설정한다."
        ),
        response_format=ToolStrategy(QuestionPlan),
    )


def run_question_planner(meta: Dict[str, Any], insight_text: str) -> QuestionPlan:
    agent = build_question_planner_agent()
    user_content = (
        "다음 인플루언서에 대해 웹 리서치를 위한 질문들을 설계해라.\n\n"
        f"[인플루언서 메타]\n{json.dumps(meta, ensure_ascii=False, indent=2)}\n\n"
        f"[인플루언서 인사이트]\n{insight_text}\n\n"
        "이 인플루언서에 대한 인사이트를 한 단계 더 강화할 수 있도록 "
        "효율적인 검색용 질문들을 만들어라."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_content}]})
    return result["structured_response"]


# 2-2. Beauty Researcher (Tavily)

def build_beauty_research_agent():
    tavily_tool = get_tavily_tool()
    middlewares = [
        SummarizationMiddleware(
            model=MODEL_NAME,
            max_tokens_before_summary=1200,
        ),
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("phone_number", strategy="redact", apply_to_input=True),
    ]
    return create_agent(
        model=get_llm(),
        tools=[tavily_tool],
        system_prompt=(
            "너는 뷰티/스킨케어/메이크업 시장을 분석하는 시니어 애널리스트다. "
            "Tavily 웹 검색 툴을 사용해서 질문에 대한 실제 기사/리포트/브랜드 정보를 찾아보고, "
            "근거가 되는 출처를 바탕으로 트렌드를 요약해라. "
            "가능하면 최근 3~5년 기준의 트렌드를 중점적으로 보고, "
            "결과는 한국어로 정리하되 제품/성분명은 원문을 그대로 사용해도 된다."
        ),
        middleware=middlewares,
    )


def run_research_for_question(agent, question: SearchQuestion) -> Dict[str, Any]:
    user_message = (
        f"[카테고리] {question.category}\n"
        f"[질문] {question.question}\n\n"
        "위 질문에 대해 뷰티/화장품 관점에서 Tavily 툴을 활용해 리서치하고, "
        "아래 형식으로 정리해줘.\n\n"
        "1) 핵심 요약 (3~5줄)\n"
        "2) 주요 키워드/성분/제품 유형 리스트\n"
        "3) 이 인플루언서에게 주는 시사점 (기회/위험)\n"
        "4) 참고할 만한 URL 리스트"
    )

    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    try:
        messages = result.get("messages", [])
        last_msg = messages[-1]
        if isinstance(last_msg, dict):
            summary_text = last_msg.get("content", "")
        else:
            summary_text = getattr(last_msg, "content", str(last_msg))
    except Exception:
        summary_text = str(result)

    return {
        "category": question.category,
        "question": question.question,
        "priority": question.priority,
        "summary": summary_text,
        "sources": [],  # 필요하면 result에서 URL 파싱
    }


# 2-3. Beauty Strategist

def build_beauty_strategist_agent():
    return create_agent(
        model=get_llm(),
        tools=[],
        system_prompt=(
            "너는 뷰티 브랜드 전략 컨설턴트이자 화장품 제품 기획자다. "
            "인플루언서 인사이트와 웹 리서치 결과를 바탕으로, "
            "해당 인플루언서에게 적합한 성분, 제품 카테고리, 브랜드/콘셉트, "
            "콘텐츠 아이디어를 제안하는 StrategyReport를 작성한다."
        ),
        response_format=ToolStrategy(StrategyReport),
    )


def run_strategist(
    meta: Dict[str, Any],
    insight_text: str,
    questions: List[Dict[str, Any]],
    research_notes: List[Dict[str, Any]],
) -> StrategyReport:
    agent = build_beauty_strategist_agent()
    user_content = (
        f"[인플루언서 메타]\n{json.dumps(meta, ensure_ascii=False, indent=2)}\n\n"
        f"[인플루언서 인사이트]\n{insight_text}\n\n"
        f"[검색 질문 리스트]\n{json.dumps(questions, ensure_ascii=False, indent=2)}\n\n"
        f"[웹 리서치 요약]\n{json.dumps(research_notes, ensure_ascii=False, indent=2)}\n\n"
        "위 정보를 바탕으로 StrategyReport 모델을 알차게 채워라. "
        "각 필드는 한국어로 작성한다."
    )
    result = agent.invoke({"messages": [{"role": "user", "content": user_content}]})
    return result["structured_response"]


def render_strategy_report_markdown(report: StrategyReport) -> str:
    lines = []
    lines.append("# 인플루언서 뷰티 전략 리포트\n")

    lines.append("## 1. 인플루언서 개요 & 현재 포지셔닝\n")
    lines.append(report.overview.strip() + "\n")

    lines.append("## 2. 관련 뷰티/스킨케어 트렌드 요약\n")
    lines.append(report.trend_summary.strip() + "\n")

    lines.append("## 3. 인플루언서와의 Fit / Gap 분석\n")
    lines.append(report.fit_analysis.strip() + "\n")

    lines.append("## 4. 제품/브랜드 콘셉트 제안\n")
    for i, concept in enumerate(report.product_concepts, start=1):
        lines.append(f"### 4-{i}. {concept.name}\n")
        lines.append(concept.summary.strip() + "\n")
        lines.append(f"- **타깃 피부/고민**: {concept.target_skin}")
        lines.append(f"- **가격 포지셔닝**: {concept.price_positioning}")
        if concept.hero_ingredients:
            lines.append("- **핵심 성분**: " + ", ".join(concept.hero_ingredients))
        if concept.content_hooks:
            lines.append("- **콘텐츠 후크 아이디어**:")
            for hook in concept.content_hooks:
                lines.append(f"  - {hook}")
        lines.append("")

    lines.append("## 5. 콘텐츠/캠페인 아이디어\n")
    for idea in report.content_ideas:
        lines.append(f"- {idea}")

    lines.append("\n## 6. 리스크 & 주의 포인트\n")
    for risk in report.risks:
        lines.append(f"- {risk}")

    return "\n".join(lines)


# ---------------------------------------------------------
# 3. LangGraph State 정의
# ---------------------------------------------------------

class PipelineState(TypedDict, total=False):
    meta: Dict[str, Any]
    insight_text: str
    questions: List[Dict[str, Any]]
    research_notes: List[Dict[str, Any]]
    report_structured: Optional[Dict[str, Any]]
    report_markdown: Optional[str]
    errors: List[str]


def _ensure_question_ids(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for idx, q in enumerate(questions):
        if "id" not in q:
            q["id"] = f"q{idx+1}"
    return questions


# ---------------------------------------------------------
# 4. LangGraph 노드 함수들
# ---------------------------------------------------------

def plan_questions_node(state: PipelineState) -> PipelineState:
    meta = state.get("meta", {})
    insight_text = state.get("insight_text", "")

    plan = run_question_planner(meta, insight_text)
    questions_dicts = [q.model_dump() for q in plan.questions]
    questions_dicts = _ensure_question_ids(questions_dicts)

    return {
        "questions": questions_dicts,
        "research_notes": [],
        "report_structured": None,
        "report_markdown": None,
    }


def research_node(state: PipelineState) -> PipelineState:
    questions = state.get("questions", [])
    research_notes = state.get("research_notes", [])

    done_ids = {n.get("question_id") for n in research_notes}
    pending = [q for q in questions if q.get("id") not in done_ids]

    if not pending:
        # 더 할 게 없으면 그대로 반환 (route 함수에서 synthesize로 넘어감)
        return {}

    research_agent = build_beauty_research_agent()
    max_per_call = 3
    updated_notes = list(research_notes)

    for q in pending[:max_per_call]:
        q_model = SearchQuestion(
            category=q["category"],
            question=q["question"],
            priority=q.get("priority", 1),
        )
        note = run_research_for_question(research_agent, q_model)

        if len(note.get("summary", "")) < 200:
            refined_q_model = SearchQuestion(
                category=q_model.category,
                question=q_model.question + " (최근 2~3년 기준의 구체적인 사례 중심으로)",
                priority=q_model.priority,
            )
            note_retry = run_research_for_question(research_agent, refined_q_model)
            if len(note_retry.get("summary", "")) > len(note.get("summary", "")):
                note = note_retry

        note["question_id"] = q.get("id")
        updated_notes.append(note)

    return {"research_notes": updated_notes}


def synthesize_node(state: PipelineState) -> PipelineState:
    meta = state.get("meta", {})
    insight_text = state.get("insight_text", "")
    questions = state.get("questions", [])
    research_notes = state.get("research_notes", [])

    errors = state.get("errors", [])

    if not questions:
        errors.append("질문이 없습니다. plan_questions_node가 먼저 실행되어야 합니다.")
        return {"errors": errors}

    if not research_notes:
        errors.append("리서치 결과가 없습니다. research_node가 먼저 실행되어야 합니다.")
        return {"errors": errors}

    report = run_strategist(meta, insight_text, questions, research_notes)
    markdown = render_strategy_report_markdown(report)

    return {
        "report_structured": report.model_dump(),
        "report_markdown": markdown,
    }


# ---------------------------------------------------------
# 5. research 노드에서 다음 노드 라우팅
# ---------------------------------------------------------

def route_from_research(state: PipelineState) -> str:
    questions = state.get("questions", [])
    research_notes = state.get("research_notes", [])

    done_ids = {n.get("question_id") for n in research_notes}
    pending = [q for q in questions if q.get("id") not in done_ids]

    if pending:
        return "research"     # 아직 남은 질문 있으면 한 번 더 research 노드
    return "synthesize"       # 다 채웠으면 synthesize로


# ---------------------------------------------------------
# 6. 그래프 정의 및 컴파일
# ---------------------------------------------------------

builder = StateGraph(PipelineState)

builder.add_node("plan_questions", plan_questions_node)
builder.add_node("research", research_node)
builder.add_node("synthesize", synthesize_node)

builder.set_entry_point("plan_questions")
builder.add_edge("plan_questions", "research")
builder.add_conditional_edges(
    "research",
    route_from_research,
    {
        "research": "research",
        "synthesize": "synthesize",
    },
)
builder.add_edge("synthesize", END)

graph = builder.compile()  # ⬅️ LangGraph Studio에서 이 graph를 바라보게 하면 됨


# ---------------------------------------------------------
# 7. 파이썬에서 직접 돌려보고 싶을 때용 헬퍼
# ---------------------------------------------------------

def run_pipeline(insight_text: str, influencer_meta: Dict[str, Any]) -> PipelineState:
    initial_state: PipelineState = {
        "meta": influencer_meta,
        "insight_text": insight_text,
        "questions": [],
        "research_notes": [],
        "report_structured": None,
        "report_markdown": None,
        "errors": [],
    }
    return graph.invoke(initial_state)


if __name__ == "__main__":
    dummy_insight = """
    - 이 인플루언서는 20~30대 민감성/복합성 피부 타깃으로 성분 설명 위주의 콘텐츠를 만든다.
    - '자극 최소화', '장벽 회복', '임산부도 쓸 수 있는 스킨케어'를 자주 언급한다.
    - 고가 럭셔리보다는, 합리적인 가격대의 제품을 선호하고 솔직한 사용감을 공유한다.
    """

    dummy_meta = {
        "name": "예시 인플루언서",
        "platforms": ["Instagram", "YouTube", "TikTok"],
        "follower_range": "100k-300k",
        "target_audience": "20대 후반 ~ 30대 초반, 민감성/복합성 피부, 직장인 여성",
        "tone_style": "성분 설명 위주, 과장 없는 현실적인 리뷰",
    }

    final_state = run_pipeline(dummy_insight, dummy_meta)
    print("\n=== 최종 STATE ===")
    print(json.dumps(final_state, ensure_ascii=False, indent=2))
    print("\n=== 최종 리포트 (앞부분) ===")
    print((final_state.get("report_markdown") or "")[:2000])
