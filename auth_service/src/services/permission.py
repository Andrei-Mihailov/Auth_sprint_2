from fastapi import Depends
from functools import lru_cache

from models.entity import Permissions
from .base_service import BaseService
from db.redis_db import RedisCache, get_redis
from db.postgres_db import AsyncSession, get_session


class PermissionService(BaseService):
    def __init__(self, cache: RedisCache, storage: AsyncSession):
        super().__init__(cache, storage)
        self.model = Permissions

    async def create_permission(self, params: dict) -> Permissions:
        permission = await self.create_new_instance(params)
        return permission

    async def assign_permission_to_role(self, data: dict) -> bool:
        role = await self.permission_to_role(
            str(data.permissions_id), str(data.role_id)
        )
        if role is not None:
            return True
        return False

    async def remove_permission_from_role(self, data: dict) -> bool:
        return await self.permission_from_role(
            str(data.permissions_id), str(data.role_id)
        )


@lru_cache()
def get_permission_service(
    redis: RedisCache = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
) -> PermissionService:

    return PermissionService(redis, db)
