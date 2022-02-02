rbact
=======
A simple RBAC library with different ORM adapters
* has sync and async implementation
* supports peewee/peewee_async
* stores access data in normal form
* doesn't use cache (at least right now), so doesn't need to reload data and performs best with small role inheritance tree

## Content

- [Installation](#installation)
- [Docs](#docs)
  - [Peewee hello world](#peewee-hello-world)
  - [Peewee async example](#peewee-async-example-with-a-connection-pool-and-model-extensions)
  - [How it works?](#how-it-works)
  - [Superuser](#superuser)
  - [Get all user rules/roles](#get-all-user-rulesroles)

## Installation
```
# Basic
pip install rbact

# With adapter's dependencies
pip install rbact[peewee]
pip install rbact[peewee_async]
```

## Docs
### Peewee hello world 
```python
from peewee import PostgresqlDatabase
import rbact

db = PostgresqlDatabase('my_app', user='postgres', password='secret',
                           host='10.1.0.9', port=5432)

adapter = rbact.peewee.PeeweeAdapter(db)
adapter.create_tables()
inspector = rbact.Inspector(adapter)
result = inspector.has_access('user', 'resource', 'write')
```
With peewee your application needs to close connections explicitly. `adapter.create_tables()` and `inspector.has_access()` methods follow this logic and don't close connections by themselves.

### Peewee async example with a connection pool and model extensions
```python
import peewee as pw
from peewee_async import PooledPostgresqlDatabase, Manager
from rbact import peewee_async as rbact_peewee, AsyncInspector

db = PooledPostgresqlDatabase('my_app', user='postgres', password='secret',
                           host='10.1.0.9', port=5432)
db_manager = Manager(db)

# model extension
class Users(rbact_peewee.Users):
    class Meta:
        table_name = 'custom_users'
    email = pw.TextField()

async def main():
    loader = rbact_peewee.ModelsLoader(db_manager.database, users_model=Users)
    adapter = rbact_peewee.AsyncPeeweeAdapter(db_manager, models_loader=loader)
    inspector = AsyncInspector(adapter)
    has_access = await inspector.has_access('user', 'resource', 'write')
    role_with_access = await inspector.get_first_role_with_access('user', 'resource', 'read')
```

### How it works?
Rbact uses 4 tables to store data, default tables look like this:
![Tables](./images/rbact_tables.png)
All these tables can be created automatically with `adapter.create_tables()`. You can extend any table using inheritance but default columns mustn't be changed.

#### Rbact rules examples
The user who wants to access, the object (or resource) to which access is requested, the action that the user wants to do
```
analyst, company_metrics, read
employee, /api/write_task, write 
```

### Superuser
```python
import rbact

db = ...

adapter = rbact.peewee.PeeweeAdapter(db)
inspector = rbact.Inspector(adapter)
inspector.superuser = 'root'  # default value is admin
inspector.superuser = None  # disable superuser
```

### Get all user rules/roles
```python
import rbact

db = ...

adapter = rbact.peewee.PeeweeAdapter(db)
inspector = rbact.Inspector(adapter)
# list of tuples
list_rules = inspector.get_user_rules('user', orient='list')
# dict with resource key and list of actions value
dict_rules = inspector.get_user_rules('user', orient='dict')

# list of roles
roles = inspector.get_user_roles('user')
```



### Fake roles
Fake role is an intermediate role that mustn't be assigned to any user. All its rules will be used, but you can't get this role by `get_user_roles` or `get_first_role_with_access` methods
```python
import rbact.peewee as rbact_peewee
from rbact import Inspector

db = ...

loader = rbact_peewee.ModelsLoader(db, with_fake_roles=True)
adapter = rbact_peewee.PeeweeAdapter(db, models_loader=loader)
adapter.create_tables()

rbact_peewee.Roles.create(name="development_department", id=1, is_rbact_fake=True)
rbact_peewee.Rules.create(role=1, obj="docs", act="read")
rbact_peewee.Roles.create(name="software_developer", id=2)
rbact_peewee.Rules.create(role=1, obj="code", act="write")

rbact_peewee.Users.create(login="user1", id=1)
rbact_peewee.UsersRoles.create(user=1, role=2)

rbact_peewee.Roles.create(name="project_manager", id=3)

# all this users can read docs due to root fake role

inspector = Inspector(adapter)
result = inspector.get_user_roles('user1')  # ["software_developer"]
role_with_access = inspector.get_first_role_with_access('user1', 'docs', 'read')  # software_developer
```