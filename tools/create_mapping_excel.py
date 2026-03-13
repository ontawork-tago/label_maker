import pandas as pd
import os

def create_mapping_excel(output_path="data/label_mapping_master.xlsx"):
    # 4페이지에서 추출된 인덱스 기반 초기 데이터프레임 구성
    data = {
        "Index": ["a", "b", "c", "d", "e", "f", "p", "z-2", "w-5", "z-9"],
        "Field Name": ["Sales Model Name", "Product Name", "Product Code", "Power Info", "Serial No", "Manufacture Date", "Origin", "JQA Cert", "Specific Cert", "Module Info"],
        "Type": ["Direct Input", "Direct Input", "Auto (Global)", "Fixed/Auto", "Direct/Auto", "Select", "Select", "Delete/Fixed", "Delete/Fixed", "Fixed"],
        "Description": ["사용자가 직접 입력하는 판매 모델명", "제품명", "공통 제품 코드", "정격 정보", "시리얼 번호", "제조년월", "원산지 정보", "JQA 인증 (삭제 가능)", "특정 국가 인증 (삭제 가능)", "무선 모듈 정보"],
        "Status": ["Active", "Active", "Active", "Active", "Active", "Active", "Active", "Optional", "Optional", "Optional"]
    }
    
    df = pd.DataFrame(data)
    
    # data 디렉토리 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 엑셀 파일로 저장
    df.to_excel(output_path, index=False)
    print(f"Created master mapping excel at: {output_path}")

if __name__ == "__main__":
    create_mapping_excel()
