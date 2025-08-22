#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho tính năng truyền động mới
"""

from core.models import ConveyorParameters, ChainSpec, TransmissionSolution
from core.engine import select_transmission, calculate
from core.specs import ACTIVE_CHAIN_SPECS

def test_transmission_selection():
    """Test hàm select_transmission"""
    print("=== TEST TRUYỀN ĐỘNG ===")
    
    # Test case 1: Vận tốc 2.5 m/s, puly 500mm, động cơ 1450 rpm
    print("\nTest case 1:")
    result1 = select_transmission(2.5, 500, 1450, ACTIVE_CHAIN_SPECS)
    if result1:
        print(f"✓ Tìm thấy giải pháp:")
        print(f"  - Hộp số: tỉ số truyền {result1.gearbox_ratio}")
        print(f"  - Nhông: {result1.drive_sprocket_teeth} → {result1.driven_sprocket_teeth} răng")
        print(f"  - Xích: {result1.chain_designation} ({result1.chain_pitch_mm} mm)")
        print(f"  - Tổng tỉ số truyền: {result1.total_transmission_ratio:.2f}")
        print(f"  - Vận tốc thực tế: {result1.actual_belt_velocity:.3f} m/s")
        print(f"  - Sai số: {result1.error:.2f}%")
    else:
        print("✗ Không tìm thấy giải pháp")
    
    # Test case 2: Vận tốc 1.8 m/s, puly 400mm, động cơ 2900 rpm
    print("\nTest case 2:")
    result2 = select_transmission(1.8, 400, 2900, ACTIVE_CHAIN_SPECS)
    if result2:
        print(f"✓ Tìm thấy giải pháp:")
        print(f"  - Hộp số: tỉ số truyền {result2.gearbox_ratio}")
        print(f"  - Nhông: {result2.drive_sprocket_teeth} → {result2.driven_sprocket_teeth} răng")
        print(f"  - Xích: {result2.chain_designation} ({result2.chain_pitch_mm} mm)")
        print(f"  - Tổng tỉ số truyền: {result2.total_transmission_ratio:.2f}")
        print(f"  - Vận tốc thực tế: {result2.actual_belt_velocity:.3f} m/s")
        print(f"  - Sai số: {result2.error:.2f}%")
    else:
        print("✗ Không tìm thấy giải pháp")

def test_full_calculation():
    """Test toàn bộ hệ thống tính toán"""
    print("\n=== TEST TOÀN BỘ HỆ THỐNG ===")
    
    # Tạo tham số đơn giản
    params = ConveyorParameters(
        calculation_standard="CEMA",
        project_name="Test Project",
        designer="Test Designer",
        client="Test Client",
        location="Test Location",
        material="Than đá",
        density_tpm3=0.9,
        particle_size_mm=50,
        angle_repose_deg=35,
        material_temp_c=25,
        is_abrasive=True,
        is_corrosive=False,
        is_dusty=True,
        Qt_tph=100,
        L_m=50,
        H_m=5,
        inclination_deg=5,
        V_mps=2.5,
        operating_hours=8000,
        B_mm=800,
        belt_type="Vải EP (Polyester)",
        belt_thickness_mm=12,
        trough_angle_label="35°",
        surcharge_angle_deg=35,
        carrying_idler_spacing_m=1.5,
        return_idler_spacing_m=3.0,
        drive_type="Đơn",
        motor_efficiency=0.95,
        gearbox_efficiency=0.95,
        mu_pulley=0.35,
        wrap_deg=180,
        Kt_start=1.5,
        ambient_temp_c=25,
        humidity_percent=60,
        altitude_m=0,
        dusty_environment=True,
        corrosive_environment=False,
        explosion_proof=False,
        motor_rpm=1450
    )
    
    try:
        # Gọi hàm tính toán chính
        result = calculate(params)
        
        if result.transmission_solution:
            print("✓ Tính toán thành công!")
            t = result.transmission_solution
            print(f"  - Hộp số: tỉ số truyền {t.gearbox_ratio}")
            print(f"  - Nhông: {t.drive_sprocket_teeth} → {t.driven_sprocket_teeth} răng")
            print(f"  - Xích: {t.chain_designation} ({t.chain_pitch_mm} mm)")
            print(f"  - Vận tốc thực tế: {t.actual_belt_velocity:.3f} m/s")
            print(f"  - Sai số: {t.error:.2f}%")
        else:
            print("✗ Không tìm thấy giải pháp truyền động")
            
    except Exception as e:
        print(f"✗ Lỗi khi tính toán: {e}")

def test_chain_data():
    """Test dữ liệu xích"""
    print("\n=== TEST DỮ LIỆU XÍCH ===")
    print(f"Đã tải {len(ACTIVE_CHAIN_SPECS)} loại xích:")
    
    for i, chain in enumerate(ACTIVE_CHAIN_SPECS[:5]):  # Chỉ hiển thị 5 loại đầu
        print(f"  {i+1}. {chain.designation}: bước {chain.pitch_mm} mm, rộng {chain.inner_width_mm} mm")

if __name__ == "__main__":
    test_chain_data()
    test_transmission_selection()
    test_full_calculation()
    print("\n=== HOÀN TẤT TEST ===")
