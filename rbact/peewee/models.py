import peewee as pw

from rbact.errors import InvalidModelError


database_proxy = pw.DatabaseProxy()


class BaseModel(pw.Model):
    class Meta:
        database = database_proxy


class Users(BaseModel):
    class Meta:
        table_name = 'rbact_users'
    id = pw.AutoField(primary_key=True)
    login = pw.TextField()


class Roles(BaseModel):
    class Meta:
        table_name = 'rbact_roles'
    id = pw.AutoField(primary_key=True)
    name = pw.TextField()
    parent = pw.ForeignKeyField('self', null=True)


class UsersRoles(BaseModel):
    class Meta:
        table_name = 'rbact_users_roles'
    id = pw.AutoField(primary_key=True)
    user_id = pw.ForeignKeyField(Users)
    role_id = pw.ForeignKeyField(Roles)


class PermRules(BaseModel):
    class Meta:
        table_name = 'rbact_perm_rules'
    id = pw.AutoField(primary_key=True)
    role_id = pw.ForeignKeyField(Roles)
    obj = pw.TextField()
    act = pw.TextField()


class ModelsLoader:
    def __init__(self, db: pw.Database,
                 users_model: pw.Model = None,
                 roles_model: pw.Model = None,
                 users_roles_model: pw.Model = None,
                 perm_rules_model: pw.Model = None):
        self.users = self.roles = self.users_roles = self.perm_rules = None

        self._check_tables(users_model, roles_model, users_roles_model, perm_rules_model)

        database_proxy.initialize(db)

    def _check_tables(self, users_model, roles_model, users_roles_model, perm_rules_model):
        self._check_table(users_model, Users, 'users')
        self._check_table(roles_model, Roles, 'roles')
        self._check_table(users_roles_model, UsersRoles, 'users_roles')
        self._check_table(perm_rules_model, PermRules, 'perm_rules')

    def _check_table(self, custom_model, default_model, class_model):
        if custom_model is not None:
            for f in default_model._meta.fields:
                if f == 'id':
                    continue
                if f not in custom_model._meta.fields:
                    raise InvalidModelError(custom_model, f)
            setattr(self, class_model, custom_model)
        else:
            setattr(self, class_model, default_model)
