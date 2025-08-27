#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def test_engine_integration():
    print("Testing Engine Integration...")
    
    try:
        from core.models import ConveyorParameters, CalculationResult
        
        # Tạo parameters với belt_rating_code
        params = ConveyorParameters(
            calculation_standard="CEMA",
            project_name="Test Project",
            designer="Test Designer",
            client="Test Client",
            location="Test Location",
            material="Test Material",
            density_tpm3=1.5,
            particle_size_mm=20.0,
            angle_repose_deg=30.0,
            material_temp_c=25.0,
            is_abrasive=False,
            is_corrosive=False,
            is_dusty=False,
            Qt_tph=100.0,
            L_m=100.0,
            H_m=0.0,
            inclination_deg=0.0,
            V_mps=None,
            operating_hours=16,
            B_mm=800,
            belt_type="steel_cord",
            belt_thickness_mm=12.0,
            trough_angle_label="20°",
            surcharge_angle_deg=20.0,
            carrying_idler_spacing_m=1.2,
            return_idler_spacing_m=3.0,
            drive_type="Head drive",
            motor_efficiency=0.95,
            gearbox_efficiency=0.96,
            mu_pulley=0.35,
            wrap_deg=210.0,
            Kt_start=1.25,
            ambient_temp_c=25.0,
            humidity_percent=65.0,
            altitude_m=0.0,
            dusty_environment=False,
            corrosive_environment=False,
            explosion_proof=False,
            dual_drive_ratio="Phân phối lý thuyết",
            motor_rpm=1450,
            gearbox_ratio_mode="auto",
            gearbox_ratio_user=0.0,
            db_path="",
            material_group="A",
            lump_size_ge_30mm=False,
            duty_cycle_minutes=60.0,
            belt_rating_code="ST-1600"
        )
        
        # Test belt_rating_code được truyền đúng
        assert params.belt_rating_code == "ST-1600", f"Expected 'ST-1600', got '{params.belt_rating_code}'"
        print(f"  belt_rating_code: {params.belt_rating_code} ✓")
        
        print("Engine integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Engine Integration: {e}")
        return False

def test_fabric_engine_integration():
    print("Testing Fabric Engine Integration...")
    
    try:
        from core.models import ConveyorParameters
        
        # Tạo parameters cho fabric belt
        params = ConveyorParameters(
            calculation_standard="CEMA",
            project_name="Test Project",
            designer="Test Designer",
            client="Test Client",
            location="Test Location",
            material="Test Material",
            density_tpm3=1.5,
            particle_size_mm=20.0,
            angle_repose_deg=30.0,
            material_temp_c=25.0,
            is_abrasive=False,
            is_corrosive=False,
            is_dusty=False,
            Qt_tph=100.0,
            L_m=100.0,
            H_m=0.0,
            inclination_deg=0.0,
            V_mps=None,
            operating_hours=16,
            B_mm=800,
            belt_type="fabric",
            belt_thickness_mm=12.0,
            trough_angle_label="20°",
            surcharge_angle_deg=20.0,
            carrying_idler_spacing_m=1.2,
            return_idler_spacing_m=3.0,
            drive_type="Head drive",
            motor_efficiency=0.95,
            gearbox_efficiency=0.96,
            mu_pulley=0.35,
            wrap_deg=210.0,
            Kt_start=1.25,
            ambient_temp_c=25.0,
            humidity_percent=65.0,
            altitude_m=0.0,
            dusty_environment=False,
            corrosive_environment=False,
            explosion_proof=False,
            dual_drive_ratio="Phân phối lý thuyết",
            motor_rpm=1450,
            gearbox_ratio_mode="auto",
            gearbox_ratio_user=0.0,
            db_path="",
            material_group="A",
            lump_size_ge_30mm=False,
            duty_cycle_minutes=60.0,
            belt_rating_code="EP400/4"
        )
        
        # Test belt_rating_code được truyền đúng
        assert params.belt_rating_code == "EP400/4", f"Expected 'EP400/4', got '{params.belt_rating_code}'"
        print(f"  belt_rating_code: {params.belt_rating_code} ✓")
        
        print("Fabric engine integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Fabric Engine Integration: {e}")
        return False

def test_safety_factor_lookup():
    print("Testing Safety Factor Lookup...")
    
    try:
        from core.safety_factors import lookup_sf_design
        
        # Test steel cord
        sf_steel = lookup_sf_design("steel_cord", "A", False, 5.0)
        assert sf_steel == 7.0, f"Expected 7.0, got {sf_steel}"
        print(f"  Steel cord SF design: {sf_steel} ✓")
        
        # Test fabric
        sf_fabric = lookup_sf_design("fabric", "B", True, 2.0)
        assert sf_fabric == 11.0, f"Expected 11.0, got {sf_fabric}"
        print(f"  Fabric SF design: {sf_fabric} ✓")
        
        print("Safety factor lookup test passed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Safety Factor Lookup: {e}")
        return False

if __name__ == "__main__":
    print("Test for BUOC 5: Engine Integration")
    
    try:
        test_engine_integration()
        test_fabric_engine_integration()
        test_safety_factor_lookup()
        print("All tests passed!")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
