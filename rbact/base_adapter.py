from abc import ABC, abstractmethod


class AsyncBaseAdapter(ABC):
    def __init__(self):
        self.with_fake_roles = False

    @abstractmethod
    async def _get_user(self, login):
        pass

    @abstractmethod
    async def get_user_zero_depth_rules(self, login):
        pass

    @abstractmethod
    async def get_user_zero_depth_roles(self, login):
        pass

    @abstractmethod
    async def get_extended_rules(self, role):
        pass

    @abstractmethod
    def create_tables(self):
        pass


class BaseAdapter(ABC):
    def __init__(self):
        self.with_fake_roles = False

    @abstractmethod
    def _get_user(self, login):
        pass

    @abstractmethod
    def get_user_zero_depth_rules(self, login):
        pass

    @abstractmethod
    def get_user_zero_depth_roles(self, login):
        pass

    @abstractmethod
    def get_extended_rules(self, role):
        pass

    @abstractmethod
    def create_tables(self):
        pass
