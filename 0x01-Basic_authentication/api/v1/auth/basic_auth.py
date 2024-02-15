#!/usr/bin/env python3
""" Module of BasicAuth views
"""
from api.v1.auth.auth import Auth
import base64
from typing import Tuple, TypeVar
from models.user import User


class BasicAuth(Auth):
    """BasicAuth class"""

    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """extract_base64_authorization_header method"""
        if authorization_header is None:
            return None
        if type(authorization_header) is not str:
            return None
        if authorization_header[:6] != "Basic ":
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(
        self, base64_authorization_header: str
    ) -> str:
        """decode_base64_authorization_header method"""
        if (
            base64_authorization_header is None
            or type(base64_authorization_header) is not str
        ):
            return None
        try:
            decode_header = base64.b64decode(base64_authorization_header)
            return decode_header.decode("utf-8")
        except Exception:
            return None

    def extract_user_credentials(
        self, decoded_base64_authorization_header: str
    ) -> Tuple[str, str]:
        """extract_user_credentials method"""
        if (
            decoded_base64_authorization_header is None
            or type(decoded_base64_authorization_header) is not str
        ):
            return (None, None)
        if ":" not in decoded_base64_authorization_header:
            return (None, None)
        return tuple(decoded_base64_authorization_header.split(":", 1))

    def user_object_from_credentials(
        self, user_email: str, user_pwd: str
    ) -> TypeVar("User"):
        """user_object_from_credentials method"""
        if (
            user_email is None
            or type(user_email) is not str
            or user_pwd is None
            or type(user_pwd) is not str
        ):
            return None
        try:
            user = User.search({"email": user_email})
            # print(user)
        except Exception:
            return None
        if user is None:
            return None
        if len(user) == 0 or not user[0].is_valid_password(user_pwd):
            return None
        return user[0]

    def current_user(self, request=None) -> TypeVar("User"):
        """Current user"""
        authorization_header = self.authorization_header(request)
        extract_head = self.extract_base64_authorization_header(
            authorization_header
        )
        if extract_head is None:
            return None
        decoded_header = self.decode_base64_authorization_header(extract_head)
        if decoded_header is None:
            return None

        user_credentials = self.extract_user_credentials(decoded_header)
        if user_credentials == (None, None):
            return None
        user = self.user_object_from_credentials(
            user_credentials[0], user_credentials[1]
        )
        return user
