import peewee as pw

from rbact.base_adapter import BaseAdapter, AsyncBaseAdapter
from .models import ModelsLoader


class PeeweeAdapter(BaseAdapter):
    def __init__(self, db: pw.Database, models_loader: ModelsLoader = None):
        if models_loader is None:
            models_loader = ModelsLoader(db)

        self.users = models_loader.users
        self.roles = models_loader.roles
        self.users_roles = models_loader.users_roles
        self.perm_rules = models_loader.perm_rules
        self.db = db

        self._create_tables()

    def _get_user(self, login):
        try:
            return self.users.get(login=login)
        except pw.DoesNotExist:
            pass

    def get_user_roles(self, login):
        user = self._get_user(login)
        if user is None:
            return []

        q = (self.users_roles
             .select(self.users_roles, self.perm_rules)
             .join(self.perm_rules, pw.JOIN.LEFT_OUTER, on=(self.users_roles.role_id == self.perm_rules.role_id), attr='perm_rules')
             .where(self.users_roles.user_id == user))

        return q

    def get_extended_role(self, role):
        q = self.perm_rules.select().where(self.perm_rules.role_id == role)

        return q

    def _create_tables(self):
        self.db.create_tables([self.users, self.roles, self.users_roles, self.perm_rules])


class AsyncPeeweeAdapter(AsyncBaseAdapter):
    import peewee_async

    def __init__(self, db_manager: peewee_async.Manager, models_loader: ModelsLoader = None):
        if models_loader is None:
            models_loader = ModelsLoader(db_manager.database)

        self.users = models_loader.users
        self.roles = models_loader.roles
        self.users_roles = models_loader.users_roles
        self.perm_rules = models_loader.perm_rules
        self.db_manager = db_manager

        self._create_tables()

    async def _get_user(self, login):
        try:
            return await self.db_manager.get(self.users, login=login)
        except pw.DoesNotExist:
            pass

    async def get_user_roles(self, login):
        user = await self._get_user(login)
        if user is None:
            return []

        q = (self.users_roles
             .select(self.users_roles, self.perm_rules)
             .join(self.perm_rules, pw.JOIN.LEFT_OUTER, on=(self.users_roles.role_id == self.perm_rules.role_id), attr='perm_rules')
             .where(self.users_roles.user_id == user))

        return await self.db_manager.execute(q)

    async def get_extended_role(self, role):
        q = self.perm_rules.select().where(self.perm_rules.role_id == role)

        return await self.db_manager.execute(q)

    def _create_tables(self):
        with self.db_manager.allow_sync():
            self.db_manager.database.create_tables([self.users, self.roles, self.users_roles, self.perm_rules])
