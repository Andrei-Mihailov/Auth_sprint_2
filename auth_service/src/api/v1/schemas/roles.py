from pydantic import BaseModel
from models.value_objects import UserID, RoleID, PermissionID
from typing import Union


class UserRoleSchema(BaseModel):
    id_role: RoleID
    user_id: UserID


class PermissionsSchema(BaseModel):
    uuid: PermissionID
    name: str


class RolesSchema(BaseModel):
    uuid: RoleID
    type: str


class RolesPermissionsSchema(BaseModel):
    uuid: RoleID
    type: str
    permissions: Union[list[PermissionsSchema], None]


class RoleParams(BaseModel):
    type: str


class RoleEditParams(BaseModel):
    type: str


class PermissionsParams(BaseModel):
    name: str


class RolePermissionsParams(BaseModel):
    role_id: RoleID
    permissions_id: PermissionID
