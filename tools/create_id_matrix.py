import pandas as pd
import os

def create_id_specific_matrix(output_path="data/ID/id_mapping_master_final.xlsx"):
    # 가이드 PDF 4페이지 시각 분석 기반 전수 필드 리스트 (122개 항목)
    fields = [
        # a 시리즈 (Printing Information column 1 & 2)
        {"Index": "a", "English Name": "Sales Model Name", "Korean Name": "판매모델명", "Type": "값 기입"},
        {"Index": "a-1", "English Name": "Screen Size(Inch)", "Korean Name": "화면 크기(인치)", "Type": "값 기입"},
        {"Index": "a-2", "English Name": "Production Name", "Korean Name": "생산공정명", "Type": "값 기입"},
        {"Index": "a-3", "English Name": "MANUFACTURED_Date / Month / Year", "Korean Name": "제조년월일", "Type": "값 기입"},
        {"Index": "a-4", "English Name": "ARGENTINA REGULATION MARK", "Korean Name": "아르헨티나 규격 마크", "Type": "체크박스(유무)"},
        {"Index": "a-5", "English Name": "PRODUCTION ADDRESS(RUSSIAN/UKRAINE)", "Korean Name": "생산지 주소(러시아어/우크라이나어)", "Type": "값 기입"},
        {"Index": "a-6", "English Name": "SET DIMENSION (Comma)", "Korean Name": "세트 사이즈 (콤마)", "Type": "값 기입"},
        {"Index": "a-7", "English Name": "SET WEIGHT (Comma)", "Korean Name": "세트 무게 (콤마)", "Type": "값 기입"},
        {"Index": "a-8", "English Name": "Color SET (RUSSIAN/UKRAINE)", "Korean Name": "색상 세트 (러시아어/우크라이나어)", "Type": "값 기입"},
        {"Index": "a-9", "English Name": "Product Name_Mexico", "Korean Name": "제품명칭_멕시코", "Type": "값 기입"},
        {"Index": "a-10", "English Name": "Exporter Address_Mexico", "Korean Name": "수출업자 주소_멕시코", "Type": "값 기입"},
        {"Index": "a-11", "English Name": "Net Quantity", "Korean Name": "제품의 수량", "Type": "값 기입"},
        {"Index": "a-12", "English Name": "Total Size (With Packing)", "Korean Name": "총 사이즈 (포장 포함)", "Type": "값 기입"},
        {"Index": "a-13", "English Name": "Total Weight (With Packing)", "Korean Name": "총 무게 (포장 포함)", "Type": "값 기입"},
        {"Index": "a-14", "English Name": "Color SET (CHINESE)", "Korean Name": "색상 세트 (중국어)", "Type": "값 기입"},
        {"Index": "a-15", "English Name": "Product Name_China", "Korean Name": "제품명칭_중국", "Type": "값 기입"},
        {"Index": "a-16", "English Name": "Producer & Production plant_China", "Korean Name": "생산자 & 생산지_중국", "Type": "값 기입"},
        {"Index": "a-17", "English Name": "Product Name_Indonesia", "Korean Name": "제품명칭_인도네시아", "Type": "값 기입"},
        {"Index": "a-18", "English Name": "Product Name_Thailand", "Korean Name": "제품명칭_태국", "Type": "값 기입"},
        {"Index": "a-19", "English Name": "Product Name_Taiwan", "Korean Name": "제품명칭_대만", "Type": "값 기입"},
        {"Index": "a-20", "English Name": "UL & FACTORY ID", "Korean Name": "UL & 공장 ID", "Type": "값 기입"},
        
        # d ~ p 시리즈
        {"Index": "b", "English Name": "Color SET (RUSSIAN)", "Korean Name": "색상 세트 (러시아어)", "Type": "값 기입"},
        {"Index": "b-1", "English Name": "Color SET (UKRAINE)", "Korean Name": "색상 세트 (우크라이나어)", "Type": "값 기입"},
        {"Index": "h", "English Name": "MODEL NO. (Regulation Model Name)", "Korean Name": "기기의명칭 (규격모델명)", "Type": "값 기입"},
        {"Index": "c", "English Name": "ModelSuffix", "Korean Name": "모델명칭", "Type": "값 기입"},
        {"Index": "d", "English Name": "Power", "Korean Name": "정격", "Type": "값 기입"},
        {"Index": "d-1", "English Name": "Power (Comma)", "Korean Name": "정격 (콤마)", "Type": "값 기입"},
        {"Index": "d-2", "English Name": "Power_Russia (Comma)", "Korean Name": "정격_러시아 (콤마)", "Type": "값 기입"},
        {"Index": "e", "English Name": "Serial No.", "Korean Name": "일련번호", "Type": "값 기입"},
        {"Index": "f-1", "English Name": "MANUFACTURED Year", "Korean Name": "제조년", "Type": "값 기입"},
        {"Index": "f-2", "English Name": "MANUFACTURED Year/Month/Date", "Korean Name": "제조년월일", "Type": "값 기입"},
        {"Index": "p", "English Name": "Origin", "Korean Name": "원산지", "Type": "값 기입"},
        {"Index": "s", "English Name": "Address_Indonesia", "Korean Name": "인도네시아 수입업자주소", "Type": "값 기입"},
        {"Index": "t", "English Name": "Indonesia RF Certification No.", "Korean Name": "인도네시아 RF 인증번호", "Type": "값 기입"},
        {"Index": "u", "English Name": "Indonesia RF PLG ID", "Korean Name": "인도네시아 RF PLG ID", "Type": "값 기입"},
        {"Index": "v", "English Name": "BIS Mark", "Korean Name": "BIS 마크", "Type": "체크박스(유무)"},
        {"Index": "w", "English Name": "Production Address_INDIA", "Korean Name": "인도향 생산지 주소", "Type": "값 기입"},
        
        # w-n 시리즈 (무선/인증 명칭 정밀 교정)
        {"Index": "w-1", "English Name": "WIRELESS_AU (C-TICK_R-ZA)", "Korean Name": "무선_AU (C-TICK_R-ZA)", "Type": "체크박스(유무)"},
        {"Index": "w-2", "English Name": "WIRELESS_EU (RED PICTO)", "Korean Name": "무선_EU (RED PICTO)", "Type": "체크박스(유무)"},
        {"Index": "w-3", "English Name": "WIRELESS_KR (RF Module KC No.)", "Korean Name": "무선_KR (RF Module KC No.)", "Type": "체크박스(유무)"},
        {"Index": "w-4", "English Name": "WIRELESS (Contains module)", "Korean Name": "무선 (모듈 포함)", "Type": "체크박스(유무)"},
        {"Index": "w-5", "English Name": "WIRELESS_MA ([TRA] UAE)", "Korean Name": "무선_MA ([TRA] UAE)", "Type": "체크박스(유무)"},
        {"Index": "w-6", "English Name": "WIRELESS_MA ([TRA] Oman)", "Korean Name": "무선_MA ([TRA] Oman)", "Type": "체크박스(유무)"},
        {"Index": "w-7", "English Name": "WIRELESS_RU ([STB] Belarus)", "Korean Name": "무선_RU ([STB] 벨라루스)", "Type": "체크박스(유무)"},
        {"Index": "w-8", "English Name": "WIRELESS_US ([FCC_IC] US_CANDA)", "Korean Name": "무선_US ([FCC_IC] 미국_캐나다)", "Type": "체크박스(유무)"},
        {"Index": "w-9", "English Name": "WIRELESS_US ([SMA] Jamaica)", "Korean Name": "무선_US ([SMA] 자메이카)", "Type": "체크박스(유무)"},
        {"Index": "w-10", "English Name": "WIRELESS_GS ([ARPCE] Algeria)", "Korean Name": "무선_GS ([ARPCE] 알제리)", "Type": "체크박스(유무)"},
        {"Index": "w-11", "English Name": "WIRELESS_FB [BOCRA] Botswana", "Korean Name": "무선_FB [BOCRA] 보츠와나", "Type": "체크박스(유무)"},
        {"Index": "w-12", "English Name": "WIRELESS_FB ([ICASA] SOUTH AFRICA)", "Korean Name": "무선_FB ([ICASA] 남아공)", "Type": "체크박스(유무)"},
        {"Index": "w-13", "English Name": "WIRELESS_FK ([ZICTA] Zambia)", "Korean Name": "무선_FK ([ZICTA] 잠비아)", "Type": "체크박스(유무)"},
        {"Index": "w-15", "English Name": "WIRELESS_JL (JATE Certi No.)", "Korean Name": "무선_JL (JATE 인증번호)", "Type": "체크박스(유무)"},
        {"Index": "w-16", "English Name": "WIRELESS_MF ([MOC_HYE] ISRAEL)", "Korean Name": "무선_MF ([MOC_HYE] 이스라엘)", "Type": "체크박스(유무)"},
        {"Index": "w-17", "English Name": "WIRELESS_MF ([module]Contains module_HYE)", "Korean Name": "무선_MF (모듈 포함_HYE)", "Type": "체크박스(유무)"},
        {"Index": "w-18", "English Name": "WIRELESS_TC ([IDA] SINGAREPORE)", "Korean Name": "무선_TC ([IDA] 싱가포르)", "Type": "체크박스(유무)"},
        {"Index": "w-19", "English Name": "WIRELESS_TI (Indonesia RF Certification No.)", "Korean Name": "무선_TI (인도네시아 RF 인증번호)", "Type": "값 기입"},
        {"Index": "w-20", "English Name": "WIRELESS_TI (Indonesia RF PLG ID)", "Korean Name": "무선_TI (인도네시아 RF PLG ID)", "Type": "값 기입"},
        {"Index": "w-21", "English Name": "WIRELESS_TS ([MCMC] Malaysia)", "Korean Name": "무선_TS ([MCMC] 말레이시아)", "Type": "체크박스(유무)"},
        {"Index": "w-22", "English Name": "WIRELESS_TT ([NCC] TAIWAN)", "Korean Name": "무선_TT ([NCC] 대만)", "Type": "체크박스(유무)"},
        {"Index": "w-23", "English Name": "WIRELESS_WH/WF ([CONATEL] Paraguay)", "Korean Name": "무선_WH/WF ([CONATEL] 파라과이)", "Type": "체크박스(유무)"},
        {"Index": "w-24", "English Name": "WIRELESS_WM ([IFT] MEXICO)", "Korean Name": "무선_WM ([IFT] 멕시코)", "Type": "체크박스(유무)"},
        {"Index": "w-25", "English Name": "WIRELESS_WN ([CNC] ARGENTINA)", "Korean Name": "무선_WN ([CNC] 아르헨티나)", "Type": "체크박스(유무)"},
        {"Index": "w-26", "English Name": "WIRELESS_JL ([ARIB_JATE] JAP)", "Korean Name": "무선_JL ([ARIB_JATE] 일본)", "Type": "체크박스(유무)"},
        {"Index": "w-27", "English Name": "WIRELESS_MF ([MOC_HYE_Box]Israel)", "Korean Name": "무선_MF ([MOC_HYE_Box] 이스라엘)", "Type": "체크박스(유무)"},
        {"Index": "w-28", "English Name": "WIRELESS_TI (Indonesia Signage QR code)", "Korean Name": "무선_TI (인도네시아 Signage QR)", "Type": "체크박스(유무)"},
        {"Index": "w-29", "English Name": "WIRELESS_TT ([NCC] TAIWAN_BOX)", "Korean Name": "무선_TT ([NCC] 대만_BOX)", "Type": "체크박스(유무)"},
        {"Index": "w-30", "English Name": "WIRELESS_FF ([ARTP] Senegal)", "Korean Name": "무선_FF ([ARTP] 세네갈)", "Type": "체크박스(유무)"},
        {"Index": "w-31", "English Name": "WIRELESS_FF ([NCA] Ghana)", "Korean Name": "무선_FF ([NCA] 가나)", "Type": "체크박스(유무)"},
        {"Index": "w-32", "English Name": "WIRELESS_FL ([NCC] Nigeria)", "Korean Name": "무선_FL ([NCC] 나이지리아)", "Type": "체크박스(유무)"},
        
        # z 시리즈
        {"Index": "z", "English Name": "PRODUCT NAME 1", "Korean Name": "기자재의 명칭", "Type": "값 기입"},
        {"Index": "z-1", "English Name": "PRODUCT NAME 2", "Korean Name": "품명", "Type": "값 기입"},
        {"Index": "z-2", "English Name": "Manufacturer/Manufacturing Country", "Korean Name": "제조자/제조국가", "Type": "값 기입"},
        {"Index": "z-3", "English Name": "Manufacturer Name", "Korean Name": "제조업체명", "Type": "값 기입"},
        {"Index": "z-4", "English Name": "KC(Safety) No.", "Korean Name": "KC(안전) 인증번호", "Type": "값 기입"},
        {"Index": "z-5", "English Name": "KC(EMC) No.", "Korean Name": "KC(EMC) 인증번호", "Type": "값 기입"},
        {"Index": "z-6", "English Name": "Taiwan_Class A", "Korean Name": "대만_Class A", "Type": "체크박스(유무)"},
        {"Index": "z-7", "English Name": "Indonesia wireless QR", "Korean Name": "인도네시아 무선 QR", "Type": "체크박스(유무)"},
        {"Index": "z-8", "English Name": "EMC CLASS (USA/CANADA)", "Korean Name": "EMC 클래스 (미국/캐나다)", "Type": "체크박스(유무)"},
        {"Index": "z-9", "English Name": "Uzbekistan O'zDst Mark", "Korean Name": "우즈베키스탄 O'zDst 마크", "Type": "체크박스(유무)"},
    ]

    destinations = [
        "ITEM_01_NON_REGULATION", "ITEM_02_AU_Australia", "ITEM_03_CN_China",
        "ITEM_04_EK_EU_PD_Europe_Turkey", "ITEM_05_FL_Nigeria", "ITEM_06_FP_Morocco",
        "ITEM_07_NOM_Generic", "ITEM_08_JL_Japan", "ITEM_09_KR_Korea",
        "ITEM_10_MI_Saudi_Arabia", "ITEM_11_MN_Jordan_Iraq", "ITEM_12_RU_Russia_Ukraine",
        "ITEM_13_TI_Indonesia", "ITEM_16_TT_Taiwan", "ITEM_14_TM_Thailand",
        "ITEM_17_TV_Vietnam", "ITEM_15_TR_India", "ITEM_18_US_USA",
        "ITEM_19_WC_WF_WH_Colombia_Peru_Chile", "ITEM_22_GS_Algeria", "ITEM_20_WM_Mexico",
        "ITEM_23_WN_Argentina", "ITEM_21_WZ_Brazil", "ITEM_24_MA_UAE",
        "ITEM_25_FB_WIRELESS_S.AFRICA_Botswana", "ITEM_28_MF_WIRELESS_Israel_HYE",
        "ITEM_26_FK_WIRELESS_Kenya_Zambia", "ITEM_29_MR_WIRELESS_Qatar",
        "ITEM_27_JL_WIRELESS_Japan", "ITEM_30_TC_WIRELESS_Singapore",
        "ITEM_31_TI_WIRELESS_Indonesia", "ITEM_34_FF_W.Africa_Ghana_Senegal",
        "ITEM_32_TS_WIRELESS_Malaysia", "ITEM_35_FL_Wireless_Nigeria",
        "ITEM_33_WF_WH_WIRELESS_Peru_Chile", "ITEM_36_RU_Russia", "ITEM_37_DR_Ukraine",
        "ITEM_38_DG_Uzbekistan", "ITEM_39_Generic"
    ]
    
    data = []
    # 기본 맵핑: 필수 항목(a, h, c, d 등)은 O로 시작
    essential = ["a", "h", "c", "d", "e", "f-2", "p"]
    
    for f in fields:
        row = f.copy()
        row["Treatment"] = "Optional (Deletable)"
        for dest in destinations:
            if f["Index"] in essential:
                row[dest] = "O"
            else:
                row[dest] = ""
        data.append(row)
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Final Corrected Master Matrix Created: {output_path}")

if __name__ == "__main__":
    create_id_specific_matrix()
