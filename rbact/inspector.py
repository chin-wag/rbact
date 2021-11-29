import logging

from .base_adapter import AsyncBaseAdapter, BaseAdapter


logger = logging.getLogger(__name__)


class AsyncInspector:
    def __init__(self, adapter: AsyncBaseAdapter):
        self.adapter = adapter
        self.superuser = "admin"

    async def has_access(self, user, obj, act):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role_id}
            for ur in await self.adapter.get_user_roles(user)
        ]

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["role"].name == self.superuser:
                logger.debug(f"User {user}: access to {act} {obj} approved")
                return True

            if (
                cur_role["rules"] is not None
                and cur_role["rules"].obj == obj
                and cur_role["rules"].act == act
            ):
                logger.debug(f"User {user}: access to {act} {obj} approved")
                return True

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role_id}
                    for ur in await self.adapter.get_extended_role(
                        cur_role["role"].parent
                    )
                ]
                roles.extend(res)

        logger.debug(f"User {user}: access to {act} {obj} denied")
        return False


class Inspector:
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
        self.superuser = "admin"

    def has_access(self, user, obj, act):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role_id}
            for ur in self.adapter.get_user_roles(user)
        ]

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["role"].name == self.superuser:
                logger.debug(f"User {user}: access to {act} {obj} approved")
                return True

            if (
                cur_role["rules"] is not None
                and cur_role["rules"].obj == obj
                and cur_role["rules"].act == act
            ):
                logger.debug(f"User {user}: access to {act} {obj} approved")
                return True

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role_id}
                    for ur in self.adapter.get_extended_role(cur_role["role"].parent)
                ]
                roles.extend(res)

        logger.debug(f"User {user}: access to {act} {obj} denied")
        return False
