from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework_simplejwt.backends import TokenBackend
from .models import User


class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return None

        try:
            access_token = token.split(" ")[1]
        except IndexError as e:
            raise exceptions.AuthenticationFailed("Token prefix missing") from e

        try:
            validated_token = RefreshToken(access_token)
            user = validated_token.user
        except Exception as e:
            raise exceptions.AuthenticationFailed("Token is invalid") from e

        return (user, None)


class UserTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return None

        try:
            access_token = token.split(" ")[1]
            print("access_token: ", access_token)
        except IndexError as e:
            raise exceptions.AuthenticationFailed("Token prefix missing") from e

        try:
            token_backend = TokenBackend(algorithm="HS256")
            validated_token = token_backend.decode(access_token, verify=False)
            print("validated_token: ", validated_token)
            user_id = validated_token["user_id"]
            user_obj = User.objects.get(id=user_id)

        except exceptions.TokenError:
            raise exceptions.NotAuthenticated("Token has expired")

        except Exception as e:
            print("Exception:", e)
            raise exceptions.AuthenticationFailed("Token is invalid") from e

        return (user_obj, None)
