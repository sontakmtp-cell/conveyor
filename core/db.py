# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
from typing import Tuple, Dict
from .specs import ACTIVE_MATERIAL_DB, ACTIVE_BELT_SPECS
from .security import encryption
from .utils.paths import resource_path

REQUIRED_MAT_COLS = ["name","density","angle_repose","v_max","abrasive","temperature_max","moisture","corrosive"]
REQUIRED_BELT_COLS = ["type","strength","elongation","temp_max","layers","T_allow_Npm"]

class AccountsManager:
    """Quản lý tài khoản người dùng với mã hóa"""
    
    def __init__(self):
        self.db_path = resource_path("data/accounts.v1.json")
        self.accounts = {}
        self.load_accounts()
    
    def load_accounts(self):
        """Tải danh sách tài khoản từ file đã mã hóa"""
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    encrypted_data = f.read()
                
                # Giải mã dữ liệu
                self.accounts = encryption.decrypt_data(encrypted_data) or {}
            else:
                self.accounts = {}
                self.save_accounts()
        except Exception as e:
            try:
                print(f"Lỗi tải tài khoản: {e}")
            except UnicodeEncodeError:
                print(f"Error loading accounts: {e}".encode('ascii', 'replace').decode('ascii'))
            self.accounts = {}
    
    def save_accounts(self):
        """Lưu danh sách tài khoản với mã hóa"""
        try:
            # Tạo thư mục nếu chưa có
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Mã hóa dữ liệu trước khi lưu
            encrypted_data = encryption.encrypt_data(self.accounts)
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Lỗi lưu tài khoản: {e}")
            return False
    
    def add_account(self, username: str, password: str, role: str = "user"):
        """Thêm tài khoản mới"""
        self.accounts[username] = {
            "password": password,
            "role": role,
            "created_at": str(pd.Timestamp.now())
        }
        return self.save_accounts()
    
    def verify_account(self, username: str, password: str) -> bool:
        """Xác thực tài khoản"""
        if username in self.accounts:
            return self.accounts[username]["password"] == password
        return False
    
    def get_account_role(self, username: str) -> str:
        """Lấy vai trò của tài khoản"""
        if username in self.accounts:
            return self.accounts[username].get("role", "user")
        return "guest"
    
    def remove_account(self, username: str) -> bool:
        """Xóa tài khoản"""
        if username in self.accounts:
            del self.accounts[username]
            return self.save_accounts()
        return False

# Instance mặc định để sử dụng trong toàn bộ ứng dụng
accounts_manager = AccountsManager()

def load_database(path: str) -> Tuple[Dict, Dict, str]:
    """
    Đọc Excel/CSV. Sheet/tab/CSV cần các cột bắt buộc như trên.
    - Nếu Excel: sheet 'materials', 'belts'
    - Nếu CSV: dùng tiền tố materials_*.csv và belts_*.csv lành mạnh hơn, nhưng nếu chỉ 1 file thì coi như materials.
    """
    if path.lower().endswith((".xlsx",".xls")):
        mats = pd.read_excel(path, sheet_name="materials")
        belts = pd.read_excel(path, sheet_name="belts")
    else:
        # CSV đơn lẻ: coi như materials
        mats = pd.read_csv(path)
        belts = pd.DataFrame(columns=REQUIRED_BELT_COLS)

    def _validate(df, req):
        missing = [c for c in req if c not in df.columns]
        if missing:
            raise ValueError(f"Thiếu cột: {', '.join(missing)}")

    _validate(mats, REQUIRED_MAT_COLS)
    if not belts.empty:
        _validate(belts, REQUIRED_BELT_COLS)

    mat_db = {}
    for _, row in mats.iterrows():
        name = str(row["name"]).strip()
        mat_db[name] = {
            "density": float(row["density"]),
            "angle_repose": float(row["angle_repose"]),
            "v_max": float(row["v_max"]),
            "abrasive": str(row["abrasive"]),
            "temperature_max": float(row["temperature_max"]),
            "moisture": str(row["moisture"]),
            "corrosive": bool(row["corrosive"]),
        }

    belt_db = {}
    if not belts.empty:
        for _, row in belts.iterrows():
            name = str(row["type"]).strip()
            layers = row["layers"]
            if isinstance(layers, str):
                layers = [int(x) for x in layers.replace("[","").replace("]","").split(",") if x.strip()]
            belt_db[name] = {
                "strength": float(row["strength"]),
                "elongation": float(row["elongation"]),
                "temp_max": float(row["temp_max"]),
                "layers": layers,
                "T_allow_Npm": float(row["T_allow_Npm"]),
            }

    # Ghi đè runtime
    ACTIVE_MATERIAL_DB.clear()
    ACTIVE_MATERIAL_DB.update(mat_db)
    if belt_db:
        ACTIVE_BELT_SPECS.clear()
        ACTIVE_BELT_SPECS.update(belt_db)

    report = f"Đã nạp {len(mat_db)} vật liệu và {len(belt_db)} loại băng từ: {path}"
    return ACTIVE_MATERIAL_DB, ACTIVE_BELT_SPECS, report
