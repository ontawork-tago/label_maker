import fitz
import os

def extract_base_images(pdf_path, output_dir="assets/templates"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc = fitz.open(pdf_path)
    # ITEM 22 (Algeria)가 있는 8페이지 분석
    page = doc[7]
    
    # 빨간색 (0.93, 0.11, 0.14) 구성 요소들을 숨기거나 제거한 후 캡쳐 시도
    # 하지만 단순 캡쳐 후 빨간색 픽셀을 검은색으로 치환하는 방식이 더 확실할 수 있음
    
    # 1. 고해상도 렌더링
    zoom = 4 # 4x 해상도
    mat = fitz.Matrix(zoom, zoom)
    
    # ITEM 22 영역 (좌표는 이전 분석 결과 참조)
    # [600, 0, 1190, 280] 근처
    item_22_rect = fitz.Rect(600, 30, 1050, 250)
    pix = page.get_pixmap(matrix=mat, clip=item_22_rect)
    
    output_path = os.path.join(output_dir, "base_item_22.png")
    pix.save(output_path)
    print(f"Saved base image to {output_path}")
    
    return output_path

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    extract_base_images(pdf_path)
