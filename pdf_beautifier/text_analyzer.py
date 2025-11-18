"""텍스트 분석 및 구조화 모듈"""

from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel


class TextAnalyzer:
    """LLM을 사용하여 긴 텍스트를 구조화된 마크다운으로 변환"""

    def __init__(self, llm: BaseChatModel):
        """
        Args:
            llm: LangChain 호환 LLM 모델
        """
        self.llm = llm
        self.parser = StrOutputParser()

    def analyze_and_structure(
        self, text: str, title: Optional[str] = None, style: str = "business"
    ) -> str:
        """
        텍스트를 분석하고 구조화된 마크다운으로 변환

        Args:
            text: 분석할 원본 텍스트
            title: 문서 제목 (없으면 자동 생성)
            style: 문서 스타일 (business, academic, casual 등)

        Returns:
            구조화된 마크다운 텍스트
        """
        style_instructions = self._get_style_instructions(style)

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_prompt(style_instructions)),
                ("human", self._get_human_prompt(title)),
            ]
        )

        chain = prompt | self.llm | self.parser

        result = chain.invoke({"text": text, "title": title or "자동 제목"})
        return result

    def _get_style_instructions(self, style: str) -> str:
        """스타일별 지침 반환"""
        styles = {
            "business": """
- 비즈니스 보고서 형식을 따릅니다
- 명확하고 간결한 문장을 사용합니다
- 핵심 포인트를 강조합니다
- 필요시 테이블이나 리스트로 정리합니다
- 섹션을 논리적으로 구분합니다
""",
            "academic": """
- 학술 논문 형식을 따릅니다
- 서론, 본론, 결론 구조를 유지합니다
- 인용이나 참조가 필요한 부분을 표시합니다
- 전문적이고 형식적인 어조를 사용합니다
""",
            "casual": """
- 읽기 쉽고 친근한 형식을 사용합니다
- 짧은 단락과 간단한 문장을 선호합니다
- 이모티콘이나 강조 표현을 적절히 사용합니다
""",
        }
        return styles.get(style, styles["business"])

    def _get_system_prompt(self, style_instructions: str) -> str:
        """시스템 프롬프트 생성"""
        return f"""당신은 텍스트를 아름다운 문서로 변환하는 전문가입니다.
주어진 텍스트를 분석하여 잘 구조화된 마크다운 형식으로 변환해야 합니다.

스타일 지침:
{style_instructions}

마크다운 규칙:
1. 제목 계층을 올바르게 사용하세요 (# 메인 제목, ## 섹션, ### 하위섹션)
2. 핵심 내용은 **굵게** 표시하세요
3. 리스트나 테이블로 정리하면 좋은 내용은 적절히 변환하세요
4. 긴 텍스트는 논리적인 섹션으로 나누세요
5. 코드나 기술적 내용은 ```코드블록```을 사용하세요
6. 중요한 참고사항은 > 인용구로 표시하세요

반드시 마크다운 형식으로만 응답하세요. 추가 설명은 하지 마세요."""

    def _get_human_prompt(self, title: Optional[str]) -> str:
        """사용자 프롬프트 생성"""
        if title:
            return f"""다음 텍스트를 "{title}" 제목으로 구조화된 마크다운 문서로 변환해주세요:

{{text}}

위 텍스트를 분석하여 아름답고 읽기 쉬운 마크다운 문서로 변환해주세요."""
        else:
            return """다음 텍스트를 분석하여 적절한 제목을 붙이고 구조화된 마크다운 문서로 변환해주세요:

{text}

위 텍스트를 분석하여 아름답고 읽기 쉬운 마크다운 문서로 변환해주세요."""
