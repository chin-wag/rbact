from playhouse.db_url import connect
import peewee as pw
import pytest

import rbact.errors
import rbact.peewee as rbact_peewee
from rbact import Inspector


def test_inspector_with_peewee_adapter_has_access():
    db = connect("sqlite:///:memory:")

    adapter = rbact_peewee.PeeweeAdapter(db)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    rbact_peewee.Roles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)
    res = inspector.has_access("user1", "resource1", "read")
    assert res
    res = inspector.has_access("user1", "resource1", "write")
    assert not res
    res = inspector.has_access("user1", "resource2", "write")
    assert not res
    res = inspector.has_access("user2", "resource2", "write")
    assert not res

    rbact_peewee.Roles.create(name="role2", id=2)
    rbact_peewee.UsersRoles.create(user=1, role=2)
    rbact_peewee.Rules.create(role=2, obj="resource1", act="write")

    res = inspector.has_access("user1", "resource1", "write")
    assert res

    rbact_peewee.Users.create(login="user2", id=2)
    rbact_peewee.Roles.create(name="role3", id=3, parent=2)
    rbact_peewee.UsersRoles.create(user=2, role=3)
    res = inspector.has_access("user2", "resource1", "write")
    assert res
    res = inspector.has_access("user2", "resource1", "read")
    assert not res


def test_inspector_with_peewee_adapter_get_first_role_with_access():
    db = connect("sqlite:///:memory:")

    adapter = rbact_peewee.PeeweeAdapter(db)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    rbact_peewee.Roles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)
    res = inspector.get_first_role_with_access("user1", "resource1", "read")
    assert res == "role1"
    res = inspector.get_first_role_with_access("user1", "resource1", "write")
    assert res is None
    res = inspector.get_first_role_with_access("user1", "resource2", "write")
    assert res is None
    res = inspector.get_first_role_with_access("user2", "resource2", "write")
    assert res is None

    rbact_peewee.Roles.create(name="role2", id=2)
    rbact_peewee.UsersRoles.create(user=1, role=2)
    rbact_peewee.Rules.create(role=2, obj="resource1", act="write")

    res = inspector.get_first_role_with_access("user1", "resource1", "write")
    assert res == "role2"

    rbact_peewee.Users.create(login="user2", id=2)
    rbact_peewee.Roles.create(name="role3", id=3, parent=2)
    rbact_peewee.UsersRoles.create(user=2, role=3)
    res = inspector.get_first_role_with_access("user2", "resource1", "write")
    assert res == "role2"
    res = inspector.get_first_role_with_access("user2", "resource1", "read")
    assert res is None


def test_inspector_with_peewee_adapter_get_first_role_with_access_with_fakes():
    db = connect("sqlite:///:memory:")

    loader = rbact_peewee.ModelsLoader(db, with_fake_roles=True)
    adapter = rbact_peewee.PeeweeAdapter(db, models_loader=loader)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    rbact_peewee.Roles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)
    res = inspector.get_first_role_with_access("user1", "resource1", "read")
    assert res == "role1"
    res = inspector.get_first_role_with_access("user1", "resource1", "write")
    assert res is None
    res = inspector.get_first_role_with_access("user1", "resource2", "write")
    assert res is None
    res = inspector.get_first_role_with_access("user2", "resource2", "write")
    assert res is None

    r = rbact_peewee.Roles.get(rbact_peewee.Roles.name == "role1")
    r.is_rbact_fake = True
    r.save()

    rbact_peewee.Roles.create(name="role2", id=2)
    rbact_peewee.UsersRoles.create(user=1, role=2)
    rbact_peewee.Rules.create(role=2, obj="resource1", act="write")

    res = inspector.get_first_role_with_access("user1", "resource1", "write")
    assert res == "role2"

    with pytest.raises(rbact.errors.UserHasFakeRoleError):
        res = inspector.get_first_role_with_access("user1", "resource1", "read")

    r = rbact_peewee.Roles.get(rbact_peewee.Roles.name == "role2")
    r.is_rbact_fake = True
    r.save()

    rbact_peewee.Users.create(login="user2", id=2)
    rbact_peewee.Roles.create(name="role3", id=3, parent=2)
    rbact_peewee.Roles.create(name="role4", id=4, parent=2)
    rbact_peewee.UsersRoles.create(user=2, role=3)
    rbact_peewee.UsersRoles.create(user=2, role=4)
    res = inspector.get_first_role_with_access("user2", "resource1", "write")
    assert res == "role4"
    res = inspector.get_first_role_with_access("user2", "resource1", "read")
    assert res is None


def test_inspector_with_peewee_adapter_get_user_rules():
    db = connect("sqlite:///:memory:")

    adapter = rbact_peewee.PeeweeAdapter(db)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    rbact_peewee.Roles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)

    res = inspector.get_user_rules("user1", orient="list")
    assert isinstance(res, list)

    with pytest.raises(ValueError):
        inspector.get_user_rules("user1", orient="smthg")

    res = inspector.get_user_rules("user1")
    assert isinstance(res, dict)
    assert len(res["resource1"]) == 1
    assert res["resource1"][0] == "read"

    rbact_peewee.Rules.create(role=1, obj="resource1", act="write")
    res = inspector.get_user_rules("user1")
    assert len(res["resource1"]) == 2
    assert "read" in res["resource1"]
    assert "write" in res["resource1"]

    # nested roles
    rbact_peewee.Roles.create(name="role2", id=2)
    rbact_peewee.Rules.create(role=2, obj="resource2", act="read")
    rbact_peewee.Roles.create(name="role3", id=3, parent=2)
    rbact_peewee.Rules.create(role=3, obj="resource2", act="write")
    rbact_peewee.UsersRoles.create(user=1, role=3)
    res = inspector.get_user_rules("user1")
    assert len(res["resource1"]) == 2
    assert len(res["resource2"]) == 2


def test_inspector_with_peewee_adapter_get_user_roles():
    db = connect("sqlite:///:memory:")

    adapter = rbact_peewee.PeeweeAdapter(db)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    rbact_peewee.Roles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)

    temp = rbact_peewee.Roles.select().dicts()

    res = inspector.get_user_roles("user1")
    assert len(res) == 1
    assert "role1" in res

    # nested roles
    rbact_peewee.Roles.create(name="role2", id=2)
    rbact_peewee.Roles.create(name="role3", id=3, parent=2)
    rbact_peewee.Roles.create(name="role4", id=4, parent=3)
    rbact_peewee.UsersRoles.create(user=1, role=4)
    res = inspector.get_user_roles("user1")
    assert len(res) == 4


def test_inspector_with_peewee_adapter_get_user_roles_with_fakes():
    db = connect("sqlite:///:memory:")

    class TestRoles(rbact_peewee.Roles):
        class Meta:
            table_name = "rbact_roles"

        test_field = pw.BooleanField(default=False)

    loader = rbact_peewee.ModelsLoader(db, roles_model=TestRoles, with_fake_roles=True)
    adapter = rbact_peewee.PeeweeAdapter(db, models_loader=loader)
    adapter.create_tables()

    rbact_peewee.Users.create(login="user1", id=1)
    TestRoles.create(name="role1", id=1)
    rbact_peewee.UsersRoles.create(user=1, role=1)
    rbact_peewee.Rules.create(role=1, obj="resource1", act="read")

    inspector = Inspector(adapter)

    res = inspector.get_user_roles("user1")
    assert len(res) == 1
    assert "role1" in res

    # nested roles
    TestRoles.create(name="role2", id=2)
    TestRoles.create(name="role3", id=3, parent=2)
    TestRoles.create(name="role4", id=4, parent=3)
    rbact_peewee.UsersRoles.create(user=1, role=4)
    res = inspector.get_user_roles("user1")
    assert len(res) == 4

    r = TestRoles.get(TestRoles.name == "role2")
    r.is_rbact_fake = True
    r.save()

    res = inspector.get_user_roles("user1")
    assert len(res) == 3

    r = TestRoles.get(TestRoles.name == "role3")
    r.is_rbact_fake = True
    r.save()

    res = inspector.get_user_roles("user1")
    assert len(res) == 2
