import base64
from gmssl import sm2
from config_loader import load_sm2_public_key

def sm2_encrypt_data(data: str, yaml_path='config.yaml') -> str:
    """
    使用配置文件中的 SM2 公钥进行加密，返回 Base64 编码的密文
    :param data: 明文字符串
    :param yaml_path: YAML 配置路径
    :return: base64 编码密文
    """
    public_key = load_sm2_public_key(yaml_path)
    sm2_crypt = sm2.CryptSM2(public_key=public_key, private_key='')
    encrypted_bytes = sm2_crypt.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted_bytes).decode('utf-8')
