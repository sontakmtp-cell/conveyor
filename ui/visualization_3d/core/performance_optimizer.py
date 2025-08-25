"""
Performance Optimizer for 3D Visualization
Tối ưu hóa performance, memory và rendering quality
"""

import time
import psutil
import gc
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Mức độ tối ưu hóa"""
    LOW = "low"           # Chất lượng cao, performance thấp
    MEDIUM = "medium"     # Cân bằng
    HIGH = "high"         # Performance cao, chất lượng thấp
    ULTRA = "ultra"       # Performance tối đa


@dataclass
class PerformanceMetrics:
    """Metrics về performance"""
    fps: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    render_time_ms: float = 0.0
    triangle_count: int = 0
    texture_memory_mb: float = 0.0
    gpu_memory_mb: float = 0.0


@dataclass
class OptimizationSettings:
    """Cài đặt tối ưu hóa"""
    level: OptimizationLevel = OptimizationLevel.MEDIUM
    max_triangles: int = 100000
    max_texture_size: int = 2048
    enable_frustum_culling: bool = True
    enable_lod: bool = True
    enable_occlusion_culling: bool = True
    enable_shadow_mapping: bool = True
    enable_post_processing: bool = True
    max_lights: int = 4
    enable_antialiasing: bool = True
    enable_anisotropic_filtering: bool = True


class PerformanceOptimizer:
    """Bộ tối ưu hóa performance chính"""
    
    def __init__(self):
        self.settings = OptimizationSettings()
        self.metrics = PerformanceMetrics()
        self.optimization_history: List[PerformanceMetrics] = []
        self.start_time = time.time()
        
    def optimize_scene(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa scene dựa trên cài đặt"""
        logger.info(f"Bắt đầu tối ưu hóa scene với level: {self.settings.level.value}")
        
        # Tối ưu hóa geometry
        optimized_geometry = self._optimize_geometry(scene_data.get('geometry', {}))
        
        # Tối ưu hóa materials
        optimized_materials = self._optimize_materials(scene_data.get('materials', {}))
        
        # Tối ưu hóa textures
        optimized_textures = self._optimize_textures(scene_data.get('textures', {}))
        
        # Tối ưu hóa lighting
        optimized_lighting = self._optimize_lighting(scene_data.get('lighting', {}))
        
        # Tối ưu hóa animation
        optimized_animation = self._optimize_animation(scene_data.get('animation', {}))
        
        return {
            'geometry': optimized_geometry,
            'materials': optimized_materials,
            'textures': optimized_textures,
            'lighting': optimized_lighting,
            'animation': optimized_animation,
            'optimization_level': self.settings.level.value,
            'performance_metrics': self.metrics.__dict__
        }
    
    def _optimize_geometry(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa geometry"""
        if self.settings.level == OptimizationLevel.ULTRA:
            return self._ultra_geometry_optimization(geometry_data)
        elif self.settings.level == OptimizationLevel.HIGH:
            return self._high_geometry_optimization(geometry_data)
        elif self.settings.level == OptimizationLevel.MEDIUM:
            return self._medium_geometry_optimization(geometry_data)
        else:
            return self._low_geometry_optimization(geometry_data)
    
    def _ultra_geometry_optimization(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa geometry ở mức ULTRA"""
        optimized = {}
        
        for key, geo in geometry_data.items():
            if isinstance(geo, dict) and 'vertices' in geo:
                # Giảm số lượng vertices
                vertices = geo['vertices']
                if len(vertices) > self.settings.max_triangles * 3:
                    # Decimate geometry
                    decimated_vertices = self._decimate_vertices(vertices, self.settings.max_triangles * 3)
                    optimized[key] = {**geo, 'vertices': decimated_vertices}
                else:
                    optimized[key] = geo
            else:
                optimized[key] = geo
        
        return optimized
    
    def _high_geometry_optimization(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa geometry ở mức HIGH"""
        return self._ultra_geometry_optimization(geometry_data)
    
    def _medium_geometry_optimization(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa geometry ở mức MEDIUM"""
        # Giữ nguyên geometry, chỉ tối ưu hóa nhẹ
        return geometry_data
    
    def _low_geometry_optimization(self, geometry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa geometry ở mức LOW"""
        # Không tối ưu hóa, giữ nguyên chất lượng
        return geometry_data
    
    def _decimate_vertices(self, vertices: List[float], target_count: int) -> List[float]:
        """Giảm số lượng vertices"""
        if len(vertices) <= target_count:
            return vertices
        
        # Thuật toán decimation đơn giản - giữ lại mỗi n vertex
        step = len(vertices) // target_count
        return vertices[::step]
    
    def _optimize_materials(self, materials_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa materials"""
        optimized = {}
        
        for key, material in materials_data.items():
            if isinstance(material, dict):
                # Tối ưu hóa material properties
                optimized_material = self._optimize_material_properties(material)
                optimized[key] = optimized_material
            else:
                optimized[key] = material
        
        return optimized
    
    def _optimize_material_properties(self, material: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa properties của material"""
        optimized = material.copy()
        
        # Tối ưu hóa dựa trên level
        if self.settings.level in [OptimizationLevel.HIGH, OptimizationLevel.ULTRA]:
            # Giảm độ phức tạp của material
            if 'roughness' in optimized:
                optimized['roughness'] = round(optimized['roughness'], 1)
            if 'metalness' in optimized:
                optimized['metalness'] = round(optimized['metalness'], 1)
            if 'normalScale' in optimized:
                optimized['normalScale'] = [1.0, 1.0]  # Đơn giản hóa normal mapping
        
        return optimized
    
    def _optimize_textures(self, textures_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa textures"""
        optimized = {}
        
        for key, texture in textures_data.items():
            if isinstance(texture, dict):
                # Tối ưu hóa texture properties
                optimized_texture = self._optimize_texture_properties(texture)
                optimized[key] = optimized_texture
            else:
                optimized[key] = texture
        
        return optimized
    
    def _optimize_texture_properties(self, texture: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa properties của texture"""
        optimized = texture.copy()
        
        # Tối ưu hóa dựa trên level
        if self.settings.level == OptimizationLevel.ULTRA:
            # Giảm chất lượng texture tối đa
            if 'anisotropy' in optimized:
                optimized['anisotropy'] = 1
            if 'minFilter' in optimized:
                optimized['minFilter'] = 'LinearFilter'
            if 'magFilter' in optimized:
                optimized['magFilter'] = 'LinearFilter'
        elif self.settings.level == OptimizationLevel.HIGH:
            # Giảm chất lượng texture vừa phải
            if 'anisotropy' in optimized:
                optimized['anisotropy'] = min(optimized.get('anisotropy', 16), 4)
        
        return optimized
    
    def _optimize_lighting(self, lighting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa lighting"""
        optimized = lighting_data.copy()
        
        # Giới hạn số lượng lights
        if 'lights' in optimized and len(optimized['lights']) > self.settings.max_lights:
            optimized['lights'] = optimized['lights'][:self.settings.max_lights]
        
        # Tối ưu hóa shadow mapping
        if not self.settings.enable_shadow_mapping:
            for light in optimized.get('lights', []):
                if isinstance(light, dict):
                    light['castShadow'] = False
        
        return optimized
    
    def _optimize_animation(self, animation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Tối ưu hóa animation"""
        optimized = animation_data.copy()
        
        # Tối ưu hóa dựa trên level
        if self.settings.level in [OptimizationLevel.HIGH, OptimizationLevel.ULTRA]:
            # Giảm độ mượt của animation
            if 'fps' in optimized:
                optimized['fps'] = min(optimized['fps'], 30)
            if 'interpolation' in optimized:
                optimized['interpolation'] = 'LinearInterpolation'
        
        return optimized
    
    def update_performance_metrics(self, new_metrics: PerformanceMetrics):
        """Cập nhật performance metrics"""
        self.metrics = new_metrics
        self.optimization_history.append(new_metrics)
        
        # Giữ lại lịch sử 100 metrics gần nhất
        if len(self.optimization_history) > 100:
            self.optimization_history = self.optimization_history[-100:]
        
        # Ghi log performance
        logger.info(f"Performance: FPS={new_metrics.fps:.1f}, "
                   f"Memory={new_metrics.memory_usage_mb:.1f}MB, "
                   f"CPU={new_metrics.cpu_usage_percent:.1f}%")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Lấy báo cáo performance"""
        if not self.optimization_history:
            return {}
        
        # Tính toán thống kê
        fps_values = [m.fps for m in self.optimization_history]
        memory_values = [m.memory_usage_mb for m in self.optimization_history]
        cpu_values = [m.cpu_usage_percent for m in self.optimization_history]
        
        return {
            'current': self.metrics.__dict__,
            'average': {
                'fps': sum(fps_values) / len(fps_values),
                'memory_mb': sum(memory_values) / len(memory_values),
                'cpu_percent': sum(cpu_values) / len(cpu_values)
            },
            'min': {
                'fps': min(fps_values),
                'memory_mb': min(memory_values),
                'cpu_percent': min(cpu_values)
            },
            'max': {
                'fps': max(fps_values),
                'memory_mb': max(memory_values),
                'cpu_percent': max(cpu_values)
            },
            'history_count': len(self.optimization_history),
            'uptime_seconds': time.time() - self.start_time
        }
    
    def auto_optimize(self, current_fps: float, target_fps: float = 60.0) -> OptimizationSettings:
        """Tự động tối ưu hóa dựa trên FPS hiện tại"""
        if current_fps >= target_fps:
            # Performance tốt, có thể tăng chất lượng
            if self.settings.level == OptimizationLevel.ULTRA:
                self.settings.level = OptimizationLevel.HIGH
            elif self.settings.level == OptimizationLevel.HIGH:
                self.settings.level = OptimizationLevel.MEDIUM
            elif self.settings.level == OptimizationLevel.MEDIUM:
                self.settings.level = OptimizationLevel.LOW
        else:
            # Performance kém, giảm chất lượng
            if self.settings.level == OptimizationLevel.LOW:
                self.settings.level = OptimizationLevel.MEDIUM
            elif self.settings.level == OptimizationLevel.MEDIUM:
                self.settings.level = OptimizationLevel.HIGH
            elif self.settings.level == OptimizationLevel.HIGH:
                self.settings.level = OptimizationLevel.ULTRA
        
        logger.info(f"Auto-optimization: FPS={current_fps:.1f}, "
                   f"Target={target_fps:.1f}, New Level={self.settings.level.value}")
        
        return self.settings
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Lấy thông tin sử dụng memory"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
    
    def cleanup_memory(self):
        """Dọn dẹp memory"""
        logger.info("Bắt đầu cleanup memory")
        
        # Garbage collection
        collected = gc.collect()
        logger.info(f"Garbage collected: {collected} objects")
        
        # Xóa lịch sử cũ
        if len(self.optimization_history) > 50:
            self.optimization_history = self.optimization_history[-50:]
        
        # Reset metrics
        self.metrics = PerformanceMetrics()
        
        logger.info("Memory cleanup completed")


class MemoryManager:
    """Quản lý memory cho visualization"""
    
    def __init__(self, max_memory_mb: float = 1024.0):
        self.max_memory_mb = max_memory_mb
        self.current_usage_mb = 0.0
        self.texture_cache: Dict[str, Any] = {}
        self.geometry_cache: Dict[str, Any] = {}
        self.material_cache: Dict[str, Any] = {}
        
    def can_allocate(self, size_mb: float) -> bool:
        """Kiểm tra có thể allocate memory không"""
        return (self.current_usage_mb + size_mb) <= self.max_memory_mb
    
    def allocate(self, size_mb: float, resource_type: str, resource_id: str) -> bool:
        """Allocate memory cho resource"""
        if not self.can_allocate(size_mb):
            logger.warning(f"Không thể allocate {size_mb:.1f}MB cho {resource_type}:{resource_id}")
            return False
        
        self.current_usage_mb += size_mb
        logger.info(f"Allocated {size_mb:.1f}MB cho {resource_type}:{resource_id}")
        return True
    
    def deallocate(self, size_mb: float, resource_type: str, resource_id: str):
        """Deallocate memory"""
        self.current_usage_mb = max(0.0, self.current_usage_mb - size_mb)
        logger.info(f"Deallocated {size_mb:.1f}MB từ {resource_type}:{resource_id}")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Lấy thống kê sử dụng memory"""
        return {
            'current_mb': self.current_usage_mb,
            'max_mb': self.max_memory_mb,
            'usage_percent': (self.current_usage_mb / self.max_memory_mb) * 100,
            'available_mb': self.max_memory_mb - self.current_usage_mb,
            'texture_cache_count': len(self.texture_cache),
            'geometry_cache_count': len(self.geometry_cache),
            'material_cache_count': len(self.material_cache)
        }
    
    def clear_cache(self, cache_type: str = 'all'):
        """Xóa cache"""
        if cache_type == 'all' or cache_type == 'texture':
            self.texture_cache.clear()
        if cache_type == 'all' or cache_type == 'geometry':
            self.geometry_cache.clear()
        if cache_type == 'all' or cache_type == 'material':
            self.material_cache.clear()
        
        logger.info(f"Cleared {cache_type} cache")
    
    def optimize_cache(self):
        """Tối ưu hóa cache"""
        # Xóa cache cũ nếu memory usage cao
        if self.current_usage_mb > self.max_memory_mb * 0.8:
            self.clear_cache('all')
            logger.info("Cleared all caches due to high memory usage")
