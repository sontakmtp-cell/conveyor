# Conveyor Calculator AI - Phần Mềm Tính Toán Băng Tải Công Nghiệp

## 📋 Tổng Quan Dự Án

**Conveyor Calculator AI** là một ứng dụng desktop chuyên nghiệp được thiết kế để tính toán, thiết kế và tối ưu hóa hệ thống băng tải công nghiệp. Ứng dụng tích hợp AI chat thông minh, mô phỏng 3D, và các công cụ tính toán theo tiêu chuẩn quốc tế.

**Phiên bản hiện tại:** 3.5 Professional (Enhanced Chain Support)  
**Nhà phát triển:** haingocson@gmail.com

## 🚀 Tính Năng Chính

### 🔧 Tính Toán Kỹ Thuật
- **Tiêu chuẩn tính toán:** DIN 22101, CEMA, ISO 5048
- **Tính toán băng tải:** Lực căng, công suất, vận tốc, góc nghiêng
- **Lựa chọn thiết bị:** Băng tải, con lăn, động cơ, hộp số, xích truyền
- **Tối ưu hóa thiết kế:** Thuật toán di truyền (GA) tự động

### 🤖 AI Chat & Hỗ Trợ
- **Tích hợp Google Gemini AI:** Trả lời thông minh về kỹ thuật băng tải
- **RAG System:** Tìm kiếm và trích xuất thông tin từ tài liệu kỹ thuật
- **Hỗ trợ tiếng Việt:** Giao tiếp hoàn toàn bằng tiếng Việt
- **Tư vấn chuyên môn:** Như kỹ sư trưởng dày dạn kinh nghiệm

### 🎨 Giao Diện 3D Hiện Đại
- **Mô phỏng 3D:** Hiển thị mô hình băng tải với Three.js
- **Giao diện responsive:** Thiết kế hiện đại, dễ sử dụng
- **Dark/Light theme:** Hỗ trợ chế độ sáng/tối
- **Visualization:** Biểu đồ, đồ thị trực quan

### 📊 Báo Cáo & Xuất Dữ Liệu
- **PDF Reports:** Tạo báo cáo chuyên nghiệp với fonts tùy chỉnh
- **Excel Export:** Xuất dữ liệu ra định dạng Excel
- **Templates:** Mẫu báo cáo có sẵn
- **Đa ngôn ngữ:** Hỗ trợ tiếng Việt và tiếng Anh

## 🏗️ Cấu Trúc Dự Án

```
Conveyor Calculator AI/
├── 📁 core/                           # Core Components
│   ├── ai/                            # AI & Chat Services
│   │   ├── chat_service.py            # Dịch vụ chat AI chính
│   │   └── providers/                 # AI Providers
│   │       ├── base.py                # Base class cho AI providers
│   │       └── gemini_provider.py     # Google Gemini AI provider
│   ├── db.py                          # Quản lý cơ sở dữ liệu
│   ├── engine.py                      # Engine tính toán chính
│   ├── licensing.py                   # Quản lý giấy phép
│   ├── models.py                      # Data models & enums
│   ├── optimizer/                     # Tối ưu hóa thiết kế
│   │   ├── models.py                  # Models cho optimizer
│   │   └── optimizer.py               # Thuật toán di truyền
│   ├── rag/                           # Retrieval-Augmented Generation
│   │   ├── embedder.py                # Tạo embeddings
│   │   ├── index.py                   # Indexing documents
│   │   ├── pdf_loader.py              # Xử lý PDF files
│   │   └── schema.py                  # Schema cho RAG system
│   ├── security.py                    # Bảo mật & authentication
│   ├── specs.py                       # Specifications & constants
│   ├── thread_worker.py               # Xử lý đa luồng
│   └── utils/                         # Utility functions
│       ├── paths.py                   # Quản lý đường dẫn
│       ├── trough_utils.py            # Utilities cho trough
│       └── unit_conversion.py         # Chuyển đổi đơn vị
│
├── 📁 data/                           # Data Storage
│   ├── accounts.v1.json               # Dữ liệu tài khoản
│   ├── Bang tra 1.csv                 # Bảng tra xích chuẩn
│   ├── hidden/                        # Dữ liệu nhạy cảm
│   └── index/                         # RAG index files
│
├── 📁 reports/                        # Báo Cáo & Export
│   ├── exporter_excel.py              # Export Excel
│   ├── exporter_pdf.py                # Export PDF
│   ├── fonts/                         # Fonts cho PDF
│   └── templates.py                   # Templates báo cáo
│
├── 📁 ui/                             # Giao Diện Người Dùng
│   ├── activation_dialog.py           # Dialog kích hoạt
│   ├── ad_banner_widget.py            # Widget banner quảng cáo
│   ├── chat/                          # Module chat
│   │   └── chat_panel.py             # Panel chat chính
│   ├── images/                        # Hình ảnh & icons
│   ├── js/                            # JavaScript libraries
│   │   ├── GLTFLoader.js             # 3D model loader
│   │   └── three.min.js              # Three.js library
│   ├── login_dialog.py                # Dialog đăng nhập
│   ├── main_window_3d_enhanced.py    # Cửa sổ chính 3D
│   ├── models/                        # 3D models
│   │   └── Bang_tai_4m.glb           # Model băng tải 4m
│   ├── plotting.py                    # Vẽ biểu đồ
│   ├── styles.py                      # CSS styling
│   ├── tooltips.py                    # Tooltips & hints
│   ├── ui_components_3d_enhanced.py  # Components UI 3D
│   └── visualization_3d.py            # Visualization 3D
│
├── 📁 core/logs/                      # Log files
├── cloud.py                           # Entry point chính
├── requirements_3d_enhanced.txt       # Dependencies Python
├── env_config.txt                     # Cấu hình môi trường
├── icon.ico                           # Icon ứng dụng
├── users.json                         # Dữ liệu người dùng
└── ConveyorCalculator.spec            # PyInstaller spec
```

## 🛠️ Công Nghệ Sử Dụng

### Backend
- **Python 3.8+** - Ngôn ngữ lập trình chính
- **PySide6** - Framework GUI hiện đại
- **NumPy/SciPy** - Tính toán số học
- **Pandas** - Xử lý dữ liệu

### AI & Machine Learning
- **Google Gemini API** - AI chat thông minh
- **Sentence Transformers** - Tạo embeddings
- **FAISS** - Vector search engine
- **RAG System** - Retrieval-Augmented Generation

### 3D Graphics & Visualization
- **Three.js** - 3D graphics library
- **GLTF/GLB** - 3D model format
- **Matplotlib/Plotly** - 2D charts & graphs
- **PyMuPDF** - PDF processing

### Database & Storage
- **JSON** - Data storage format
- **SQLite** - Local database (nếu cần)
- **Vector Index** - FAISS index cho RAG

## 📋 Yêu Cầu Hệ Thống

### Hệ Điều Hành
- **Windows 10/11** (Khuyến nghị)
- **Linux** (Ubuntu 20.04+)
- **macOS** (10.15+)

### Phần Cứng
- **RAM:** Tối thiểu 4GB, khuyến nghị 8GB+
- **CPU:** Intel i3/AMD Ryzen 3 trở lên
- **GPU:** Hỗ trợ OpenGL 3.3+ (cho 3D)
- **Storage:** 2GB trống

### Python Dependencies
```bash
# Cài đặt cơ bản
pip install -r requirements_3d_enhanced.txt

# Nếu gặp lỗi WebEngine
pip install PySide6-WebEngine

# Trên Linux có thể cần
sudo apt-get install qt6-webengine-dev
```

## 🚀 Hướng Dẫn Cài Đặt & Chạy

### 1. Chuẩn Bị Môi Trường
```bash
# Clone repository
git clone <repository-url>
cd "Cloude Gemini 6.4 API BM"

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 2. Cài Đặt Dependencies
```bash
# Cài đặt requirements
pip install -r requirements_3d_enhanced.txt

# Hoặc cài từng package
pip install PySide6 pandas numpy scipy matplotlib plotly
pip install openpyxl python-dotenv faiss-cpu sentence-transformers
pip install google-generativeai reportlab Pillow cryptography
```

### 3. Cấu Hình Môi Trường
```bash
# Tạo file .env hoặc sử dụng env_config.txt
cp env_config.txt .env

# Cấu hình API key
echo "AI_API_KEY=your_gemini_api_key_here" >> .env
echo "INDEX_DIR=./data/index" >> .env
```

### 4. Chạy Ứng Dụng
```bash
# Chạy từ source
python cloud.py

# Hoặc build executable
pyinstaller ConveyorCalculator.spec
```

## 🔑 Cấu Hình & API Keys

### Google Gemini API
- Đăng ký tại [Google AI Studio](https://makersuite.google.com/app/apikey)
- Thêm API key vào `env_config.txt` hoặc `.env`
- Format: `AI_API_KEY=your_api_key_here`

### Cấu Hình Môi Trường
```ini
# env_config.txt
AI_API_KEY=your_gemini_api_key
INDEX_DIR=./data/index
LOG_LEVEL=INFO
THEME=light
```

## 📚 Tài Liệu Kỹ Thuật

### Tiêu Chuẩn Tính Toán
- **DIN 22101** - Tiêu chuẩn Đức cho băng tải
- **CEMA** - Conveyor Equipment Manufacturers Association
- **ISO 5048** - Tiêu chuẩn quốc tế

### Công Thức Chính
- **Lực căng băng tải:** T = f × L × g × (m + mb + mc)
- **Công suất động cơ:** P = (T × V) / (1000 × η)
- **Góc nghiêng tối đa:** αmax = arctan(μ × cos(β))

### Tối Ưu Hóa Thiết Kế
- **Thuật toán di truyền:** Population size: 100, Generations: 50
- **Fitness function:** Chi phí + Hiệu suất + Độ tin cậy
- **Constraints:** Tiêu chuẩn kỹ thuật, giới hạn vật liệu

## 🤝 Đóng Góp & Phát Triển

### Cách Đóng Góp
1. Fork repository
2. Tạo feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Tạo Pull Request

### Cấu Trúc Code
- **PEP 8** - Python style guide
- **Type hints** - Sử dụng typing
- **Docstrings** - Documentation cho functions
- **Error handling** - Try-catch với logging

### Testing
```bash
# Chạy tests
pytest

# Tests với Qt
pytest-qt

# Coverage report
pytest --cov=core --cov=ui
```

## 📞 Hỗ Trợ & Liên Hệ

### Thông Tin Liên Hệ
- **Email:** haingocson@gmail.com
- **GitHub:** [Repository URL]
- **Documentation:** [Wiki/Readme]

### Báo Cáo Lỗi
- Sử dụng GitHub Issues
- Mô tả chi tiết vấn đề
- Đính kèm log files nếu có
- Screenshot cho UI issues

### Feature Requests
- Mô tả tính năng mong muốn
- Use case cụ thể
- Priority level
- Mockup/design nếu có

## 📄 Giấy Phép

### License
- **Commercial License** - Cho sử dụng thương mại
- **Academic License** - Cho nghiên cứu và giáo dục
- **Trial Version** - Dùng thử 30 ngày

### Activation
- Yêu cầu license key hợp lệ
- Online activation
- Offline activation (nếu cần)
- Hardware binding

## 🔄 Changelog

### Version 3.5 Professional (Enhanced Chain Support)
- ✅ Hỗ trợ xích truyền động nâng cao
- ✅ Tối ưu hóa thuật toán di truyền
- ✅ Cải thiện giao diện 3D
- ✅ Tích hợp AI chat thông minh
- ✅ Hỗ trợ đa ngôn ngữ (Việt/Anh)

### Version 3.4
- ✅ Tính năng RAG system
- ✅ PDF processing
- ✅ Enhanced security
- ✅ Performance optimization

### Version 3.3
- ✅ 3D visualization
- ✅ Modern UI design
- ✅ Multi-threading support
- ✅ Excel/PDF export

## 🎯 Roadmap

### Q1 2026
- [ ] Mobile app version
- [ ] Cloud synchronization
- [ ] Advanced analytics
- [ ] API integration

### Q2 2026
- [ ] Machine learning models
- [ ] Predictive maintenance
- [ ] IoT integration
- [ ] Multi-language support

### Q3 2026
- [ ] VR/AR support
- [ ] Collaborative design
- [ ] Cloud-based calculations
- [ ] Enterprise features

## 🙏 Lời Cảm Ơn

Cảm ơn cộng đồng open source và các thư viện đã hỗ trợ:
- **PySide6** - Modern Qt bindings
- **Three.js** - 3D graphics library
- **Google Gemini** - AI capabilities
- **FAISS** - Vector search engine
- **Cộng đồng Python** - Hỗ trợ và đóng góp

---

**© 2024 Conveyor Calculator AI. All rights reserved.**
*Phát triển với ❤️ tại Việt Nam*
