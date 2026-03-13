import fitz
import json

def build_master_mapping(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[3] # Page 4
    
    # 초록색 (Green) 값 탐색 (주로 RGB 0, 0.5, 0.3 혹은 0, 150, 80 수준)
    # 이미지에서 본 초록색은 인덱스 기호로 쓰임
    TARGET_GREEN = (0.0, 0.588, 0.314) # 대략적인 LG 그린 계열
    
    drawings = page.get_drawings()
    green_drawings = []
    for d in drawings:
        fill = d.get("fill")
        if fill and len(fill) == 3:
            if fill[1] > 0.4 and fill[0] < 0.2 and fill[2] < 0.4:
                green_drawings.append(d)
                
    print(f"Found {len(green_drawings)} green circles/shapes on Page 4")
    
    # 각 초록색 도형 근처에 있는 텍스트를 찾아 맵핑
    mapping = {}
    for d in green_drawings:
        rect = d.get("rect")
        # 해당 도형 내부 혹은 근처의 알파벳/숫자 인덱스 추출
        index_text = page.get_text("text", clip=rect).strip()
        if not index_text:
            # 약간 확장해서 찾기
            expanded_rect = fitz.Rect(rect.x0-2, rect.y0-2, rect.x1+2, rect.y1+2)
            index_text = page.get_text("text", clip=expanded_rect).strip()
            
        if index_text:
            # 해당 인덱스 오른쪽의 설명 텍스트 추출
            desc_rect = fitz.Rect(rect.x1 + 5, rect.y0 - 5, rect.x1 + 400, rect.y1 + 5)
            desc_text = page.get_text("blocks", clip=desc_rect)
            primary_desc = ""
            if desc_text:
                primary_desc = desc_text[0][4].strip().split("\n")[0]
            
            mapping[index_text] = primary_desc
            print(f"[{index_text}]: {primary_desc}")
            
    return mapping

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    mapping = build_master_mapping(pdf_path)
    with open("src/index_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
