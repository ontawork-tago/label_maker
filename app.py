import streamlit as st
import json
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="LG LED Label Maker", layout="wide")

# 설정 파일 로드
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

st.title("🏷️ LG LED Label Maker")
st.markdown("향지별 라벨 규격에 맞춰 데이터를 입력하고 PDF를 생성합니다.")

# 사이드바: 향지 선택
st.sidebar.header("1. 향지 선택 (Destination)")
dest_key = st.sidebar.selectbox(
    "라벨 규격 선택",
    options=list(config["destinations"].keys()),
    format_func=lambda x: config["destinations"][x]["name"]
)

selected_dest = config["destinations"][dest_key]

# 메인 화면: 데이터 입력 폼
st.header(f"📝 {selected_dest['name']} 라벨 정보 입력")

col1, col2 = st.columns([1, 1])

with col1:
    input_data = {}
    st.subheader("데이터 필드")
    
    # 공통 및 특수 필드 동적 생성
    for field in selected_dest["fields"]:
        default_val = config["default_values"].get(field, "")
        label_text = field.replace("_", " ").title()
        
        if field == "manufacture_date":
            input_data[field] = st.date_input(label_text, value=datetime.now())
        elif field == "origin":
             input_data[field] = st.selectbox(label_text, options=["MADE IN CHINA", "MADE IN KOREA", "MADE IN INDONESIA"])
        else:
            input_data[field] = st.text_input(label_text, value=default_val)

with col2:
    st.subheader("🖼️ 라벨 미리보기 (Preview)")
    # TODO: Canvas 구현 또는 이미지 합성 미리보기
    st.info("입력된 데이터를 바탕으로 실시간 미리보기가 렌더링될 영역입니다.")
    st.write("---")
    st.write(f"**Selected Logos:** {', '.join(selected_dest['logos'])}")
    
    # 템플릿 정보 요약 테이블
    df = pd.DataFrame([input_data])
    st.table(df)

from generator import generate_label_pdf

# 생성 버튼
if st.button("Generate Label PDF"):
    with st.spinner("Generating PDF..."):
        pdf_buffer = generate_label_pdf(selected_dest, input_data)
        
        st.success(f"{selected_dest['name']} 라벨 PDF 생성이 완료되었습니다!")
        
        st.download_button(
            label="💾 Download Label PDF",
            data=pdf_buffer,
            file_name=f"Label_{dest_key}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )
