import base64
import os
from module_logger import log
from gameaccount import gamereg_uid, gamereg_export, gamereg_import
import json  # 新增：需要JSON模块

# === 关键修改：动态生成绝对路径 ===
current_script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本所在目录（app/tools）
data_dir = os.path.join(current_script_dir, "settings", "accounts")  # 绝对路径：d:/.../settings/accounts
# === 关键修改结束 ===

xor_key = "TI4ftRSDaP63kBxxoLoZ5KpVmRBz00JikzLNweryzZ4wecWJxJO9tbxlH9YDvjAr"

class Account:
    def __init__(self, account_id: int, account_name: str, timestamp: int = 0):
        self.account_id = account_id
        self.account_name = account_name
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.account_id}: {self.account_name}"

def read_all_account_from_files():
    # 原逻辑：自动创建目录（改为绝对路径后仍有效）
    os.makedirs(data_dir, exist_ok=True)
    accounts = []
    for file in os.listdir(data_dir):
        if file.endswith(".json"):
            file_path = os.path.join(data_dir, file)
            timestamp = os.path.getmtime(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                account_id = data["account_id"]
                account_name = data.get("account_name", str(account_id))
                accounts.append(Account(account_id, account_name, timestamp))
    return accounts

accounts = []

try:
    accounts = read_all_account_from_files()
except Exception as e:
    log.error(f"read_all_account_from_files: {e}")

def reload_all_account_from_files():
    global accounts
    accounts.clear()
    for a in read_all_account_from_files():
        accounts.append(a)

import time  # 新增：用于获取当前时间戳

def dump_current_account(gamereg_uid_value: int):  # 修改：增加参数
    # 原逻辑：删除硬编码的 gamereg_uid_value = int，改为使用传入的参数
    if gamereg_uid_value is None:
        log.warning("No account found (dump)")
        return
    
    json_file = os.path.join(data_dir, f"{gamereg_uid_value}.json")
    # 修复：首次保存时文件不存在，用当前时间戳替代
    timestamp = int(time.time()) if not os.path.exists(json_file) else int(os.path.getmtime(json_file))
    
    json_data = {
        "account_id": gamereg_uid_value,
        "account_name": str(gamereg_uid_value),  # 默认名称为ID
        "timestamp": timestamp
    }
    
    # 保存为JSON文件
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    reload_all_account_from_files()

def save_account_name(account_id: int, account_name: str):
    # 原逻辑：写.name文件 → 修改为更新JSON中的account_name字段
    json_file = os.path.join(data_dir, f"{account_id}.json")
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Account {account_id} not found (save name)")
    
    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["account_name"] = account_name  # 更新名称
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)  # 覆盖写入
    
    reload_all_account_from_files()

def save_acc_and_pwd(account_id: int, account_name: str, account_pass: str):
    # 原逻辑：写.acc文件 → 修改为更新JSON中的加密密码字段
    encrypted_text = xor_encrypt_to_base64(account_name + "," + account_pass)
    json_file = os.path.join(data_dir, f"{account_id}.json")
    
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Account {account_id} not found (save pwd)")
    
    with open(json_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["encrypted_credentials"] = encrypted_text  # 新增加密密码字段
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)  # 覆盖写入

def load_acc_and_pwd(account_id: int) -> tuple[str, str]:
    # 原逻辑：读.acc文件 → 修改为从JSON中读取加密密码字段
    json_file = os.path.join(data_dir, f"{account_id}.json")
    if not os.path.exists(json_file):
        return None, None
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        encrypted_text = data.get("encrypted_credentials")
        if not encrypted_text:
            return None, None
        
        decrypted_text = xor_decrypt_from_base64(encrypted_text)
        return decrypted_text.split(",")

def delete_account(account_id: int):
    # 原逻辑：删除.reg/.name/.acc → 修改为删除JSON文件
    json_file = os.path.join(data_dir, f"{account_id}.json")
    if os.path.exists(json_file):
        os.remove(json_file)
    reload_all_account_from_files()

def auto_renewal_account():
    """更新保存的账户（改为检查JSON文件）"""
    try:
        gamereg_uid_value = int
        if gamereg_uid_value is None:
            return
        # 关键修改：检查JSON文件是否存在（原检查.reg）
        if os.path.exists(os.path.join(data_dir, f"{gamereg_uid_value}.json")):
            dump_current_account()
    except Exception as e:
        log.error(f"auto_renewal_account: {e}")

def import_account(account_id: int):
    auto_renewal_account()
    gamereg_uid_value = int
    if gamereg_uid_value == account_id:
        return
    # 关键修改：使用JSON文件路径（原.reg）
    json_file = os.path.join(data_dir, f"{account_id}.json")
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"Account {account_id} not found (load)")
    gamereg_import(json_file)  # 假设gamereg_import支持JSON导入

# 删除重复的旧函数（基于.name/.acc的版本）
# >>> def save_account_name(account_id: int, account_name: str):
# >>>     name_file = os.path.join(data_dir, f"{account_id}.name")
# >>>     with open(name_file, "w") as f:
# >>>         f.write(account_name)
# >>>     reload_all_account_from_files()

# >>> def save_acc_and_pwd(account_id: int, account_name: str, account_pass: str):
# >>>     encrypted_text = xor_encrypt_to_base64(account_name + "," + account_pass)
# >>>     name_file = os.path.join(data_dir, f"{account_id}.acc")
# >>>     with open(name_file, "w") as f:
# >>>         f.write(encrypted_text)

# >>> def load_acc_and_pwd(account_id: int) -> tuple[str, str]:
# >>>     name_file = os.path.join(data_dir, f"{account_id}.acc")
# >>>     if not os.path.exists(name_file):
# >>>         return None, None
# >>>     with open(name_file, "r") as f:
# >>>         encrypted_text = f.read().strip()
# >>>     decrypted_text = xor_decrypt_from_base64(encrypted_text)
# >>>     return decrypted_text.split(",")

def load_to_account(account_id: int) -> bool:
    """
    将游戏账号切换到account_id
    return True: 切换成功且需要重新加载游戏
    return False: 不需要重新加载游戏
    抛出异常: 切换失败，账号不存在
    """
    gamereg_uid_value = int
    if gamereg_uid_value != None and gamereg_uid_value == account_id:
        return False
    import_account(account_id)
    return True

#def save_acc_and_pwd(account_id: int, account_name: str, account_pass: str):
    #encrypted_text = xor_encrypt_to_base64(account_name + "," + account_pass)
    #name_file = os.path.join(data_dir, f"{account_id}.acc")
    #with open(name_file, "w") as f:
        #f.write(encrypted_text)

#def load_acc_and_pwd(account_id: int) -> tuple[str, str]:
    #name_file = os.path.join(data_dir, f"{account_id}.acc")
    #if not os.path.exists(name_file):
        #return None, None
    #with open(name_file, "r") as f:
        #encrypted_text = f.read().strip()
    #decrypted_text = xor_decrypt_from_base64(encrypted_text)
    #return decrypted_text.split(",")

def xor_encrypt_to_base64(plaintext: str) -> str:
    secret_key = xor_key
    plaintext_bytes = plaintext.encode('utf-8')
    key_bytes = secret_key.encode('utf-8')

    encrypted_bytes = bytearray()
    for i in range(len(plaintext_bytes)):
        byte_plaintext = plaintext_bytes[i]
        byte_key = key_bytes[i % len(key_bytes)]
        encrypted_byte = byte_plaintext ^ byte_key
        encrypted_bytes.append(encrypted_byte)

    base64_encoded = base64.b64encode(encrypted_bytes).decode('utf-8')
    return base64_encoded

def xor_decrypt_from_base64(encrypted_base64: str) -> str:
    secret_key = xor_key
    encrypted_bytes = base64.b64decode(encrypted_base64.encode('utf-8'))
    key_bytes = secret_key.encode('utf-8')

    decrypted_bytes = bytearray()
    for i in range(len(encrypted_bytes)):
        byte_encrypted = encrypted_bytes[i]
        byte_key = key_bytes[i % len(key_bytes)]
        decrypted_byte = byte_encrypted ^ byte_key
        decrypted_bytes.append(decrypted_byte)

    decrypted_str = decrypted_bytes.decode('utf-8')
    return decrypted_str




if __name__ == "__main__":
    # 1. 初始化：加载所有已保存的账号
    print("初始化账号列表...")
    reload_all_account_from_files()
    print("当前保存的账号：", [str(acc) for acc in accounts])

    # 2. 保存当前游戏账号（用户输入UID版本）
    print("\n尝试保存当前游戏账号...")
    try:
        # 新增：用户输入UID
        gamereg_uid_value = int(input("请输入要保存的游戏账号UID(数字):"))
        dump_current_account(gamereg_uid_value)  # 传递用户输入的值
        print("当前账号已保存，刷新后账号列表：", [str(acc) for acc in accounts])
    except ValueError:
        print("错误:请输入有效的整数UID")
    except Exception as e:
        print(f"保存失败：{e}")

    # 3. 为账号添加自定义名称（用户输入示例）
    print(f"\n为账号设置自定义名称...")
    # 新增：用户输入账号ID和名称
    test_account_id = int(input("请输入需要设置名称的账号ID(数字0)"))  # 输入ID并转为整数
    user_input_account_name = input("请输入该账号的自定义名称：")
    print(f"\n为账号 {test_account_id} 设置名称...")
    save_account_name(test_account_id, user_input_account_name)
    print("名称保存后，账号信息：", [str(acc) for acc in accounts if acc.account_id == test_account_id])

    # 4. 保存加密的账号密码（用户输入示例）
    print(f"\n保存账号 {test_account_id} 的账号和密码...")
    # 新增：用户手动输入账号名和密码
    user_input_name = input("请输入需要保存的账号：")
    user_input_pass = input("请输入需要保存的密码：")
    save_acc_and_pwd(test_account_id, user_input_name, user_input_pass)  # 使用用户输入的值

    # 5. 读取加密的账号密码
    print(f"\n读取账号 {test_account_id} 的密码...")
    name, pwd = load_acc_and_pwd(test_account_id)
    print(f"解密后的账号信息： 用户名={name}, 密码={pwd}")

    # 6. 切换到指定账号（需确保该账号已保存 .reg 文件）
    target_account_id = gamereg_uid_value # 需替换为实际存在的账号 ID
    print(f"\n尝试切换到账号 {target_account_id}...")
    try:
        need_reload = load_to_account(target_account_id)
        print(f"切换结果：{'需要重新加载游戏' if need_reload else '无需重新加载'}")
    except FileNotFoundError as e:
        print(f"切换失败：{e}")


