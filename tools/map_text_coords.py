import fitz
import json

def map_text_coordinates(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text("words") # (x0, y0, x1, y1, "word", block_no, line_no, word_no)
    
    # 주요 키워드(모델명, 시리얼 등) 근처의 좌표 찾기
    keywords = ["MODEL", "SERIAL", "PRODUCT", "POWER", "MANUFACTURE", "MADE", "ORIGIN"]
    mappings = []
    
    for w in words:
        text = w[4].upper()
        for key in keywords:
            if key in text:
                mappings.append({
                    "text": w[4],
                    "rect": [w[0], w[1], w[2], w[3]],
                    "center": [(w[0]+w[2])/2, (w[1]+w[3])/2]
                })
    
    doc.close()
    return mappings

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    mappings = map_text_coordinates(pdf_file)
    print(json.dumps(mappings, indent=2))
