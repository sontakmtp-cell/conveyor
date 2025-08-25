"""
HTML Templates cho Enhanced 3D Visualization
"""

# Template HTML cơ bản
BASIC_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Băng tải 3D</title>
    <style>
        body {{ margin: 0; overflow: hidden; }}
        canvas {{ display: block; }}
    </style>
</head>
<body>
    {libs}
    <script>
        {js_code}
    </script>
</body>
</html>
"""

# Template HTML nâng cao với UI controls
ENHANCED_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Băng tải 3D nâng cao</title>
    <style>
        body {{ 
            margin: 0; 
            overflow: hidden; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        canvas {{ 
            display: block; 
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }}
        
        .enhanced-hud {{
            position: fixed;
            left: 20px;
            top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            font: 14px/1.6 'Segoe UI', sans-serif;
            border-radius: 12px;
            z-index: 10;
            pointer-events: none;
            max-width: 320px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .enhanced-hud h3 {{
            margin: 0 0 15px 0;
            color: #00d4ff;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .enhanced-hud .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 4px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .enhanced-hud .info-label {{
            color: #bdc3c7;
            font-weight: 500;
        }}
        
        .enhanced-hud .info-value {{
            color: #fff;
            font-weight: 600;
        }}
        
        .component-info {{
            position: fixed;
            right: 20px;
            top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            font: 13px/1.5 'Segoe UI', sans-serif;
            border-radius: 12px;
            z-index: 10;
            max-width: 280px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .component-info h3 {{
            margin: 0 0 15px 0;
            color: #00d4ff;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .component-info .component-item {{
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .component-info .component-item:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding-left: 8px;
        }}
        
        .component-info .component-item.active {{
            background: rgba(0, 212, 255, 0.2);
            border-left: 3px solid #00d4ff;
            padding-left: 8px;
        }}
        
        .animation-controls {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            padding: 15px 25px;
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            border-radius: 25px;
            z-index: 10;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .animation-controls button {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.2s ease;
            min-width: 50px;
        }}
        
        .animation-controls button:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-2px);
        }}
        
        .animation-controls button.active {{
            background: #00d4ff;
            border-color: #00d4ff;
            color: #000;
        }}
        
        .speed-control {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .speed-control input[type="range"] {{
            width: 100px;
            height: 4px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 2px;
            outline: none;
            -webkit-appearance: none;
        }}
        
        .speed-control input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            background: #00d4ff;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .camera-controls {{
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 15px 25px;
            background: rgba(0, 0, 0, 0.85);
            color: #fff;
            border-radius: 12px;
            z-index: 10;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .camera-controls select {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            outline: none;
            font-size: 14px;
        }}
        
        .camera-controls select option {{
            background: #2c3e50;
            color: #fff;
        }}
        
        .loading-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 100;
            color: #fff;
            font-size: 18px;
            font-weight: 600;
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .performance-info {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 10px 15px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            font: 12px/1.4 'Consolas', monospace;
            border-radius: 6px;
            z-index: 10;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-spinner"></div>
        <div>Đang tải mô hình 3D...</div>
    </div>
    
    <div class="enhanced-hud">
        <h3>📊 Thông số chính</h3>
        <div class="info-row">
            <span class="info-label">Chiều dài:</span>
            <span class="info-value">{length:.1f} m</span>
        </div>
        <div class="info-row">
            <span class="info-label">Chiều rộng:</span>
            <span class="info-value">{width:.2f} m</span>
        </div>
        <div class="info-row">
            <span class="info-label">Chiều cao:</span>
            <span class="info-value">{height:.1f} m</span>
        </div>
        <div class="info-row">
            <span class="info-label">Góc dốc:</span>
            <span class="info-value">{inclination:.1f}°</span>
        </div>
        <div class="info-row">
            <span class="info-label">Tốc độ:</span>
            <span class="info-value">{speed:.2f} m/s</span>
        </div>
        <div class="info-row">
            <span class="info-label">Công suất:</span>
            <span class="info-value">{power:.1f} kW</span>
        </div>
        <div class="info-row">
            <span class="info-label">Tỷ số truyền:</span>
            <span class="info-value">{ratio:.1f}</span>
        </div>
    </div>
    
    <div class="component-info">
        <h3>🔧 Thành phần</h3>
        <div class="component-item" data-component="belt">Băng tải</div>
        <div class="component-item" data-component="drive">Hệ truyền động</div>
        <div class="component-item" data-component="idlers">Con lăn</div>
        <div class="component-item" data-component="frame">Khung đỡ</div>
        <div class="component-item" data-component="material">Vật liệu</div>
    </div>
    
    <div class="camera-controls">
        <label>Góc nhìn:</label>
        <select id="camera-preset">
            <option value="overview">Tổng quan</option>
            <option value="drive">Hệ truyền động</option>
            <option value="idlers">Con lăn</option>
            <option value="belt">Băng tải</option>
            <option value="custom">Tùy chỉnh</option>
        </select>
        <button id="reset-camera">🔄</button>
    </div>
    
    <div class="animation-controls">
        <button id="play-pause" class="active">⏸️</button>
        <button id="reset">🔄</button>
        <div class="speed-control">
            <span>🐌</span>
            <input type="range" id="speed-slider" min="0.1" max="3.0" step="0.1" value="1.0">
            <span>⚡</span>
        </div>
        <button id="wireframe">📐</button>
        <button id="fullscreen">⛶</button>
    </div>
    
    <div class="performance-info" id="performance-info">
        FPS: -- | Triangles: -- | Memory: -- MB
    </div>
    
    {libs}
    
    <script>
        // JavaScript nâng cao sẽ được inject ở đây
        {js_code}
    </script>
</body>
</html>
"""

# Template HTML cho chế độ đơn giản
SIMPLE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Băng tải 3D đơn giản</title>
    <style>
        body {{ 
            margin: 0; 
            overflow: hidden; 
            background: #1a1a1a;
        }}
        
        canvas {{ 
            display: block; 
        }}
        
        .simple-hud {{
            position: fixed;
            top: 20px;
            left: 20px;
            color: #fff;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 10;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 8px;
        }}
        
        .simple-hud h3 {{
            margin: 0 0 10px 0;
            color: #00ff88;
        }}
        
        .simple-hud div {{
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="simple-hud">
        <h3>Băng tải 3D</h3>
        <div>Chiều dài: {length:.1f} m</div>
        <div>Chiều rộng: {width:.2f} m</div>
        <div>Tốc độ: {speed:.2f} m/s</div>
    </div>
    
    {libs}
    
    <script>
        {js_code}
    </script>
</body>
</html>
"""

# Template HTML cho chế độ phân tích
ANALYSIS_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Phân tích băng tải 3D</title>
    <style>
        body {{ 
            margin: 0; 
            overflow: hidden; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        canvas {{ 
            display: block; 
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }}
        
        .analysis-panel {{
            position: fixed;
            right: 20px;
            top: 20px;
            width: 350px;
            background: rgba(0, 0, 0, 0.9);
            color: #fff;
            border-radius: 12px;
            padding: 20px;
            z-index: 10;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            max-height: 80vh;
            overflow-y: auto;
        }}
        
        .analysis-panel h2 {{
            margin: 0 0 20px 0;
            color: #00d4ff;
            font-size: 20px;
            text-align: center;
        }}
        
        .analysis-section {{
            margin-bottom: 25px;
            padding: 15px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }}
        
        .analysis-section h3 {{
            margin: 0 0 15px 0;
            color: #00ff88;
            font-size: 16px;
        }}
        
        .analysis-item {{
            display: flex;
            justify-content: space-between;
            margin: 8px 0;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .analysis-label {{
            color: #bdc3c7;
            font-weight: 500;
        }}
        
        .analysis-value {{
            color: #fff;
            font-weight: 600;
        }}
        
        .analysis-chart {{
            width: 100%;
            height: 120px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            margin: 10px 0;
            position: relative;
            overflow: hidden;
        }}
        
        .chart-bar {{
            position: absolute;
            bottom: 0;
            background: linear-gradient(to top, #00d4ff, #00ff88);
            border-radius: 2px 2px 0 0;
            transition: height 0.3s ease;
        }}
        
        .chart-label {{
            position: absolute;
            bottom: -20px;
            font-size: 10px;
            color: #bdc3c7;
            text-align: center;
            width: 100%;
        }}
        
        .control-panel {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.9);
            padding: 15px 25px;
            border-radius: 25px;
            z-index: 10;
            display: flex;
            gap: 15px;
            align-items: center;
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .control-panel button {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }}
        
        .control-panel button:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.4);
        }}
        
        .control-panel button.active {{
            background: #00d4ff;
            border-color: #00d4ff;
            color: #000;
        }}
    </style>
</head>
<body>
    <div class="analysis-panel">
        <h2>🔬 Phân tích kỹ thuật</h2>
        
        <div class="analysis-section">
            <h3>📏 Kích thước</h3>
            <div class="analysis-item">
                <span class="analysis-label">Chiều dài:</span>
                <span class="analysis-value">{length:.1f} m</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Chiều rộng:</span>
                <span class="analysis-value">{width:.2f} m</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Chiều cao:</span>
                <span class="analysis-value">{height:.1f} m</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Góc dốc:</span>
                <span class="analysis-value">{inclination:.1f}°</span>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>⚡ Hiệu suất</h3>
            <div class="analysis-item">
                <span class="analysis-label">Tốc độ:</span>
                <span class="analysis-value">{speed:.2f} m/s</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Công suất:</span>
                <span class="analysis-value">{power:.1f} kW</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Tỷ số truyền:</span>
                <span class="analysis-value">{ratio:.1f}</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Hiệu suất:</span>
                <span class="analysis-value">{efficiency:.1%}</span>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>📊 Thống kê</h3>
            <div class="analysis-item">
                <span class="analysis-label">Con lăn mang tải:</span>
                <span class="analysis-value">{carrying_idlers}</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Con lăn hồi:</span>
                <span class="analysis-value">{return_idlers}</span>
            </div>
            <div class="analysis-item">
                <span class="analysis-label">Tổng khối lượng:</span>
                <span class="analysis-value">{total_weight:.1f} kg</span>
            </div>
        </div>
        
        <div class="analysis-section">
            <h3>📈 Biểu đồ phân tích</h3>
            <div class="analysis-chart" id="performance-chart">
                <div class="chart-bar" style="left: 10%; width: 15%; height: 60%;">
                    <div class="chart-label">Tốc độ</div>
                </div>
                <div class="chart-bar" style="left: 30%; width: 15%; height: 80%;">
                    <div class="chart-label">Công suất</div>
                </div>
                <div class="chart-bar" style="left: 50%; width: 15%; height: 70%;">
                    <div class="chart-label">Hiệu suất</div>
                </div>
                <div class="chart-bar" style="left: 70%; width: 15%; height: 90%;">
                    <div class="chart-label">Độ bền</div>
                </div>
                <div class="chart-bar" style="left: 90%; width: 15%; height: 75%;">
                    <div class="chart-label">Chi phí</div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="control-panel">
        <button id="toggle-analysis" class="active">📊</button>
        <button id="toggle-wireframe">📐</button>
        <button id="toggle-labels">🏷️</button>
        <button id="toggle-animation">▶️</button>
        <button id="export-data">💾</button>
    </div>
    
    {libs}
    
    <script>
        // JavaScript phân tích sẽ được inject ở đây
        {analysis_js}
    </script>
</body>
</html>
"""
