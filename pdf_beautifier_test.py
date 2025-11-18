"""PDF Beautifier Agent 간단 테스트 스크립트"""

import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from pdf_beautifier import PDFBeautifierAgent

# 환경 변수 로드
load_dotenv()


def main():
    print("🚀 PDF Beautifier Agent 테스트 시작\n")

    # LLM 초기화
    print("1. LLM 초기화...")
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.7)
    agent = PDFBeautifierAgent(llm=llm)
    print("   ✅ 완료\n")

    # 테스트 텍스트
    sample_text = """
    클라우드 컴퓨팅의 미래

    클라우드 컴퓨팅은 현대 비즈니스의 핵심 인프라로 자리잡았습니다.
    AWS, Azure, Google Cloud와 같은 주요 클라우드 플랫폼들은 기업들에게
    확장 가능하고 안정적인 서비스를 제공하고 있습니다.

    주요 트렌드

    서버리스 아키텍처가 급속도로 성장하고 있습니다.
    개발자들은 인프라 관리에 신경 쓰지 않고 코드 작성에만 집중할 수 있습니다.

    멀티 클라우드 전략을 채택하는 기업이 증가하고 있습니다.
    이는 벤더 종속성을 줄이고 최적의 서비스를 선택할 수 있게 해줍니다.

    엣지 컴퓨팅이 클라우드와 결합되면서 실시간 데이터 처리 능력이 향상되고 있습니다.
    IoT 디바이스의 증가와 함께 엣지 컴퓨팅의 중요성이 더욱 커지고 있습니다.

    보안 고려사항

    클라우드 보안은 여전히 가장 중요한 이슈입니다.
    제로 트러스트 보안 모델, 암호화, 접근 제어 등 다층 보안 전략이 필요합니다.
    규정 준수와 데이터 주권 문제도 신중하게 다뤄야 합니다.

    결론

    클라우드 컴퓨팅은 계속해서 진화하고 있으며,
    기업들은 이러한 변화에 발맞춰 전략을 수정해야 합니다.
    """

    # PDF 생성
    print("2. PDF 생성 중...")
    result = agent.beautify(
        text=sample_text,
        output_path="./output/test_report.pdf",
        title="클라우드 컴퓨팅 트렌드 보고서",
        style="business",
    )

    # 결과 출력
    print("\n" + "=" * 60)
    if result["success"]:
        print(f"✅ {result['message']}")
        print("\n생성된 마크다운 미리보기:")
        print("-" * 60)
        print(result["markdown"])
        print("-" * 60)
    else:
        print(f"❌ {result['message']}")
    print("=" * 60)

    # HTML 미리보기도 생성
    print("\n3. HTML 미리보기 생성 중...")
    preview_result = agent.preview_html(
        text=sample_text,
        output_path="./output/test_preview.html",
        title="클라우드 컴퓨팅 트렌드 보고서",
        style="business",
    )

    if preview_result["success"]:
        print(f"   ✅ {preview_result['message']}")

    print("\n🎉 테스트 완료!")


if __name__ == "__main__":
    main()
