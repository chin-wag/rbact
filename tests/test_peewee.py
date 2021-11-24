from playhouse.db_url import connect

import rbact.peewee as rbact_peewee
from rbact import Inspector


def test_inspector_with_peewee_adapter():
    db = connect('sqlite:///:memory:')

    adapter = rbact_peewee.PeeweeAdapter(db)

    rbact_peewee.Users.create(login='user1', id=1)
    rbact_peewee.Roles.create(name='role1', id=1)
    rbact_peewee.UsersRoles.create(user_id=1, role_id=1)
    rbact_peewee.PermRules.create(role_id=1, obj='resource1', act='read')

    inspector = Inspector(adapter)
    res = inspector.has_access('user1', 'resource1', 'read')
    assert res
    res = inspector.has_access('user1', 'resource1', 'write')
    assert not res
    res = inspector.has_access('user1', 'resource2', 'write')
    assert not res
    res = inspector.has_access('user2', 'resource2', 'write')
    assert not res

    rbact_peewee.Roles.create(name='role2', id=2)
    rbact_peewee.UsersRoles.create(user_id=1, role_id=2)
    rbact_peewee.PermRules.create(role_id=2, obj='resource1', act='write')

    res = inspector.has_access('user1', 'resource1', 'write')
    assert res

    rbact_peewee.Users.create(login='user2', id=2)
    rbact_peewee.Roles.create(name='role3', id=3, parent=2)
    rbact_peewee.UsersRoles.create(user_id=2, role_id=3)
    res = inspector.has_access('user2', 'resource1', 'write')
    assert res
    res = inspector.has_access('user2', 'resource1', 'read')
    assert not res
