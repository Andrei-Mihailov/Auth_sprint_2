from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Request
from sqlalchemy.exc import MissingGreenlet

from api.v1.schemas.roles import (
    RolesSchema,
    RoleParams,
    RoleEditParams,
    UserRoleSchema,
    PermissionsSchema,
    RolesPermissionsSchema,
)
from services.role import RoleService, get_role_service
from api.v1.service import allow_this_user


router = APIRouter()


# /api/v1/roles/create
@router.post(
    "/create",
    response_model=RolesSchema,
    status_code=status.HTTP_200_OK,
    summary="Создание роли",
    description="Создание новой роли",
    response_description="Ид, тип, разрешения",
    tags=["Роли"],
)
@allow_this_user
async def create(
    request: Request,
    role_params: Annotated[RoleParams, Depends()],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RolesSchema:
    role = await role_service.create(role_params)
    if role is not None:
        return RolesSchema(uuid=role.id, type=role.type)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="This role already exists"
    )


# /api/v1/roles/{id_role}
@router.delete(
    "/{id_role}",
    status_code=status.HTTP_200_OK,
    summary="Удаление роли",
    description="Удаление существующей роли",
    tags=["Роли"],
)
@allow_this_user
async def delete(
    request: Request,
    id_role: str,
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> None:
    result = await role_service.delete(id_role)
    if result:
        return None

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# /api/v1/roles/change/{id_role}
@router.put(
    "/change/{id_role}",
    response_model=RolesSchema,
    status_code=status.HTTP_200_OK,
    summary="Редактирование роли",
    description="Редактирование существующей роли",
    response_description="Ид, тип, разрешения",
    tags=["Роли"],
)
@allow_this_user
async def change(
    request: Request,
    id_role: str,
    role_params: Annotated[RoleEditParams, Depends()],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RolesSchema:
    role = await role_service.update(id_role, role_params)
    if role is not None:
        return RolesSchema(uuid=role.id, type=role.type)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# /api/v1/roles/list
@router.get(
    "/list",
    response_model=list[RolesPermissionsSchema],
    status_code=status.HTTP_200_OK,
    summary="Список ролей",
    description="Список существующих ролей",
    response_description="Ид, тип, разрешения",
    tags=["Роли"],
)
@allow_this_user
async def list_roles(
    request: Request, role_service: Annotated[RoleService, Depends(get_role_service)]
) -> list[RolesPermissionsSchema]:
    roles_data = await role_service.elements()

    list_roles_scheme = []
    if roles_data:
        for item in roles_data:
            try:
                perms = []
                for subitem in item._data[0].permissions:
                    perms.append(PermissionsSchema(uuid=subitem.id, name=subitem.name))
            except MissingGreenlet:
                perms = None
            roles_scheme = RolesPermissionsSchema(
                uuid=item._data[0].id, type=item._data[0].type, permissions=perms
            )
            list_roles_scheme.append(roles_scheme)
    return list_roles_scheme


# /api/v1/roles/set/{user_id}/{id_role}
@router.post(
    "/set/{user_id}/{id_role}",
    response_model=UserRoleSchema,
    status_code=status.HTTP_200_OK,
    summary="Назначение ролей",
    description="Назначение выбранной роли конкретному пользователю",
    response_description="Ид роли, Ид пользователя",
    tags=["Роли"],
)
@allow_this_user
async def add_user_role(
    request: Request,
    user_id: str,
    id_role: str,
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> UserRoleSchema:
    result = await role_service.assign_role(user_id, id_role)
    if result is not None:
        return UserRoleSchema(id_role=id_role, user_id=user_id)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


# /api/v1/roles/delete/{user_id}
@router.post(
    "/delete/{user_id}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Удаление роли у пользователя",
    description="Удаление роли конкретного пользователю",
    response_description="Ид пользователя",
    tags=["Роли"],
)
@allow_this_user
async def del_user_role(
    request: Request,
    user_id: str,
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> UserRoleSchema:
    return await role_service.deassign_role(user_id)
