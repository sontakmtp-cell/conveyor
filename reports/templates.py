import os
import sys
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

def get_resource_path(relative_path):
    """
    Lấy đường dẫn tuyệt đối đến tài nguyên.
    Hàm này đảm bảo chương trình luôn tìm thấy tệp, dù được chạy trực tiếp hay đã được đóng gói.
    """
    try:
        # PyInstaller tạo một thư mục tạm thời và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Nếu không, lấy đường dẫn dựa trên vị trí của tệp mã nguồn này.
        # os.path.dirname(__file__) là thư mục 'reports'
        # os.path.join(..., '..') để đi lên một cấp, ra thư mục gốc của dự án
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    return os.path.join(base_path, relative_path)

def create_header(project_info):
    """Tạo phần đầu trang cho báo cáo PDF."""
    styles = getSampleStyleSheet()
    story = []
    
    # Sử dụng hàm get_resource_path để tìm logo.png một cách chính xác
    logo_path = get_resource_path("logo.png")
    
    header_data = []
    
    # Kiểm tra xem tệp logo.png có tồn tại không
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.5*inch, height=0.75*inch)
        logo.hAlign = 'LEFT'
        header_data.append([logo, Paragraph(project_info, styles['h1'])])
    else:
        # Nếu không có logo, chỉ hiển thị tiêu đề
        header_data.append(['', Paragraph(project_info, styles['h1'])])

    header_table = Table(header_data, colWidths=[1.7*inch, 4.8*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('SPAN', (1, 0), (1, 0)),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 0.25 * inch))
    return story

def create_footer(canvas, doc):
    """Tạo phần chân trang cho báo cáo PDF."""
    canvas.saveState()
    styles = getSampleStyleSheet()
    footer = Paragraph("Báo cáo được tạo bởi Phần mềm Tính toán Băng tải", styles['Normal'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def create_table(data, headers):
    """Tạo bảng dữ liệu cho báo cáo PDF."""
    table_data = [headers]
    for row in data:
        table_data.append([str(item) for item in row])

    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    return table
