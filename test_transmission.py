#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script cho tính năng truyền động mới
"""

from core.models import ConveyorParameters, ChainSpec, TransmissionSolution
from core.engine import select_transmission
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

def test_chain_data():
    """Test dữ liệu xích"""
    print("\n=== TEST DỮ LIỆU XÍCH ===")
    print(f"Đã tải {len(ACTIVE_CHAIN_SPECS)} loại xích:")
    
    for i, chain in enumerate(ACTIVE_CHAIN_SPECS[:5]):  # Chỉ hiển thị 5 loại đầu
        print(f"  {i+1}. {chain.designation}: bước {chain.pitch_mm} mm, rộng {chain.inner_width_mm} mm")

if __name__ == "__main__":
    test_chain_data()
    test_transmission_selection()
    print("\n=== HOÀN TẤT TEST ===")
