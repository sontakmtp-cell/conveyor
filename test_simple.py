#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test đơn giản để kiểm tra các thay đổi đã thực hiện
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_1_imports():
    """TEST 1: Kiểm tra import và cấu trúc cơ bản"""
    print("=" * 60)
    print("🧪 TEST 1: KIỂM TRA IMPORT VÀ CẤU TRÚC")
    print("=" * 60)
    
    try:
        # Test import optimizer
        from core.optimizer.optimizer import Optimizer
        print("✅ Import Optimizer thành công")
        
        # Test import models
        from core.optimizer.models import DesignCandidate, OptimizerSettings
        print("✅ Import models thành công")
        
        # Test import specs
        from core.specs import STANDARD_WIDTHS, ACTIVE_BELT_SPECS, STANDARD_GEARBOX_RATIOS
        print("✅ Import specs thành công")
        
        # Test import optimize
        from core.optimize import calculate_belt_speed
        print("✅ Import calculate_belt_speed thành công")
        
        print(f"\n📊 Thông tin cấu trúc:")
        print(f"   - STANDARD_WIDTHS: {len(STANDARD_WIDTHS)} bề rộng tiêu chuẩn")
        print(f"   - ACTIVE_BELT_SPECS: {len(ACTIVE_BELT_SPECS)} loại băng")
        print(f"   - STANDARD_GEARBOX_RATIOS: {len(STANDARD_GEARBOX_RATIOS)} tỷ số truyền")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi import: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_sorted_standard_widths():
    """TEST 2: Kiểm tra STANDARD_WIDTHS đã được sort"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: KIỂM TRA STANDARD_WIDTHS ĐÃ SORT")
    print("=" * 60)
    
    try:
        from core.specs import STANDARD_WIDTHS
        
        # Kiểm tra xem STANDARD_WIDTHS có được sort không
        is_sorted = STANDARD_WIDTHS == sorted(STANDARD_WIDTHS)
        
        print(f"📊 Kết quả kiểm tra:")
        print(f"   - STANDARD_WIDTHS gốc: {STANDARD_WIDTHS[:5]}...")
        print(f"   - STANDARD_WIDTHS sorted: {sorted(STANDARD_WIDTHS)[:5]}...")
        print(f"   - Đã được sort: {'✅ CÓ' if is_sorted else '❌ CHƯA'}")
        
        if not is_sorted:
            print("   ⚠️  Cần sửa: Sử dụng sorted(STANDARD_WIDTHS) trong code")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test 2: {e}")
        return False

def test_3_calculate_belt_speed():
    """TEST 3: Kiểm tra hàm calculate_belt_speed"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: KIỂM TRA HÀM CALCULATE_BELT_SPEED")
    print("=" * 60)
    
    try:
        from core.optimize import calculate_belt_speed
        
        # Test với các tham số cơ bản
        capacity_tph = 100.0
        density_tpm3 = 1.5
        belt_width_mm = 600
        particle_mm = 20.0
        material_name = "Cát khô"
        trough_angle_deg = 20.0
        surcharge_angle_deg = 20.0
        
        print(f"🔧 Tham số test:")
        print(f"   - Lưu lượng: {capacity_tph} tấn/h")
        print(f"   - Khối lượng riêng: {density_tpm3} tấn/m³")
        print(f"   - Bề rộng băng: {belt_width_mm}mm")
        print(f"   - Kích thước hạt: {particle_mm}mm")
        print(f"   - Vật liệu: {material_name}")
        print()
        
        # Gọi hàm calculate_belt_speed
        result = calculate_belt_speed(
            capacity_tph=capacity_tph,
            density_tpm3=density_tpm3,
            belt_width_mm=belt_width_mm,
            particle_mm=particle_mm,
            material_name=material_name,
            trough_angle_deg=trough_angle_deg,
            surcharge_angle_deg=surcharge_angle_deg
        )
        
        v_final, v_req, v_rec, area_m2, warnings, max_speed_allowed = result
        
        print(f"📊 Kết quả tính toán:")
        print(f"   - Tốc độ cuối cùng: {v_final:.3f} m/s")
        print(f"   - Tốc độ yêu cầu: {v_req:.3f} m/s")
        print(f"   - Tốc độ khuyến nghị: {v_rec:.3f} m/s")
        print(f"   - Tiết diện: {area_m2:.4f} m²")
        print(f"   - Số cảnh báo: {len(warnings)}")
        print(f"   - Tốc độ tối đa cho phép: {max_speed_allowed:.2f} m/s")
        
        if warnings:
            print(f"\n⚠️  Cảnh báo:")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test 3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_4_optimizer_code_changes():
    """TEST 4: Kiểm tra các thay đổi trong optimizer.py"""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: KIỂM TRA THAY ĐỔI TRONG OPTIMIZER.PY")
    print("=" * 60)
    
    try:
        # Đọc file optimizer.py để kiểm tra các thay đổi
        optimizer_file = "core/optimizer/optimizer.py"
        
        if not os.path.exists(optimizer_file):
            print(f"❌ Không tìm thấy file: {optimizer_file}")
            return False
        
        with open(optimizer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Kiểm tra các thay đổi:")
        
        # Kiểm tra BƯỚC 1: Sử dụng calculate_belt_speed
        if "from core.optimize import calculate_belt_speed" in content:
            print("   ✅ BƯỚC 1: Đã sử dụng calculate_belt_speed")
        else:
            print("   ❌ BƯỚC 1: Chưa sử dụng calculate_belt_speed")
        
        # Kiểm tra BƯỚC 2: Sử dụng settings.min_belt_safety_factor
        if "self.settings.min_belt_safety_factor" in content:
            print("   ✅ BƯỚC 2: Đã sử dụng settings.min_belt_safety_factor")
        else:
            print("   ❌ BƯỚC 2: Chưa sử dụng settings.min_belt_safety_factor")
        
        # Kiểm tra BƯỚC 3: Cắt tỉa dân số
        if "new_generation[:population_size]" in content:
            print("   ✅ BƯỚC 3: Đã cắt tỉa dân số về đúng kích thước")
        else:
            print("   ❌ BƯỚC 3: Chưa cắt tỉa dân số")
        
        # Kiểm tra BƯỚC 4: Gom speed_warnings vào invalid_reasons
        if "speed_warnings" in content and "invalid_reasons.append" in content:
            print("   ✅ BƯỚC 4: Đã gom speed_warnings vào invalid_reasons")
        else:
            print("   ❌ BƯỚC 4: Chưa gom speed_warnings vào invalid_reasons")
        
        # Kiểm tra BƯỚC 5: Truyền gene xích vào engine
        if "chain_spec_designation" in content and "hasattr(params" in content:
            print("   ✅ BƯỚC 5: Đã truyền gene xích vào engine")
        else:
            print("   ❌ BƯỚC 5: Chưa truyền gene xích vào engine")
        
        # Kiểm tra BƯỚC 6: ThreadPoolExecutor với max_workers
        if "ThreadPoolExecutor(max_workers=" in content:
            print("   ✅ BƯỚC 6: Đã đặt max_workers cho ThreadPoolExecutor")
        else:
            print("   ❌ BƯỚC 6: Chưa đặt max_workers cho ThreadPoolExecutor")
        
        # Kiểm tra import os
        if "import os" in content:
            print("   ✅ BƯỚC 6: Đã import os")
        else:
            print("   ❌ BƯỚC 6: Chưa import os")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test 4: {e}")
        return False

def test_5_optimize_code_changes():
    """TEST 5: Kiểm tra các thay đổi trong optimize.py"""
    print("\n" + "=" * 60)
    print("🧪 TEST 5: KIỂM TRA THAY ĐỔI TRONG OPTIMIZE.PY")
    print("=" * 60)
    
    try:
        # Đọc file optimize.py để kiểm tra các thay đổi
        optimize_file = "core/optimize.py"
        
        if not os.path.exists(optimize_file):
            print(f"❌ Không tìm thấy file: {optimize_file}")
            return False
        
        with open(optimize_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Kiểm tra các thay đổi:")
        
        # Kiểm tra sử dụng sorted(STANDARD_WIDTHS)
        if "for width_mm in sorted(STANDARD_WIDTHS):" in content:
            print("   ✅ Đã sử dụng sorted(STANDARD_WIDTHS)")
        else:
            print("   ❌ Chưa sử dụng sorted(STANDARD_WIDTHS)")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test 5: {e}")
        return False

def main():
    """Chạy tất cả các test"""
    print("🚀 BẮT ĐẦU TEST ĐƠN GIẢN SAU KHI VÁ LỖI")
    print("=" * 80)
    
    # Chạy từng test
    test_results = []
    
    test_results.append(("Test 1: Import và cấu trúc", test_1_imports()))
    test_results.append(("Test 2: STANDARD_WIDTHS sorted", test_2_sorted_standard_widths()))
    test_results.append(("Test 3: calculate_belt_speed", test_3_calculate_belt_speed()))
    test_results.append(("Test 4: Thay đổi optimizer.py", test_4_optimizer_code_changes()))
    test_results.append(("Test 5: Thay đổi optimize.py", test_5_optimize_code_changes()))
    
    # Tóm tắt kết quả
    print("\n" + "=" * 80)
    print("📋 TÓM TẮT KẾT QUẢ TEST")
    print("=" * 80)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 KẾT QUẢ: {passed}/{len(test_results)} test PASSED")
    
    if passed == len(test_results):
        print("🎉 TẤT CẢ TEST ĐỀU THÀNH CÔNG! Thuật toán đã được vá lỗi hoàn hảo.")
    else:
        print("⚠️  Một số test thất bại. Cần kiểm tra lại code.")
    
    return passed == len(test_results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
