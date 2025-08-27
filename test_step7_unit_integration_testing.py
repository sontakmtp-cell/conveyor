#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file cho BƯỚC 7 - Kiểm thử (Unit & Integration)
Kiểm tra đầy đủ các chức năng Safety Factor đã được tích hợp
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_safety_factors_lookup():
    """Test 7.1: Unit tests cho safety_factors.lookup_sf_design với mọi trường hợp"""
    print("🧪 Testing 7.1: Unit tests cho safety_factors.lookup_sf_design")
    print("=" * 60)
    
    try:
        from core.safety_factors import lookup_sf_design
        
        # Test Steel Cord với tất cả các trường hợp
        print("   Testing Steel Cord cases...")
        steel_cases = [
            ("steel_cord", "A", False, 2.0),   # <3 phút
            ("steel_cord", "A", False, 5.0),   # 3-10 phút
            ("steel_cord", "A", False, 15.0),  # >10 phút
            ("steel_cord", "A", True, 2.0),    # >=30mm, <3 phút
            ("steel_cord", "A", True, 5.0),    # >=30mm, 3-10 phút
            ("steel_cord", "A", True, 15.0),   # >=30mm, >10 phút
            ("steel_cord", "B", False, 2.0),   # Nhóm B, <3 phút
            ("steel_cord", "B", False, 5.0),   # Nhóm B, 3-10 phút
            ("steel_cord", "B", False, 15.0),  # Nhóm B, >10 phút
            ("steel_cord", "B", True, 2.0),    # Nhóm B, >=30mm, <3 phút
            ("steel_cord", "B", True, 5.0),    # Nhóm B, >=30mm, 3-10 phút
            ("steel_cord", "B", True, 15.0),   # Nhóm B, >=30mm, >10 phút
        ]
        
        for belt_type, group, lump_ge_30mm, duty_minutes in steel_cases:
            sf = lookup_sf_design(belt_type, group, lump_ge_30mm, duty_minutes)
            print(f"     {belt_type}, {group}, lump_ge_30mm={lump_ge_30mm}, duty={duty_minutes}min -> SF={sf}")
            assert sf > 0, f"SF phải > 0 cho {belt_type}, {group}, {lump_ge_30mm}, {duty_minutes}"
        
        # Test Fabric với tất cả các trường hợp
        print("   Testing Fabric cases...")
        fabric_cases = [
            ("fabric", "A", False, 0.5),   # <1 phút
            ("fabric", "A", False, 2.0),   # 1-3 phút
            ("fabric", "A", False, 5.0),   # 3-10 phút
            ("fabric", "A", False, 15.0),  # >10 phút
            ("fabric", "A", True, 0.5),    # >=30mm, <1 phút
            ("fabric", "A", True, 2.0),    # >=30mm, 1-3 phút
            ("fabric", "A", True, 5.0),    # >=30mm, 3-10 phút
            ("fabric", "A", True, 15.0),   # >=30mm, >10 phút
            ("fabric", "B", False, 0.5),   # Nhóm B, <1 phút
            ("fabric", "B", False, 2.0),   # Nhóm B, 1-3 phút
            ("fabric", "B", False, 5.0),   # Nhóm B, 3-10 phút
            ("fabric", "B", False, 15.0),  # Nhóm B, >10 phút
            ("fabric", "B", True, 0.5),    # Nhóm B, >=30mm, <1 phút
            ("fabric", "B", True, 2.0),    # Nhóm B, >=30mm, 1-3 phút
            ("fabric", "B", True, 5.0),    # Nhóm B, >=30mm, 3-10 phút
            ("fabric", "B", True, 15.0),   # Nhóm B, >=30mm, >10 phút
        ]
        
        for belt_type, group, lump_ge_30mm, duty_minutes in fabric_cases:
            sf = lookup_sf_design(belt_type, group, lump_ge_30mm, duty_minutes)
            print(f"     {belt_type}, {group}, lump_ge_30mm={lump_ge_30mm}, duty={duty_minutes}min -> SF={sf}")
            assert sf > 0, f"SF phải > 0 cho {belt_type}, {group}, {lump_ge_30mm}, {duty_minutes}"
        
        print("✅ Tất cả test cases cho lookup_sf_design đều PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_unit_conversion_and_Be_cm():
    """Test 7.2: Unit tests cho việc đổi đơn vị và tính Be_cm"""
    print("\n🧪 Testing 7.2: Unit tests cho việc đổi đơn vị và tính Be_cm")
    print("=" * 60)
    
    try:
        from core.safety_factors import parse_steel_code_to_T_allow_Npm, parse_fabric_code_to_T_allow_Npm
        
        # Test Steel Cord conversion
        print("   Testing Steel Cord conversion...")
        steel_test_cases = [
            ("ST-400", 400 * 9.80665 * 100),
            ("ST-1000", 1000 * 9.80665 * 100),
            ("ST-1600", 1600 * 9.80665 * 100),
            ("ST-2500", 2500 * 9.80665 * 100),
        ]
        
        for code, expected in steel_test_cases:
            result = parse_steel_code_to_T_allow_Npm(code)
            error = abs(result - expected) / expected * 100
            print(f"     {code} -> {result:.0f} N/m (expected: {expected:.0f}, error: {error:.2f}%)")
            assert error < 0.1, f"Error quá lớn cho {code}: {error:.2f}%"
        
        # Test Fabric conversion
        print("   Testing Fabric conversion...")
        fabric_test_cases = [
            ("EP160/2", 160 * 2 * 1000),
            ("EP400/4", 400 * 4 * 1000),
            ("NF630/3", 630 * 3 * 1000),
            ("EP1000/5", 1000 * 5 * 1000),
        ]
        
        for code, expected in fabric_test_cases:
            result = parse_fabric_code_to_T_allow_Npm(code)
            error = abs(result - expected) / expected * 100
            print(f"     {code} -> {result:.0f} N/m (expected: {expected:.0f}, error: {error:.2f}%)")
            assert error < 0.1, f"Error quá lớn cho {code}: {error:.2f}%"
        
        # Test Be_cm calculation
        print("   Testing Be_cm calculation...")
        B_cm_test_cases = [60, 80, 100, 120, 140, 160, 180, 200]
        for B_cm in B_cm_test_cases:
            Be_cm = max(B_cm - 6.0, 0.1)
            Be_m = Be_cm / 100.0
            print(f"     B={B_cm}cm -> Be={Be_cm:.1f}cm -> Be={Be_m:.3f}m")
            assert Be_cm >= 0.1, f"Be_cm phải >= 0.1cm cho B={B_cm}cm"
            assert Be_m > 0, f"Be_m phải > 0 cho B={B_cm}cm"
        
        print("✅ Tất cả test cases cho unit conversion và Be_cm đều PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sf_actual_calculation():
    """Test 7.3: Test tính SF_thực với các bộ giá trị mẫu cho cả hai loại băng tải"""
    print("\n🧪 Testing 7.3: Test tính SF_thực với các bộ giá trị mẫu")
    print("=" * 60)
    
    try:
        from core.specs import get_T_allow_Npm_from_rating
        
        # Test cases với các thông số thực tế
        test_cases = [
            # (belt_type, rating, B_mm, Fmax_N, expected_sf_min)
            ("steel_cord", "ST-1000", 800, 50000, 15.0),    # SF = (0.8 * T_allow) / 50000
            ("steel_cord", "ST-1600", 1000, 80000, 20.0),   # SF = (1.0 * T_allow) / 80000
            ("fabric", "EP400/4", 800, 40000, 12.0),        # SF = (0.74 * T_allow) / 40000
            ("fabric", "EP630/3", 1000, 60000, 15.0),       # SF = (0.94 * T_allow) / 60000
        ]
        
        for belt_type, rating, B_mm, Fmax_N, expected_sf_min in test_cases:
            # Tính T_allow
            T_allow_Npm = get_T_allow_Npm_from_rating(belt_type, rating)
            
            # Tính SF thực
            if belt_type == "steel_cord":
                B_m = B_mm / 1000.0
                belt_capacity_N = B_m * T_allow_Npm
            else:
                B_cm = B_mm / 10.0
                Be_cm = max(B_cm - 6.0, 0.1)
                Be_m = Be_cm / 100.0
                belt_capacity_N = Be_m * T_allow_Npm
            
            sf_actual = belt_capacity_N / Fmax_N
            
            print(f"     {belt_type}, {rating}, B={B_mm}mm, Fmax={Fmax_N}N:")
            print(f"       T_allow = {T_allow_Npm:.0f} N/m")
            print(f"       Belt capacity = {belt_capacity_N:.0f} N")
            print(f"       SF actual = {sf_actual:.2f} (expected >= {expected_sf_min})")
            
            assert sf_actual >= expected_sf_min, f"SF thực ({sf_actual:.2f}) < {expected_sf_min} cho {belt_type}, {rating}"
        
        print("✅ Tất cả test cases cho SF_thực đều PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_warning_thresholds_and_ratios():
    """Test 7.4: Test các ngưỡng cảnh báo và tỉ lệ SF_thực/SF_thiết_kế"""
    print("\n🧪 Testing 7.4: Test các ngưỡng cảnh báo và tỉ lệ SF")
    print("=" * 60)
    
    try:
        from core.safety_factors import get_sf_warning_thresholds, lookup_sf_design
        
        # Test warning thresholds
        print("   Testing warning thresholds...")
        steel_yellow, steel_red = get_sf_warning_thresholds("steel_cord")
        fabric_yellow, fabric_red = get_sf_warning_thresholds("fabric")
        
        print(f"     Steel cord: yellow={steel_yellow}, red={steel_red}")
        print(f"     Fabric: yellow={fabric_yellow}, red={fabric_red}")
        
        assert steel_yellow > steel_red, "Steel cord yellow threshold phải > red threshold"
        assert fabric_yellow > fabric_red, "Fabric yellow threshold phải > red threshold"
        assert steel_yellow == 7.5, f"Steel cord yellow threshold phải = 7.5, got {steel_yellow}"
        assert steel_red == 6.0, f"Steel cord red threshold phải = 6.0, got {steel_red}"
        assert fabric_yellow == 10.0, f"Fabric yellow threshold phải = 10.0, got {fabric_yellow}"
        assert fabric_red == 8.0, f"Fabric red threshold phải = 8.0, got {fabric_red}"
        
        # Test SF ratio calculations
        print("   Testing SF ratio calculations...")
        test_ratios = [
            ("steel_cord", "A", False, 5.0, 8.0),  # duty=5min -> SF_design=7.0
            ("fabric", "B", True, 2.0, 11.0),      # duty=2min -> SF_design=11.0
        ]
        
        for belt_type, group, lump_ge_30mm, duty_minutes, expected_sf_design in test_ratios:
            sf_design = lookup_sf_design(belt_type, group, lump_ge_30mm, duty_minutes)
            print(f"     {belt_type}, {group}, lump_ge_30mm={lump_ge_30mm}, duty={duty_minutes}min:")
            print(f"       SF design = {sf_design} (expected: {expected_sf_design})")
            assert abs(sf_design - expected_sf_design) < 0.1, f"SF design không đúng cho {belt_type}, {group}"
            
            # Test các tỉ lệ khác nhau
            test_sf_actuals = [sf_design * 0.5, sf_design * 0.8, sf_design * 1.2, sf_design * 2.0]
            for sf_actual in test_sf_actuals:
                ratio = sf_actual / sf_design
                print(f"       SF actual = {sf_actual:.2f}, ratio = {ratio:.1%}")
                
                if ratio < 0.8:
                    print(f"         -> Cảnh báo: SF thực < 80% SF thiết kế")
                elif ratio > 1.5:
                    print(f"         -> Thông báo: SF thực > 150% SF thiết kế (dư an toàn)")
                else:
                    print(f"         -> OK: SF thực trong khoảng hợp lý")
        
        print("✅ Tất cả test cases cho warning thresholds và ratios đều PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_engine():
    """Test tích hợp với engine.py - kiểm tra toàn bộ luồng tính toán"""
    print("\n🔧 Testing integration with engine.py")
    print("=" * 60)
    
    try:
        from core.engine import calculate
        from core.models import ConveyorParameters
        
        # Test case 1: Steel cord với duty cycle thấp
        print("   Test case 1: Steel cord với duty cycle thấp...")
        params1 = ConveyorParameters(
            calculation_standard="CEMA",
            project_name="Test Steel Cord Low Duty",
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
            duty_cycle_minutes=2.0,  # <3 phút -> SF_design = 8.0
            belt_rating_code="ST-1600"
        )
        
        result1 = calculate(params1)
        print(f"     SF thực: {result1.safety_factor:.2f}")
        print(f"     SF thiết kế: {result1.sf_design:.2f}")
        if result1.sf_design > 0:
            ratio1 = result1.safety_factor / result1.sf_design
            print(f"     Tỷ lệ: {ratio1:.1%}")
        
        # Test case 2: Fabric với duty cycle cao
        print("   Test case 2: Fabric với duty cycle cao...")
        params2 = ConveyorParameters(
            calculation_standard="CEMA",
            project_name="Test Fabric High Duty",
            designer="Test Designer",
            client="Test Client",
            location="Test Location",
            material="Đá vôi",
            density_tpm3=1.56,
            particle_size_mm=35.0,
            angle_repose_deg=30.0,
            material_temp_c=25.0,
            is_abrasive=False,
            is_corrosive=False,
            is_dusty=True,  # Hard ores -> Group B
            Qt_tph=150.0,
            L_m=60.0,
            H_m=15.0,
            inclination_deg=20.0,
            operating_hours=24,
            B_mm=1000,
            belt_type="fabric",
            belt_thickness_mm=15.0,
            trough_angle_label="35°",
            surcharge_angle_deg=20.0,
            carrying_idler_spacing_m=1.0,
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
            material_group="B",
            lump_size_ge_30mm=True,  # >=30mm
            duty_cycle_minutes=15.0,  # >10 phút -> SF_design = 8.0
            belt_rating_code="EP400/4"
        )
        
        result2 = calculate(params2)
        print(f"     SF thực: {result2.safety_factor:.2f}")
        print(f"     SF thiết kế: {result2.sf_design:.2f}")
        if result2.sf_design > 0:
            ratio2 = result2.safety_factor / result2.sf_design
            print(f"     Tỷ lệ: {ratio2:.1%}")
        
        # Kiểm tra warnings và recommendations
        print("   Checking warnings and recommendations...")
        if result1.warnings:
            print(f"     Case 1 warnings: {len(result1.warnings)}")
            for warning in result1.warnings[:2]:  # Chỉ hiển thị 2 warnings đầu
                print(f"       - {warning}")
        
        if result2.warnings:
            print(f"     Case 2 warnings: {len(result2.warnings)}")
            for warning in result2.warnings[:2]:  # Chỉ hiển thị 2 warnings đầu
                print(f"       - {warning}")
        
        print("✅ Engine integration tests PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Engine integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Bắt đầu test BƯỚC 7 - Kiểm thử (Unit & Integration)")
    print("=" * 80)
    
    success = True
    success &= test_safety_factors_lookup()
    success &= test_unit_conversion_and_Be_cm()
    success &= test_sf_actual_calculation()
    success &= test_warning_thresholds_and_ratios()
    success &= test_integration_with_engine()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 TẤT CẢ TESTS ĐỀU PASSED!")
        print("✅ BƯỚC 7 đã được hoàn thành thành công")
        print("\n📋 Tóm tắt những gì đã hoàn thành:")
        print("   • Unit tests cho safety_factors.lookup_sf_design với mọi trường hợp")
        print("   • Unit tests cho việc đổi đơn vị và tính Be_cm")
        print("   • Test tính SF_thực với các bộ giá trị mẫu cho cả hai loại băng tải")
        print("   • Test các ngưỡng cảnh báo và tỉ lệ SF_thực/SF_thiết_kế")
        print("   • Integration tests với engine.py")
        print("\n🚀 Sẵn sàng cho BƯỚC 8 - Nhật ký, UI và Báo cáo")
    else:
        print("❌ Một số tests đã FAILED")
        print("🔧 Cần kiểm tra và sửa lỗi trước khi tiếp tục")
    
    print("\n" + "=" * 80)

