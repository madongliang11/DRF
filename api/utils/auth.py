from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication
from api import models


class Authtication(BaseAuthentication):
    def authenticate(self, request):
        token = request._request.GET.get('token')
        token_obj = models.UserToken.objects.filter(token=token).first()
        if not token_obj:
            raise exceptions.AuthenticationFailed('用户认证失败')
        # 在rest framework内部会将两个字段赋值给request,以供后续操作使用
        # token_obj.user赋值给request.user，token_obj赋值给request.auth
        return (token_obj.user, token_obj)

    def authenticate_header(self, val):
        return 'Basic realm="api"'


class FirstAuthtication(BaseAuthentication):
    def authenticate(self, request):
        pass

    def authenticate_header(self, val):
        pass