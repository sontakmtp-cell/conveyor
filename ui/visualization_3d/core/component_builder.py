"""
Component Builder cho băng tải 3D
Xây dựng các thành phần 3D từ dữ liệu mô hình
"""

import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class GeometryData:
    """Dữ liệu hình học 3D"""
    type: str  # 'box', 'cylinder', 'sphere', 'custom'
    parameters: Dict[str, float]
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class MaterialData:
    """Dữ liệu vật liệu 3D"""
    name: str
    color: str = "#808080"
    opacity: float = 1.0
    metalness: float = 0.0
    roughness: float = 0.5
    texture: Optional[str] = None
    normal_map: Optional[str] = None


@dataclass
class Component3D:
    """Thành phần 3D hoàn chỉnh"""
    id: str
    name: str
    geometry: GeometryData
    material: MaterialData
    children: List['Component3D'] = field(default_factory=list)
    user_data: Dict[str, Any] = field(default_factory=dict)
    
    def add_child(self, child: 'Component3D'):
        """Thêm thành phần con"""
        self.children.append(child)
    
    def get_world_position(self) -> Tuple[float, float, float]:
        """Lấy vị trí thế giới"""
        return self.geometry.position
    
    def get_world_rotation(self) -> Tuple[float, float, float]:
        """Lấy góc quay thế giới"""
        return self.geometry.rotation


class BeltSystemBuilder:
    """Xây dựng hệ thống băng tải 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.components: List[Component3D] = []
    
    def build_complete_system(self) -> List[Component3D]:
        """Xây dựng hệ thống băng tải hoàn chỉnh"""
        # Xóa danh sách cũ
        self.components.clear()
        
        # Xây dựng từng thành phần
        self._build_main_belt()
        self._build_trough_support()
        self._build_edge_guards()
        self._build_cleaning_system()
        
        return self.components
    
    def _build_main_belt(self):
        """Xây dựng băng tải chính"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Tạo băng tải chính
        belt_geometry = GeometryData(
            type='box',
            parameters={
                'width': geometry.get('width', 0.8),
                'height': geometry.get('thickness', 0.01),
                'depth': geometry.get('length', 10.0)
            },
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        belt_material = MaterialData(
            name='Belt',
            color='#2F4F4F',
            roughness=0.8,
            texture='belt_texture'
        )
        
        belt_component = Component3D(
            id='main_belt',
            name='Băng tải chính',
            geometry=belt_geometry,
            material=belt_material,
            user_data={'type': 'belt', 'speed': geometry.get('speed', 2.0)}
        )
        
        self.components.append(belt_component)
    
    def _build_trough_support(self):
        """Xây dựng hệ thống đỡ máng"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        trough_angle = geometry.get('trough_angle', 20.0)
        
        if trough_angle > 0:
            # Tạo các tấm đỡ máng
            num_supports = max(3, int(geometry.get('length', 10.0) / 2))
            
            for i in range(num_supports):
                x_pos = (i / (num_supports - 1)) * geometry.get('length', 10.0) - geometry.get('length', 10.0) / 2
                
                # Tấm đỡ trái
                left_support = self._create_trough_support_plate(
                    x_pos, -geometry.get('width', 0.8) / 2, trough_angle, 'left'
                )
                self.components.append(left_support)
                
                # Tấm đỡ phải
                right_support = self._create_trough_support_plate(
                    x_pos, geometry.get('width', 0.8) / 2, -trough_angle, 'right'
                )
                self.components.append(right_support)
    
    def _create_trough_support_plate(self, x: float, z: float, angle: float, side: str) -> Component3D:
        """Tạo tấm đỡ máng"""
        plate_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.02,
                'height': 0.3,
                'depth': 0.8
            },
            position=(x, 0.15, z),
            rotation=(0.0, math.radians(angle), 0.0)
        )
        
        plate_material = MaterialData(
            name='Trough Support',
            color='#696969',
            metalness=0.7,
            roughness=0.3
        )
        
        return Component3D(
            id=f'trough_support_{side}_{x}',
            name=f'Tấm đỡ máng {side}',
            geometry=plate_geometry,
            material=plate_material,
            user_data={'type': 'trough_support', 'side': side}
        )
    
    def _build_edge_guards(self):
        """Xây dựng tấm chắn cạnh"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Tấm chắn cạnh trái
        left_guard = self._create_edge_guard(
            -geometry.get('width', 0.8) / 2 - 0.02, 'left'
        )
        self.components.append(left_guard)
        
        # Tấm chắn cạnh phải
        right_guard = self._create_edge_guard(
            geometry.get('width', 0.8) / 2 + 0.02, 'right'
        )
        self.components.append(right_guard)
    
    def _create_edge_guard(self, z_pos: float, side: str) -> Component3D:
        """Tạo tấm chắn cạnh"""
        guard_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.02,
                'height': 0.2,
                'depth': 10.0
            },
            position=(0.0, 0.1, z_pos),
            rotation=(0.0, 0.0, 0.0)
        )
        
        guard_material = MaterialData(
            name='Edge Guard',
            color='#8B4513',
            metalness=0.5,
            roughness=0.4
        )
        
        return Component3D(
            id=f'edge_guard_{side}',
            name=f'Tấm chắn cạnh {side}',
            geometry=guard_geometry,
            material=guard_material,
            user_data={'type': 'edge_guard', 'side': side}
        )
    
    def _build_cleaning_system(self):
        """Xây dựng hệ thống làm sạch"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Bàn chải làm sạch
        brush_geometry = GeometryData(
            type='cylinder',
            parameters={
                'radius': 0.1,
                'height': geometry.get('width', 0.8)
            },
            position=(geometry.get('length', 10.0) / 2, 0.05, 0.0),
            rotation=(0.0, 0.0, math.pi / 2)
        )
        
        brush_material = MaterialData(
            name='Cleaning Brush',
            color='#8B0000',
            roughness=0.9
        )
        
        brush_component = Component3D(
            id='cleaning_brush',
            name='Bàn chải làm sạch',
            geometry=brush_geometry,
            material=brush_material,
            user_data={'type': 'cleaning_system'}
        )
        
        self.components.append(brush_component)


class DriveSystemBuilder:
    """Xây dựng hệ thống truyền động 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.components: List[Component3D] = []
    
    def build_complete_system(self) -> List[Component3D]:
        """Xây dựng hệ thống truyền động hoàn chỉnh"""
        self.components.clear()
        
        # Xây dựng từng thành phần
        self._build_motor()
        self._build_gearbox()
        self._build_chain_drive()
        self._build_pulleys()
        self._build_tensioning_system()
        
        return self.components
    
    def _build_motor(self):
        """Xây dựng động cơ"""
        drive_data = self.data.get('drive_system', {})
        motor_data = drive_data.get('motor', {})
        
        # Thân động cơ
        motor_body = GeometryData(
            type='cylinder',
            parameters={
                'radius': 0.15,
                'height': 0.3
            },
            position=(-4.0, 0.2, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        motor_material = MaterialData(
            name='Motor Body',
            color='#4169E1',
            metalness=0.8,
            roughness=0.2
        )
        
        motor_component = Component3D(
            id='motor',
            name='Động cơ',
            geometry=motor_body,
            material=motor_material,
            user_data={
                'type': 'motor',
                'power_kw': motor_data.get('power_kw', 5.5),
                'rpm': motor_data.get('rpm', 1450)
            }
        )
        
        # Trục động cơ
        motor_shaft = GeometryData(
            type='cylinder',
            parameters={
                'radius': 0.02,
                'height': 0.1
            },
            position=(-4.0, 0.2, 0.15),
            rotation=(0.0, 0.0, 0.0)
        )
        
        shaft_material = MaterialData(
            name='Motor Shaft',
            color='#C0C0C0',
            metalness=0.9,
            roughness=0.1
        )
        
        shaft_component = Component3D(
            id='motor_shaft',
            name='Trục động cơ',
            geometry=motor_shaft,
            material=shaft_material,
            user_data={'type': 'motor_shaft'}
        )
        
        motor_component.add_child(shaft_component)
        self.components.append(motor_component)
    
    def _build_gearbox(self):
        """Xây dựng hộp số"""
        drive_data = self.data.get('drive_system', {})
        gearbox_data = drive_data.get('gearbox', {})
        
        # Thân hộp số
        gearbox_body = GeometryData(
            type='box',
            parameters={
                'width': 0.4,
                'height': 0.3,
                'depth': 0.5
            },
            position=(-3.5, 0.2, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        gearbox_material = MaterialData(
            name='Gearbox Body',
            color='#2F4F4F',
            metalness=0.7,
            roughness=0.3
        )
        
        gearbox_component = Component3D(
            id='gearbox',
            name='Hộp số',
            geometry=gearbox_body,
            material=gearbox_material,
            user_data={
                'type': 'gearbox',
                'ratio': gearbox_data.get('ratio', 20.0),
                'efficiency': gearbox_data.get('efficiency', 0.95)
            }
        )
        
        # Trục đầu ra
        output_shaft = GeometryData(
            type='cylinder',
            parameters={
                'radius': 0.025,
                'height': 0.15
            },
            position=(-3.5, 0.2, 0.25),
            rotation=(0.0, 0.0, 0.0)
        )
        
        output_shaft_material = MaterialData(
            name='Gearbox Output Shaft',
            color='#C0C0C0',
            metalness=0.9,
            roughness=0.1
        )
        
        output_shaft_component = Component3D(
            id='gearbox_output_shaft',
            name='Trục đầu ra hộp số',
            geometry=output_shaft,
            material=output_shaft_material,
            user_data={'type': 'gearbox_output_shaft'}
        )
        
        gearbox_component.add_child(output_shaft_component)
        self.components.append(gearbox_component)
    
    def _build_chain_drive(self):
        """Xây dựng truyền động xích"""
        drive_data = self.data.get('drive_system', {})
        chain_data = drive_data.get('chain_drive', {})
        
        if not chain_data:
            return
        
        # Sprocket dẫn động
        drive_sprocket = self._create_sprocket(
            -3.3, 0.2, 0.25, 'drive', chain_data.get('sprocket_teeth', {}).get('drive', 20)
        )
        self.components.append(drive_sprocket)
        
        # Sprocket bị dẫn
        driven_sprocket = self._create_sprocket(
            -2.5, 0.2, 0.25, 'driven', chain_data.get('sprocket_teeth', {}).get('driven', 40)
        )
        self.components.append(driven_sprocket)
        
        # Xích truyền động
        chain = self._create_chain(-2.9, 0.2, 0.25)
        self.components.append(chain)
    
    def _create_sprocket(self, x: float, y: float, z: float, sprocket_type: str, teeth: int) -> Component3D:
        """Tạo sprocket"""
        # Tính toán kích thước dựa trên số răng
        pitch_diameter = 0.1 + (teeth / 20) * 0.05
        
        sprocket_geometry = GeometryData(
            type='cylinder',
            parameters={
                'radius': pitch_diameter,
                'height': 0.05
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, 0.0)
        )
        
        sprocket_material = MaterialData(
            name='Sprocket',
            color='#696969',
            metalness=0.8,
            roughness=0.2
        )
        
        return Component3D(
            id=f'sprocket_{sprocket_type}',
            name=f'Sprocket {sprocket_type}',
            geometry=sprocket_geometry,
            material=sprocket_material,
            user_data={
                'type': 'sprocket',
                'sprocket_type': sprocket_type,
                'teeth': teeth
            }
        )
    
    def _create_chain(self, x: float, y: float, z: float) -> Component3D:
        """Tạo xích truyền động"""
        chain_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.6,
                'height': 0.02,
                'depth': 0.02
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, 0.0)
        )
        
        chain_material = MaterialData(
            name='Chain',
            color='#2F4F4F',
            metalness=0.9,
            roughness=0.1
        )
        
        return Component3D(
            id='chain_drive',
            name='Xích truyền động',
            geometry=chain_geometry,
            material=chain_material,
            user_data={'type': 'chain'}
        )
    
    def _build_pulleys(self):
        """Xây dựng các pulley"""
        # Pulley dẫn động
        drive_pulley = self._create_pulley(-2.0, 0.2, 0.25, 'drive')
        self.components.append(drive_pulley)
        
        # Pulley bị dẫn
        driven_pulley = self._create_pulley(2.0, 0.2, 0.25, 'driven')
        self.components.append(driven_pulley)
    
    def _create_pulley(self, x: float, y: float, z: float, pulley_type: str) -> Component3D:
        """Tạo pulley"""
        pulley_geometry = GeometryData(
            type='cylinder',
            parameters={
                'radius': 0.2,
                'height': 0.1
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, 0.0)
        )
        
        pulley_material = MaterialData(
            name='Pulley',
            color='#8B4513',
            metalness=0.6,
            roughness=0.4
        )
        
        return Component3D(
            id=f'pulley_{pulley_type}',
            name=f'Pulley {pulley_type}',
            geometry=pulley_geometry,
            material=pulley_material,
            user_data={
                'type': 'pulley',
                'pulley_type': pulley_type
            }
        )
    
    def _build_tensioning_system(self):
        """Xây dựng hệ thống căng băng"""
        # Cơ cấu căng băng
        tensioner_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.3,
                'height': 0.2,
                'depth': 0.4
            },
            position=(2.5, 0.1, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        tensioner_material = MaterialData(
            name='Tensioner',
            color='#A0522D',
            metalness=0.5,
            roughness=0.5
        )
        
        tensioner_component = Component3D(
            id='tensioner',
            name='Cơ cấu căng băng',
            geometry=tensioner_geometry,
            material=tensioner_material,
            user_data={'type': 'tensioner'}
        )
        
        self.components.append(tensioner_component)


class SupportStructureBuilder:
    """Xây dựng khung đỡ và con lăn 3D"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.components: List[Component3D] = []
    
    def build_complete_system(self) -> List[Component3D]:
        """Xây dựng khung đỡ hoàn chỉnh"""
        self.components.clear()
        
        # Xây dựng từng thành phần
        self._build_main_frame()
        self._build_carrying_idlers()
        self._build_return_idlers()
        self._build_legs()
        self._build_cross_braces()
        
        return self.components
    
    def _build_main_frame(self):
        """Xây dựng khung chính"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Khung dọc chính
        main_frame = GeometryData(
            type='box',
            parameters={
                'width': 0.1,
                'height': 0.1,
                'depth': geometry.get('length', 10.0)
            },
            position=(0.0, -0.5, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        frame_material = MaterialData(
            name='Main Frame',
            color='#2F4F4F',
            metalness=0.7,
            roughness=0.3
        )
        
        frame_component = Component3D(
            id='main_frame',
            name='Khung chính',
            geometry=main_frame,
            material=frame_material,
            user_data={'type': 'main_frame'}
        )
        
        self.components.append(frame_component)
    
    def _build_carrying_idlers(self):
        """Xây dựng con lăn đỡ tải"""
        support_data = self.data.get('support_structure', {})
        idler_data = support_data.get('carrying_idlers', {})
        
        num_idlers = idler_data.get('count', 5)
        spacing = idler_data.get('spacing', 2.0)
        diameter = idler_data.get('diameter', 0.15)
        trough_angle = idler_data.get('trough_angle', 20.0)
        
        for i in range(num_idlers):
            x_pos = (i / (num_idlers - 1)) * (num_idlers - 1) * spacing - (num_idlers - 1) * spacing / 2
            
            # Con lăn giữa
            center_idler = self._create_idler(
                x_pos, 0.0, 0.0, diameter, 'center', trough_angle
            )
            self.components.append(center_idler)
            
            # Con lăn trái
            left_idler = self._create_idler(
                x_pos, 0.0, -0.3, diameter, 'left', trough_angle
            )
            self.components.append(left_idler)
            
            # Con lăn phải
            right_idler = self._create_idler(
                x_pos, 0.0, 0.3, diameter, 'right', -trough_angle
            )
            self.components.append(right_idler)
    
    def _create_idler(self, x: float, y: float, z: float, diameter: float, position: str, angle: float) -> Component3D:
        """Tạo con lăn"""
        idler_geometry = GeometryData(
            type='cylinder',
            parameters={
                'radius': diameter / 2,
                'height': 0.8
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, math.radians(angle))
        )
        
        idler_material = MaterialData(
            name='Idler',
            color='#C0C0C0',
            metalness=0.8,
            roughness=0.2
        )
        
        return Component3D(
            id=f'idler_{position}_{x}',
            name=f'Con lăn {position}',
            geometry=idler_geometry,
            material=idler_material,
            user_data={
                'type': 'idler',
                'position': position,
                'diameter': diameter
            }
        )
    
    def _build_return_idlers(self):
        """Xây dựng con lăn đỡ về"""
        support_data = self.data.get('support_structure', {})
        idler_data = support_data.get('return_idlers', {})
        
        num_idlers = idler_data.get('count', 3)
        spacing = idler_data.get('spacing', 3.0)
        diameter = idler_data.get('diameter', 0.12)
        
        for i in range(num_idlers):
            x_pos = (i / (num_idlers - 1)) * (num_idlers - 1) * spacing - (num_idlers - 1) * spacing / 2
            
            return_idler = self._create_idler(
                x_pos, -0.3, 0.0, diameter, 'return', 0.0
            )
            self.components.append(return_idler)
    
    def _build_legs(self):
        """Xây dựng chân đỡ"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Chân đỡ trước
        front_leg = self._create_leg(-geometry.get('length', 10.0) / 2, -1.0, 0.0)
        self.components.append(front_leg)
        
        # Chân đỡ sau
        back_leg = self._create_leg(geometry.get('length', 10.0) / 2, -1.0, 0.0)
        self.components.append(back_leg)
        
        # Chân đỡ giữa
        middle_leg = self._create_leg(0.0, -1.0, 0.0)
        self.components.append(middle_leg)
    
    def _create_leg(self, x: float, y: float, z: float) -> Component3D:
        """Tạo chân đỡ"""
        leg_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.1,
                'height': 1.0,
                'depth': 0.1
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, 0.0)
        )
        
        leg_material = MaterialData(
            name='Support Leg',
            color='#696969',
            metalness=0.6,
            roughness=0.4
        )
        
        return Component3D(
            id=f'support_leg_{x}',
            name='Chân đỡ',
            geometry=leg_geometry,
            material=leg_material,
            user_data={'type': 'support_leg'}
        )
    
    def _build_cross_braces(self):
        """Xây dựng thanh giằng chéo"""
        belt_data = self.data.get('belt_system', {})
        geometry = belt_data.get('geometry', {})
        
        # Thanh giằng chéo trước
        front_brace = self._create_cross_brace(-geometry.get('length', 10.0) / 2, -0.5, 0.0)
        self.components.append(front_brace)
        
        # Thanh giằng chéo sau
        back_brace = self._create_cross_brace(geometry.get('length', 10.0) / 2, -0.5, 0.0)
        self.components.append(back_brace)
    
    def _create_cross_brace(self, x: float, y: float, z: float) -> Component3D:
        """Tạo thanh giằng chéo"""
        brace_geometry = GeometryData(
            type='box',
            parameters={
                'width': 0.05,
                'height': 0.05,
                'depth': 0.8
            },
            position=(x, y, z),
            rotation=(0.0, 0.0, math.pi / 4)
        )
        
        brace_material = MaterialData(
            name='Cross Brace',
            color='#8B4513',
            metalness=0.5,
            roughness=0.5
        )
        
        return Component3D(
            id=f'cross_brace_{x}',
            name='Thanh giằng chéo',
            geometry=brace_geometry,
            material=brace_material,
            user_data={'type': 'cross_brace'}
        )


class ComponentBuilderManager:
    """Quản lý việc xây dựng các thành phần"""
    
    def __init__(self, model_data: Dict[str, Any]):
        self.data = model_data
        self.builders = {
            'belt_system': BeltSystemBuilder(model_data),
            'drive_system': DriveSystemBuilder(model_data),
            'support_structure': SupportStructureBuilder(model_data)
        }
        self.all_components: List[Component3D] = []
    
    def build_all_components(self) -> List[Component3D]:
        """Xây dựng tất cả thành phần"""
        self.all_components.clear()
        
        # Xây dựng từng hệ thống
        for system_name, builder in self.builders.items():
            system_components = builder.build_complete_system()
            self.all_components.extend(system_components)
        
        return self.all_components
    
    def get_components_by_type(self, component_type: str) -> List[Component3D]:
        """Lấy thành phần theo loại"""
        return [comp for comp in self.all_components if comp.user_data.get('type') == component_type]
    
    def get_component_by_id(self, component_id: str) -> Optional[Component3D]:
        """Lấy thành phần theo ID"""
        for comp in self.all_components:
            if comp.id == component_id:
                return comp
        return None
    
    def export_components_data(self) -> Dict[str, Any]:
        """Xuất dữ liệu thành phần"""
        components_data = {
            'total_count': len(self.all_components),
            'systems': {},
            'components': []
        }
        
        # Thống kê theo hệ thống
        for system_name, builder in self.builders.items():
            system_components = builder.build_complete_system()
            components_data['systems'][system_name] = {
                'component_count': len(system_components),
                'types': {}
            }
            
            # Thống kê theo loại
            for comp in system_components:
                comp_type = comp.user_data.get('type', 'unknown')
                if comp_type not in components_data['systems'][system_name]['types']:
                    components_data['systems'][system_name]['types'][comp_type] = 0
                components_data['systems'][system_name]['types'][comp_type] += 1
        
        # Dữ liệu chi tiết từng thành phần
        for comp in self.all_components:
            comp_data = {
                'id': comp.id,
                'name': comp.name,
                'type': comp.user_data.get('type', 'unknown'),
                'position': comp.geometry.position,
                'rotation': comp.geometry.rotation,
                'scale': comp.geometry.scale,
                'material': {
                    'name': comp.material.name,
                    'color': comp.material.color
                },
                'user_data': comp.user_data
            }
            components_data['components'].append(comp_data)
        
        return components_data
