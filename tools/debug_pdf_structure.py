import fitz
from pathlib import Path

def debug_pdf_drawings(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()
    
    print(f"Total drawings: {len(drawings)}")
    # 처음 20개의 drawing 아이템 상세 출력
    for i, d in enumerate(drawings[:20]):
        print(f"Drawing {i}: Items={d['items']}, Rect={d['rect']}, Color={d.get('color')}")
        
    # 페이지 내의 모든 텍스트 블록도 확인 (상대적 위치 파악용)
    blocks = page.get_text("blocks")
    print("\nFirst 10 text blocks:")
    for b in blocks[:10]:
        print(f"Text block: {b[4].strip()} at {b[:4]}")
        
    doc.close()

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    debug_pdf_drawings(pdf_file)
