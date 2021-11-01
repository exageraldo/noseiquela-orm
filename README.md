# No SeiQueLa ORM
> EM DESENVOLVIMENTO

Uma ideia de ORM no estilo do Django para manipular entidades do Google Datastore.

###
Montando seu modelo:
```python
from noseiquela_orm import (Entity, ParentKey, BooleanField, FloatField,
                 IntegerField, StringField, ListField, DictField,
                 DateTimeField)

class Customer(Entity):
    name = StringField(required=True)
    age = IntegerField(required=True)
    is_deleted = BooleanField(default=False, required=True)

class CustomerAddress(Entity):
    __kind__ = "Address"
    __parent__ = ParentKey(Customer, required=True)

    number = IntegerField(required=True)
    address_one = StringField(required=True)
    address_two = StringField()
    is_default = BooleanField(required=True)
    is_deleted = BooleanField(default=False, required=True)
```

Criando entidades:

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

Fazendo queries:

```python
all_address_query = CustomerAddress.query.all()
first_address = all_address_query.first()
all_addresses = [ad.to_dict() for ad in all_address_query]

default_address_query = CustomerAddress.query.filter(is_default=True)
default_addresses = [ad.to_dict() for ad in default_address_query]

low_number_address_query = CustomerAddress.query.filter(number__lt=100)
low_number_addresses = [ad.to_dict() for ad in low_number_address_query]
```
