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

    def get_user_roles(self, login):
        user = self._get_user(login)
        if user is None:
            return []

        q = (
            self.users_roles.select(self.users_roles, self.rules)
            .join(
                self.rules,
                pw.JOIN.LEFT_OUTER,
                on=(self.users_roles.role_id == self.rules.role_id),
                attr="rules",
            )
            .where(self.users_roles.user_id == user)
        )

        return q

    def get_extended_role(self, role):
        q = self.rules.select().where(self.rules.role_id == role)

        return q

    def create_tables(self):
        self.db.create_tables([self.users, self.roles, self.users_roles, self.rules])
