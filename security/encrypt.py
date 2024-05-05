from cryptography.fernet import Fernet
import os

def generate_key():
    """ Generate a key and save it into a file """
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    """ Load the previously generated key """
    return open("secret.key", "rb").read()

def encrypt_file(file_name, key):
    """ Encrypts a file using the provided key """
    f = Fernet(key)
    with open(file_name, "rb") as file:
        # read all file data
        file_data = file.read()
    encrypted_data = f.encrypt(file_data)
    # Write the encrypted file
    with open(file_name, "wb") as file:
        file.write(encrypted_data)

def decrypt_file(file_name, key):
    """ Decrypts a file using the provided key """
    f = Fernet(key)
    with open(file_name, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    # Write the decrypted file
    with open(file_name, "wb") as file:
        file.write(decrypted_data)

# Usage
key = generate_key()  # Generate and save the key
key = load_key()  # Load the previously generated key

csv_file = 'shailers_accessKeys.csv'  # Path to the credentials CSV file

# Encrypt the CSV
encrypt_file(csv_file, key)
print(f"File '{csv_file}' has been encrypted.")
