"""이미지 포함 PDF 데모"""

from pdf_beautifier.pdf_generator import PDFGenerator
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_chart():
    """간단한 차트 이미지 생성"""
    # 800x400 이미지 생성
    img = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img)

    # 제목
    draw.text((350, 20), "매출 성장 추이", fill='#1e40af')

    # 간단한 막대 그래프
    bars = [
        ("Q1", 150, "#3b82f6"),
        ("Q2", 220, "#60a5fa"),
        ("Q3", 280, "#2563eb"),
        ("Q4", 350, "#1e40af"),
    ]

    x_start = 100
    bar_width = 120
    spacing = 50

    for i, (label, height, color) in enumerate(bars):
        x = x_start + i * (bar_width + spacing)
        y = 350 - height

        # 막대 그리기
        draw.rectangle([x, y, x + bar_width, 350], fill=color)

        # 레이블
        draw.text((x + 30, 360), label, fill='black')

        # 값
        draw.text((x + 30, y - 20), f"${height}M", fill=color)

    # 축
    draw.line([(80, 350), (720, 350)], fill='black', width=2)
    draw.line([(80, 50), (80, 350)], fill='black', width=2)

    # 저장
    os.makedirs("./output/images", exist_ok=True)
    img_path = "./output/images/chart.png"
    img.save(img_path)
    return img_path

def create_sample_logo():
    """간단한 로고 이미지 생성"""
    img = Image.new('RGB', (400, 200), color='#f0f9ff')
    draw = ImageDraw.Draw(img)

    # 원 그리기
    draw.ellipse([50, 50, 150, 150], fill='#2563eb', outline='#1e40af', width=3)

    # 텍스트
    draw.text((180, 80), "TechCorp", fill='#1e40af')

    img_path = "./output/images/logo.png"
    img.save(img_path)
    return img_path

def main():
    print("🖼️  이미지 포함 PDF 데모\n")
    print("=" * 60)

    # 샘플 이미지 생성
    print("\n1️⃣ 샘플 이미지 생성 중...")
    chart_path = create_sample_chart()
    logo_path = create_sample_logo()
    print(f"   ✅ 차트: {chart_path}")
    print(f"   ✅ 로고: {logo_path}")

    # 절대 경로로 변환
    chart_abs = os.path.abspath(chart_path)
    logo_abs = os.path.abspath(logo_path)

    # 이미지 포함 마크다운
    markdown_with_images = f"""
# 기업 분석 보고서

![Company Logo]({logo_abs})

## 개요

본 보고서는 TechCorp의 2024년 성과를 분석합니다.

## 재무 성과

### 분기별 매출 현황

다음은 2024년 분기별 매출 추이입니다:

![매출 성장 추이]({chart_abs})

**주요 하이라이트:**

- Q1: $150M (전년 대비 +15%)
- Q2: $220M (전년 대비 +22%)
- Q3: $280M (전년 대비 +28%)
- Q4: $350M (전년 대비 +35%)

### 분석

매출은 **지속적인 상승세**를 보이고 있으며, 특히 Q4에 가장 높은 성장률을 기록했습니다.

> 💡 **인사이트**: 신제품 출시와 마케팅 강화가 매출 성장의 주요 동인으로 작용했습니다.

## 시장 점유율

| 시장 | 점유율 | 순위 |
|------|--------|------|
| 북미 | 35% | 1위 |
| 유럽 | 28% | 2위 |
| 아시아 | 22% | 3위 |

## 결론

TechCorp는 **강력한 성장 모멘텀**을 유지하고 있으며,
2025년에도 지속 가능한 성장이 예상됩니다.

---

*본 보고서는 2024년 12월 기준으로 작성되었습니다.*
"""

    # PDF 생성
    print("\n2️⃣ 이미지 포함 PDF 생성 중...")
    generator = PDFGenerator()

    pdf_path = generator.generate_pdf(
        markdown_content=markdown_with_images,
        output_path="./output/report_with_images.pdf",
        style="business_report"
    )
    print(f"   ✅ PDF 생성 완료: {pdf_path}")

    # HTML 미리보기
    print("\n3️⃣ HTML 미리보기 생성 중...")
    html_path = generator.preview_html(
        markdown_content=markdown_with_images,
        output_path="./output/preview_with_images.html",
        style="business_report"
    )
    print(f"   ✅ HTML 생성 완료: {html_path}")

    print("\n" + "=" * 60)
    print("\n📸 이미지 지원 기능:")
    print("-" * 60)
    print("✅ PNG, JPG, GIF 등 모든 이미지 형식 지원")
    print("✅ 로컬 파일 경로 또는 URL 사용 가능")
    print("✅ 자동 크기 조정 (페이지 너비에 맞춤)")
    print("✅ 차트, 그래프, 로고, 스크린샷 등 삽입 가능")
    print("-" * 60)

    print("\n💡 마크다운에서 이미지 사용법:")
    print("   ![이미지 설명](이미지경로)")
    print("   예: ![로고](./images/logo.png)")

    print("\n✨ 생성된 파일:")
    print(f"   PDF: {pdf_path}")
    print(f"   HTML: {html_path}")

if __name__ == "__main__":
    main()
