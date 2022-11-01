## No SeiQueLa ORM
> IN DEVELOPMENT

[🇧🇷 Documentação em Português](/README.pt-br.md)

**No** **S***ei***Q***ue***L***a* is a small and expressive ORM (Object Relational Mapper) to interact with Google Datastore inspired by Django, Mongo-Engine and Peewee.

## Installing

The library can be installed using pip:

```bash
$ pip install noseiquela_orm
```

## Usage

Creating model classes:

```python
from noseiquela_orm.entity import Model
from noseiquela_orm.types.key import KeyProperty
from noseiquela_orm.types import properties


class Customer(Model):
    name = properties.StringProperty(required=True)
    age = properties.IntegerProperty(required=True)
    is_deleted = properties.BooleanProperty(default=False, required=True)

```

To define a key, simply assign a `KeyProperty` to an attribute with the name `id`. If not explicitly defined, it will be set automatically.

To set an "`ancestor`", just pass the model of the external key. It can be the class itself or a string with the class name.

The "type"/"`kind`" of each model is the name of the class itself, but if you want to set something different, just set `__kind__` to the desired value.

```python
class CustomerAddress(Model):
    __kind__ = "Address"
    id = KeyProperty(parent="Customer")

    number = properties.IntegerProperty(required=True)
    address_one = properties.StringProperty(required=True)
    address_two = properties.StringProperty()
    is_default = properties.BooleanProperty(required=True, default=True)
    is_deleted = properties.BooleanProperty(required=True, default=False)
```

In case the project name, namespace (or any other parameter of the [`google.cloud.datastore.Client`](https://googleapis.dev/python/datastore/latest/client.html)) needs to be changed, simply create a `Meta` class inside the template with the desired information.

```python
class Product(Model):
    quantity = properties.IntegerProperty(required=True)
    name = properties.StringProperty(required=True)
    value = properties.FloatProperty(required=True)

    class Meta:
        namespace = "production"
        project = "products"
```

Adding new entities:

```python
new_customer = Customer(
    name="Geraldo Castro",
    age=29,
)

new_customer.save()
```

If an `id` has not been set before saving, one will be set and assigned to the instance with the value entered in the database.

It is mandatory that when saving an entity that has an `ancestor`/`parent`, that the `parent_id` has an assigned value.

```python
new_address = CustomerAddress(
    parent_id=new_customer.id,
    number=199,
    address_one="Some St.",
    is_default=True
)

new_address.save()
```

Query on database:

```python
customer = Customer.query.filter(name="Geraldo Castro").first()
customer_address = Customer.query.filter(parend_id=customer.id)

less_than_or_eq_29 = Customer.query.filter(age__le=29) # age <= 29
more_than_30 = Customer.query.filter(age__gt=30) # age > 30

first_customer = Customer.query.first()

dict_customer = first_customer.as_dict()
g_entity_customer = first_customer.as_entity()

all_customers = [
    customer.as_dict()
    for customer in Customer.query.all()
]
```

## Authentication

The library uses the standard way of authenticating Google libraries ([google-auth-library-python](https://github.com/googleapis/google-auth-library-python)).

The search for credentials happens in the following order:

1. If the environment variable `GOOGLE_APPLICATION_CREDENTIALS` is set to a valid service account path.

2. If the `Google Cloud SDK` is installed and has the credentials of the application to be used, these will be loaded.

3. If the application is running in the `App Engine standard environment` (first generation), then the credentials and project ID are taken from the `App Identity Service`.

4. If the application is running in `Compute Engine`, `Cloud Run`, `App Engine flexible environment` or `App Engine standard environment` (second generation), then the credentials and project ID are taken from the `Metadata Service`.

More details at [this link](https://github.com/googleapis/google-auth-library-python/blob/main/google/auth/_default.py#L356).
