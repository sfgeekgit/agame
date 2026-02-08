from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CsrfEnforcement(BaseAuthentication):
    """DRF authentication class that enforces CSRF on unsafe methods.

    DRF's @api_view applies csrf_exempt, so Django's middleware alone
    won't protect API views. This class re-enables the check.
    """

    def authenticate(self, request):
        reason = CsrfViewMiddleware(lambda r: None).process_view(
            request, None, (), {}
        )
        if reason:
            raise AuthenticationFailed(f'CSRF check failed.')
        return None
