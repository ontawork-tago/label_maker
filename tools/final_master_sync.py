import fitz
import pandas as pd
import os
import json

def get_markers_per_item(pdf_path):
    doc = fitz.open(pdf_path)
    
    # 39개 향지 구성 (Page 3 기반)
    PAGE_CONFIG = {
        5: ["ITEM_01_NON_REGULATION", "ITEM_04_EK_EU_PD_Europe_Turkey", "ITEM_02_AU_Australia", "ITEM_05_FL_Nigeria", "ITEM_03_CN_China", "ITEM_06_FP_Morocco"],
        6: ["ITEM_07_NOM_Generic", "ITEM_10_MI_Saudi_Arabia", "ITEM_08_JL_Japan", "ITEM_11_MN_Jordan_Iraq", "ITEM_09_KR_Korea", "ITEM_12_RU_Russia_Ukraine"],
        7: ["ITEM_13_TI_Indonesia", "ITEM_16_TT_Taiwan", "ITEM_14_TM_Thailand", "ITEM_17_TV_Vietnam", "ITEM_15_TR_India", "ITEM_18_US_USA"],
        8: ["ITEM_19_WC_WF_WH_Colombia_Peru_Chile", "ITEM_22_GS_Algeria", "ITEM_20_WM_Mexico", "ITEM_23_WN_Argentina", "ITEM_21_WZ_Brazil", "ITEM_24_MA_UAE"],
        9: ["ITEM_25_FB_WIRELESS_S.AFRICA_Botswana", "ITEM_28_MF_WIRELESS_Israel_HYE", "ITEM_26_FK_WIRELESS_Kenya_Zambia", "ITEM_29_MR_WIRELESS_Qatar", "ITEM_27_JL_WIRELESS_Japan", "ITEM_30_TC_WIRELESS_Singapore"],
        10: ["ITEM_31_TI_WIRELESS_Indonesia", "ITEM_34_FF_W.Africa_Ghana_Senegal", "ITEM_32_TS_WIRELESS_Malaysia", "ITEM_35_FL_Wireless_Nigeria", "ITEM_33_WF_WH_WIRELESS_Peru_Chile", "ITEM_36_RU_Russia"],
        11: ["ITEM_37_DR_Ukraine", "ITEM_38_DG_Uzbekistan", "ITEM_39_Generic"]
    }
    
    item_mappings = {}
    
    for page_num in [5, 6, 7, 8, 9, 10, 11]:
        if page_num > len(doc): continue
        page = doc[page_num - 1]
        
        # 1. 라벨 프레임 식별 (이전과 동일 로직)
        drawings = page.get_drawings()
        frames = []
        for d in drawings:
            fill = d.get("fill")
            rect = d.get("rect")
            if fill and sum(fill) < 0.7 and 200 < rect.width < 350 and 70 < rect.height < 180:
                should_add = True
                for i, existing in enumerate(frames):
                    if existing.contains(rect): should_add = False; break
                    if rect.contains(existing): frames[i] = rect; should_add = False; break
                if should_add: frames.append(rect)
        
        frames.sort(key=lambda r: (round(r.y0 / 40), r.x0))
        dest_names = PAGE_CONFIG.get(page_num, [])
        
        # 2. 페이지 내 모든 텍스트(마커 후보) 추출
        words = page.get_text("words")
        
        for i, f_rect in enumerate(frames):
            if i >= len(dest_names): break
            dest_name = dest_names[i]
            
            # 프레임 내부에 있는 마커 찾기
            found = []
            for w in words:
                txt = w[4].strip().lower()
                w_rect = fitz.Rect(w[0], w[1], w[2], w[3])
                # 프레임 내부(약간의 마진 허용)에 있는지 확인
                if f_rect.contains(w_rect) or f_rect.intersects(w_rect):
                    if 1 <= len(txt) <= 5:
                        if txt not in ["lg", "mm", "vac", "hz", "v~", "v-"]:
                            found.append(txt)
            
            item_mappings[dest_name] = sorted(list(set(found)))
            print(f"Mapped {dest_name}: {item_mappings[dest_name]}")
            
    doc.close()
    return item_mappings

def final_sync():
    # 1. 검출 실행
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    item_mappings = get_markers_per_item(pdf_path)
    
    # 2. 엑셀 로드
    matrix_path = "data/ID/id_mapping_master.xlsx"
    df = pd.read_excel(matrix_path)
    
    # 3. 맵핑 반영
    for dest_name, markers in item_mappings.items():
        if dest_name in df.columns:
            df[dest_name] = "" # 초기화
            for m in markers:
                mask = df['Index'].astype(str).str.lower() == m
                if mask.any():
                    df.loc[mask, dest_name] = "O"
                    
    df.to_excel(matrix_path, index=False)
    print(f"Final Synchronized Matrix Saved: {matrix_path}")

if __name__ == "__main__":
    final_sync()
