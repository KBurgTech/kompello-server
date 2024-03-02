from kompello.app.settings.shared import OAUTH_PROVIDERS
from kompello.core.models.auth_models import KompelloUser, KompelloUserSocialAuths

def parse_id_token(data: dict[str, str]) -> dict[str, str] or None: # type: ignore
    client = OAUTH_PROVIDERS.create_client(data['provider'])
    if client is None:
        return None
    
    token = client.parse_id_token(data, {})
    return token

def get_user_social_auth(provider: str, sub: str) -> KompelloUser or None: # type: ignore
    try:
        return KompelloUserSocialAuths.objects.get(provider=provider, sub=sub).user
    except KompelloUserSocialAuths.DoesNotExist:
        return None
    
def register_social_auth_user(id_token: dict[str, str], provider: str) -> KompelloUser: # type: ignore
    user = KompelloUser.objects.create(email=id_token['email'], username=id_token['email'])
    KompelloUserSocialAuths.objects.create(user=user, provider=provider, sub=id_token['sub'])
    return user