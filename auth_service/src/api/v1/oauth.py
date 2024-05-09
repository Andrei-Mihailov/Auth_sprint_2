from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from services.oauth import get_provider_service
from services.oauth.yandex import YandexOAuthService, get_yandex_service
from service.oauth.yandex.base import AbstractOAuthService
from services.user import UserService, get_user_service
from http import HTTPStatus

from api.v1.schemas.auth import (
    TokenSchema
)


PROVIDER = 'yandex'

router = APIRouter(prefix="/oauth")


@router.get(
    "/{provider}/authorize-url",
    response_class=RedirectResponse,
    status_code=status.HTTP_303_SEE_OTHER,
    summary="Войти с помощью провайдера",
    tags=["Авторизация"])
async def get_authorize_url(provider: str):
    oauth_service: AbstractOAuthService = get_provider_service(provider)
    if oauth_service is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Unknown provider")

    return await oauth_service.get_authorize_url()


@router.get(
    "/webhook",
    response_model=TokenSchema,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Войти с помощью яндекса",
    tags=["Авторизация"]
)
async def receive_verification_code(
    code: int,
    yandex_provider: YandexOAuthService = Depends(get_yandex_service),
    user_service: UserService = Depends(get_user_service)
):
    login_result = await user_service.login_by_yandex(
        code=code,
        yandex_provider=yandex_provider
    )
    if login_result == HTTPStatus.CONFLICT:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='User not found'
        )

    if login_result == HTTPStatus.UNAUTHORIZED:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid password'
        )
    if not login_result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't login"
        )
    return login_result
