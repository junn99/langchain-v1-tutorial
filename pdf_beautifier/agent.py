"""PDF 미화 에이전트 - 메인 클래스"""

from typing import Optional
from pathlib import Path
from langchain_core.language_models import BaseChatModel

from .text_analyzer import TextAnalyzer
from .pdf_generator import PDFGenerator


class PDFBeautifierAgent:
    """LLM이 생성한 텍스트를 예쁜 PDF로 변환하는 에이전트"""

    def __init__(
        self,
        llm: BaseChatModel,
        template_dir: Optional[Path] = None,
    ):
        """
        Args:
            llm: LangChain 호환 LLM 모델
            template_dir: CSS 템플릿 디렉토리 (기본값: pdf_beautifier/templates)
        """
        self.llm = llm
        self.analyzer = TextAnalyzer(llm)
        self.generator = PDFGenerator(template_dir)

    def beautify(
        self,
        text: str,
        output_path: str,
        title: Optional[str] = None,
        style: str = "business",
    ) -> dict:
        """
        텍스트를 예쁜 PDF로 변환

        Args:
            text: 변환할 텍스트
            output_path: 출력 PDF 파일 경로
            title: 문서 제목 (없으면 자동 생성)
            style: 문서 스타일 (business, academic, casual)

        Returns:
            결과 정보를 담은 딕셔너리
            {
                "success": bool,
                "pdf_path": str,
                "markdown": str,
                "message": str
            }
        """
        try:
            # 1단계: 텍스트 분석 및 마크다운 변환
            print("📝 텍스트를 분석하고 구조화하는 중...")
            markdown_content = self.analyzer.analyze_and_structure(
                text=text, title=title, style=style
            )

            # 2단계: PDF 생성
            print("🎨 PDF를 생성하는 중...")
            pdf_path = self.generator.generate_pdf(
                markdown_content=markdown_content,
                output_path=output_path,
                style="business_report",  # CSS 템플릿 이름
            )

            print(f"✅ PDF 생성 완료: {pdf_path}")

            return {
                "success": True,
                "pdf_path": pdf_path,
                "markdown": markdown_content,
                "message": f"PDF가 성공적으로 생성되었습니다: {pdf_path}",
            }

        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            return {
                "success": False,
                "pdf_path": None,
                "markdown": None,
                "message": f"PDF 생성 중 오류가 발생했습니다: {str(e)}",
            }

    def preview_html(
        self,
        text: str,
        output_path: str,
        title: Optional[str] = None,
        style: str = "business",
    ) -> dict:
        """
        HTML 미리보기 생성 (디버깅 및 미리보기용)

        Args:
            text: 변환할 텍스트
            output_path: 출력 HTML 파일 경로
            title: 문서 제목
            style: 문서 스타일

        Returns:
            결과 정보를 담은 딕셔너리
        """
        try:
            # 텍스트 분석 및 마크다운 변환
            markdown_content = self.analyzer.analyze_and_structure(
                text=text, title=title, style=style
            )

            # HTML 생성
            html_path = self.generator.preview_html(
                markdown_content=markdown_content,
                output_path=output_path,
                style="business_report",
            )

            return {
                "success": True,
                "html_path": html_path,
                "markdown": markdown_content,
                "message": f"HTML 미리보기가 생성되었습니다: {html_path}",
            }

        except Exception as e:
            return {
                "success": False,
                "html_path": None,
                "markdown": None,
                "message": f"HTML 생성 중 오류가 발생했습니다: {str(e)}",
            }

    def markdown_to_pdf(
        self,
        markdown_content: str,
        output_path: str,
        style: str = "business_report",
    ) -> dict:
        """
        이미 구조화된 마크다운을 PDF로 직접 변환

        Args:
            markdown_content: 마크다운 텍스트
            output_path: 출력 PDF 파일 경로
            style: CSS 스타일 템플릿 이름

        Returns:
            결과 정보를 담은 딕셔너리
        """
        try:
            pdf_path = self.generator.generate_pdf(
                markdown_content=markdown_content,
                output_path=output_path,
                style=style,
            )

            return {
                "success": True,
                "pdf_path": pdf_path,
                "message": f"PDF가 성공적으로 생성되었습니다: {pdf_path}",
            }

        except Exception as e:
            return {
                "success": False,
                "pdf_path": None,
                "message": f"PDF 생성 중 오류가 발생했습니다: {str(e)}",
            }
