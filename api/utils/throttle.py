from rest_framework.throttling import BaseThrottle, SimpleRateThrottle

# 自定义的节流限制
# 对匿名用户做限制，让其一分钟只能访问3次，实现方式以ip作为key
# {'ip': [访问时间段1， 访问时间段2, 访问时间段3]}
"""
import time
VISIT_RECORD = {}
class VisitThrottles(BaseThrottle):

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
        # remote_addr = request.META.get('REMOTE_ADDR')
        remote_addr = self.get_ident(request)
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
"""


# 继承SimpleRateThrottle的话，可直接实现上述功能
class VisitThrottles(SimpleRateThrottle):
    scope = 'Luffy'

    def get_cache_key(self, request, view):
        return self.get_ident(request)


# 对普通用户做限制，一分钟可以最多访问10次
# 以用户id或者用户名（要求用户名唯一）作为key
# {'用户名': [访问时间段1， 访问时间段2, 访问时间段3]}
class UserThrottles(SimpleRateThrottle):
    scope = 'LuffyUser'

    def get_cache_key(self, request, view):
        return request.user.username
