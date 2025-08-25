"""
Test Giai đoạn 3: Animation Engine
Kiểm thử các thành phần đã được tạo trong Giai đoạn 3
"""

import sys
import os
import json
import unittest
from unittest.mock import Mock, MagicMock

# Thêm đường dẫn để import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ui', 'visualization_3d', 'core'))

# Import các modules cần test
from animation_engine import (
    ConveyorAnimationEngine, BeltAnimation, DriveAnimation, 
    IdlerAnimation, MaterialFlowAnimation, AnimationState
)

from component_builder import (
    ComponentBuilderManager, BeltSystemBuilder, DriveSystemBuilder, 
    SupportStructureBuilder, Component3D, GeometryData, MaterialData
)

from physics_simulator import (
    ConveyorPhysicsSimulator, BeltPhysics, DriveSystemPhysics,
    IdlerPhysics, MaterialFlowPhysics, MaterialProperties
)


class TestAnimationEngine(unittest.TestCase):
    """Test Animation Engine"""
    
    def setUp(self):
        """Thiết lập dữ liệu test"""
        self.model_data = {
            'belt_system': {
                'geometry': {
                    'width': 0.8,
                    'length': 10.0,
                    'thickness': 0.01,
                    'trough_angle': 20.0
                }
            },
            'drive_system': {
                'motor': {
                    'power_kw': 5.5,
                    'rpm': 1450,
                    'efficiency': 0.9
                },
                'gearbox': {
                    'ratio': 20.0,
                    'efficiency': 0.95
                }
            },
            'support_structure': {
                'carrying_idlers': {
                    'count': 5,
                    'spacing': 2.0,
                    'diameter': 0.15,
                    'trough_angle': 20.0
                }
            },
            'material_properties': {
                'flow_rate_tph': 100,
                'density_kg_m3': 1600,
                'belt_width_m': 0.8,
                'belt_speed_mps': 2.0
            },
            'belt_speed_mps': 2.0
        }
    
    def test_animation_state(self):
        """Test AnimationState"""
        state = AnimationState()
        self.assertTrue(state.is_playing)
        self.assertEqual(state.speed, 1.0)
        self.assertEqual(state.time, 0.0)
    
    def test_belt_animation(self):
        """Test BeltAnimation"""
        belt_anim = BeltAnimation(speed_mps=2.0)
        self.assertEqual(belt_anim.speed_mps, 2.0)
        self.assertEqual(belt_anim.texture_offset, 0.0)
        
        # Test update
        result = belt_anim.update(0.016)  # 60 FPS
        self.assertIn('texture_offset', result)
        self.assertIn('material_flow_speed', result)
    
    def test_drive_animation(self):
        """Test DriveAnimation"""
        drive_anim = DriveAnimation(motor_rpm=1450, gearbox_ratio=20.0)
        self.assertEqual(drive_anim.motor_rpm, 1450)
        self.assertEqual(drive_anim.gearbox_ratio, 20.0)
        self.assertEqual(drive_anim.output_rpm, 72.5)  # 1450 / 20
        
        # Test update
        result = drive_anim.update(0.016)
        self.assertIn('motor_rpm', result)
        self.assertIn('output_rpm', result)
        self.assertIn('pulley_rotation', result)
    
    def test_idler_animation(self):
        """Test IdlerAnimation"""
        idler_anim = IdlerAnimation(belt_speed_mps=2.0, idler_diameter_m=0.15)
        self.assertEqual(idler_anim.belt_speed_mps, 2.0)
        self.assertEqual(idler_anim.idler_diameter_m, 0.15)
        
        # Test update
        result = idler_anim.update(0.016)
        self.assertIn('rotation_speed', result)
        self.assertIn('angular_velocity', result)
    
    def test_material_flow_animation(self):
        """Test MaterialFlowAnimation"""
        material_anim = MaterialFlowAnimation(
            flow_rate_tph=100,
            material_density_kg_m3=1600,
            belt_width_m=0.8,
            belt_speed_mps=2.0
        )
        
        self.assertEqual(material_anim.flow_rate_tph, 100)
        self.assertEqual(len(material_anim.particles), 10)  # 100/10
        
        # Test update
        result = material_anim.update(0.016)
        self.assertIn('particles', result)
        self.assertIn('flow_rate', result)
    
    def test_conveyor_animation_engine(self):
        """Test ConveyorAnimationEngine"""
        engine = ConveyorAnimationEngine(self.model_data)
        
        # Test khởi tạo
        self.assertIsNotNone(engine.animations)
        self.assertIn('belt', engine.animations)
        self.assertIn('drive', engine.animations)
        self.assertIn('idler', engine.animations)
        self.assertIn('material_flow', engine.animations)
        
        # Test play/pause
        engine.pause()
        self.assertFalse(engine.state.is_playing)
        
        engine.play()
        self.assertTrue(engine.state.is_playing)
        
        # Test reset
        engine.reset()
        self.assertEqual(engine.state.time, 0.0)
        
        # Test set speed
        engine.set_speed(2.0)
        self.assertEqual(engine.state.speed, 2.0)
        
        # Test update animations
        result = engine.update_all_animations(0.016)
        self.assertIsInstance(result, dict)
        
        # Test get animation data
        data = engine.get_animation_data()
        self.assertIn('state', data)
        self.assertIn('animations', data)
        
        # Test export script
        script = engine.export_animation_script()
        self.assertIsInstance(script, str)
        self.assertIn('ConveyorAnimationController', script)


class TestComponentBuilder(unittest.TestCase):
    """Test Component Builder"""
    
    def setUp(self):
        """Thiết lập dữ liệu test"""
        self.model_data = {
            'belt_system': {
                'geometry': {
                    'width': 0.8,
                    'length': 10.0,
                    'thickness': 0.01,
                    'trough_angle': 20.0
                }
            },
            'drive_system': {
                'motor': {
                    'power_kw': 5.5,
                    'rpm': 1450
                },
                'gearbox': {
                    'ratio': 20.0,
                    'efficiency': 0.95
                },
                'chain_drive': {
                    'sprocket_teeth': {
                        'drive': 20,
                        'driven': 40
                    }
                }
            },
            'support_structure': {
                'carrying_idlers': {
                    'count': 5,
                    'spacing': 2.0,
                    'diameter': 0.15,
                    'trough_angle': 20.0
                },
                'return_idlers': {
                    'count': 3,
                    'spacing': 3.0,
                    'diameter': 0.12
                }
            }
        }
    
    def test_geometry_data(self):
        """Test GeometryData"""
        geo = GeometryData(
            type='box',
            parameters={'width': 1.0, 'height': 1.0, 'depth': 1.0},
            position=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )
        
        self.assertEqual(geo.type, 'box')
        self.assertEqual(geo.parameters['width'], 1.0)
        self.assertEqual(geo.position, (0.0, 0.0, 0.0))
    
    def test_material_data(self):
        """Test MaterialData"""
        material = MaterialData(
            name='Test Material',
            color='#FF0000',
            metalness=0.8,
            roughness=0.2
        )
        
        self.assertEqual(material.name, 'Test Material')
        self.assertEqual(material.color, '#FF0000')
        self.assertEqual(material.metalness, 0.8)
    
    def test_component_3d(self):
        """Test Component3D"""
        geo = GeometryData(type='box', parameters={'width': 1.0, 'height': 1.0, 'depth': 1.0})
        material = MaterialData(name='Test', color='#FF0000')
        
        component = Component3D(
            id='test_component',
            name='Test Component',
            geometry=geo,
            material=material
        )
        
        self.assertEqual(component.id, 'test_component')
        self.assertEqual(component.name, 'Test Component')
        self.assertEqual(component.geometry, geo)
        self.assertEqual(component.material, material)
        
        # Test add child
        child = Component3D(
            id='child',
            name='Child',
            geometry=geo,
            material=material
        )
        component.add_child(child)
        self.assertEqual(len(component.children), 1)
    
    def test_belt_system_builder(self):
        """Test BeltSystemBuilder"""
        builder = BeltSystemBuilder(self.model_data)
        components = builder.build_complete_system()
        
        self.assertIsInstance(components, list)
        self.assertGreater(len(components), 0)
        
        # Kiểm tra có băng tải chính
        belt_component = next((c for c in components if c.id == 'main_belt'), None)
        self.assertIsNotNone(belt_component)
        self.assertEqual(belt_component.user_data['type'], 'belt')
    
    def test_drive_system_builder(self):
        """Test DriveSystemBuilder"""
        builder = DriveSystemBuilder(self.model_data)
        components = builder.build_complete_system()
        
        self.assertIsInstance(components, list)
        self.assertGreater(len(components), 0)
        
        # Kiểm tra có động cơ
        motor_component = next((c for c in components if c.id == 'motor'), None)
        self.assertIsNotNone(motor_component)
        self.assertEqual(motor_component.user_data['type'], 'motor')
    
    def test_support_structure_builder(self):
        """Test SupportStructureBuilder"""
        builder = SupportStructureBuilder(self.model_data)
        components = builder.build_complete_system()
        
        self.assertIsInstance(components, list)
        self.assertGreater(len(components), 0)
        
        # Kiểm tra có khung chính
        frame_component = next((c for c in components if c.id == 'main_frame'), None)
        self.assertIsNotNone(frame_component)
        self.assertEqual(frame_component.user_data['type'], 'main_frame')
    
    def test_component_builder_manager(self):
        """Test ComponentBuilderManager"""
        manager = ComponentBuilderManager(self.model_data)
        components = manager.build_all_components()
        
        self.assertIsInstance(components, list)
        self.assertGreater(len(components), 0)
        
        # Test get components by type
        belt_components = manager.get_components_by_type('belt')
        self.assertGreater(len(belt_components), 0)
        
        # Test get component by id
        component = manager.get_component_by_id('main_belt')
        self.assertIsNotNone(component)
        
        # Test export data
        data = manager.export_components_data()
        self.assertIn('total_count', data)
        self.assertIn('systems', data)
        self.assertIn('components', data)


class TestPhysicsSimulator(unittest.TestCase):
    """Test Physics Simulator"""
    
    def setUp(self):
        """Thiết lập dữ liệu test"""
        self.model_data = {
            'belt_system': {
                'geometry': {
                    'width': 0.8,
                    'length': 10.0,
                    'thickness': 0.01
                }
            },
            'drive_system': {
                'motor': {
                    'power_kw': 5.5,
                    'rpm': 1450,
                    'efficiency': 0.9
                },
                'gearbox': {
                    'ratio': 20.0,
                    'efficiency': 0.95
                }
            },
            'support_structure': {
                'carrying_idlers': {
                    'count': 5,
                    'spacing': 2.0,
                    'diameter': 0.15
                }
            },
            'material_properties': {
                'flow_rate_tph': 100,
                'density_kg_m3': 1600,
                'belt_width_m': 0.8,
                'belt_speed_mps': 2.0
            },
            'belt_speed_mps': 2.0
        }
    
    def test_material_properties(self):
        """Test MaterialProperties"""
        material = MaterialProperties(
            name='Than đá',
            density_kg_m3=1600,
            friction_coefficient=0.6,
            particle_size_mm=25.0
        )
        
        self.assertEqual(material.name, 'Than đá')
        self.assertEqual(material.density_kg_m3, 1600)
        self.assertEqual(material.friction_coefficient, 0.6)
        
        # Test effective density
        effective_density = material.get_effective_density()
        self.assertEqual(effective_density, 1600)  # Không có độ ẩm
        
        # Test angle of repose
        angle_rad = material.get_angle_of_repose_radians()
        self.assertAlmostEqual(angle_rad, 0.5236, places=3)  # 30° = 0.5236 rad
    
    def test_belt_physics(self):
        """Test BeltPhysics"""
        material = MaterialProperties(
            name='Test',
            density_kg_m3=1600,
            friction_coefficient=0.6,
            particle_size_mm=25.0
        )
        
        belt = BeltPhysics(
            width_m=0.8,
            length_m=10.0,
            thickness_m=0.01,
            material=material,
            speed_mps=2.0
        )
        
        self.assertEqual(belt.width_m, 0.8)
        self.assertEqual(belt.length_m, 10.0)
        
        # Test calculate mass
        mass = belt.calculate_mass()
        expected_mass = 0.8 * 10.0 * 0.01 * 1600
        self.assertEqual(mass, expected_mass)
        
        # Test calculate tension force
        tension = belt.calculate_tension_force(100, 15)  # 100kg, 15°
        self.assertGreater(tension, 0)
        
        # Test calculate power required
        power = belt.calculate_power_required(100, 15)
        self.assertGreater(power, 0)
    
    def test_drive_system_physics(self):
        """Test DriveSystemPhysics"""
        drive = DriveSystemPhysics(
            motor_power_kw=5.5,
            motor_rpm=1450,
            gearbox_ratio=20.0,
            gearbox_efficiency=0.95,
            chain_efficiency=0.98,
            pulley_diameter_m=0.4
        )
        
        self.assertEqual(drive.motor_power_kw, 5.5)
        self.assertEqual(drive.motor_rpm, 1450)
        
        # Test calculate output torque
        output_torque = drive.calculate_output_torque()
        self.assertGreater(output_torque, 0)
        
        # Test calculate belt tension capacity
        tension_capacity = drive.calculate_belt_tension_capacity()
        self.assertGreater(tension_capacity, 0)
    
    def test_idler_physics(self):
        """Test IdlerPhysics"""
        material = MaterialProperties(
            name='Test',
            density_kg_m3=1600,
            friction_coefficient=0.6,
            particle_size_mm=25.0
        )
        
        idler = IdlerPhysics(
            diameter_m=0.15,
            length_m=0.8,
            material=material
        )
        
        self.assertEqual(idler.diameter_m, 0.15)
        self.assertEqual(idler.length_m, 0.8)
        
        # Test calculate rolling resistance
        resistance = idler.calculate_rolling_resistance(1000)  # 1000N
        self.assertGreater(resistance, 0)
        
        # Test calculate angular acceleration
        acceleration = idler.calculate_angular_acceleration(10)  # 10Nm
        self.assertGreater(acceleration, 0)
    
    def test_material_flow_physics(self):
        """Test MaterialFlowPhysics"""
        material = MaterialProperties(
            name='Than đá',
            density_kg_m3=1600,
            friction_coefficient=0.6,
            particle_size_mm=25.0
        )
        
        flow = MaterialFlowPhysics(
            material=material,
            flow_rate_tph=100,
            belt_width_m=0.8,
            belt_speed_mps=2.0,
            trough_angle_degrees=20.0
        )
        
        self.assertEqual(flow.flow_rate_tph, 100)
        self.assertEqual(flow.belt_width_m, 0.8)
        
        # Test calculate cross sectional area
        area = flow.calculate_cross_sectional_area()
        self.assertGreater(area, 0)
        
        # Test calculate material height
        height = flow.calculate_material_height()
        self.assertGreater(height, 0)
        
        # Test calculate actual flow rate
        actual_rate = flow.calculate_actual_flow_rate()
        self.assertGreater(actual_rate, 0)
        
        # Test calculate particle trajectory
        x, y, z = flow.calculate_particle_trajectory(1.0, (0.0, 0.1, 0.0))
        self.assertIsInstance(x, float)
        self.assertIsInstance(y, float)
        self.assertIsInstance(z, float)
    
    def test_conveyor_physics_simulator(self):
        """Test ConveyorPhysicsSimulator"""
        simulator = ConveyorPhysicsSimulator(self.model_data)
        
        # Test khởi tạo
        self.assertIsNotNone(simulator.physics_objects)
        self.assertIn('belt', simulator.physics_objects)
        self.assertIn('drive', simulator.physics_objects)
        self.assertIn('idler', simulator.physics_objects)
        self.assertIn('material_flow', simulator.physics_objects)
        
        # Test simulate step
        result = simulator.simulate_step(0.016)
        self.assertIsInstance(result, dict)
        
        # Test get physics summary
        summary = simulator.get_physics_summary()
        self.assertIn('total_mass_kg', summary)
        self.assertIn('total_power_kw', summary)
        self.assertIn('efficiency', summary)
        self.assertIn('safety_factor', summary)
        
        # Test export physics data
        data = simulator.export_physics_data()
        self.assertIsInstance(data, str)
        
        # Test parse JSON
        try:
            data_dict = json.loads(data)
            self.assertIn('objects', data_dict)
            self.assertIn('simulation', data_dict)
            self.assertIn('summary', data_dict)
        except json.JSONDecodeError:
            self.fail("Physics data export should be valid JSON")


if __name__ == '__main__':
    # Chạy tất cả tests
    unittest.main(verbosity=2)
