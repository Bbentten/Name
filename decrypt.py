import json
import time
from cryptography.fernet import Fernet

# Load the key and expiration time from info.json
with open('info.json', 'r') as info_file:
    info_data = json.load(info_file)
    key = info_data.get('key', None)
    key2_str = info_data.get('key2', None)

if key is None or key2_str is None:
    print("Invalid key or key2 in info.json. File will not run.")
else:
    null = int(time.time())
    key = key.encode()
    cipher_suite = Fernet(key)

    # Decrypt key2_str using Fernet
    try:
        key2_bytes = cipher_suite.decrypt(key2_str.encode())
        key2 = int(key2_bytes.decode())
    except Exception as e:
        print("Error decrypting key2:", str(e))
        key2 = None

    if key2 is not None and null > key2:
        print("Key has expired. File will not run.")
    else:
        # Read and decrypt the encrypted content
        with open('main.bin', 'rb') as encrypted_file:
            encrypted_content = encrypted_file.read()
            decrypted_content = cipher_suite.decrypt(encrypted_content)

        # Execute the decrypted content as a Python script
        try:
            exec(decrypted_content)
        except Exception as e:
            print("An error occurred:", str(e))
