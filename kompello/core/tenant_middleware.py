from kompello.core.models.auth_models import Tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None
        if "X-KOMPELLO-TENANT" in request.headers:
            try:
                request.tenant = Tenant.objects.get(uuid=request.headers["X-KOMPELLO-TENANT"])
            except Exception:
                pass

        return self.get_response(request)