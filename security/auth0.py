import jwt
from configparser import ConfigParser
from fastapi import HTTPException, status, Request

from settings.config import auth0_config
from schemas import user as schema_u




class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token, crud, permissions=None, scopes=None):
        self.token = token
        self.crud = crud
        self.permissions = permissions
        self.scopes = scopes
        self.config = auth0_config
        self.credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

        # This gets the JWKS from a given URL and does processing so you can use any of
        # the keys available
        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    async def verify(self):
        # This gets the 'kid' from the passed token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}   

        try: 
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["AUTH0_ALGORITHM"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        if self.scopes:
            result = await self._check_claims(payload, 'scope', str, self.scopes.split(' '))
            if result.get("error"):
                return result

        if self.permissions:
            result = self._check_claims(payload, 'permissions', list, self.permissions)
            if result.get("error"):
                return result

        user = await self.get_or_create_user(payload=payload)
        return user

    async def _check_claims(self, payload, claim_name, claim_type, expected_value):

        instance_check = isinstance(payload[claim_name], claim_type)
        result = {"status": "success", "status_code": 200}

        payload_claim = payload[claim_name]

        if claim_name not in payload or not instance_check:
            result["status"] = "error"
            result["status_code"] = 400

            result["code"] = f"missing_{claim_name}"
            result["msg"] = f"No claim '{claim_name}' found in token."
            return result

        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')

        for value in expected_value:
            if value not in payload_claim:
                result["status"] = "error"
                result["status_code"] = 403

                result["code"] = f"insufficient_{claim_name}"
                result["msg"] = (f"Insufficient {claim_name} ({value}). You don't have "
                                  "access to this resource")
                return result
        
        return result

    async def get_or_create_user(self, payload) -> schema_u.ResponseUserDataFromToken:

        """ Get user by email from token or create new user with this email 
        """
        email = payload.get('email')
        if not email:
            raise self.credentials_exception
        user = await self.crud.get_by_email(email=email)
        if user:
            return schema_u.ResponseUserDataFromToken(id=user.id, is_admin=user.is_admin)
        return await self.crud.create_auth0_user(email=email)
