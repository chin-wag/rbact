import peewee as pw
import peewee_async

from rbact.base_adapter import AsyncBaseAdapter
from rbact.peewee import ModelsLoader


class AsyncPeeweeAdapter(AsyncBaseAdapter):
    def __init__(
        self, db_manager: peewee_async.Manager, models_loader: ModelsLoader = None
    ):
        if models_loader is None:
            models_loader = ModelsLoader(db_manager.database)

        self.users = models_loader.users
        self.roles = models_loader.roles
        self.users_roles = models_loader.users_roles
        self.rules = models_loader.rules
        self.db_manager = db_manager

    async def _get_user(self, login):
        try:
            return await self.db_manager.get(self.users, login=login)
        except pw.DoesNotExist:
            pass

    async def get_user_zero_depth_rules(self, login):
        user = await self._get_user(login)
        if user is None:
            return []

        q = (
            self.users_roles.select(self.users_roles, self.rules)
            .join(
                self.rules,
                pw.JOIN.LEFT_OUTER,
                on=(self.users_roles.role == self.rules.role),
                attr="rules",
            )
            .where(self.users_roles.user == user)
        )

        return await self.db_manager.execute(q)

    async def get_user_zero_depth_roles(self, login):
        user = await self._get_user(login)
        if user is None:
            return []

        q = self.users_roles.select(self.users_roles).where(
            self.users_roles.user == user
        )

        return await self.db_manager.execute(q)

    async def get_extended_rules(self, role):
        q = self.rules.select().where(self.rules.role == role)

        return await self.db_manager.execute(q)

    def create_tables(self):
        with self.db_manager.allow_sync():
            self.db_manager.database.create_tables(
                [self.users, self.roles, self.users_roles, self.rules]
            )
