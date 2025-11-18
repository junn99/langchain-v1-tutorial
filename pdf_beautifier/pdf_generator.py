"""PDF 생성 모듈 - 개선 버전"""

import os
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class PDFGenerator:
    """마크다운을 예쁜 PDF로 변환 (목차, 메타데이터, 색상 테마 지원)"""

    # 색상 테마 정의
    COLOR_THEMES = {
        "blue": {
            "primary": "#2563eb",
            "secondary": "#1e40af",
            "tertiary": "#1e3a8a",
            "accent": "#3b82f6",
            "light": "#dbeafe",
        },
        "green": {
            "primary": "#059669",
            "secondary": "#047857",
            "tertiary": "#065f46",
            "accent": "#10b981",
            "light": "#d1fae5",
        },
        "purple": {
            "primary": "#7c3aed",
            "secondary": "#6d28d9",
            "tertiary": "#5b21b6",
            "accent": "#8b5cf6",
            "light": "#ede9fe",
        },
        "red": {
            "primary": "#dc2626",
            "secondary": "#b91c1c",
            "tertiary": "#991b1b",
            "accent": "#ef4444",
            "light": "#fee2e2",
        },
        "orange": {
            "primary": "#ea580c",
            "secondary": "#c2410c",
            "tertiary": "#9a3412",
            "accent": "#f97316",
            "light": "#fed7aa",
        },
    }

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Args:
            template_dir: CSS 템플릿 디렉토리 경로
        """
        if template_dir is None:
            template_dir = Path(__file__).parent / "templates"
        self.template_dir = Path(template_dir)

    def generate_pdf(
        self,
        markdown_content: str,
        output_path: str,
        style: str = "business_report",
        metadata: Optional[Dict[str, str]] = None,
        color_theme: str = "blue",
        include_toc: bool = True,
    ) -> str:
        """
        마크다운 컨텐츠를 PDF로 변환

        Args:
            markdown_content: 마크다운 형식의 텍스트
            output_path: 출력 PDF 파일 경로
            style: 사용할 CSS 스타일 템플릿 이름
            metadata: PDF 메타데이터 (title, author, subject, keywords)
            color_theme: 색상 테마 (blue, green, purple, red, orange)
            include_toc: 목차 포함 여부

        Returns:
            생성된 PDF 파일의 절대 경로
        """
        try:
            # 마크다운을 HTML로 변환
            html_content, toc_html = self._markdown_to_html(
                markdown_content, include_toc=include_toc
            )

            # CSS 스타일 생성 (색상 테마 적용)
            css_content = self._generate_css(style, color_theme)

            # 메타데이터 기본값 설정
            if metadata is None:
                metadata = {}
            metadata.setdefault("title", "Document")
            metadata.setdefault("author", "PDF Beautifier Agent")
            metadata.setdefault("subject", "Generated Report")
            metadata.setdefault("creator", "LangChain PDF Beautifier")

            # 메타데이터를 HTML에 추가
            html_with_meta = self._add_metadata_to_html(
                html_content, metadata, toc_html
            )

            # PDF 생성
            font_config = FontConfiguration()
            html_obj = HTML(string=html_with_meta)
            css_obj = CSS(string=css_content, font_config=font_config)

            output_path = Path(output_path).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # PDF 메타데이터 추가하여 생성
            html_obj.write_pdf(
                output_path,
                stylesheets=[css_obj],
                font_config=font_config,
                pdf_metadata={
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "keywords": metadata.get("keywords", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": "WeasyPrint with LangChain",
                },
            )

            return str(output_path)

        except Exception as e:
            raise Exception(f"PDF 생성 실패: {str(e)}") from e

    def _markdown_to_html(
        self, markdown_content: str, include_toc: bool = True
    ) -> tuple[str, str]:
        """
        마크다운을 HTML로 변환 (개선된 버전)

        Args:
            markdown_content: 마크다운 텍스트
            include_toc: 목차 포함 여부

        Returns:
            (HTML 문자열, TOC HTML) 튜플
        """
        # 마크다운 익스텐션 설정 (모든 기능 활성화)
        extensions = [
            "extra",  # 테이블, 각주, 속성 리스트 등
            "codehilite",  # 코드 하이라이팅
            "sane_lists",  # 개선된 리스트 처리
            "smarty",  # 스마트 따옴표, 대시 등
            "admonition",  # 경고/정보 박스
            "meta",  # 메타데이터
            "wikilinks",  # 위키 스타일 링크
            "abbr",  # 약어
            "def_list",  # 정의 리스트
        ]

        if include_toc:
            extensions.append("toc")

        extension_configs = {
            "codehilite": {
                "css_class": "highlight",
                "linenums": False,
                "guess_lang": False,
            },
            "toc": {
                "title": "목차",
                "toc_depth": "2-3",  # h2, h3만 목차에 포함
            },
        }

        try:
            md = markdown.Markdown(
                extensions=extensions, extension_configs=extension_configs
            )

            # HTML 변환
            body_html = md.convert(markdown_content)

            # 목차 HTML 추출
            toc_html = ""
            if include_toc and hasattr(md, "toc"):
                toc_html = md.toc

            # 완전한 HTML 문서 생성
            html_template = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
{body_html}
</body>
</html>"""

            return html_template, toc_html

        except Exception as e:
            raise Exception(f"마크다운 변환 실패: {str(e)}") from e

    def _generate_css(self, style: str, color_theme: str) -> str:
        """
        CSS 생성 (색상 테마 적용)

        Args:
            style: CSS 스타일 템플릿 이름
            color_theme: 색상 테마

        Returns:
            CSS 문자열
        """
        # 기본 템플릿 로드
        css_path = self.template_dir / f"{style}.css"
        if not css_path.exists():
            css_path = self.template_dir / "business_report.css"

        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()

            # 색상 테마 적용
            theme = self.COLOR_THEMES.get(color_theme, self.COLOR_THEMES["blue"])

            # CSS 변수 치환 (파란색을 선택한 테마 색상으로 변경)
            css_content = css_content.replace("#2563eb", theme["primary"])
            css_content = css_content.replace("#1e40af", theme["secondary"])
            css_content = css_content.replace("#1e3a8a", theme["tertiary"])
            css_content = css_content.replace("#3b82f6", theme["accent"])
            css_content = css_content.replace("#dbeafe", theme["light"])

            return css_content

        except Exception as e:
            raise Exception(f"CSS 로드 실패: {str(e)}") from e

    def _add_metadata_to_html(
        self, html_content: str, metadata: Dict[str, str], toc_html: str
    ) -> str:
        """
        HTML에 메타데이터와 목차 추가

        Args:
            html_content: 원본 HTML
            metadata: 메타데이터 딕셔너리
            toc_html: 목차 HTML

        Returns:
            메타데이터가 추가된 HTML
        """
        # 메타 태그 생성
        meta_tags = f"""
    <meta name="author" content="{metadata.get('author', '')}">
    <meta name="description" content="{metadata.get('subject', '')}">
    <meta name="keywords" content="{metadata.get('keywords', '')}">
    <meta name="generator" content="PDF Beautifier Agent">
    <meta name="created" content="{datetime.now().isoformat()}">
"""

        # 제목 업데이트
        html_content = html_content.replace(
            "<title>Document</title>", f"<title>{metadata.get('title', 'Document')}</title>"
        )

        # 메타 태그 삽입
        html_content = html_content.replace("</head>", f"{meta_tags}</head>")

        # 목차가 있으면 본문 앞에 삽입
        if toc_html:
            toc_section = f"""
<div class="table-of-contents">
<h2>목차</h2>
{toc_html}
</div>
<div class="page-break"></div>
"""
            html_content = html_content.replace("<body>", f"<body>\n{toc_section}")

        return html_content

    def preview_html(
        self,
        markdown_content: str,
        output_path: str,
        style: str = "business_report",
        color_theme: str = "blue",
        include_toc: bool = True,
    ) -> str:
        """
        HTML 미리보기 파일 생성 (개선된 버전)

        Args:
            markdown_content: 마크다운 텍스트
            output_path: 출력 HTML 파일 경로
            style: CSS 스타일
            color_theme: 색상 테마
            include_toc: 목차 포함 여부

        Returns:
            생성된 HTML 파일의 절대 경로
        """
        try:
            html_content, toc_html = self._markdown_to_html(
                markdown_content, include_toc=include_toc
            )

            # CSS 생성
            css_content = self._generate_css(style, color_theme)

            # 메타데이터 추가
            metadata = {
                "title": "Preview",
                "author": "PDF Beautifier Agent",
                "subject": "HTML Preview",
            }
            html_with_meta = self._add_metadata_to_html(
                html_content, metadata, toc_html
            )

            # CSS를 HTML에 인라인으로 포함
            html_with_css = html_with_meta.replace(
                "</head>", f"<style>\n{css_content}\n</style>\n</head>"
            )

            output_path = Path(output_path).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_with_css)

            return str(output_path)

        except Exception as e:
            raise Exception(f"HTML 미리보기 생성 실패: {str(e)}") from e
