import peewee as pw

from rbact.errors import InvalidModelError, InvalidModelTypeError


database_proxy = pw.DatabaseProxy()


class BaseModel(pw.Model):
    class Meta:
        database = database_proxy


class Users(BaseModel):
    class Meta:
        table_name = "rbact_users"

    id = pw.AutoField(primary_key=True)
    login = pw.TextField()


class Roles(BaseModel):
    class Meta:
        table_name = "rbact_roles"

    id = pw.AutoField(primary_key=True)
    name = pw.TextField()
    parent = pw.ForeignKeyField("self", null=True)


class UsersRoles(BaseModel):
    class Meta:
        table_name = "rbact_users_roles"

    id = pw.AutoField(primary_key=True)
    user = pw.ForeignKeyField(Users)
    role = pw.ForeignKeyField(Roles)


class Rules(BaseModel):
    class Meta:
        table_name = "rbact_rules"

    id = pw.AutoField(primary_key=True)
    role = pw.ForeignKeyField(Roles)
    obj = pw.TextField()
    act = pw.TextField()


class ModelsLoader:
    def __init__(
        self,
        db: pw.Database,
        users_model=None,
        roles_model=None,
        users_roles_model=None,
        rules_model=None,
    ):
        self.users = self.roles = self.users_roles = self.rules = None

        self._check_tables(users_model, roles_model, users_roles_model, rules_model)

        database_proxy.initialize(db)

    def _check_tables(self, users_model, roles_model, users_roles_model, rules_model):
        self._check_table(users_model, Users, "users")
        self._check_table(roles_model, Roles, "roles")
        self._check_table(users_roles_model, UsersRoles, "users_roles")
        self._check_table(rules_model, Rules, "rules")

    def _check_table(self, custom_model, default_model, class_model):
        if custom_model is None:
            setattr(self, class_model, default_model)
            return

        if not issubclass(custom_model, pw.Model):
            raise InvalidModelTypeError(custom_model, "peewee")

        for f in default_model._meta.fields:
            if f == "id":
                continue
            if f not in custom_model._meta.fields:
                raise InvalidModelError(custom_model, f)

        setattr(self, class_model, custom_model)
