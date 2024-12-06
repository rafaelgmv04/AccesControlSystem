from cryptography.fernet import Fernet

#Function to generate the key
def generate_key():
    # key generation
    key = Fernet.generate_key()

    # string the key in a file
    with open('filekey.key', 'wb') as filekey:
        filekey.write(key)

#Function to read the key
def read_key():

    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()
    return key



#Function to encrypt the file
def encrypt_file():

    key = read_key()
    fernet = Fernet(key)
    # opening the original file to encrypt
    with open('file.txt', 'rb') as file:
        original = file.read()


    encrypted = fernet.encrypt(original)


    with open('fileEnc.txt', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)


# Function to decrypt the file
def decrypt_file():

    key = read_key()
    fernet = Fernet(key)


    with open('fileEnc.txt', 'rb') as enc_file:
        encrypted = enc_file.read()


    decrypted = fernet.decrypt(encrypted)
    return decrypted


def addLicense(license):

    try:
        with open('file.txt', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""


    with open('file.txt', 'a') as f:
        if content.strip():
            f.write("\n" + license)
        else:
            f.write(license)
    encrypt_file()


#Function to verify the license
def verifyLicense(license):
    matriculas = list(decrypt_file().decode("utf-8").split("\n"))
    matriculas = [matricula.strip() for matricula in matriculas]

    if license in matriculas:
        return True
    return False


#Function to get the licenses
def getLicenses():
    try:
        licenses = list(decrypt_file().decode("utf-8").split("\n"))
        return licenses
    except FileNotFoundError:
        return []
    except Exception as e:
        return []





