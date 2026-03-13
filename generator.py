from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
import io

def generate_label_pdf(dest_config, input_data):
    """
    라벨 데이터를 바탕으로 PDF를 생성하여 BytesIO 객체로 반환
    """
    # 라벨 사이즈 정의 (예: 100mm x 50mm)
    width = 100 * mm
    height = 50 * mm
    
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(width, height))
    
    # 배경 그리기 (검정색 라운드 사각형 예시)
    can.setFillGray(0.1)
    can.roundRect(0, 0, width, height, 5, stroke=0, fill=1)
    
    # 텍스트 그리기 설정
    can.setFillGray(1.0) # 흰색 텍스트
    
    layout = dest_config.get("layout", {})
    
    for field, data in input_data.items():
        if field in layout:
            pos = layout[field]
            can.setFont("Helvetica-Bold" if "model" in field else "Helvetica", pos["size"])
            
            # 데이터가 날짜 객체인 경우 문자열 변환
            val = str(data)
            if hasattr(data, 'strftime'):
                val = data.strftime("%Y.%m")
            
            # 좌표는 mm로 환산하거나 pt로 직접 사용 (현재 pt 기준)
            can.drawString(pos["x"], pos["y"], f"{field.replace('_', ' ').upper()}: {val}")
            
    # 로고 표시 (자리 표시자)
    can.setFont("Helvetica-Bold", 12)
    can.drawString(10, height - 20, "LG")
    
    can.save()
    packet.seek(0)
    return packet
