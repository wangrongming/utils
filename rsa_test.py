import rsa
from binascii import a2b_hex, b2a_hex

class rsacrypt():

    def __init__(self):
        self.pub_key,self.priv_key = rsa.newkeys(1024) # 生成公钥和私钥
        print(self.pub_key)
        print(self.priv_key)

    def rsa_encrypt(self,text):
        self.encrypt_text = rsa.encrypt(text.encode(), self.pub_key)  # 此时是bytes
        return b2a_hex(self.encrypt_text)  # 转成16进制密文

    def rsa_decrypt(self,text):
        self.decrypt_text = rsa.decrypt(a2b_hex(text), self.priv_key)  # 把16进制密文转成bytes,然后解密
        return self.decrypt_text.decode()


if __name__ == '__main__':
    rs = rsacrypt()
    text = "hello world"
    en_text = rs.rsa_encrypt(text)
    print('密文：',en_text)
    de_text = rs.rsa_decrypt(en_text)
    print('明文：',de_text)


# 密文： b'0ecaa6c11e95d1f720ae22d4d80280aa3f28052072773f608bba2c80ee93dfc9cbd5d47c76134c6fec0c26398807b0836e221fdb28eb20bee2d676ebb2c37671c926e11109aa19e1f1ee9e3f2e37e5218b0452390878a4d2aa557aa278462691ff08eababbd02707d7be8e25f6e6b814a88b107f56f8afbb6b7c4d14e9352808'
# 明文： hello world
