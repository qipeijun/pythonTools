project/

├── config.yaml             # ✅ 公钥配置文件（YAML）
├── config_loader.py        # ✅ 从 YAML 读取配置
├── crypto_utils.py         # ✅ 使用配置的加密工具
├── test.py                 # ⏯️ 测试入口




## 在项目根目录执行：

`pip install -e .`

然后你可以在任何地方这样用：

`from gmcrypto import sm2_encrypt_data`

`from gmcrypto.crypto_utils import sm2_encrypt_data`

