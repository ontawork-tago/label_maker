import pandas as pd
import os

def generate_super_master_matrix(output_path="data/ID/id_mapping_master_super_final.xlsx"):
    # 가이드 PDF 4페이지 정밀 분석 기반 전수 필드 리스트
    field_data = []
    
    # a 시리즈 (가이드 기반 전수 수동 매핑)
    field_data.append({"Index": "a", "English": "Sales Model Name", "Korean": "판매모델명", "Example": "LED-OS", "Type": "값 기입"})
    # a-1 ~ a-32 (실제 가이드 마커 리스트)
    a_items = [
        ("a-2", "Energy Logo", "에너지 로고", "[MARK]", "체크박스(유무)", ["ITEM_04_EK_EU_PD_Europe_Turkey"]),
        ("a-15", "Russia Warning", "러시아 경고문", "[TEXT]", "값 기입", ["ITEM_12_RU_Russia_Ukraine", "ITEM_36_RU_Russia"]),
        ("a-29", "Service Center (KR)", "서비스센터(한국)", "1544-7777", "값 기입", ["ITEM_09_KR_Korea"]),
        ("a-30", "Customer Care (KR)", "고객상담(한국)", "www.lgservice.co.kr", "값 기입", ["ITEM_09_KR_Korea"]),
        ("a-31", "VCCI Box (JL)", "VCCI 로고 박스", "[MARK]", "체크박스(유무)", ["ITEM_08_JL_Japan"]),
        ("a-32", "JQA Mark (JL)", "JQA 로고", "[MARK]", "체크박스(유무)", ["ITEM_08_JL_Japan"]),
    ]
    for idx, eng, kor, ex, typ, targets in a_items:
        field_data.append({"Index": idx, "English": eng, "Korean": kor, "Example": ex, "Type": typ, "Targets": targets})

    # b ~ p 시리즈
    field_data.extend([
        {"Index": "b", "English": "Regulation Model Name", "Korean": "기기의명칭 (규격모델명)", "Example": "MONITOR SIGNAGE LED", "Type": "값 기입", "Targets": ["ITEM_09_KR_Korea", "ITEM_08_JL_Japan"]},
        {"Index": "c", "English": "ModelSuffix", "Korean": "모델명칭", "Example": "LED-OS.SUFFIX", "Type": "값 기입"},
        {"Index": "d", "English": "Power", "Korean": "정격", "Example": "AC 100-240 V~ 50/60 Hz", "Type": "값 기입"},
        {"Index": "e", "English": "Serial No.", "Korean": "일련번호", "Example": "S..........S", "Type": "값 기입"},
        {"Index": "f-2", "English": "MANUFACTURED Date", "Korean": "제조년월일", "Example": "06/2020", "Type": "값 기입"},
        {"Index": "h", "English": "Logistic Code", "Korean": "물류 코드", "Example": "from Barcode", "Type": "값 기입"},
        {"Index": "i", "English": "G-Logo / Info", "Korean": "G-로고 / 정보", "Example": "[MARK]", "Type": "체크박스(유무)", "Targets": ["ITEM_08_JL_Japan", "ITEM_09_KR_Korea"]},
        {"Index": "p", "English": "Origin", "Korean": "원산지", "Example": "MADE IN KOREA", "Type": "값 기입"},
        {"Index": "x", "English": "Extra Caution", "Korean": "추가 주의사항", "Example": "[TEXT]", "Type": "값 기입", "Targets": ["ITEM_09_KR_Korea", "ITEM_08_JL_Japan"]},
    ])

    # [중복 인덱스 분리 설계] w 시리즈 (무선/인증)
    w_items = [
        (1, "AU (C-TICK_R-ZA)", "무선_AU (C-TICK_R-ZA)", "[MARK]", "체크박스(유무)", ["ITEM_02_AU_Australia"]),
        (2, "EU (RED PICTO)", "무선_EU (RED PICTO)", "[MARK]", "체크박스(유무)", ["ITEM_04_EK_EU_PD_Europe_Turkey"]),
        (3, "KR (RF Module KC No.)", "무선_KR (RF Module KC No.)", "MSIP-CRM-LGE...", "값 기입", ["ITEM_09_KR_Korea"]),
        (8, "US ([FCC_IC] US_CANDA)", "무선_US ([FCC_IC] 미국_캐나다)", "BEJLGSBWAC", "값 기입", ["ITEM_18_US_USA"]),
        (9, "FP ([ANRT] Morocco)", "무선_FP ([ANRT] 모로코)", "[MARK]", "체크박스(유무)", ["ITEM_06_FP_Morocco"]),
        (12, "FB ([ICASA] SOUTH AFRICA)", "무선_FB ([ICASA] 남아프리카)", "TA-20xx/xxxx", "값 기입", ["ITEM_25_FB_WIRELESS_S.AFRICA_Botswana"]),
    ]
    
    for i, eng, kor, ex, typ, targets in w_items:
        field_data.append({"Index": f"w-{i}", "English": eng, "Korean": kor, "Example": ex, "Type": typ, "Targets": targets})

    # z 시리즈 (KR 특화 전수 매핑)
    z_items = [
        ("1", "KC(Safety) Mark", "KC(안전) 마크", "[MARK]", "체크박스(유무)", ["ITEM_09_KR_Korea"]),
        ("2", "KC(EMC) Mark", "KC(EMC) 마크", "[MARK]", "체크박스(유무)", ["ITEM_09_KR_Korea"]),
        ("3", "Company Name (KR)", "상호명", "엘지전자(주)", "값 기입", ["ITEM_09_KR_Korea"]),
        ("4", "Manufacturer", "제조업체", "엘지전자(주)", "값 기입", ["ITEM_09_KR_Korea"]),
        ("5", "Manufacturer/Origin (KR)", "제조국/제조원", "한국/대한민국", "값 기입", ["ITEM_09_KR_Korea"]),
    ]
    for i, eng, kor, ex, typ, targets in z_items:
        field_data.append({"Index": f"z-{i}", "English": eng, "Korean": kor, "Example": ex, "Type": typ, "Targets": targets})

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
    
    data = []
    essential = ["a", "h", "c", "d", "e", "f-2", "p"]
    
    for f in field_data:
        row = f.copy()
        row["Deletable"] = "Y"
        # Targets 정보가 있으면 해당 향지에만 'O' 표시
        targets = row.pop("Targets", [])
        for dest in destinations:
            if f["Index"] in essential:
                row[dest] = "O"
            elif dest in targets:
                row[dest] = "O"
            else:
                row[dest] = ""
        data.append(row)
        
    df = pd.DataFrame(data)
    # [핵심] 고유 ID 부여 - Index가 중복되어도 구분 가능하도록
    df.insert(0, "ID", range(1, len(df) + 1))
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Super Master Matrix (w-9 Split & ID added) Created: {output_path}")

if __name__ == "__main__":
    generate_super_master_matrix()
