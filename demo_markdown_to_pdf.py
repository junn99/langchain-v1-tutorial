"""마크다운 → PDF 변환 데모 (LLM 없이 실행 가능)"""

from pdf_beautifier.pdf_generator import PDFGenerator

# 예제 마크다운 (보고서 형태)
sample_markdown = """
# 2024 AI 기술 트렌드 분석 보고서

## 개요

본 보고서는 2024년 인공지능 기술의 주요 트렌드와 비즈니스 영향을 분석합니다.

## 주요 발견사항

### 1. 생성형 AI의 폭발적 성장

생성형 AI 시장은 **전년 대비 300% 성장**을 기록했습니다. 주요 동인은 다음과 같습니다:

- **대규모 언어 모델(LLM)** 기술의 발전
- **멀티모달 AI**의 상용화
- 비용 효율적인 클라우드 서비스

> "AI는 더 이상 미래가 아닌 현재입니다" - Gartner 2024

### 2. 기업 도입 현황

다음은 산업별 AI 도입률입니다:

| 산업 | 도입률 | 전년 대비 |
|------|--------|-----------|
| 금융 | 78% | +15% |
| 제조 | 65% | +22% |
| 유통 | 71% | +18% |
| 헬스케어 | 59% | +25% |

### 3. 기술 스택

현재 가장 많이 사용되는 AI 프레임워크:

1. **TensorFlow** - 구글의 오픈소스 ML 프레임워크
2. **PyTorch** - Meta의 딥러닝 라이브러리
3. **LangChain** - LLM 애플리케이션 개발 프레임워크
4. **Hugging Face** - 사전학습 모델 허브

## 코드 예제

간단한 LLM 활용 예제:

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# LLM 초기화
llm = ChatOpenAI(model="gpt-4")

# 프롬프트 생성
prompt = ChatPromptTemplate.from_messages([
    ("system", "당신은 비즈니스 분석 전문가입니다."),
    ("human", "{question}")
])

# 체인 실행
chain = prompt | llm
result = chain.invoke({"question": "AI 트렌드는?"})
```

## 향후 전망

### 단기 전망 (6-12개월)

- 멀티모달 AI의 일반화
- AI 에이전트 생태계 확장
- 온디바이스 AI 성능 향상

### 중장기 전망 (1-3년)

- AGI(Artificial General Intelligence) 기초 연구 가속화
- AI 규제 프레임워크 확립
- 산업별 특화 AI 솔루션 증가

## 권장사항

기업들이 고려해야 할 핵심 액션 아이템:

1. ✅ **AI 전략 수립** - 명확한 비즈니스 목표 설정
2. ✅ **인재 확보** - AI 전문가 채용 및 교육
3. ✅ **데이터 품질 개선** - AI 성능의 핵심
4. ✅ **윤리 가이드라인** - 책임있는 AI 활용

## 결론

AI 기술은 **비즈니스 혁신의 핵심 동력**으로 자리잡았습니다.
조기 도입 기업들은 경쟁 우위를 확보하고 있으며,
이러한 격차는 시간이 지날수록 더욱 벌어질 것으로 예상됩니다.

---

**참고 자료:**
- Gartner AI Trends Report 2024
- McKinsey AI Impact Survey 2024
- Forrester AI Adoption Study 2024
"""

def main():
    print("📄 마크다운 → PDF 변환 데모\n")
    print("=" * 60)

    # PDF 생성기 초기화
    generator = PDFGenerator()

    # PDF 생성
    print("\n1️⃣ PDF 생성 중...")
    pdf_path = generator.generate_pdf(
        markdown_content=sample_markdown,
        output_path="./output/demo_report.pdf",
        style="business_report"
    )
    print(f"   ✅ PDF 생성 완료: {pdf_path}")

    # HTML 미리보기도 생성
    print("\n2️⃣ HTML 미리보기 생성 중...")
    html_path = generator.preview_html(
        markdown_content=sample_markdown,
        output_path="./output/demo_preview.html",
        style="business_report"
    )
    print(f"   ✅ HTML 생성 완료: {html_path}")

    print("\n" + "=" * 60)
    print("\n📊 생성된 보고서 내용:")
    print("-" * 60)
    print("- A4 사이즈")
    print("- 페이지 번호 자동 삽입")
    print("- 제목: 파란색 밑줄")
    print("- 섹션: 왼쪽 파란색 바")
    print("- 표: 스트라이프 스타일")
    print("- 코드 블록: 회색 배경")
    print("- 인용구: 왼쪽 회색 바")
    print("-" * 60)

    print("\n🎨 스타일 특징:")
    print("- 비즈니스 전문적 디자인")
    print("- 파란색 계열 강조색")
    print("- 깔끔한 타이포그래피")
    print("- 읽기 편한 간격과 여백")

    print("\n✨ 생성된 파일:")
    print(f"   PDF: {pdf_path}")
    print(f"   HTML: {html_path}")
    print("\n💡 HTML 파일을 브라우저에서 열어보세요!")

if __name__ == "__main__":
    main()
