# -*- coding: utf-8 -*-
import pandas as pd
from typing import Tuple, Dict
from .specs import ACTIVE_MATERIAL_DB, ACTIVE_BELT_SPECS

REQUIRED_MAT_COLS = ["name","density","angle_repose","v_max","abrasive","temperature_max","moisture","corrosive"]
REQUIRED_BELT_COLS = ["type","strength","elongation","temp_max","layers","T_allow_Npm"]

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
