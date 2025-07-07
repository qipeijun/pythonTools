import yaml
import os

def load_sm2_public_key(yaml_path='config.yaml') -> str:
    """
    从 YAML 配置文件中加载 SM2 公钥
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"配置文件不存在: {yaml_path}")

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    public_key = config.get('sm2', {}).get('public_key')
    if not public_key:
        raise ValueError("配置文件中未找到 'sm2.public_key'")

    if not public_key.startswith("04") or len(public_key) != 130:
        raise ValueError("SM2 公钥必须是 65 字节未压缩格式（以 04 开头）")

    return public_key
