from datetime import datetime, timedelta, timezone

import jwt


class JWTService:
    def __init__(self, secret_key: str, expires_minutes: int) -> None:
        self.secret_key = secret_key
        self.expires_minutes = expires_minutes

    def create_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(
            minutes=self.expires_minutes
        )

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": expires_at,
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm="HS256",
        )

    def decode_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.secret_key,
            algorithms=["HS256"],
        )
