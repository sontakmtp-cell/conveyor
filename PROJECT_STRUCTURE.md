# Cấu Trúc Dự Án - Cloud Gemini 6.4 API BM

## Tổng Quan
Dự án này là một ứng dụng desktop 3D enhanced với tích hợp AI chat và các tính năng quản lý dữ liệu.

## Cấu Trúc Thư Mục

### 📁 Root Directory
```
Cloude Gemini 6.4 API BM/
├── cloud.py                    # File chính khởi chạy ứng dụng
├── requirements_3d_enhanced.txt # Danh sách dependencies Python
├── env_config.txt              # File cấu hình môi trường
├── icon.ico                    # Icon cho ứng dụng
├── users.json                  # Dữ liệu người dùng
└── PROJECT_STRUCTURE.md        # File này - tài liệu cấu trúc dự án
```

### 📁 core/ - Core Components
```
core/
├── __init__.py                 # Khởi tạo package core
├── ai/                         # Module AI và Chat
│   ├── chat_service.py         # Dịch vụ chat AI chính
│   └── providers/              # Các provider AI
│       ├── base.py             # Base class cho AI providers
│       └── gemini_provider.py  # Google Gemini AI provider
├── db.py                       # Quản lý cơ sở dữ liệu
├── engine.py                   # Engine chính của ứng dụng
├── licensing.py                # Quản lý giấy phép và activation
├── logs/                       # Thư mục chứa log files
├── models.py                   # Các model dữ liệu
├── optimize.py                 # Tối ưu hóa hiệu suất
├── rag/                        # Retrieval-Augmented Generation
│   ├── embedder.py             # Tạo embeddings cho documents
│   ├── index.py                # Indexing documents
│   ├── pdf_loader.py           # Load và xử lý PDF files
│   └── schema.py               # Schema cho RAG system
├── security.py                 # Bảo mật và authentication
├── specs.py                    # Specifications và configurations
├── thread_worker.py            # Xử lý đa luồng
└── utils/                      # Utility functions
    ├── __init__.py             # Khởi tạo utils package
    ├── paths.py                # Quản lý đường dẫn
    ├── trough_utils.py         # Utilities cho trough calculations
    └── unit_conversion.py      # Chuyển đổi đơn vị
```

### 📁 data/ - Data Storage
```
data/
├── accounts.v1.json            # Dữ liệu tài khoản người dùng
├── hidden/                     # Thư mục ẩn chứa dữ liệu nhạy cảm
└── index/                      # Index files cho RAG system
```

### 📁 reports/ - Báo Cáo và Export
```
reports/
├── __init__.py                 # Khởi tạo reports package
├── exporter_excel.py           # Export dữ liệu ra Excel
├── exporter_pdf.py             # Export dữ liệu ra PDF
├── fonts/                      # Fonts cho PDF generation
│   ├── DejaVuSans-Bold.ttf
│   ├── DejaVuSans-BoldOblique.ttf
│   ├── DejaVuSans-Oblique.ttf
│   ├── DejaVuSans.ttf
│   └── DejaVuSerif-Italic.ttf
└── templates.py                # Templates cho báo cáo
```

### 📁 ui/ - Giao Diện Người Dùng
```
ui/
├── __init__.py                 # Khởi tạo UI package
├── activation_dialog.py        # Dialog kích hoạt giấy phép
├── ad_banner_widget.py         # Widget hiển thị banner quảng cáo
├── ads_banner.html             # HTML template cho banner
├── chat/                       # Module chat
│   └── chat_panel.py          # Panel chat chính
├── images/                     # Hình ảnh và icons
│   ├── login.png               # Hình ảnh đăng nhập
│   ├── surcharge_angle.png     # Hình ảnh góc surcharge
│   ├── trough_angle.png        # Hình ảnh góc trough
│   ├── Whisk_zkxmgy.png        # Hình ảnh Whisk
│   ├── Whisk_zkxmgy2.png       # Hình ảnh Whisk 2
│   └── Whisk_zkxmgy3.png       # Hình ảnh Whisk 3
├── js/                         # JavaScript libraries
│   ├── GLTFLoader.js           # Loader cho 3D models (GLTF format)
│   └── three.min.js            # Three.js library cho 3D graphics
├── login_dialog.py             # Dialog đăng nhập
├── main_window_3d_enhanced.py  # Cửa sổ chính với tính năng 3D
├── models/                     # 3D models
│   └── Bang_tai_4m.glb        # 3D model băng tải 4m (GLB format)
├── plotting.py                 # Vẽ biểu đồ và charts
├── styles.py                   # Định dạng CSS và styling
├── tooltips.py                 # Tooltips và hints
├── ui_components_3d_enhanced.py # Components UI với tính năng 3D
└── visualization_3d.py         # Visualization 3D chính
```

## Chức Năng Chính

### 🔧 Core Features
- **AI Chat Service**: Tích hợp Google Gemini AI cho chat thông minh
- **RAG System**: Hệ thống tìm kiếm và trả lời dựa trên documents
- **Database Management**: Quản lý dữ liệu người dùng và hệ thống
- **Security**: Xác thực và bảo mật người dùng
- **Licensing**: Quản lý giấy phép và kích hoạt

### 🎨 UI Features
- **3D Visualization**: Hiển thị mô hình 3D với Three.js
- **Modern Interface**: Giao diện người dùng hiện đại và responsive
- **Chat Panel**: Giao diện chat tích hợp AI
- **Multi-format Export**: Xuất báo cáo ra Excel và PDF

### 📊 Data & Reports
- **PDF Generation**: Tạo báo cáo PDF với fonts tùy chỉnh
- **Excel Export**: Xuất dữ liệu ra định dạng Excel
- **Data Indexing**: Index dữ liệu cho tìm kiếm nhanh
- **Document Processing**: Xử lý PDF và tạo embeddings

## Công Nghệ Sử Dụng

- **Backend**: Python
- **Frontend**: PyQt/PySide với JavaScript
- **3D Graphics**: Three.js, GLTF format
- **AI**: Google Gemini API
- **Database**: JSON-based storage
- **PDF**: Custom PDF generation
- **RAG**: Vector embeddings và semantic search

## Hướng Dẫn Chạy

1. Cài đặt dependencies: `pip install -r requirements_3d_enhanced.txt`
2. Cấu hình môi trường trong `env_config.txt`
3. Chạy ứng dụng: `python cloud.py`

## Lưu Ý

- Cần có giấy phép hợp lệ để sử dụng đầy đủ tính năng
- 3D models sử dụng định dạng GLB/GLTF
- AI chat yêu cầu API key Google Gemini
- Fonts DejaVu được sử dụng cho PDF generation


