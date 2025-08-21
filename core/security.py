import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class DataEncryption:
    """Module xử lý mã hóa và giải mã dữ liệu nhạy cảm"""
    
    def __init__(self, master_key=None):
        """Khởi tạo với master key hoặc tạo mới"""
        if master_key is None:
            # Tạo master key mới từ một chuỗi cố định
            master_key = "ConveyorCalculatorAI_2024_Security_Key"
        
        # Tạo salt cố định để đảm bảo tính nhất quán
        salt = b'conveyor_calc_salt_2024'
        
        # Tạo key từ master key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt_data(self, data):
        """Mã hóa dữ liệu"""
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        elif not isinstance(data, str):
            data = str(data)
        
        encrypted = self.cipher.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        """Giải mã dữ liệu"""
        try:
            # Giải mã base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            # Giải mã Fernet
            decrypted = self.cipher.decrypt(encrypted_bytes)
            # Chuyển về string
            decrypted_str = decrypted.decode('utf-8')
            
            # Thử parse JSON
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        except Exception as e:
            try:
                print(f"Lỗi giải mã: {e}")
            except UnicodeEncodeError:
                print(f"Decryption error: {e}".encode('ascii', 'replace').decode('ascii'))
            return None
    
    def encrypt_file(self, file_path, output_path=None):
        """Mã hóa file và lưu vào output_path"""
        if output_path is None:
            output_path = file_path + '.encrypted'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            encrypted_data = self.encrypt_data(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Lỗi mã hóa file {file_path}: {e}")
            return False
    
    def decrypt_file(self, file_path, output_path=None):
        """Giải mã file và lưu vào output_path"""
        if output_path is None:
            output_path = file_path.replace('.encrypted', '')
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_data(encrypted_data)
            
            if isinstance(decrypted_data, dict):
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(decrypted_data, f, ensure_ascii=False, indent=2)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(decrypted_data))
            
            return True
        except Exception as e:
            print(f"Lỗi giải mã file {file_path}: {e}")
            return False

# Instance mặc định để sử dụng trong toàn bộ ứng dụng
encryption = DataEncryption()
