from .base_adapter import AsyncBaseAdapter, BaseAdapter


class AsyncInspector:
    def __init__(self, adapter: AsyncBaseAdapter):
        self.adapter = adapter
        self.superuser = "admin"

    async def has_access(self, user, obj, act):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role}
            for ur in await self.adapter.get_user_zero_depth_rules(user)
        ]

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["role"].name == self.superuser:
                return True

            if (
                cur_role["rules"] is not None
                and cur_role["rules"].obj == obj
                and cur_role["rules"].act == act
            ):
                return True

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role}
                    for ur in await self.adapter.get_extended_rules(
                        cur_role["role"].parent
                    )
                ]
                roles.extend(res)

        return False

    async def get_user_rules(self, user, orient="dict"):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role}
            for ur in await self.adapter.get_user_zero_depth_rules(user)
        ]
        result = set()

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["rules"] is not None:
                result.add((cur_role["rules"].obj, cur_role["rules"].act))

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role}
                    for ur in await self.adapter.get_extended_rules(
                        cur_role["role"].parent
                    )
                ]
                roles.extend(res)

        if orient == "dict":
            dict_result = dict()
            for obj, act in result:
                dict_result.setdefault(obj, []).append(act)
            return dict_result
        if orient == "list":
            return list(result)
        raise ValueError(f"Orient must be dict or list")

    async def get_user_roles(self, user):
        roles = [ur.role for ur in await self.adapter.get_user_zero_depth_roles(user)]
        result = set()

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role.name is not None:
                result.add(cur_role.name)

            if cur_role.parent is not None:
                roles.append(cur_role.parent)

        return list(result)


class Inspector:
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
        self.superuser = "admin"

    def has_access(self, user, obj, act):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role}
            for ur in self.adapter.get_user_zero_depth_rules(user)
        ]

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["role"].name == self.superuser:
                return True

            if (
                cur_role["rules"] is not None
                and cur_role["rules"].obj == obj
                and cur_role["rules"].act == act
            ):
                return True

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role}
                    for ur in self.adapter.get_extended_rules(cur_role["role"].parent)
                ]
                roles.extend(res)

        return False

    def get_user_rules(self, user, orient="dict"):
        roles = [
            {"rules": getattr(ur, "rules", None), "role": ur.role}
            for ur in self.adapter.get_user_zero_depth_rules(user)
        ]
        result = set()

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role["rules"] is not None:
                result.add((cur_role["rules"].obj, cur_role["rules"].act))

            if cur_role["role"].parent is not None:
                res = [
                    {"rules": ur, "role": ur.role}
                    for ur in self.adapter.get_extended_rules(cur_role["role"].parent)
                ]
                roles.extend(res)

        if orient == "dict":
            dict_result = dict()
            for obj, act in result:
                dict_result.setdefault(obj, []).append(act)
            return dict_result
        if orient == "list":
            return list(result)
        raise ValueError(f"Orient must be dict or list")

    def get_user_roles(self, user):
        roles = [ur.role for ur in self.adapter.get_user_zero_depth_roles(user)]
        result = set()

        while len(roles) > 0:
            cur_role = roles.pop()
            if cur_role.name is not None:
                result.add(cur_role.name)

            if cur_role.parent is not None:
                roles.append(cur_role.parent)

        return list(result)
