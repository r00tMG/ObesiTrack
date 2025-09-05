import os
import time
from typing import Dict

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("SECRET")
JWT_ALGORITHM = os.getenv("ALGORITHM")

def token_response(token:str):
    return {
        "access_tokenn":token
    }

def sign_jwt(user_id:str)->Dict[str,str]:
    payload = {
        "user_id":user_id,
        "expires":time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decode_jwt(token:str)->dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token['expires'] >= time.time() else None
    except Exception as e:
        print(f"Erreur decode_jwt: {e}")
        return {}

