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
    # 1) Running from source tree
    src_path = Path(__file__).resolve().parents[1] / "data" / "accounts.v1.json"
    if src_path.exists():
        return src_path
    # 2) PyInstaller _MEIPASS bundle
    try:
        base_path = Path(getattr(sys, "_MEIPASS"))  # type: ignore[attr-defined]
        bundled = base_path / "data" / "accounts.v1.json"
        if bundled.exists():
            return bundled
    except Exception:
        pass
    # 3) Next to executable (one-dir)
    exe_dir = Path(sys.executable).resolve().parent
    exe_data = exe_dir / "data" / "accounts.v1.json"
    return exe_data


def load_accounts() -> dict:
    p = _accounts_file_path()
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def assigned_account_id() -> str:
    mid = machine_id()
    idx = map_account_index(mid)
    db = load_accounts()["accounts"]
    return db[idx]["id"]


def _argon_verify(password: str, record: dict, params: dict) -> bool:
    # We stored the full Argon2 encoded string (base64-wrapped). Use verify_secret for correctness.
    try:
        stored_encoded = base64.b64decode(record["argon2"])  # bytes of encoded string
        return verify_secret(stored_encoded, password.encode(), Type.ID)
    except Exception:
        return False


def verify_input(username: str, password: str) -> bool:
    db = load_accounts()
    params = db["argon_params"]
    rec = next((x for x in db["accounts"] if x["id"] == username), None)
    if not rec:
        return False
    return _argon_verify(password, rec, params)


# --------- Activation state (HMAC-signed JSON) ---------
def activation_path() -> Path:
    return user_data_root() / "activation.json"


def _sign(payload: bytes) -> str:
    sig = hmac.new(PEPPER, payload, hashlib.sha256).digest()
    return base64.b64encode(sig).decode()


def is_activated() -> Tuple[bool, Optional[dict]]:
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


def write_activation(username: str) -> None:
    data = {"username": username, "machine": machine_id(), "ts": int(time.time())}
    body = json.dumps(data, separators=(",", ":")).encode()
    obj = dict(data)
    obj["_sig"] = _sign(body)
    p = activation_path()
    p.write_text(
        json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8"
    )


