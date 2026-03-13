import fitz

def find_red_boxes(pdf_path, pages=[4, 5, 6]): # 0-indexed for pages 5, 6, 7
    doc = fitz.open(pdf_path)
    results = {}
    
    for pno in pages:
        page = doc[pno]
        red_rects = []
        drawings = page.get_drawings()
        for d in drawings:
            # 빨간색 (RGB 1,0,0) 스트로크 검색
            color = d.get("color")
            if color and color[0] > 0.8 and color[1] < 0.2 and color[2] < 0.2:
                # 사각형(rect) 혹은 닫힌 경로인 경우
                rect = d.get("rect")
                if rect:
                    red_rects.append(rect)
        
        results[pno + 1] = red_rects
        print(f"Page {pno + 1}: Found {len(red_rects)} red boxes")
        for i, r in enumerate(red_rects):
            print(f"  [{i}] {r}")
            
    return results

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    find_red_boxes(pdf_path)
