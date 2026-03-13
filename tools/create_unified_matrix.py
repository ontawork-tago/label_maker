import pandas as pd
import os

def create_unified_matrix(output_path="data/label_mapping_master.xlsx"):
    # 1. Page 3 기반 향지(Destination) 전수 리스트 (ITEM 01 ~ 39)
    # 이미지에서 판독한 정확한 명칭 매칭
    destinations = [
        "ITEM_01_NON_REGULATION",
        "ITEM_02_AU_Australia",
        "ITEM_03_CN_China",
        "ITEM_04_EK_EU_PD_Europe_Turkey",
        "ITEM_05_FL_Nigeria",
        "ITEM_06_FP_Morocco",
        "ITEM_07_Generic_07",
        "ITEM_08_JL_Japan",
        "ITEM_09_KR_Korea",
        "ITEM_10_MI_Saudi_Arabia",
        "ITEM_11_MN_Jordan",
        "ITEM_12_RU_Russia_Ukraine",
        "ITEM_13_TI_Indonesia",
        "ITEM_14_TM_Thailand",
        "ITEM_15_TR_India",
        "ITEM_16_TT_Taiwan",
        "ITEM_17_TV_Vietnam",
        "ITEM_18_US_USA",
        "ITEM_19_WC_WF_WH_Colombia_Peru_Chile",
        "ITEM_20_WM_Mexico",
        "ITEM_21_WZ_Brazil",
        "ITEM_22_GS_Algeria",
        "ITEM_23_WN_Argentina",
        "ITEM_24_MA_UAE",
        # 25번 이후 무선(Wireless) 시리즈
        "ITEM_25_FB_WIRELESS_S.AFRICA_Botswana",
        "ITEM_26_FK_WIRELESS_Kenya_Zambia",
        "ITEM_27_JL_WIRELESS_Japan",
        "ITEM_28_MF_WIRELESS_Israel_HY.E",
        "ITEM_29_MR_WIRELESS_Qatar",
        "ITEM_30_TC_WIRELESS_Singapore",
        "ITEM_31_TI_WIRELESS_Indonesia",
        "ITEM_32_TS_WIRELESS_Malaysia",
        "ITEM_33_WF_WH_WIRELESS_Peru_Chile_Paraguay",
        "ITEM_34_FF_W.Africa_Ghana_Senegal_Ivory_Coast",
        "ITEM_35_FL_Wireless_Nigeria",
        "ITEM_36_RU_Russia",
        "ITEM_37_DR_Ukraine",
        "ITEM_38_DG_Uzbekistan",
        "ITEM_39_Generic_39"
    ]

    # 2. Page 4 전수 필드 (a ~ z-9) 100여 개
    field_list = []
    # a 시리즈
    for i in range(50):
        idx = "a" if i == 0 else f"a-{i}"
        field_list.append({"Index": idx, "Treatment": "Optional"})
    # b~p 시리즈
    for idx in ["b", "c", "d", "d-1", "d-2", "d-3", "d-4", "d-5", "d-6", "d-7", "e", "f", "g", "h", "k", "p"]:
        field_list.append({"Index": idx, "Treatment": "Input" if idx in ["b", "c", "d", "e"] else "Optional"})
    # s~w 시리즈
    for idx in ["s", "t", "u", "v", "w"] + [f"w-{i}" for i in range(1, 33)]:
        field_list.append({"Index": idx, "Treatment": "Optional"})
    # z 시리즈
    for idx in ["z"] + [f"z-{i}" for i in range(1, 10)]:
        field_list.append({"Index": idx, "Treatment": "Optional"})

    # 3. 데이터 통합
    data = []
    for f in field_list:
        row = {"Index": f["Index"], "Treatment_Type": f["Treatment"]}
        for d in destinations:
            row[d] = "O"
        data.append(row)
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        df.to_excel(output_path, index=False)
        print(f"Excel Master Created: {output_path} with {len(destinations)} destinations and {len(df)} fields.")
    except PermissionError:
        alt = output_path.replace(".xlsx", "_v2.xlsx")
        df.to_excel(alt, index=False)
        print(f"Saved to backup: {alt}")

if __name__ == "__main__":
    create_unified_matrix()
