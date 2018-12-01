import hashlib
import base64
import pyaes

def encrypt(plaintext, password):
    print('on_pre_save password: ' + password)
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    key = m.digest();
    print(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    ciphertext = aes.encrypt(plaintext)
    encrypted_content = base64.b64encode(ciphertext)
    print(encrypted_content)
    return encrypted_content.decode('utf-8')


def decrypt(ciphertext, password):
    ciphertext_string = ciphertext.encode('utf-8');
    ciphertext_string = base64.b64decode(ciphertext_string)
    print('on_pre_save password: ' + password)
    m = hashlib.md5()
    m.update(password.encode('utf-8'))
    key = m.digest();
    print(key)
    aes = pyaes.AESModeOfOperationCTR(key)
    plaintext = aes.decrypt(ciphertext_string)
    return plaintext.decode('utf-8')

a = encrypt('text', '1111')
print(a)
print(decrypt(a, '1111'))
