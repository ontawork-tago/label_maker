import fitz
import json

def get_markers_and_labels(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    
    # 1. 문서 내 모든 텍스트 블록 추출
    words = page.get_text("words") # (x0, y0, x1, y1, text, block_no, line_no, word_no)
    
    # 2. 벡터 드로잉 추출 (원형 마커 찾기 위해)
    drawings = page.get_drawings()
    
    # 마커 정보 저장 (인덱스 문자와 위치)
    markers = []
    
    # 특정 패턴(알파벳 한두 자리)을 가진 작은 텍스트들 찾기
    for w in words:
        text = w[4].strip()
        # 마커는 보통 1-4 글자 (a, a-1, w-32 등)
        if 1 <= len(text) <= 5:
            # 원형 마커 근처에 있는지 확인 (임의의 로직)
            markers.append({
                "text": text,
                "rect": [w[0], w[1], w[2], w[3]]
            })
            
    return markers

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    p4_markers = get_markers_and_labels(pdf_path, 4)
    print(f"Detected {len(p4_markers)} potential markers on Page 4")
    
    # 상세 분석을 위해 저장
    with open("p4_markers_debug.json", "w", encoding="utf-8") as f:
        json.dump(p4_markers, f, indent=4, ensure_ascii=False)
