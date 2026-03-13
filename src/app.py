import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
from engine import IDLabelEngine
from mapping import IDMappingMaster

# 페이지 설정
st.set_page_config(page_title="LG LED Label Maker (Pro)", layout="wide")

# 매핑 데이터 로드 (캐시 초기화 버튼 지원을 위해 리소스 캐싱)
@st.cache_resource
def load_mapping():
    return IDMappingMaster("data/ID/id_mapping_master_super_final_v2.xlsx")

# 엔진 인스턴스 초기화 (캐시 초기화 버튼 지원을 위해 리소스 캐싱)
@st.cache_resource
def init_engine():
    return IDLabelEngine()

def get_auto_suffix(item_id):
    """향지 ID에서 코드를 추출하여 A{Code}Q 패턴의 Suffix 생성"""
    parts = item_id.split("_")
    if len(parts) >= 3:
        code = parts[2] # 보통 3번째 항목이 짧은 코드 (FP, KR, NA 등)
        return f"A{code}Q"
    return "A**Q"

engine = init_engine()
mapping_master = load_mapping()

# 사이드바 모드 선택
st.sidebar.header("🕹️ 모드 선택")
mode = st.sidebar.radio("작업 모드", ["Single (단일 생성)", "Bulk (일괄 생성)"])
st.sidebar.divider()

if mode == "Single (단일 생성)":
    # 1. 향지 선택
    st.sidebar.header("🗺️ 1. 향지 선택")
    items = [col for col in mapping_master.df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    selected_item = st.sidebar.selectbox("대상 라벨 템플릿", options=items)

    # 메인 UI 레이아웃
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("📋 데이터 입력")
        st.caption(f"**{selected_item}**의 활성 필드 데이터를 입력하세요.")
        
        active_ids = mapping_master.get_active_fields_for_item(selected_item)
        input_data = {}
        
        if not active_ids:
            st.warning("선택된 향지에 활성 필드가 정의되어 있지 않습니다.")
        else:
            # 필드를 타입별로 분리하여 가독성 증대
            text_fields = []
            check_fields = []
            for fid in active_ids:
                f_info = mapping_master.get_field_by_id(fid)
                if f_info["Type"] == "체크박스(유무)":
                    check_fields.append(f_info)
                else:
                    text_fields.append(f_info)

            # 1. 체크박스 항목 (상단 배치)
            if check_fields:
                with st.container(border=True):
                    st.markdown("**✅ 체크 항목 (유무 선택)**")
                    cols = st.columns(2)
                    for i, field in enumerate(check_fields):
                        with cols[i % 2]:
                            input_data[field["Index"]] = st.checkbox(
                                f"[{field['Index']}] {field['Korean']}", 
                                value=True, 
                                key=f"single_check_{selected_item}_{field['ID']}"
                            )

            # 2. 텍스트 입력 항목
            with st.container(border=True):
                st.markdown("**📝 텍스트 입력 항목**")
                for field in text_fields:
                    idx = field["Index"]
                    label = f"[{idx}] {field['Korean']}"
                    spec_val_col = f"{selected_item}_Val"
                    # Suffix(c) 자동화 또는 향지별 특화값 적용
                    if idx == "c":
                        default_val = get_auto_suffix(selected_item)
                    else:
                        default_val = field[spec_val_col] if spec_val_col in field and pd.notna(field[spec_val_col]) else field["Example"]
                    input_data[idx] = st.text_input(label, value=str(default_val), key=f"single_text_{selected_item}_{field['ID']}")

    with col2:
        st.subheader("🖼️ 생성 및 미리보기")
        if st.button("🚀 PDF 생성 및 다운로드", use_container_width=True, type="primary"):
            with st.spinner("생성 중..."):
                res_pdf = f"output/ID/pdf/single_{selected_item}.pdf"
                res_png = f"output/ID/png/single_{selected_item}.png"
                final_active_data = {k: v for k, v in input_data.items() if v is not False}
                result_path = engine.generate_label(selected_item, final_active_data, res_pdf, png_path=res_png)
                if result_path and os.path.exists(result_path):
                    with open(result_path, "rb") as f:
                        st.download_button("💾 PDF 다운로드", f, file_name=f"{selected_item}.pdf", mime="application/pdf")
                    st.info(f"💡 PNG 파일이 생성되었습니다: {res_png}")

else: # Bulk Mode
    st.subheader("🚀 Bulk Generation (일괄 생성)")
    st.markdown("모든 향지에 공통으로 적용될 데이터와 향지별 가변 데이터(원산지 등)를 입력하세요.")

    # 전체 향지 리스트
    items = [col for col in mapping_master.df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    
    # 1. Global Input (공통 필드)
    st.markdown("### 1️⃣ Global Data (공통 항목)")
    sample_item = items[0]
    active_ids = mapping_master.get_active_fields_for_item(sample_item)
    global_fields, variable_fields = mapping_master.get_field_categories(active_ids)
    
    global_inputs = {}
    
    # Global 필드 내에서도 체크박스/텍스트 분리
    g_text = [f for f in global_fields if f["Type"] != "체크박스(유무)"]
    g_check = [f for f in global_fields if f["Type"] == "체크박스(유무)"]

    if g_check:
        with st.container(border=True):
            st.markdown("**✅ 공통 체크 항목**")
            cols = st.columns(3)
            for i, field in enumerate(g_check):
                with cols[i % 3]:
                    global_inputs[field["Index"]] = st.checkbox(
                        f"{field['Korean']} ({field['Index']})", 
                        value=True, 
                        key=f"bulk_global_check_{field['Index']}"
                    )

    with st.container(border=True):
        st.markdown("**📝 공통 텍스트 항목**")
        cols = st.columns(3)
        for i, field in enumerate(g_text):
            with cols[i % 3]:
                global_inputs[field["Index"]] = st.text_input(
                    f"{field['Korean']} ({field['Index']})", 
                    value=str(field["Example"]),
                    key=f"bulk_global_text_{field['Index']}"
                )

    # 2. Variable Input (가변 필드 - Suffix(c), 원산지(p) 등)
    st.markdown("### 2️⃣ Variable Data (향지별 개별 항목)")
    st.caption("아래 표에서 각 향지별 Suffix(c) 및 원산지(p) 정보를 직접 수정하세요.")
    
    var_data = []
    for itm in items:
        row = {"Destination": itm}
        for v_field in variable_fields:
            v_idx = v_field["Index"]
            # Suffix(c) 자동화 또는 향지별 특화값 적용
            if v_idx == "c":
                val = get_auto_suffix(itm)
            else:
                spec_col = f"{itm}_Val"
                val = v_field.get(spec_col)
                if pd.isna(val) or val == "":
                    val = v_field["Example"]
            row[v_idx] = val
        var_data.append(row)
    
    edited_df = st.data_editor(pd.DataFrame(var_data), hide_index=True, use_container_width=True)

    # 3. 일괄 생성 실행
    st.divider()
    if st.button("📦 39개 라벨 일괄 생성 및 ZIP 다운로드", use_container_width=True, type="primary"):
        import zipfile
        zip_buffer = io.BytesIO()
        
        with st.spinner("전수 라벨 생성 및 압축 중..."):
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for _, row in edited_df.iterrows():
                    target_item = row["Destination"]
                    
                    # 해당 향지의 활성 데이터 조합
                    target_active_ids = mapping_master.get_active_fields_for_item(target_item)
                    current_active_data = {}
                    
                    for fid in target_active_ids:
                        f_info = mapping_master.get_field_by_id(fid)
                        idx = f_info["Index"]
                        
                        if idx in global_inputs:
                            current_active_data[idx] = global_inputs[idx]
                        elif idx in row:
                            current_active_data[idx] = row[idx]
                        else:
                            current_active_data[idx] = f_info["Example"]
                    
                    # 폴더 분리를 위한 경로 설정
                    res_pdf = f"output/ID/bulk/pdf/{target_item}.pdf"
                    res_png = f"output/ID/bulk/png/{target_item}.png"
                    engine.generate_label(target_item, current_active_data, res_pdf, png_path=res_png)
                    
                    if os.path.exists(res_pdf):
                        # ZIP 내부에 폴더 구조로 추가
                        zip_file.write(res_pdf, arcname=f"pdf/{target_item}.pdf")
                        if os.path.exists(res_png):
                            zip_file.write(res_png, arcname=f"png/{target_item}.png")
                        
                        os.remove(res_pdf) # 임시 파일 삭제
                        if os.path.exists(res_png):
                            os.remove(res_png)
            
            st.success(f"✅ 39개 라벨 생성 완료!")
            st.download_button(
                label="💾 ID_Labels_All.zip 다운로드",
                data=zip_buffer.getvalue(),
                file_name=f"ID_Labels_Bulk_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                mime="application/zip",
                use_container_width=True
            )

st.sidebar.divider()
st.sidebar.caption("v1.6 - Precision Mapping & Widget Sync Active")
if st.sidebar.button("♻️ 데이터 캐시 초기화"):
    st.cache_resource.clear()
    st.rerun()
