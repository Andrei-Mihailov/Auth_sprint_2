from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from typing import Annotated

from services.oauth import get_provider_service
from services.oauth.yandex import YandexOAuthService
from services.user import UserService

from api.v1.schemas.auth import (
    AuthenticationParams,
)
from .service import get_tokens_from_cookie

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
    user_params: Annotated[AuthenticationParams, Depends()]
    verification_code = request.query_params.get('code', None)
    state = request.query_params.get('state', None)

    if verification_code is None:
        return {'msg': 'code not found in params'}

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=400, detail="Unknown provider")

    user_service = UserService()
    token_data = oauth_service.get_token(verification_code, state)

    if token_data.get('access_token') is None:
        raise HTTPException(status_code=400, detail=token_data)

    user_info = oauth_service.get_user_info(
        access_token=token_data.get('access_token'))

    user = user_service.get_user_by_email(
        email=user_info.get(user_params.email)
    )
    if user is None:
        user = await user_service.create_user(user_params)
        social_account = await user_service.create_social_account(user.id, provider)
    social_account = await user_service.get_social_account(user.id, provider)
    if social_account is None:
        social_account = await user_service.create_social_account(user.id, provider)
    user_service.refresh_access_token(user.id, PROVIDER, data.get('expires_in'))

    return {'user_id': user.id}


@router.get("/{provider}/who")
async def get_user_info(request: Request, provider: str, current_user: str = Depends()):
    """Endpoint returns user information from Yandex service."""
    user_service = UserService

    oauth_service = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=400, detail="Unknown provider")

    refresh_token = get_tokens_from_cookie(request)

    data = oauth_service.refresh_token(refresh_token=refresh_token)

    user_service.refresh_access_token(
        current_user.id,
        PROVIDER,
        data.get('refresh_token'),
        data.get('expires_in'))
    user_info = oauth_service.get_user_info(
        access_token=data.get('access_token'))

    if user_info is None:
        user_info = {'data': 'no data'}

    return user_info
