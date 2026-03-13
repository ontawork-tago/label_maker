import fitz
import json

def analyze_specfic_label(pdf_path, page_num, label_name):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    # 텍스트 검색을 통해 해당 라벨 영역 대략적으로 찾기 (예: "NON REGULATION")
    found = page.search_for(label_name)
    if not found:
        print(f"Could not find {label_name} on page {page_num + 1}")
        return
    
    anchor = found[0] # [x0, y0, x1, y1]
    print(f"Anchor '{label_name}' found at: {anchor}")
    
    # 해당 앵커 아래쪽 영역을 라벨 영역으로 가정 (대략 300x200 크기)
    label_rect = fitz.Rect(anchor.x0 - 10, anchor.y1 + 5, anchor.x0 + 350, anchor.y1 + 180)
    print(f"Analyzing label rect: {label_rect}")
    
    words = page.get_text("words")
    internal_text = []
    for w in words:
        w_rect = fitz.Rect(w[:4])
        if label_rect.contains(w_rect):
            internal_text.append({
                "text": w[4],
                "rect": [w[0], w[1], w[2], w[3]],
                "rel_rect": [w[0] - label_rect.x0, w[1] - label_rect.y0, w[2] - label_rect.x0, w[3] - label_rect.y0]
            })
            
    doc.close()
    return {
        "label_rect": [label_rect.x0, label_rect.y0, label_rect.x1, label_rect.y1],
        "elements": internal_text
    }

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    # Page 5 is index 4
    result = analyze_specfic_label(pdf_file, 4, "NON REGULATION")
    if result:
        with open("non_reg_layout.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("Analysis saved to non_reg_layout.json")
