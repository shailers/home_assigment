from cryptography.fernet import Fernet

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


key = 'Enter key here'
csv_file = 'path_to_your_credentials.csv'  # Path to the credentials CSV file

decrypt_file(csv_file, key)
print(f"File '{csv_file}' has been decrypted.")