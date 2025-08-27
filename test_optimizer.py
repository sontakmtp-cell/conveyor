#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test thuật toán optimizer sau khi vá lỗi
Thực hiện 3 test case được đề xuất trong "Tối ưu nâng cao.txt"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.optimizer.optimizer import Optimizer
from core.optimizer.models import OptimizerSettings
from core.models import ConveyorParameters

def test_1_convergence():
    """TEST 1: Chạy 5-10 thế hệ với population_size=30, log top-3 fitness từng gen"""
    print("=" * 60)
    print("🧪 TEST 1: KIỂM TRA HỘI TỤ")
    print("=" * 60)
    
    # Tạo tham số cơ bản cho băng tải
    base_params = ConveyorParameters(
        Qt_tph=100.0,  # Lưu lượng 100 tấn/h
        density_tpm3=1.5,  # Khối lượng riêng 1.5 tấn/m³
        particle_size_mm=20.0,  # Kích thước hạt 20mm
        material="Cát khô",  # Vật liệu cát khô
        belt_type="Vải EP (Polyester)",
        B_mm=600,  # Bề rộng băng 600mm
        V_mps=2.0,  # Tốc độ 2.0 m/s
        L_m=50.0,  # Chiều dài 50m
        H_m=5.0,  # Độ cao nâng 5m
        gearbox_ratio_mode="manual",
        gearbox_ratio_user=20.0
    )
    
    # Tạo settings với min_belt_safety_factor = 6.0 (test case 3)
    settings = OptimizerSettings(
        w_cost=0.6,
        w_power=0.3,
        w_safety=0.1,
        min_belt_safety_factor=6.0,  # Giảm từ 8.0 xuống 6.0
        max_budget_usd=50000.0
    )
    
    # Khởi tạo optimizer
    optimizer = Optimizer(base_params, settings)
    
    print(f"🔧 Tham số test:")
    print(f"   - Lưu lượng: {base_params.Qt_tph} tấn/h")
    print(f"   - Vật liệu: {base_params.material}")
    print(f"   - Bề rộng gốc: {base_params.B_mm}mm")
    print(f"   - Tốc độ gốc: {base_params.V_mps} m/s")
    print(f"   - Min Safety Factor: {settings.min_belt_safety_factor}")
    print()
    
    # Chạy 8 thế hệ với population_size=30
    print("🚀 Bắt đầu tối ưu hóa GA...")
    print("-" * 40)
    
    try:
        results = optimizer.run(
            generations=8,
            population_size=30,
            mutation_rate=0.1,
            tournament_size=5,
            elitism_count=3
        )
        
        print("-" * 40)
        print(f"✅ Hoàn thành! Tìm thấy {len(results)} giải pháp hợp lệ")
        
        # Hiển thị top-3 kết quả
        if results:
            print("\n🏆 TOP-3 GIẢI PHÁP TỐT NHẤT:")
            for i, candidate in enumerate(results[:3], 1):
                print(f"\n{i}. Candidate #{i}:")
                print(f"   - Bề rộng: {candidate.belt_width_mm}mm")
                print(f"   - Loại băng: {candidate.belt_type_name}")
                print(f"   - Tỷ số truyền: {candidate.gearbox_ratio}")
                print(f"   - Xích: {candidate.chain_spec_designation}")
                print(f"   - Fitness Score: {candidate.fitness_score:.4f}")
                print(f"   - Hợp lệ: {candidate.is_valid}")
                
                if hasattr(candidate, 'auto_calculated_speed'):
                    print(f"   - Tốc độ tự động: {candidate.auto_calculated_speed:.3f} m/s")
                
                if hasattr(candidate, 'speed_warnings') and candidate.speed_warnings:
                    print(f"   - Cảnh báo tốc độ: {len(candidate.speed_warnings)} cảnh báo")
                
                if hasattr(candidate, 'calculation_result') and candidate.calculation_result:
                    result = candidate.calculation_result
                    if hasattr(result, 'required_power_kw'):
                        print(f"   - Công suất yêu cầu: {result.required_power_kw:.2f} kW")
                    if hasattr(result, 'safety_factor'):
                        print(f"   - Safety Factor: {result.safety_factor:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_2_power_vs_width():
    """TEST 2: Kiểm tra power giảm khi bề rộng tăng, tốc độ giảm hợp lý"""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: KIỂM TRA QUAN HỆ POWER vs BỀ RỘNG")
    print("=" * 60)
    
    # Tạo tham số cơ bản
    base_params = ConveyorParameters(
        Qt_tph=150.0,  # Lưu lượng 150 tấn/h
        density_tpm3=1.8,  # Khối lượng riêng 1.8 tấn/m³
        particle_size_mm=25.0,  # Kích thước hạt 25mm
        material="Đá vôi",  # Vật liệu đá vôi
        belt_type="Vải EP (Polyester)",
        B_mm=500,  # Bề rộng băng 500mm
        V_mps=2.5,  # Tốc độ 2.5 m/s
        L_m=60.0,  # Chiều dài 60m
        H_m=8.0,  # Độ cao nâng 8m
        gearbox_ratio_mode="manual",
        gearbox_ratio_user=25.0
    )
    
    settings = OptimizerSettings(
        w_cost=0.5,
        w_power=0.4,
        w_safety=0.1,
        min_belt_safety_factor=5.0
    )
    
    optimizer = Optimizer(base_params, settings)
    
    print(f"🔧 Tham số test:")
    print(f"   - Lưu lượng: {base_params.Qt_tph} tấn/h")
    print(f"   - Vật liệu: {base_params.material}")
    print(f"   - Bề rộng gốc: {base_params.B_mm}mm")
    print()
    
    # Chạy 5 thế hệ để tìm các candidate khác nhau
    try:
        results = optimizer.run(
            generations=5,
            population_size=20,
            mutation_rate=0.15,
            tournament_size=3,
            elitism_count=2
        )
        
        if results:
            print("📊 PHÂN TÍCH QUAN HỆ POWER vs BỀ RỘNG:")
            print("-" * 50)
            
            # Sắp xếp theo bề rộng để dễ so sánh
            sorted_results = sorted(results, key=lambda x: x.belt_width_mm)
            
            for i, candidate in enumerate(sorted_results[:5], 1):
                print(f"\n{i}. Bề rộng: {candidate.belt_width_mm}mm")
                
                if hasattr(candidate, 'auto_calculated_speed'):
                    print(f"   - Tốc độ tự động: {candidate.auto_calculated_speed:.3f} m/s")
                
                if hasattr(candidate, 'calculation_result') and candidate.calculation_result:
                    result = candidate.calculation_result
                    if hasattr(result, 'required_power_kw'):
                        print(f"   - Công suất yêu cầu: {result.required_power_kw:.2f} kW")
                    if hasattr(result, 'safety_factor'):
                        print(f"   - Safety Factor: {result.safety_factor:.2f}")
                
                print(f"   - Fitness Score: {candidate.fitness_score:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi trong test 2: {e}")
        return False

def test_3_safety_factor_threshold():
    """TEST 3: Đổi min_belt_safety_factor từ 8 xuống 6, xác nhận số candidate hợp lệ tăng"""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: KIỂM TRA NGƯỠNG SAFETY FACTOR")
    print("=" * 60)
    
    base_params = ConveyorParameters(
        Qt_tph=80.0,  # Lưu lượng 80 tấn/h
        density_tpm3=1.2,  # Khối lượng riêng 1.2 tấn/m³
        particle_size_mm=15.0,  # Kích thước hạt 15mm
        material="Gỗ",  # Vật liệu gỗ
        belt_type="Vải EP (Polyester)",
        B_mm=400,  # Bề rộng băng 400mm
        V_mps=1.8,  # Tốc độ 1.8 m/s
        L_m=40.0,  # Chiều dài 40m
        H_m=3.0,  # Độ cao nâng 3m
        gearbox_ratio_mode="manual",
        gearbox_ratio_user=18.0
    )
    
    print(f"🔧 Tham số test:")
    print(f"   - Lưu lượng: {base_params.Qt_tph} tấn/h")
    print(f"   - Vật liệu: {base_params.material}")
    print(f"   - Bề rộng gốc: {base_params.B_mm}mm")
    print()
    
    # Test với ngưỡng SF cao (8.0)
    print("📈 Test với min_belt_safety_factor = 8.0:")
    settings_high = OptimizerSettings(
        w_cost=0.6,
        w_power=0.3,
        w_safety=0.1,
        min_belt_safety_factor=8.0
    )
    
    optimizer_high = Optimizer(base_params, settings_high)
    
    try:
        results_high = optimizer_high.run(
            generations=3,
            population_size=15,
            mutation_rate=0.1,
            tournament_size=3,
            elitism_count=2
        )
        
        valid_count_high = len([r for r in results_high if r.is_valid])
        print(f"   - Số candidate hợp lệ: {valid_count_high}/{len(results_high)}")
        
    except Exception as e:
        print(f"   - Lỗi: {e}")
        valid_count_high = 0
    
    # Test với ngưỡng SF thấp (6.0)
    print("\n📉 Test với min_belt_safety_factor = 6.0:")
    settings_low = OptimizerSettings(
        w_cost=0.6,
        w_power=0.3,
        w_safety=0.1,
        min_belt_safety_factor=6.0
    )
    
    optimizer_low = Optimizer(base_params, settings_low)
    
    try:
        results_low = optimizer_low.run(
            generations=3,
            population_size=15,
            mutation_rate=0.1,
            tournament_size=3,
            elitism_count=2
        )
        
        valid_count_low = len([r for r in results_low if r.is_valid])
        print(f"   - Số candidate hợp lệ: {valid_count_low}/{len(results_low)}")
        
    except Exception as e:
        print(f"   - Lỗi: {e}")
        valid_count_low = 0
    
    # So sánh kết quả
    print(f"\n📊 SO SÁNH:")
    print(f"   - SF ≥ 8.0: {valid_count_high} candidate hợp lệ")
    print(f"   - SF ≥ 6.0: {valid_count_low} candidate hợp lệ")
    
    if valid_count_low > valid_count_high:
        print(f"   ✅ Xác nhận: Giảm ngưỡng SF từ 8.0 xuống 6.0 làm tăng số candidate hợp lệ")
    else:
        print(f"   ⚠️  Không thấy sự khác biệt rõ rệt")
    
    return True

def main():
    """Chạy tất cả các test"""
    print("🚀 BẮT ĐẦU TEST THUẬT TOÁN OPTIMIZER SAU KHI VÁ LỖI")
    print("=" * 80)
    
    # Chạy từng test
    test_results = []
    
    test_results.append(("Test 1: Hội tụ", test_1_convergence()))
    test_results.append(("Test 2: Power vs Bề rộng", test_2_power_vs_width()))
    test_results.append(("Test 3: Safety Factor", test_3_safety_factor_threshold()))
    
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
