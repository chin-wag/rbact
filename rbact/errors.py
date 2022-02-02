class InvalidModelError(Exception):
    def __init__(self, model, field):
        super().__init__(f"Model {model} doesn't have field {field}")


class InvalidModelTypeError(Exception):
    def __init__(self, model, orm):
        super().__init__(f"Model {model} is not {orm} model")


class UserHasFakeRoleError(Exception):
    def __init__(self, role_name):
        super().__init__(f"User has fake role {role_name}")
