import fitz
import pandas as pd
import os
import json

def detect_markers_in_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text("words")
    
    found_markers = []
    for w in words:
        txt = w[4].strip().lower()
        # 마커는 원 안에 있고 보통 작음. 텍스트 패턴으로 1차 필터링
        if len(txt) <= 5:
            # 특수 기호나 단위 제외
            if txt not in ["lg", "mm", "vac", "hz", "v~", "v-", "a", "d"]:
                found_markers.append(txt)
                
    doc.close()
    return sorted(list(set(found_markers)))

def update_matrix_with_detection():
    # 1. 마스터 매트릭스 로드 (또는 새로 생성)
    # 기존 create_id_matrix.py의 필드 리스트를 활용
    from create_id_matrix import create_id_specific_matrix
    matrix_path = "data/ID/id_mapping_master.xlsx"
    
    # 39개 향지 리스트
    destinations = [
        "ITEM_01_NON_REGULATION", "ITEM_02_AU_Australia", "ITEM_03_CN_China",
        "ITEM_04_EK_EU_PD_Europe_Turkey", "ITEM_05_FL_Nigeria", "ITEM_06_FP_Morocco",
        "ITEM_07_NOM_Generic", "ITEM_08_JL_Japan", "ITEM_09_KR_Korea",
        "ITEM_10_MI_Saudi_Arabia", "ITEM_11_MN_Jordan_Iraq", "ITEM_12_RU_Russia_Ukraine",
        "ITEM_13_TI_Indonesia", "ITEM_14_TM_Thailand", "ITEM_15_TR_India",
        "ITEM_16_TT_Taiwan", "ITEM_17_TV_Vietnam", "ITEM_18_US_USA",
        "ITEM_19_WC_WF_WH_Colombia_Peru_Chile", "ITEM_20_WM_Mexico", "ITEM_21_WZ_Brazil",
        "ITEM_22_GS_Algeria", "ITEM_23_WN_Argentina", "ITEM_24_MA_UAE",
        "ITEM_25_FB_WIRELESS_S.AFRICA_Botswana", "ITEM_26_FK_WIRELESS_Kenya_Zambia",
        "ITEM_27_JL_WIRELESS_Japan", "ITEM_28_MF_WIRELESS_Israel_HYE",
        "ITEM_29_MR_WIRELESS_Qatar", "ITEM_30_TC_WIRELESS_Singapore",
        "ITEM_31_TI_WIRELESS_Indonesia", "ITEM_32_TS_WIRELESS_Malaysia",
        "ITEM_33_WF_WH_WIRELESS_Peru_Chile", "ITEM_34_FF_W.Africa_Ghana_Senegal",
        "ITEM_35_FL_Wireless_Nigeria", "ITEM_36_RU_Russia", "ITEM_37_DR_Ukraine",
        "ITEM_38_DG_Uzbekistan", "ITEM_39_Generic"
    ]
    
    # 2. 각 템플릿별 마커 검출
    template_dir = "assets/templates/ID"
    detection_results = {}
    
    for dest in destinations:
        pdf_path = os.path.join(template_dir, f"{dest}.pdf")
        if os.path.exists(pdf_path):
            markers = detect_markers_in_pdf(pdf_path)
            detection_results[dest] = markers
            print(f"Detected in {dest}: {markers}")
        else:
            detection_results[dest] = []
            
    # 3. 엑셀 업데이트
    df = pd.read_excel(matrix_path)
    
    # 모든 향지 컬럼을 빈값으로 초기화
    for dest in destinations:
        df[dest] = ""
        
    # 검출 결과 반영
    for dest, markers in detection_results.items():
        for marker in markers:
            # 엑셀의 Index 컬럼과 대소문자 구분 없이 매칭
            mask = df['Index'].astype(str).str.lower() == marker
            if mask.any():
                df.loc[mask, dest] = "O"
                
    df.to_excel(matrix_path, index=False)
    print(f"Matrix updated with detection results: {matrix_path}")

if __name__ == "__main__":
    update_matrix_with_detection()
