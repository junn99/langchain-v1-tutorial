"""PDF를 이미지로 변환하여 미리보기 생성"""

import fitz  # PyMuPDF
from PIL import Image
import os


def pdf_to_images(pdf_path, output_dir="./output/preview_images", max_pages=3):
    """
    PDF를 이미지로 변환

    Args:
        pdf_path: PDF 파일 경로
        output_dir: 출력 디렉토리
        max_pages: 최대 페이지 수 (기본 3페이지)

    Returns:
        생성된 이미지 파일 경로 리스트
    """
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)

    # PDF 열기
    doc = fitz.open(pdf_path)

    image_paths = []

    # 최대 페이지 수만큼 변환
    num_pages = min(len(doc), max_pages)

    print(f"📄 PDF: {os.path.basename(pdf_path)}")
    print(f"   총 페이지: {len(doc)}, 변환할 페이지: {num_pages}\n")

    for page_num in range(num_pages):
        page = doc[page_num]

        # 고해상도로 렌더링 (zoom=2.0)
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)

        # 이미지 저장
        output_path = os.path.join(
            output_dir,
            f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page{page_num + 1}.png"
        )
        pix.save(output_path)

        image_paths.append(output_path)
        print(f"✅ 페이지 {page_num + 1} → {output_path}")

    doc.close()
    return image_paths


def main():
    print("🖼️  PDF → 이미지 변환 데모\n")
    print("=" * 70)

    # 변환할 PDF 파일들
    pdfs_to_convert = [
        "./output/improved_blue_with_toc.pdf",
        "./output/improved_green.pdf",
        "./output/report_with_images.pdf",
    ]

    all_images = []

    for pdf_path in pdfs_to_convert:
        if os.path.exists(pdf_path):
            print(f"\n📄 {pdf_path} 변환 중...")
            print("-" * 70)
            images = pdf_to_images(pdf_path, max_pages=3)
            all_images.extend(images)
        else:
            print(f"⚠️  파일 없음: {pdf_path}")

    print("\n" + "=" * 70)
    print(f"\n✨ 총 {len(all_images)}개 이미지 생성 완료!")
    print(f"📁 저장 위치: ./output/preview_images/")

    return all_images


if __name__ == "__main__":
    images = main()
