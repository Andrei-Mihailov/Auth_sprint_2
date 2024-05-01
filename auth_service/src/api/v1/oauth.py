from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request

#from auth.models import db
from auth_service.src.models import db !!
from auth_service.src.services.oauth import get_provider_service
from auth_service.src.services.oauth.yandex import YandexOAuthService
from auth_service.src.services.user import UserService
from auth_service.src.utils.rbac import allow, current_identity

PROVIDER = 'yandex'

router = APIRouter(prefix="/oauth")


@router.get("/{provider}/authorize-url")
async def get_authorize_url(provider: str):
    """Returns url for authorization."""
    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=400, detail="Unknown provider")

    return {
        'authorize_url': oauth_service.get_authorize_url()
    }


@router.get("/{provider}/webhook")
async def receive_verification_code(request: Request, provider: str):
    """Webhook for redirect after authorization in Yandex."""
    verification_code = request.query_params.get('code', None)
    state = request.query_params.get('state', None)

    if verification_code is None:
        return {'msg': 'code not found in params'}

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=400, detail="Unknown provider")

    user_service = UserService(db)
    token_data = oauth_service.get_token(verification_code, state)

    if token_data.get('access_token') is None:
        raise HTTPException(status_code=400, detail=token_data)

    user_info = oauth_service.get_user_info(
        access_token=token_data.get('access_token'))

    user = user_service.get_user_by_email(
        email=user_info.get('default_email'),
    )

    if user is None:
        user = user_service.create_user(
            email=user_info.get('default_email'),
            password='123',  # TODO Hardcoded for now, later, after adding a notification service, send a notification with a generated password
            first_name=user_info.get('first_name'),
            last_name=user_info.get('last_name'),
        )

    user_service.save_user_oauth_refresh_token(
        user.id,
        PROVIDER,
        token_data.get('refresh_token'),
        token_data.get('expires_in'))

    return {'user_id': user.id}


@router.get("/{provider}/who")
async def get_user_info(provider: str, current_user: str = Depends(current_identity)):
    """Endpoint returns user information from Yandex service."""
    user_service = UserService(db)

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=400, detail="Unknown provider")

    refresh_token = user_service.get_user_oauth_refresh_token(current_user.id,
                                                              PROVIDER)

    data = oauth_service.refresh_token(refresh_token=refresh_token)

    user_service.save_user_oauth_refresh_token(
        current_user.id,
        PROVIDER,
        data.get('refresh_token'),
        data.get('expires_in'))
    user_info = oauth_service.get_user_info(
        access_token=data.get('access_token'))

    if user_info is None:
        user_info = {'data': 'no data'}

    return user_info