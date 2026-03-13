import fitz
import os

def extract_labels_as_pdf(pdf_path, output_dir="assets/templates/ID"):
    # ID 라벨 전용 폴더 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    doc = fitz.open(pdf_path)
    
    # 페이지별 ID 라벨 향지 이름 매팅 (Page 3 인덱스 기반 전수 매핑)
    PAGE_CONFIG = {
        5: [
            "ITEM_01_NON_REGULATION", "ITEM_04_EK_EU_PD_Europe_Turkey",
            "ITEM_02_AU_Australia",   "ITEM_05_FL_Nigeria",
            "ITEM_03_CN_China",      "ITEM_06_FP_Morocco"
        ],
        6: [
            "ITEM_07_NOM_Generic",    "ITEM_10_MI_Saudi_Arabia",
            "ITEM_08_JL_Japan",       "ITEM_11_MN_Jordan_Iraq",
            "ITEM_09_KR_Korea",       "ITEM_12_RU_Russia_Ukraine"
        ],
        7: [
            "ITEM_13_TI_Indonesia",   "ITEM_16_TT_Taiwan",
            "ITEM_14_TM_Thailand",    "ITEM_17_TV_Vietnam",
            "ITEM_15_TR_India",       "ITEM_18_US_USA"
        ],
        8: [
            "ITEM_19_WC_WF_WH_Colombia_Peru_Chile", "ITEM_22_GS_Algeria",
            "ITEM_20_WM_Mexico",                    "ITEM_23_WN_Argentina",
            "ITEM_21_WZ_Brazil",                    "ITEM_24_MA_UAE"
        ],
        9: [
            "ITEM_25_FB_WIRELESS_S.AFRICA_Botswana", "ITEM_28_MF_WIRELESS_Israel_HYE",
            "ITEM_26_FK_WIRELESS_Kenya_Zambia",     "ITEM_29_MR_WIRELESS_Qatar",
            "ITEM_27_JL_WIRELESS_Japan",            "ITEM_30_TC_WIRELESS_Singapore"
        ],
        10: [
            "ITEM_31_TI_WIRELESS_Indonesia",        "ITEM_34_FF_W.Africa_Ghana_Senegal",
            "ITEM_32_TS_WIRELESS_Malaysia",         "ITEM_35_FL_Wireless_Nigeria",
            "ITEM_33_WF_WH_WIRELESS_Peru_Chile",    "ITEM_36_RU_Russia"
        ],
        11: [
            "ITEM_37_DR_Ukraine", "ITEM_38_DG_Uzbekistan", "ITEM_39_Generic"
        ]
    }

    for page_num in [5, 6, 7, 8, 9, 10, 11]:
        if page_num > len(doc): continue
        page = doc[page_num - 1]
        drawings = page.get_drawings()
        
        # 1. 벡터 기반 프레임 감지
        black_frames = []
        for d in drawings:
            fill = d.get("fill")
            rect = d.get("rect")
            
            is_dark = False
            if fill:
                if len(fill) == 3 and (sum(fill) < 0.7):
                    is_dark = True
                elif len(fill) == 1 and fill[0] < 0.7:
                    is_dark = True
            
            if is_dark and 200 < rect.width < 350 and 70 < rect.height < 180:
                should_add = True
                for i, existing in enumerate(black_frames):
                    if existing.contains(rect):
                        should_add = False
                        break
                    if rect.contains(existing):
                        black_frames[i] = rect
                        should_add = False
                        break
                if should_add:
                    black_frames.append(rect)
        
        # 상단->하단, 좌측->우측 순으로 정렬 (y좌표 40단위 정규화)
        black_frames.sort(key=lambda r: (round(r.y0 / 40), r.x0))
        
        print(f"Page {page_num}: Detected {len(black_frames)} ID Label frames")
        
        dest_names = PAGE_CONFIG.get(page_num, [])
        
        for i, rect in enumerate(black_frames):
            if i < len(dest_names):
                filename = dest_names[i]
            else:
                filename = f"ID_Page{page_num}_Label_{i+1}"
            
            new_doc = fitz.open()
            margin = 1.5
            crop_rect = fitz.Rect(rect.x0 - margin, rect.y0 - margin, rect.x1 + margin, rect.y1 + margin)
            
            new_page = new_doc.new_page(width=crop_rect.width, height=crop_rect.height)
            new_page.show_pdf_page(new_page.rect, doc, page_num - 1, clip=crop_rect)
            
            output_path = os.path.join(output_dir, f"{filename}.pdf")
            new_doc.save(output_path)
            new_doc.close()
            print(f"  > Saved ID Template: {output_path}")
            
    doc.close()

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    extract_labels_as_pdf(pdf_path)
