import pandas as pd
import os

def export_all_fields_to_excel(output_path="data/label_mapping_master.xlsx"):
    # 4페이지 이미지 분석 기반 전체 필드 리스트
    fields = [
        # 컬럼 1
        {"Index": "a", "Field Name": "Sales Model Name", "Korean": "판매모델명"},
        {"Index": "a-1", "Field Name": "Screen Size (Inch)", "Korean": "화면 크기 (인치)"},
        {"Index": "a-3", "Field Name": "Production Name", "Korean": "생산공장명"},
        {"Index": "a-4", "Field Name": "MANUFACTURED_Date/Month/Year", "Korean": "제조년월일 (일/월/년)"},
        {"Index": "a-5", "Field Name": "ARGENTIAN REGULATION MARK", "Korean": "아르헨티나 규제 마크"},
        {"Index": "a-6", "Field Name": "PRODUCTION ADDRESS (RUSSIAN/UKRAINE)", "Korean": "생산지 주소 (러시아어/우크라이나어)"},
        {"Index": "a-7", "Field Name": "SET DIMENSION (Comma)", "Korean": "세트 사이즈 (콤마)"},
        {"Index": "a-8", "Field Name": "SET WEIGHT (Comma)", "Korean": "세트 무게 (콤마)"},
        {"Index": "a-9", "Field Name": "Color_SET (RUSSIAN/UKRAINE)", "Korean": "색상_세트 (러시아어/우크라이나어)"},
        {"Index": "a-10", "Field Name": "Product Name_Mexico", "Korean": "제품명칭_멕시코"},
        {"Index": "a-11", "Field Name": "Exporter Address_Mexico", "Korean": "수출업자 주소_멕시코"},
        {"Index": "a-12", "Field Name": "Net Quantity", "Korean": "제품의 수량"},
        {"Index": "a-13", "Field Name": "Total Size (With Packing)", "Korean": "총 사이즈 (포장 포함)"},
        {"Index": "a-14", "Field Name": "Total Weight (With Packing)", "Korean": "총 무게 (포장 포함)"},
        {"Index": "a-15", "Field Name": "Color_SET (CHINESE)", "Korean": "색상_세트 (중국어)"},
        {"Index": "a-16", "Field Name": "Product Name_China", "Korean": "제품명칭_중국"},
        {"Index": "a-17", "Field Name": "Producer & Production plant_China", "Korean": "생산지 & 생산자_중국"},
        {"Index": "a-18", "Field Name": "Product Name_Indonesia", "Korean": "제품명칭_인도네시아"},
        {"Index": "a-19", "Field Name": "Product Name_Thailand", "Korean": "제품명칭_태국"},
        {"Index": "a-20", "Field Name": "Product Name_Taiwan", "Korean": "제품명칭_대만"},
        {"Index": "a-21", "Field Name": "UL & FACTORY ID", "Korean": "UL & 공장 ID"},
        {"Index": "a-22", "Field Name": "Product Name_Mexico (2)", "Korean": "제품명칭_멕시코 (중복확인 필요)"},
        {"Index": "a-23", "Field Name": "HDMI", "Korean": "HDMI"},
        {"Index": "a-24", "Field Name": "Product Name_Russia", "Korean": "제품명칭_러시아"},

        # 컬럼 2 (일부 추출)
        {"Index": "a-25", "Field Name": "Indonesia MOT No.", "Korean": "인도네시아 MOT 번호"},
        {"Index": "a-26", "Field Name": "Product Name_Peru", "Korean": "제품명칭_페루"},
        {"Index": "a-27", "Field Name": "Japan Annual Power Consumption", "Korean": "일본 연간 소비전력"},
        {"Index": "a-28", "Field Name": "Japan JQA", "Korean": "일본 JQA"},
        {"Index": "a-29", "Field Name": "Taiwan Warning", "Korean": "대만 경고문구"},
        {"Index": "a-30", "Field Name": "Production Address_Turkey", "Korean": "생산지 주소_터키"},
        {"Index": "a-31", "Field Name": "Representative address", "Korean": "대표 주소"},
        {"Index": "a-32", "Field Name": "Product Name_Vietnam", "Korean": "제품명칭_베트남"},
        {"Index": "a-33", "Field Name": "Production Address_Vietnam", "Korean": "생산지 주소_베트남"},
        {"Index": "a-34", "Field Name": "Production Name_India", "Korean": "제품명칭_인도"},
        {"Index": "a-35", "Field Name": "Manufacturer_Taiwan", "Korean": "제조자_대만"},
        {"Index": "a-36", "Field Name": "DoU Mark_Ukraine", "Korean": "DoU 마크_우크라이나"},
        {"Index": "a-37", "Field Name": "HG or CD Free Mark_Europe", "Korean": "수은 or 카드뮴 프리 마크_유럽"},
        {"Index": "a-38", "Field Name": "VCCI_Japan", "Korean": "VCCI_일본"},
        {"Index": "a-39", "Field Name": "CLASS A CAUTION_CHINA", "Korean": "CLASS A 경고문구_중국"},
        {"Index": "a-40", "Field Name": "Representative address_Algeria", "Korean": "대표 주소_알제리"},
        {"Index": "a-41", "Field Name": "Product Name_Argentina", "Korean": "제품명칭_아르헨티나"},
        {"Index": "a-42", "Field Name": "Product Name_Israel", "Korean": "제품명칭_이스라엘"},
        {"Index": "a-43", "Field Name": "Production Address_Argentina", "Korean": "생산지 주소_아르헨티나"},
        {"Index": "a-44", "Field Name": "BSMI_Taiwan", "Korean": "BSMI_대만"},
        {"Index": "a-45", "Field Name": "PSE_Japan", "Korean": "PSE_일본"},
        {"Index": "a-46", "Field Name": "Representative address_Georgian", "Korean": "대표 주소_조지아어"},
        {"Index": "a-47", "Field Name": "Production address_Russia", "Korean": "생산지 주소_러시아"},
        {"Index": "a-48", "Field Name": "Production address_Ukraine", "Korean": "생산지 주소_우크라이나"},
        {"Index": "a-49", "Field Name": "Product Name_Ukraine", "Korean": "제품명칭_우크라이나"},

        # 컬럼 5 & 6 (무선 모듈 및 인증 - s ~ w-25)
        {"Index": "s", "Field Name": "Address_Indonesia", "Korean": "인도네시아 수입업자 주소"},
        {"Index": "t", "Field Name": "Indonesia RF Certification No.", "Korean": "인도네시아 RF 인증번호"},
        {"Index": "u", "Field Name": "Indonesia RF PLG ID", "Korean": "인도네시아 RF PLG ID"},
        {"Index": "v", "Field Name": "BIS Mark", "Korean": "BIS Mark"},
        {"Index": "w", "Field Name": "Production Address_INDIA", "Korean": "인도어 생산지 주소"},
        {"Index": "w-1", "Field Name": "WIRELESS_AU (C-TICK_R-ZA)", "Korean": "무선_AU (C-TICK_R-ZA)"},
        {"Index": "w-2", "Field Name": "WIRELESS_EU (RED PICTO)", "Korean": "무선_EU (RED PICTO)"},
        {"Index": "w-3", "Field Name": "WIRELESS_KR (RF Module KC No.)", "Korean": "무선_KR (RF Module KC No.)"},
        {"Index": "w-4", "Field Name": "WIRELESS (Contains module)", "Korean": "무선_(Contains module)"},
        {"Index": "w-5", "Field Name": "WIRELESS_KR (RF Module KC No.) (2)", "Korean": "무선_KR (RF Module KC No.)"},
        {"Index": "w-6", "Field Name": "WIRELESS (Contains module) (2)", "Korean": "무선_(Contains module)"},
        {"Index": "w-7", "Field Name": "WIRELESS_MA [(TRA) UAE]", "Korean": "무선_MA [(TRA) UAE]"},
        {"Index": "w-8", "Field Name": "WIRELESS_MA [(TRA) Oman]", "Korean": "무선_MA [(TRA) Oman]"},
        {"Index": "w-9", "Field Name": "WIRELESS_RU [(STB)Belarus]", "Korean": "무선_RU [(STB)Belarus]"},
        {"Index": "w-10", "Field Name": "WIRELESS_US [(FCC_IC) US_CANDA]", "Korean": "무선_US [(FCC_IC) US_CANDA]"},
        {"Index": "w-11", "Field Name": "WIRELESS_US [(SMA)Jamaica]", "Korean": "무선_US [(SMA)Jamaica]"},
        {"Index": "w-12", "Field Name": "WIRELESS_WZ [(ANATEL) BRAZIL]", "Korean": "무선_WZ [(ANATEL) BRAZIL]"},
        {"Index": "w-13", "Field Name": "WIRELESS_FP [(ANRT) Morocco]", "Korean": "무선_FP [(ANRT) Morocco]"},
        {"Index": "w-14", "Field Name": "WIRELESS_GS [(ARPCE) Algeria]", "Korean": "무선_GS [(ARPCE) Algeria]"},
        {"Index": "w-15", "Field Name": "WIRELESS_FB [(BOCRA) Botswana]", "Korean": "무선_FB [(BOCRA) Botswana]"},
        {"Index": "w-16", "Field Name": "WIRELESS_FB [(ICASA) SOUTH AFRICA]", "Korean": "무선_FB [(ICASA) SOUTH AFRICA]"},
        {"Index": "w-17", "Field Name": "WIRELESS_FK [(ZICTA) Zambia]", "Korean": "무선_FK [(ZICTA) Zambia]"},
        {"Index": "w-18", "Field Name": "WIRELESS_JL (JATE Certi No.)", "Korean": "무선_JL (JATE Certi No.)"},
        {"Index": "w-19", "Field Name": "WIRELESS_MF [(MOC_HYE) ISRAEL]", "Korean": "무선_MF [(MOC_HYE) ISRAEL]"},
        {"Index": "w-20", "Field Name": "WIRELESS_MF [(module)Contains module_HYE]", "Korean": "무선_MF [(module)Contains module_HYE]"},
        {"Index": "w-21", "Field Name": "WIRELESS_TC [(IDA) SINGARPORE]", "Korean": "무선_TC [(IDA) SINGARPORE]"},
        {"Index": "w-22", "Field Name": "WIRELESS_TI (Indonesia RF Certification No.)", "Korean": "무선_TI (Indonesia RF Certification No.)"},
        {"Index": "w-23", "Field Name": "WIRELESS_TI (Indonesia RF PLG ID)", "Korean": "무선_TI (Indonesia RF PLG ID)"},
        {"Index": "w-24", "Field Name": "WIRELESS_TS [(MCMC) Malaysia]", "Korean": "무선_TS [(MCMC) Malaysia]"},
        {"Index": "w-25", "Field Name": "WIRELESS_TT [(NCC) TAIWAN]", "Korean": "무선_TT [(NCC) TAIWAN]"},

        # 컬럼 7 & 8 (w-26 ~ w-32 및 z 시리즈)
        {"Index": "w-26", "Field Name": "WIRELESS_WH/WF ([CONATEL]Paraguay)", "Korean": "무선_WH/WF ([CONATEL]Paraguay)"},
        {"Index": "w-27", "Field Name": "WIRELESS_WM [(IFT) MEXICO]", "Korean": "무선_WM [(IFT) MEXICO]"},
        {"Index": "w-28", "Field Name": "WIRELESS_WN ([CNC] ARGENTINA)", "Korean": "무선_WN ([CNC] ARGENTINA)"},
        {"Index": "w-29", "Field Name": "WIRELESS_JL ([ARIB_JATE] JAP)", "Korean": "무선_JL ([ARIB_JATE] JAP)"},
        {"Index": "w-30", "Field Name": "WIRELESS_MF [(MOC_HYE_Box)Israel]", "Korean": "무선_MF [(MOC_HYE_Box)Israel]"},
        {"Index": "w-31", "Field Name": "WIRELESS_TI (Indonesia Signage QR code)", "Korean": "무선_TI (Indonesia Signage QR code)"},
        {"Index": "w-32", "Field Name": "WIRELESS_TT ([NCC] TAIWAN_BOX)", "Korean": "무선_TT ([NCC] TAIWAN_BOX)"},
        
        {"Index": "z", "Field Name": "Manufacturer/Production Plant_China", "Korean": "생산자 & 생산회사_중국"},
        {"Index": "z-1", "Field Name": "Product Name 1", "Korean": "기자재의 명칭"},
        {"Index": "z-2", "Field Name": "Product Name 2", "Korean": "품명"},
        {"Index": "z-3", "Field Name": "Manufacturer/Country", "Korean": "제조자/제조국가"},
        {"Index": "z-4", "Field Name": "Manufacturer Name", "Korean": "제조업자명"},
        {"Index": "z-5", "Field Name": "KC(Safety) No.", "Korean": "KC(안전) 인증번호"},
        {"Index": "z-6", "Field Name": "KC(EMC) No.", "Korean": "KC(EMC) 인증번호"},
        {"Index": "z-7", "Field Name": "Indonesia wireless QR", "Korean": "인도네시아 무선 QR"},
        {"Index": "z-8", "Field Name": "EMC Class (USA/CANADA)", "Korean": "EMC Class (USA/CANADA) - 미국/캐나다"},
        {"Index": "z-9", "Field Name": "Uzbekistan Mark", "Korean": "우즈베키스탄 마크"}
    ]
    
    df = pd.DataFrame(fields)
    
    # 처리 유형 컬럼 추가 (사용자가 설명해주실 부분)
    df["Treatment"] = "To Be Defined" # 입력 / 삭제 / 고정 중 선택 예정
    df["Value/Rule"] = ""
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_excel(output_path, index=False)
    print(f"Exported {len(df)} fields to {output_path}")

if __name__ == "__main__":
    export_all_fields_to_excel()
