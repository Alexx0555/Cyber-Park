import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
FERNET_KEY = os.getenv("FERNET_SECRET_KEY")
fernet = Fernet(FERNET_KEY)

def encpwd(pwd):
    return fernet.encrypt(pwd.encode()).decode()

def decpwd(encr_pwd):
    return fernet.decrypt(encr_pwd.encode()).decode()