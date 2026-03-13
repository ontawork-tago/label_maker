import fitz
import json

def analyze_crop_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[7] # Page 8
    
    # 가이드 PDF의 레드 박스 색상 (RGB 대략 0.93, 0.11, 0.14)
    # 실제로는 텍스트 주변의 점선 박스임
    
    # 템플릿 크롭 영역 (extract_label_pdfs.py와 동일)
    crops = {
        "ITEM_19_Colombia": fitz.Rect(75, 140, 360, 280),
        "ITEM_22_Algeria": fitz.Rect(400, 140, 705, 280)
    }
    
    # 레드 박스 찾기 (벡터 그래픽 분석)
    drawings = page.get_drawings()
    red_boxes = []
    for d in drawings:
        # 빨간색 스트로크 찾기
        color = d.get("color")
        if color and len(color) == 3 and color[0] > 0.8 and color[1] < 0.2:
            red_boxes.append(d["rect"])
            
    print(f"Found {len(red_boxes)} red boxes on Page 8")
    
    results = {}
    for name, crop_rect in crops.items():
        print(f"\n--- Analyzing {name} ---")
        item_boxes = []
        for rb in red_boxes:
            # 레드 박스가 크롭 영역 내에 있는지 확인
            if crop_rect.contains(rb):
                # 상대 좌표 계산 (Top-Left 기준)
                rel_x = rb.x0 - crop_rect.x0
                rel_y = rb.y0 - crop_rect.y0
                
                # 해당 위치의 텍스트 혹은 인덱스(a, b, c) 유추
                # 주변에 초록색 동그라미가 있는지 확인하면 더 정밀함
                # 여기서는 우선 좌표만 리스트업
                item_boxes.append({
                    "abs_rect": [rb.x0, rb.y0, rb.x1, rb.y1],
                    "rel_pos": [rel_x, rel_y],
                    "size": [rb.width, rb.height]
                })
                print(f"Rel Pos: [{rel_x:.1f}, {rel_y:.1f}], Size: {rb.width:.1f}x{rb.height:.1f}")
        
        results[name] = item_boxes
        
    doc.close()
    return results

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    analyze_crop_coordinates(pdf_path)
