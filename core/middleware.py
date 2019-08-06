from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class AdminPermissionCheckMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwarg):
        if request.user is not None:
            if request.resolver_match.namespace == 'admin' or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff and request.user.is_authenticated():
                    return HttpResponse('User not authorized for admin access', status=401)
