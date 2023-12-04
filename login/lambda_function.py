import json
import os
import base64
import hashlib
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Any


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
ALGORITHM = os.environ["ALGORITHM"]
SECRET_KEY = os.environ["SECRET_KEY"]

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]


class AuthRequestModel(BaseModel):
    username: str
    password: str


class UserResponseModel(BaseModel):
    username: str
    access_token: str
    token_type: str
    exp: int


class Authenticator:
    @staticmethod
    def hash_password(password: str) -> str:
        # Generate a random 16-byte salt
        salt = os.urandom(16)
        # Use hashlib to create a hash of the password with the salt
        pwdhash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        # Store the salt and the hash together, separated by a colon
        return base64.b64encode(salt + pwdhash).decode("utf-8")

    @classmethod
    def create_access_token(cls, data: Dict[str, Any]) -> str:
        expiry = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expiry_timestamp = int(expiry.timestamp())
        return jwt.encode(
            {**data, "exp": expiry_timestamp}, SECRET_KEY, algorithm=ALGORITHM
        )

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        decoded = base64.b64decode(stored_password)
        salt = decoded[:16]
        stored_hash = decoded[16:]
        pwdhash = hashlib.pbkdf2_hmac(
            "sha256", provided_password.encode("utf-8"), salt, 100000
        )
        return pwdhash == stored_hash

    @classmethod
    def login(cls, data: AuthRequestModel) -> UserResponseModel:
        if not USERNAME == data.username:
            raise Exception("Unauthorized")
        if not Authenticator.verify_password(PASSWORD, data.password):
            raise Exception("Unauthorized")

        access_token = Authenticator.create_access_token(data={"sub": data.username})
        decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])

        res = UserResponseModel(
            username=data.username,
            access_token=access_token,
            token_type="bearer",
            exp=decoded_token["exp"],
        )

        return res


def lambda_handler(event, context):
    try:
        username = event.get("username")
        password = event.get("password")
        auth_data = AuthRequestModel(username=username, password=password)
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps(str(e))}

    try:
        response = Authenticator.login(auth_data)
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "username": response.username,
                    "access_token": response.access_token,
                    "token_type": response.token_type,
                    "exp": response.exp,
                }
            ),
        }
    except Exception as e:
        raise Exception("Unauthorized", e)
