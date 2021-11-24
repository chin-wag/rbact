class InvalidModelError(Exception):
    def __init__(self, model, field):
        super().__init__(f"Model {model} doesn't have field {field}")
