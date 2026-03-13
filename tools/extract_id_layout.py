import fitz
import json
from pathlib import Path

def extract_detailed_id_layout(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # "words"로 텍스트 위치 및 관계 파악
    words = page.get_text("words")
    
    # 우리가 찾고자 하는 항목들
    targets = {
        "MODEL": "MODEL NAME",
        "PRODUCT": "PRODUCT CODE",
        "POWER": "POWER",
        "SERIAL": "SERIAL NO.",
        "MANUFACTURE": "MANUFACTURE DATE",
        "MADE": "MADE IN"
    }
    
    layout_data = []
    
    for i, w in enumerate(words):
        text = w[4].upper()
        for key, full_name in targets.items():
            if key in text:
                # 키워드 발견! 주변 텍스트들을 탐색하여 '값'이 올 위치 추정
                # 보통 키워드 오른쪽에 데이터가 위치함
                neighbor_data = []
                for j in range(i+1, min(i+5, len(words))):
                    nw = words[j]
                    # 같은 라인에 있는 단어들 수집
                    if abs(nw[1] - w[1]) < 3:
                        neighbor_data.append({
                            "text": nw[4],
                            "rect": [nw[0], nw[1], nw[2], nw[3]]
                        })
                
                layout_data.append({
                    "field": full_name,
                    "keyword_rect": [w[0], w[1], w[2], w[3]],
                    "neighbors": neighbor_data
                })
    
    doc.close()
    return layout_data

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    if Path(pdf_file).exists():
        layout = extract_detailed_id_layout(pdf_file)
        with open("id_layout_analysis.json", "w", encoding="utf-8") as f:
            json.dump(layout, f, indent=2, ensure_ascii=False)
        print("Analysis saved to id_layout_analysis.json")
    else:
        print(f"File not found: {pdf_file}")
