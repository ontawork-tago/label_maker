import fitz
from pathlib import Path


def export_precise_labels(pdf_path: str, out_dir: str):
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    src = fitz.open(pdf_path)

    for page_index in range(len(src)):
        page = src[page_index]
        full = page.rect

        # ---- 비율 설정 ----
        v_start = 0.18
        v_end   = 0.78
        h_margin = 0.06

        x0 = full.x0 + full.width * h_margin
        x1 = full.x1 - full.width * h_margin
        y0 = full.y0 + full.height * v_start
        y1 = full.y0 + full.height * v_end

        label_area = fitz.Rect(x0, y0, x1, y1)

        cols = 2
        rows = 3

        cell_w = label_area.width / cols
        cell_h = label_area.height / rows

        for r in range(rows):
            for c in range(cols):
                cx0 = label_area.x0 + c * cell_w
                cx1 = cx0 + cell_w
                cy0 = label_area.y0 + r * cell_h
                cy1 = cy0 + cell_h

                clip = fitz.Rect(cx0, cy0, cx1, cy1)

                dst = fitz.open()
                dst.insert_pdf(src,
                               from_page=page_index,
                               to_page=page_index,
                               clip=clip)

                name = f"{pdf_path.stem}_p{page_index+1:03d}_r{r+1}c{c+1}.pdf"
                dst.save(out_dir / name)
                dst.close()

    src.close()


if __name__ == "__main__":
    export_precise_labels(
        "data/MEZ68824201_LED OS ID_1.7.pdf",
        "vector_labels_precise"
    )