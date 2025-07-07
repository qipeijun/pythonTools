from crypto_utils import sm2_encrypt_data

if __name__ == "__main__":
    plaintext = "hello 国密 with yaml"
    cipher = sm2_encrypt_data(plaintext)
    print("加密结果：", cipher)
