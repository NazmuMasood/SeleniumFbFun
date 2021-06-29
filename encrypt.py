from Crypto.Cipher import AES

password = 'Taqiuddin1996'
key = 'This is a key123'

def resize_length(string):
    #resizes the String to a size divisible by 16 (needed for this Cipher)
    return string.rjust((len(string) // 16 + 1) * 16)

def encrypt(url, cipher):
    # Converts the string to bytes and encodes them with your Cipher
    return cipher.encrypt(resize_length(url).encode())

def decrypt(text, cipher):
    # Converts the string to bytes and decodes them with your Cipher
    return cipher.decrypt(text).decode().lstrip()


# It is important to use 2 ciphers with the same information, else the system breaks (at least for me)
# Define the Cipher with your data (Encryption Key and IV)
cipher1 = AES.new(key.encode('utf-8'), AES.MODE_CBC, 'This is an IV456'.encode('utf-8'))
cipher2 = AES.new(key.encode('utf-8'), AES.MODE_CBC, 'This is an IV456'.encode('utf-8'))
# print(encrypt("https://booking.com", cipher1))
# print(decrypt(encrypt("https://booking.com", cipher1), cipher2))


#  If you want to have an encoded string in the hex format you..
#   could use the join and the format command in combination.
#For encoding
print('Generating hashed password....\nKey used: '+key)
cipherstring = cipher1.encrypt(resize_length(password).encode())
cipherstring = "".join("{:02x}".format(c) for c in cipherstring)
print('Hashed msg: '+cipherstring)

#For decoding
text = bytes.fromhex(cipherstring)
original_msg = cipher2.decrypt(text).decode().lstrip()
print('Original msg: '+original_msg)



# # Using python 3+ and NONCE
# key1 = b'Sixteen byte key'
# cipher = AES.new(key1, AES.MODE_EAX)
# nonce = cipher.nonce
# ciphertext, tag = cipher.encrypt_and_digest(str.encode(password))
# print(ciphertext) #b'\x068f\xa8d\xae\xfez\t\x8d\xaa\xbe<'
# print(tag)

# key2 = b'Sixteen byte key'
# cipher = AES.new(key2, AES.MODE_EAX, nonce=nonce)
# plaintext = cipher.decrypt(ciphertext)
# try:
#     cipher.verify(tag)
#     print("The message is authentic:", plaintext.decode('utf-8'))
# except ValueError:
#     print("Key incorrect or message corrupted")
