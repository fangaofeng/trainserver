from django.utils.deprecation import MiddlewareMixin

from .models import Website_views


class VisitTimes(MiddlewareMixin):

    def process_request(self, request):

        # 统计访问的url以及次数
        path = request.path
        try:
            # 取出表格中的东西
            visit = Website_views.objects.get(name='webvisitor')
            if visit:
                # 更改表格中的东西要保存
                visit.views()

        except Exception as e:
            Website_views.objects.create(name='webvisitor', views=1)
