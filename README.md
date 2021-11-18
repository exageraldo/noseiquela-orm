## No SeiQueLa ORM
> IN DEVELOPMENT

[🇧🇷 Documentação em Português](link.para/arquivo-da-traducao)

**No** **S***ei***Q***ue***L***a* is a small and expressive ORM (Object Relational Mapper) to interact with Google Datastore inspired by Django and Mongo-Engine.

- python 3.8+
- support many projects/namespaces

### Examples

Defining models is similar to Django or Mongo-Engine:

```python
from noseiquela_orm.entity import Model
from noseiquela_orm.key import ParentKey
from noseiquela_orm.properties import import (
    BooleanProperty, FloatProperty, IntegerProperty,
    StringProperty, ListProperty, DictProperty,
    DateTimeProperty
)


class Customer(Entity):
    name = StringProperty(required=True)
    age = IntegerProperty(required=True)
    is_deleted = BooleanProperty(default=False, required=True)


class CustomerAddress(Entity):
    __kind__ = "Address"
    __parent__ = ParentKey(Customer, required=True)

    number = IntegerProperty(required=True)
    address_one = StringProperty(required=True)
    address_two = StringProperty()
    is_default = BooleanProperty(required=True)
    is_deleted = BooleanProperty(default=False, required=True)

    class Meta:
        namespace = "some-namespace"
        project = "other-project"
```

If `Meta` class is not defined, the default values from service account are used.

Creating some entities:

```python
new_customer = Customer(
    name="Geraldo Castro",
    age=29,
)

new_customer.save()

new_address = CustomerAddress(
    parent_id=new_customer.id,
    number=199,
    address_one="Some St.",
    is_default=True
)

new_address.save()
```

When a new entity is created, its `id` is assigned only after it is saved in the database.

Making some queries:

```python
all_address_query = CustomerAddress.query.all()
first_address = all_address_query.first()
all_addresses = [ad.to_dict() for ad in all_address_query]

default_address_query = CustomerAddress.query.filter(is_default=True)
default_addresses = [ad.to_dict() for ad in default_address_query]

low_number_address_query = CustomerAddress.query.filter(number__lt=100)
low_number_addresses = [ad.to_dict() for ad in low_number_address_query]
```
