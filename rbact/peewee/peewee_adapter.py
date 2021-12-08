import peewee as pw

from rbact.base_adapter import BaseAdapter
from .models import ModelsLoader


class PeeweeAdapter(BaseAdapter):
    def __init__(self, db: pw.Database, models_loader: ModelsLoader = None):
        if models_loader is None:
            models_loader = ModelsLoader(db)

        self.users = models_loader.users
        self.roles = models_loader.roles
        self.users_roles = models_loader.users_roles
        self.rules = models_loader.rules
        self.db = db

    def _get_user(self, login):
        try:
            return self.users.get(login=login)
        except pw.DoesNotExist:
            pass

    def get_user_zero_depth_rules(self, login):
        user = self._get_user(login)
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

        return q.execute()

    def get_user_zero_depth_roles(self, login):
        user = self._get_user(login)
        if user is None:
            return []

        q = self.users_roles.select(self.users_roles).where(
            self.users_roles.user == user
        )

        return q.execute()

    def get_extended_rules(self, role):
        q = self.rules.select().where(self.rules.role == role)

        return q.execute()

    def create_tables(self):
        self.db.create_tables([self.users, self.roles, self.users_roles, self.rules])
