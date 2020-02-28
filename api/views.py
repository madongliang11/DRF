from django.shortcuts import render, HttpResponse
from rest_framework.views import APIView
from django.http import JsonResponse
from api import models
import hashlib
import time

from api.utils.permission import SvipPermission, MyPermission1

ORDER_DIC = {
    1: {
        'name': '猫',
        'age': 2,
        'gender': '雄性',
        'content': '........'
    },
    2: {
        'name': '狗',
        'age': 3,
        'gender': '雌性',
        'content': '........'
    }
}
VISIT_RECORD = {}


def md5(user):
    ctime = str(time.time())
    m = hashlib.md5(bytes(user, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()


class VisitThrottles(object):

    def __init__(self):
        self.history = None

    def allow_request(self, request, view):
        '''
        60s内只能访问3次
        1、获取用户ip
        :param request:
        :param view:
        :return:
        '''
        # 如果返回False，表示访问频率太高，被限制
        # 如果返回True，表示可以继续访问
        remote_addr = request.META.get('REMOTE_ADDR')
        ctime = time.time()
        if remote_addr not in VISIT_RECORD:
            VISIT_RECORD[remote_addr] = [ctime, ]
            return True
        history = VISIT_RECORD.get(remote_addr)
        self.history = history

        while history and history[-1] < ctime - 60:
            history.pop()

        if len(history) < 3:
            history.append(ctime)
            return True

    def wait(self):
        '''
        用于提示还需要等多少秒才访问
        :return:
        '''
        ctime = time.time()
        return 60 - (ctime - self.history[-1])


class AuthView(APIView):
    '''
    用于用户登录认证
    '''
    authentication_classes = []
    permission_classes = []
    throttle_classes = [VisitThrottles, ]

    def post(self, request, *args, **kwargs):
        # 1、去request中获取ip
        # 2、访问记录
        ret = {
            'code': 1000,
            'msg': None
        }
        try:
            user = request._request.POST.get('username')
            password = request._request.POST.get('password')
            obj = models.UserInfo.objects.filter(username=user, password=password).first()
            if not obj:
                ret['code'] = 1001
                ret['msg'] = '用户名密码错误'
            # 为登录用户创建token
            token = md5(user)
            # 存在就更新token，不存在就创建
            models.UserToken.objects.update_or_create(user=obj, defaults={'token': token})
            ret['token'] = token
        except Exception as e:
            ret['code'] = 1002
            ret['msg'] = '请求异常'
        return JsonResponse(ret)


class OrderView(APIView):
    '''
    订单相关业务（只让SVIP用户有权限）
    '''
    # authentication_classes = [FirstAuthtication, Authtication, ]
    # permission_classes = [SvipPermission, ]

    def get(self, request, *args, **kwargs):
        ret = {
            'code': 1000,
            'msg': None,
            'data': None
        }
        # self.dispatch()
        # token = request._request.GET.get('token')
        # if not token:
        #     ret['code'] = 1001
        #     ret['msg'] = '用户未登录'
        #     return JsonResponse(ret)
        try:
            ret['data'] = ORDER_DIC
        except Exception as e:
            ret['code'] = 1002
            ret['msg'] = '请求异常'
        return JsonResponse(ret)


class UserInfoView(APIView):
    '''
    用户中心（普通用户，VIP用户都有权限）
    '''
    # authentication_classes = [Authtication, ]
    permission_classes = [MyPermission1, ]

    def get(self, request, *args, **kwargs):
        # if request.user.user_type == 3:
        #     return HttpResponse('无权访问')
        print(request.user)
        return HttpResponse('用户信息')