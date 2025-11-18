"""PDF 미화 에이전트 - 메인 클래스 (개선 버전)"""

from typing import Optional, Dict
from pathlib import Path
from datetime import datetime
from langchain_core.language_models import BaseChatModel

from .text_analyzer import TextAnalyzer
from .pdf_generator import PDFGenerator


class PDFBeautifierAgent:
    """LLM이 생성한 텍스트를 예쁜 PDF로 변환하는 에이전트 (개선 버전)"""

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
        color_theme: str = "blue",
        author: Optional[str] = None,
        include_toc: bool = True,
        metadata: Optional[Dict[str, str]] = None,
    ) -> dict:
        """
        텍스트를 예쁜 PDF로 변환 (개선 버전)

        Args:
            text: 변환할 텍스트
            output_path: 출력 PDF 파일 경로
            title: 문서 제목 (없으면 자동 생성)
            style: 문서 스타일 (business, academic, casual)
            color_theme: 색상 테마 (blue, green, purple, red, orange)
            author: 작성자 이름
            include_toc: 목차 포함 여부 (기본값: True)
            metadata: 추가 PDF 메타데이터 (subject, keywords 등)

        Returns:
            결과 정보를 담은 딕셔너리
            {
                "success": bool,
                "pdf_path": str,
                "markdown": str,
                "metadata": dict,
                "message": str
            }
        """
        try:
            # 1단계: 텍스트 분석 및 마크다운 변환
            print("📝 텍스트를 분석하고 구조화하는 중...")
            markdown_content = self.analyzer.analyze_and_structure(
                text=text, title=title, style=style
            )

            # 2단계: 메타데이터 준비
            if metadata is None:
                metadata = {}

            # 제목이 제공되지 않았다면 마크다운의 첫 번째 헤딩 추출 시도
            if title:
                metadata["title"] = title
            else:
                metadata.setdefault("title", self._extract_title(markdown_content))

            metadata.setdefault("author", author or "PDF Beautifier Agent")
            metadata.setdefault("subject", f"{metadata['title']} - Generated Report")
            metadata.setdefault("keywords", "report, analysis, business")
            metadata.setdefault("creator", "LangChain PDF Beautifier")

            # 3단계: PDF 생성
            print(f"🎨 PDF를 생성하는 중 (테마: {color_theme})...")
            pdf_path = self.generator.generate_pdf(
                markdown_content=markdown_content,
                output_path=output_path,
                style="business_report",
                metadata=metadata,
                color_theme=color_theme,
                include_toc=include_toc,
            )

            print(f"✅ PDF 생성 완료: {pdf_path}")

            return {
                "success": True,
                "pdf_path": pdf_path,
                "markdown": markdown_content,
                "metadata": metadata,
                "message": f"PDF가 성공적으로 생성되었습니다: {pdf_path}",
            }

        except Exception as e:
            error_msg = f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "pdf_path": None,
                "markdown": None,
                "metadata": None,
                "message": error_msg,
                "error": str(e),
            }

    def preview_html(
        self,
        text: str,
        output_path: str,
        title: Optional[str] = None,
        style: str = "business",
        color_theme: str = "blue",
        include_toc: bool = True,
    ) -> dict:
        """
        HTML 미리보기 생성 (개선 버전)

        Args:
            text: 변환할 텍스트
            output_path: 출력 HTML 파일 경로
            title: 문서 제목
            style: 문서 스타일
            color_theme: 색상 테마
            include_toc: 목차 포함 여부

        Returns:
            결과 정보를 담은 딕셔너리
        """
        try:
            # 텍스트 분석 및 마크다운 변환
            print("📝 텍스트를 분석하고 구조화하는 중...")
            markdown_content = self.analyzer.analyze_and_structure(
                text=text, title=title, style=style
            )

            # HTML 생성
            print(f"🌐 HTML 미리보기 생성 중 (테마: {color_theme})...")
            html_path = self.generator.preview_html(
                markdown_content=markdown_content,
                output_path=output_path,
                style="business_report",
                color_theme=color_theme,
                include_toc=include_toc,
            )

            print(f"✅ HTML 생성 완료: {html_path}")

            return {
                "success": True,
                "html_path": html_path,
                "markdown": markdown_content,
                "message": f"HTML 미리보기가 생성되었습니다: {html_path}",
            }

        except Exception as e:
            error_msg = f"HTML 생성 중 오류가 발생했습니다: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "html_path": None,
                "markdown": None,
                "message": error_msg,
                "error": str(e),
            }

    def markdown_to_pdf(
        self,
        markdown_content: str,
        output_path: str,
        style: str = "business_report",
        color_theme: str = "blue",
        metadata: Optional[Dict[str, str]] = None,
        include_toc: bool = True,
    ) -> dict:
        """
        이미 구조화된 마크다운을 PDF로 직접 변환 (개선 버전)

        Args:
            markdown_content: 마크다운 텍스트
            output_path: 출력 PDF 파일 경로
            style: CSS 스타일 템플릿 이름
            color_theme: 색상 테마
            metadata: PDF 메타데이터
            include_toc: 목차 포함 여부

        Returns:
            결과 정보를 담은 딕셔너리
        """
        try:
            # 메타데이터 기본값 설정
            if metadata is None:
                metadata = {}
            metadata.setdefault("title", self._extract_title(markdown_content))
            metadata.setdefault("author", "PDF Beautifier Agent")

            print(f"🎨 PDF 생성 중 (테마: {color_theme})...")
            pdf_path = self.generator.generate_pdf(
                markdown_content=markdown_content,
                output_path=output_path,
                style=style,
                metadata=metadata,
                color_theme=color_theme,
                include_toc=include_toc,
            )

            print(f"✅ PDF 생성 완료: {pdf_path}")

            return {
                "success": True,
                "pdf_path": pdf_path,
                "metadata": metadata,
                "message": f"PDF가 성공적으로 생성되었습니다: {pdf_path}",
            }

        except Exception as e:
            error_msg = f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "pdf_path": None,
                "metadata": None,
                "message": error_msg,
                "error": str(e),
            }

    def _extract_title(self, markdown_content: str) -> str:
        """
        마크다운에서 첫 번째 헤딩을 제목으로 추출

        Args:
            markdown_content: 마크다운 텍스트

        Returns:
            추출된 제목 또는 기본값
        """
        lines = markdown_content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line.lstrip("# ").strip()
        return "Document"
