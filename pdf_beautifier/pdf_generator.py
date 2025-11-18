"""PDF 생성 모듈"""

import os
from pathlib import Path
from typing import Optional
import markdown
from weasyprint import HTML, CSS


class PDFGenerator:
    """마크다운을 예쁜 PDF로 변환"""

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
    ) -> str:
        """
        마크다운 컨텐츠를 PDF로 변환

        Args:
            markdown_content: 마크다운 형식의 텍스트
            output_path: 출력 PDF 파일 경로
            style: 사용할 CSS 스타일 템플릿 이름

        Returns:
            생성된 PDF 파일의 절대 경로
        """
        # 마크다운을 HTML로 변환
        html_content = self._markdown_to_html(markdown_content)

        # CSS 스타일 로드
        css_path = self.template_dir / f"{style}.css"
        if not css_path.exists():
            css_path = self.template_dir / "business_report.css"

        # PDF 생성
        html = HTML(string=html_content)
        css = CSS(filename=str(css_path))

        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html.write_pdf(output_path, stylesheets=[css])

        return str(output_path)

    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        마크다운을 HTML로 변환

        Args:
            markdown_content: 마크다운 텍스트

        Returns:
            HTML 문자열
        """
        # 마크다운 익스텐션 설정
        md = markdown.Markdown(
            extensions=[
                "extra",  # 테이블, 각주 등 추가 기능
                "codehilite",  # 코드 하이라이팅
                "toc",  # 목차
                "nl2br",  # 줄바꿈을 <br>로 변환
                "sane_lists",  # 개선된 리스트 처리
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "linenums": False,
                },
            },
        )

        # HTML 변환
        body_html = md.convert(markdown_content)

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

        return html_template

    def preview_html(
        self, markdown_content: str, output_path: str, style: str = "business_report"
    ) -> str:
        """
        HTML 미리보기 파일 생성 (디버깅용)

        Args:
            markdown_content: 마크다운 텍스트
            output_path: 출력 HTML 파일 경로
            style: CSS 스타일

        Returns:
            생성된 HTML 파일의 절대 경로
        """
        html_content = self._markdown_to_html(markdown_content)

        # CSS 인라인으로 포함
        css_path = self.template_dir / f"{style}.css"
        if not css_path.exists():
            css_path = self.template_dir / "business_report.css"

        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        # CSS를 HTML에 포함
        html_with_css = html_content.replace(
            "</head>", f"<style>\n{css_content}\n</style>\n</head>"
        )

        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_with_css)

        return str(output_path)
