# Hướng Dẫn Sử Dụng Visualization 3D Nâng Cao

## 📖 Tổng Quan

Visualization 3D nâng cao là module mới được phát triển để tự động tạo mô hình 3D hoàn chỉnh của băng tải dựa trên tham số tính toán. Module này cung cấp:

- **Tự động tạo mô hình 3D** từ tham số tính toán
- **Animation và chuyển động** thực tế
- **Mô phỏng vật lý** cơ bản
- **Tối ưu hóa performance** tự động
- **Giao diện tương tác** nâng cao

## 🚀 Bắt Đầu Nhanh

### 1. Khởi tạo Visualization

```python
from ui.visualization_3d.enhanced_widget import EnhancedVisualization3DWidget

# Tạo widget
visualization_widget = EnhancedVisualization3DWidget()

# Cập nhật với dữ liệu
visualization_widget.update_enhanced_visualization(conveyor_params, calculation_result)
```

### 2. Sử dụng Model Generator

```python
from ui.visualization_3d.core.model_generator import ConveyorModelGenerator

# Tạo model generator
model_generator = ConveyorModelGenerator(conveyor_params, calculation_result)

# Tạo mô hình hoàn chỉnh
model_data = model_generator.generate_complete_model()
```

### 3. Sử dụng Component Builder

```python
from ui.visualization_3d.core.component_builder import ComponentBuilderManager

# Tạo component builder
component_builder = ComponentBuilderManager()

# Xây dựng tất cả components
components = component_builder.build_all_components(model_data)
```

## 🎯 Các Thành Phần Chính

### 1. Model Generator (`core/model_generator.py`)

**Chức năng:** Tạo mô hình 3D hoàn chỉnh từ tham số tính toán

**Các phương thức chính:**
- `generate_complete_model()`: Tạo mô hình hoàn chỉnh
- `_generate_belt_system()`: Tạo hệ thống băng tải
- `_generate_drive_system()`: Tạo hệ truyền động
- `_generate_support_structure()`: Tạo khung đỡ

**Ví dụ sử dụng:**
```python
# Tạo model generator
model_generator = ConveyorModelGenerator(conveyor_params, calculation_result)

# Tạo mô hình
model_data = model_generator.generate_complete_model()

# Truy cập các thành phần
belt_system = model_data['belt_system']
drive_system = model_data['drive_system']
support_structure = model_data['support_structure']
```

### 2. Component Builder (`core/component_builder.py`)

**Chức năng:** Xây dựng các thành phần 3D riêng lẻ

**Các builder chính:**
- `BeltSystemBuilder`: Xây dựng hệ thống băng tải
- `DriveSystemBuilder`: Xây dựng hệ truyền động
- `SupportStructureBuilder`: Xây dựng khung đỡ

**Ví dụ sử dụng:**
```python
# Tạo component builder manager
component_builder = ComponentBuilderManager()

# Xây dựng tất cả components
components = component_builder.build_all_components(model_data)

# Xây dựng từng thành phần riêng lẻ
belt_components = component_builder.belt_builder.build_belt_geometry()
drive_components = component_builder.drive_builder.build_drive_components()
support_components = component_builder.support_builder.build_support_structure()
```

### 3. Animation Engine (`core/animation_engine.py`)

**Chức năng:** Quản lý animation và chuyển động

**Các animation chính:**
- `BeltAnimation`: Animation cho băng tải
- `DriveAnimation`: Animation cho hệ truyền động
- `IdlerAnimation`: Animation cho con lăn
- `MaterialFlowAnimation`: Animation cho dòng vật liệu

**Ví dụ sử dụng:**
```python
# Tạo animation engine
animation_engine = ConveyorAnimationEngine(model_data)

# Cập nhật animations
animation_engine.update_animations(delta_time)

# Lấy thông tin animation
belt_animation = animation_engine.animations.get('belt')
if belt_animation:
    belt_animation.update(delta_time)
```

### 4. Physics Simulator (`core/physics_simulator.py`)

**Chức năng:** Mô phỏng vật lý cơ bản

**Các physics component:**
- `BeltPhysics`: Vật lý băng tải
- `DriveSystemPhysics`: Vật lý hệ truyền động
- `IdlerPhysics`: Vật lý con lăn
- `MaterialFlowPhysics`: Vật lý dòng vật liệu

**Ví dụ sử dụng:**
```python
# Tạo physics simulator
physics_simulator = ConveyorPhysicsSimulator(model_data)

# Cập nhật simulation
physics_simulator.update_simulation(delta_time)

# Lấy thông tin vật lý
belt_physics = physics_simulator.physics_components.get('belt')
if belt_physics:
    tension = belt_physics.calculate_belt_tension()
    power = belt_physics.calculate_power_consumption()
```

### 5. Performance Optimizer (`core/performance_optimizer.py`)

**Chức năng:** Tối ưu hóa performance và memory

**Các optimization level:**
- `LOW`: Chất lượng cao, performance thấp
- `MEDIUM`: Cân bằng
- `HIGH`: Performance cao, chất lượng thấp
- `ULTRA`: Performance tối đa

**Ví dụ sử dụng:**
```python
# Tạo performance optimizer
optimizer = PerformanceOptimizer()

# Thiết lập optimization level
optimizer.settings.level = OptimizationLevel.HIGH

# Tối ưu hóa scene
optimized_scene = optimizer.optimize_scene(scene_data)

# Tự động tối ưu hóa dựa trên FPS
optimizer.auto_optimize(current_fps=45, target_fps=60)
```

## 🎮 Giao Diện Người Dùng

### 1. Enhanced Widget

Widget chính tích hợp tất cả tính năng:

```python
# Tạo widget
widget = EnhancedVisualization3DWidget()

# Các panel có sẵn:
# - AnimationControlPanel: Điều khiển animation
# - InformationPanel: Hiển thị thông tin
# - ComponentTogglePanel: Bật/tắt thành phần
# - CameraControlPanel: Điều khiển camera
```

### 2. Animation Control Panel

**Các chức năng:**
- ⏸️ Play/Pause animation
- 🔄 Reset animation
- 🎚️ Điều chỉnh tốc độ (0.1x - 5.0x)
- 📊 Hiển thị thông số animation

### 3. Component Toggle Panel

**Các thành phần có thể bật/tắt:**
- ✅ Hệ thống băng tải
- ✅ Hệ truyền động
- ✅ Khung đỡ
- ✅ Dòng vật liệu

### 4. Camera Control Panel

**Các góc nhìn preset:**
- 👁️ Tổng quan
- ⚙️ Hệ truyền động
- 🔄 Con lăn
- 📏 Băng tải
- 🎛️ Tùy chỉnh

## ⚡ Tối Ưu Hóa Performance

### 1. Tự Động Tối Ưu Hóa

```python
# Tự động tối ưu hóa dựa trên FPS
optimizer = PerformanceOptimizer()
optimizer.auto_optimize(current_fps=45, target_fps=60)

# Kết quả: Tự động chuyển sang HIGH optimization level
```

### 2. Memory Management

```python
# Quản lý memory
memory_manager = MemoryManager(max_memory_mb=1024.0)

# Kiểm tra có thể allocate không
if memory_manager.can_allocate(100.0):
    memory_manager.allocate(100.0, "texture", "belt_texture")

# Dọn dẹp memory
memory_manager.cleanup_memory()
```

### 3. Cache Optimization

```python
# Tối ưu hóa cache
memory_manager.optimize_cache()

# Xóa cache cụ thể
memory_manager.clear_cache('texture')
memory_manager.clear_cache('geometry')
memory_manager.clear_cache('material')
```

## 🧪 Testing và Benchmarking

### 1. Chạy Tests

```python
# Chạy tất cả tests
from ui.visualization_3d.testing.test_framework import run_all_tests

results = run_all_tests()
```

### 2. Performance Benchmarking

```python
# Chạy performance benchmark
from ui.visualization_3d.testing.performance_benchmark import run_benchmark_demo

benchmarker = run_benchmark_demo()
```

### 3. Tạo Performance Charts

```python
# Tạo biểu đồ performance
benchmarker.generate_performance_charts("output_charts/")

# Các biểu đồ được tạo:
# - Execution Time Comparison
# - Memory Usage Comparison
# - FPS Comparison
# - Performance vs Parameters
```

## 📊 Cấu Trúc Dữ Liệu

### 1. Model Data Structure

```json
{
  "belt_system": {
    "geometry": {
      "width": 0.8,
      "length": 50.0,
      "thickness": 0.012,
      "trough_angle": 35.0
    },
    "material": "EP800/4",
    "texture": "belt_texture_01"
  },
  "drive_system": {
    "motor": {
      "power_kw": 15.5,
      "rpm": 1450,
      "efficiency": 0.95
    },
    "gearbox": {
      "ratio": 25.0,
      "efficiency": 0.98
    },
    "chain_drive": {
      "chain_type": "16B-1",
      "sprocket_teeth": {
        "drive": 19,
        "driven": 38
      },
      "chain_pitch": 0.0254
    }
  },
  "support_structure": {
    "carrying_idlers": {
      "count": 42,
      "spacing": 1.2,
      "diameter": 0.133,
      "trough_angle": 35.0
    },
    "return_idlers": {
      "count": 17,
      "spacing": 3.0,
      "diameter": 0.108
    }
  },
  "material_flow": {
    "density": 1600.0,
    "flow_rate": 125.0,
    "particle_size": 0.05
  }
}
```

### 2. Component Data Structure

```json
{
  "belt": {
    "geometry": "BoxGeometry",
    "parameters": {
      "width": 0.8,
      "height": 0.012,
      "depth": 50.0
    },
    "material": "belt_material",
    "position": [0, 0, 0],
    "rotation": [0, 0, 0]
  },
  "motor": {
    "geometry": "CylinderGeometry",
    "parameters": {
      "radiusTop": 0.15,
      "radiusBottom": 0.15,
      "height": 0.3
    },
    "material": "motor_material",
    "position": [0, 0.5, 0],
    "rotation": [0, 0, 0]
  }
}
```

## 🔧 Cấu Hình và Tùy Chỉnh

### 1. Cấu Hình Optimization

```python
# Tùy chỉnh optimization settings
optimizer = PerformanceOptimizer()
optimizer.settings.max_triangles = 50000
optimizer.settings.max_texture_size = 1024
optimizer.settings.enable_frustum_culling = True
optimizer.settings.enable_lod = True
optimizer.settings.enable_occlusion_culling = True
optimizer.settings.enable_shadow_mapping = False
optimizer.settings.max_lights = 2
```

### 2. Cấu Hình Animation

```python
# Tùy chỉnh animation settings
animation_engine = ConveyorAnimationEngine(model_data)
animation_engine.animation_speed = 1.5
animation_engine.enable_material_flow = True
animation_engine.enable_particle_system = True
```

### 3. Cấu Hình Physics

```python
# Tùy chỉnh physics settings
physics_simulator = ConveyorPhysicsSimulator(model_data)
physics_simulator.gravity = 9.81
physics_simulator.time_step = 0.016  # 60 FPS
physics_simulator.enable_collision_detection = True
```

## 🚨 Xử Lý Lỗi và Troubleshooting

### 1. Lỗi Thường Gặp

**Lỗi Import Module:**
```python
# Kiểm tra đường dẫn
import sys
sys.path.append('path/to/visualization_3d')

# Kiểm tra dependencies
pip install -r requirements.txt
```

**Lỗi Memory:**
```python
# Dọn dẹp memory
import gc
gc.collect()

# Giảm optimization level
optimizer.settings.level = OptimizationLevel.HIGH
```

**Lỗi Performance:**
```python
# Tự động tối ưu hóa
optimizer.auto_optimize(current_fps=30, target_fps=60)

# Kiểm tra memory usage
memory_stats = memory_manager.get_usage_stats()
print(f"Memory usage: {memory_stats['usage_percent']:.1f}%")
```

### 2. Debug Mode

```python
# Bật debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Kiểm tra performance metrics
performance_report = optimizer.get_performance_report()
print(json.dumps(performance_report, indent=2))
```

## 📈 Best Practices

### 1. Performance Optimization

- **Sử dụng optimization level phù hợp** với hardware
- **Monitor memory usage** thường xuyên
- **Cleanup resources** khi không sử dụng
- **Batch operations** thay vì individual calls

### 2. Memory Management

- **Set memory limits** phù hợp với system
- **Clear caches** định kỳ
- **Monitor memory leaks** với debug tools
- **Use weak references** cho large objects

### 3. Animation Performance

- **Limit animation complexity** dựa trên FPS target
- **Use LOD (Level of Detail)** cho complex models
- **Optimize texture sizes** và compression
- **Batch render calls** khi có thể

## 🔮 Tính Năng Tương Lai

### 1. Đang Phát Triển

- **Real-time collaboration** giữa nhiều users
- **Advanced physics simulation** với Bullet Physics
- **VR/AR support** cho immersive experience
- **Cloud rendering** cho heavy scenes

### 2. Roadmap

- **Q1 2024**: Performance optimization và testing
- **Q2 2024**: Advanced physics và VR support
- **Q3 2024**: Cloud rendering và collaboration
- **Q4 2024**: AI-powered optimization

## 📞 Hỗ Trợ và Liên Hệ

### 1. Documentation

- **API Reference**: Chi tiết các class và method
- **Examples**: Code examples và tutorials
- **Troubleshooting**: Hướng dẫn xử lý lỗi
- **Performance Guide**: Tối ưu hóa performance

### 2. Community

- **GitHub Issues**: Báo cáo bugs và feature requests
- **Discussions**: Thảo luận và hỏi đáp
- **Contributions**: Đóng góp code và documentation

### 3. Support

- **Email**: support@visualization3d.com
- **Chat**: Discord community
- **Forum**: Technical discussions

---

## 📝 Changelog

### Version 1.0.0 (Giai đoạn 4)
- ✅ Performance optimization và memory management
- ✅ Comprehensive testing framework
- ✅ Performance benchmarking tools
- ✅ Advanced documentation và user guide
- ✅ Integration testing với hệ thống chính

### Version 0.9.0 (Giai đoạn 3)
- ✅ Animation engine hoàn chỉnh
- ✅ Physics simulator cơ bản
- ✅ Component builder nâng cao
- ✅ Enhanced UI controls

### Version 0.8.0 (Giai đoạn 2)
- ✅ Component builders cơ bản
- ✅ Model generator framework
- ✅ Basic 3D visualization

### Version 0.7.0 (Giai đoạn 1)
- ✅ Cơ sở hạ tầng cơ bản
- ✅ Integration với hệ thống hiện tại
- ✅ Basic 3D rendering

---

**© 2024 Visualization 3D Team. All rights reserved.**
