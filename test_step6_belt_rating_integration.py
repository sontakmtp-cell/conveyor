#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file cho BƯỚC 6 - Chuẩn hóa nguồn dữ liệu rating đai
Kiểm tra tích hợp giữa specs.py và safety_factors.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_specs_integration():
    """Test tích hợp giữa specs.py và safety_factors.py"""
    print("🧪 Testing BƯỚC 6: Chuẩn hóa nguồn dữ liệu rating đai")
    print("=" * 60)
    
    try:
        # Test import
        print("1. Testing imports...")
        from core.specs import (
            get_valid_ratings_for_belt_type,
            get_rating_parser_for_belt_type,
            validate_belt_rating,
            get_T_allow_Npm_from_rating
        )
        print("✅ Import thành công")
        
        # Test Steel Cord ratings
        print("\n2. Testing Steel Cord ratings...")
        steel_ratings = get_valid_ratings_for_belt_type("steel_cord")
        print(f"   Steel Cord ratings: {len(steel_ratings)} mã")
        print(f"   Ví dụ: {steel_ratings[:3]}...")
        
        # Test Fabric ratings
        print("\n3. Testing Fabric ratings...")
        fabric_ratings = get_valid_ratings_for_belt_type("fabric")
        print(f"   Fabric ratings: {len(fabric_ratings)} mã")
        print(f"   Ví dụ: {fabric_ratings[:5]}...")
        
        # Test validation
        print("\n4. Testing rating validation...")
        assert validate_belt_rating("steel_cord", "ST-1600") == True
        assert validate_belt_rating("fabric", "EP400/4") == True
        assert validate_belt_rating("steel_cord", "INVALID") == False
        print("✅ Validation tests passed")
        
        # Test T_allow calculation
        print("\n5. Testing T_allow calculation...")
        steel_T_allow = get_T_allow_Npm_from_rating("steel_cord", "ST-1600")
        fabric_T_allow = get_T_allow_Npm_from_rating("fabric", "EP400/4")
        print(f"   ST-1600 -> T_allow = {steel_T_allow:.0f} N/m")
        print(f"   EP400/4 -> T_allow = {fabric_T_allow:.0f} N/m")
        
        # Verify calculations
        expected_steel = 1600 * 9.80665 * 100  # ST-1600: 1600 kgf/cm -> N/m
        expected_fabric = 400 * 4 * 1000  # EP400/4: 400 N/mm * 4 lớp -> N/m
        assert abs(steel_T_allow - expected_steel) < 1
        assert abs(fabric_T_allow - expected_fabric) < 1
        print("✅ T_allow calculations correct")
        
        # Test parser functions
        print("\n6. Testing parser functions...")
        parser_steel = get_rating_parser_for_belt_type("steel_cord")
        parser_fabric = get_rating_parser_for_belt_type("fabric")
        assert parser_steel is not None
        assert parser_fabric is not None
        print("✅ Parser functions available")
        
        print("\n🎉 Tất cả tests cho BƯỚC 6 đều PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_engine_integration():
    """Test tích hợp với engine.py"""
    print("\n🔧 Testing engine integration...")
    
    try:
        from core.engine import calculate
        from core.models import ConveyorParameters
        
        # Tạo parameters test
        params = ConveyorParameters(
            calculation_standard="CEMA",
            project_name="Test Project",
            designer="Test Designer",
            client="Test Client",
            location="Test Location",
            material="Than đá",
            density_tpm3=0.9,
            particle_size_mm=25.0,
            angle_repose_deg=35.0,
            material_temp_c=25.0,
            is_abrasive=True,
            is_corrosive=False,
            is_dusty=False,
            Qt_tph=100.0,
            L_m=50.0,
            H_m=10.0,
            inclination_deg=15.0,
            operating_hours=24,
            B_mm=800,
            belt_type="steel_cord",
            belt_thickness_mm=12.0,
            trough_angle_label="35°",
            surcharge_angle_deg=20.0,
            carrying_idler_spacing_m=1.2,
            return_idler_spacing_m=3.0,
            drive_type="Single drive",
            motor_efficiency=0.95,
            gearbox_efficiency=0.96,
            mu_pulley=0.35,
            wrap_deg=180.0,
            Kt_start=1.25,
            ambient_temp_c=25.0,
            humidity_percent=60.0,
            altitude_m=100.0,
            dusty_environment=False,
            corrosive_environment=False,
            explosion_proof=False,
            material_group="A",
            lump_size_ge_30mm=False,
            duty_cycle_minutes=5.0,
            belt_rating_code="ST-1600"
        )
        
        # Gọi hàm calculate trực tiếp
        result = calculate(params)
        
        print(f"   Safety Factor thực: {result.safety_factor:.2f}")
        print(f"   Safety Factor thiết kế: {result.sf_design:.2f}")
        
        if result.sf_design > 0:
            sf_ratio = result.safety_factor / result.sf_design
            print(f"   Tỷ lệ SF thực/SF thiết kế: {sf_ratio:.1%}")
        
        print("✅ Engine integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Engine integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """Test xử lý lỗi"""
    print("\n⚠️ Testing error handling...")
    
    try:
        from core.specs import get_T_allow_Npm_from_rating
        
        # Test invalid belt type
        try:
            get_T_allow_Npm_from_rating("invalid_type", "ST-1600")
            print("❌ Should have raised error for invalid belt type")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly caught error: {e}")
        
        # Test invalid rating
        try:
            get_T_allow_Npm_from_rating("steel_cord", "INVALID-RATING")
            print("❌ Should have raised error for invalid rating")
            return False
        except ValueError as e:
            print(f"   ✅ Correctly caught error: {e}")
        
        print("✅ Error handling tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Bắt đầu test BƯỚC 6 - Chuẩn hóa nguồn dữ liệu rating đai")
    print("=" * 80)
    
    success = True
    success &= test_specs_integration()
    success &= test_engine_integration()
    success &= test_error_handling()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TẤT CẢ TESTS ĐỀU PASSED!")
        print("✅ BƯỚC 6 đã được hoàn thành thành công")
        print("\n📋 Tóm tắt những gì đã hoàn thành:")
        print("   • Tích hợp STEEL_CORD_STANDARD và FABRIC_STANDARD vào specs.py")
        print("   • Thêm các hàm helper để quản lý rating")
        print("   • Cập nhật ACTIVE_BELT_SPECS với rating_codes và parse_rating")
        print("   • Tích hợp đầy đủ vào engine.py")
        print("   • Hỗ trợ parse mã rating ST-1600, EP400/4, etc.")
    else:
        print("❌ Một số tests đã FAILED")
        print("🔧 Cần kiểm tra và sửa lỗi trước khi tiếp tục")
    
    print("\n" + "=" * 80)
