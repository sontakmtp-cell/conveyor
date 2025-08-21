from __future__ import annotations

import os
import json
import hmac
import hashlib
import base64
import time
from pathlib import Path
import sys
from typing import Tuple, Optional

from argon2.low_level import Type, hash_secret, verify_secret
from platformdirs import user_data_dir


APP_NAME = "Conveyor Calculator 3D"
APP_AUTHOR = "Your Company"

# 32 bytes pepper (hex) – rotate per release if needed
PEPPER = bytes.fromhex(
    "d3f1af5a9c4e1b2d7a67c3b1e59f8a0c4b3d2e1f9a8c7b6d5e4f3a2b1908c7d6"
)


def user_data_root() -> Path:
    p = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    p.mkdir(parents=True, exist_ok=True)
    return p


def machine_id() -> str:
    # Prefer Windows MachineGuid
    try:
        import winreg  # type: ignore

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
        )
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        mid_raw = str(value).strip()
    except Exception:
        # Fallback: hostname + MAC (best-effort)
        host = os.environ.get("COMPUTERNAME", "unknown")
        try:
            mac_text = os.popen("getmac").read()
            mac_digits = "".join(ch for ch in mac_text if ch.isalnum())
            mac = mac_digits[:12]
        except Exception:
            mac = "000000000000"
        mid_raw = f"{host}-{mac}"

    return hashlib.sha256(mid_raw.encode("utf-8")).hexdigest()


def map_account_index(machine_id_hex: str) -> int:
    mac = hmac.new(PEPPER, machine_id_hex.encode(), hashlib.sha256).digest()
    return int.from_bytes(mac, "big") % 1000


def _accounts_file_path() -> Path:
    """Lấy đường dẫn đến file accounts.v1.json với fallback cho PyInstaller"""
    try:
        # Thử import resource_path từ core.utils.paths
        try:
            from core.utils.paths import resource_path
            return Path(resource_path("data/accounts.v1.json"))
        except ImportError:
            pass
        
        # Fallback 1: Running from source tree
        src_path = Path(__file__).resolve().parents[1] / "data" / "accounts.v1.json"
        if src_path.exists():
            return src_path
            
        # Fallback 2: PyInstaller _MEIPASS bundle
        try:
            base_path = Path(getattr(sys, "_MEIPASS", ""))
            if base_path:
                bundled = base_path / "data" / "accounts.v1.json"
                if bundled.exists():
                    return bundled
        except Exception:
            pass
            
        # Fallback 3: Next to executable (one-dir)
        exe_dir = Path(sys.executable).resolve().parent
        exe_data = exe_dir / "data" / "accounts.v1.json"
        if exe_data.exists():
            return exe_data
            
        # Fallback 4: Current working directory
        cwd_data = Path.cwd() / "data" / "accounts.v1.json"
        if cwd_data.exists():
            return cwd_data
            
        # Fallback 5: Relative to script location
        script_dir = Path(__file__).resolve().parent
        script_data = script_dir.parent.parent / "data" / "accounts.v1.json"
        if script_data.exists():
            return script_data
            
        # Nếu không tìm thấy, trả về đường dẫn mặc định
        return Path("data/accounts.v1.json")
        
    except Exception as e:
        print(f"Warning: Error finding accounts file: {e}")
        return Path("data/accounts.v1.json")


def load_accounts() -> dict:
    """Load accounts với xử lý lỗi tốt hơn"""
    try:
        p = _accounts_file_path()
        if not p.exists():
            print(f"Warning: Accounts file not found at {p}")
            # Trả về dữ liệu mặc định nếu không tìm thấy file
            return {
                "accounts": [
                    {
                        "id": "admin",
                        "argon2": "JDJhJDEwJGV4dHJhLmRhdGEkYWRtaW4kYWRtaW4=",
                        "role": "admin"
                    }
                ],
                "argon_params": {
                    "type": "id",
                    "version": 19,
                    "params": {
                        "m": 65536,
                        "t": 3,
                        "p": 1
                    }
                }
            }
        
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading accounts: {e}")
        # Trả về dữ liệu mặc định nếu có lỗi
        return {
            "accounts": [
                {
                    "id": "admin",
                    "argon2": "JDJhJDEwJGV4dHJhLmRhdGEkYWRtaW4kYWRtaW4=",
                    "role": "admin"
                }
            ],
            "argon_params": {
                "type": "id",
                "version": 19,
                "params": {
                    "m": 65536,
                    "t": 3,
                    "p": 1
                }
            }
        }


def assigned_account_id() -> str:
    try:
        mid = machine_id()
        idx = map_account_index(mid)
        db = load_accounts()
        if "accounts" in db and len(db["accounts"]) > 0:
            return db["accounts"][idx % len(db["accounts"])]["id"]
        else:
            return "admin"  # Fallback
    except Exception as e:
        print(f"Error getting assigned account ID: {e}")
        return "admin"  # Fallback


def _argon_verify(password: str, record: dict, params: dict) -> bool:
    # We stored the full Argon2 encoded string (base64-wrapped). Use verify_secret for correctness.
    try:
        stored_encoded = base64.b64decode(record["argon2"])  # bytes of encoded string
        return verify_secret(stored_encoded, password.encode(), Type.ID)
    except Exception:
        return False


def verify_input(username: str, password: str) -> bool:
    try:
        db = load_accounts()
        if "accounts" not in db or "argon_params" not in db:
            print("Warning: Invalid accounts database structure")
            return False
            
        params = db["argon_params"]
        rec = next((x for x in db["accounts"] if x["id"] == username), None)
        if not rec:
            return False
        return _argon_verify(password, rec, params)
    except Exception as e:
        print(f"Error verifying input: {e}")
        return False


# --------- Activation state (HMAC-signed JSON) ---------
def activation_path() -> Path:
    return user_data_root() / "activation.json"


def _sign(payload: bytes) -> str:
    sig = hmac.new(PEPPER, payload, hashlib.sha256).digest()
    return base64.b64encode(sig).decode()


def is_activated() -> Tuple[bool, Optional[dict]]:
    try:
        p = activation_path()
        if not p.exists():
            return (False, None)
        raw = p.read_bytes()
        try:
            obj = json.loads(raw.decode("utf-8"))
            sig = obj.get("_sig", "")
            body = json.dumps({k: v for k, v in obj.items() if k != "_sig"}, separators=(",", ":")).encode()
            if not hmac.compare_digest(sig, _sign(body)):
                return (False, None)
            return (True, obj)
        except Exception:
            return (False, None)
    except Exception as e:
        print(f"Error checking activation: {e}")
        return (False, None)


def write_activation(username: str) -> None:
    try:
        data = {"username": username, "machine": machine_id(), "ts": int(time.time())}
        body = json.dumps(data, separators=(",", ":")).encode()
        obj = dict(data)
        obj["_sig"] = _sign(body)
        p = activation_path()
        p.write_text(
            json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
        )
    except Exception as e:
        print(f"Error writing activation: {e}")


