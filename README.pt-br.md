# No SeiQueLa ORM

> EM DESENVOLVIMENTO

[🇺🇸 Documentação em Inglês](/README.md)

**No** **S***ei***Q***ue***L***a* é um ORM pequeno e expressivo para interagir com o Google Datastore inspirado no Django, Mongo-Engine e Peewee.


## Pré-requisitos

- Credenciais no [Google Cloud](https://cloud.google.com/)
- [Python>=3.8](https://www.python.org/downloads/)

## Instalação

A biblioteca pode ser baixada usando o pip:

`pip install noseiquela_orm`

## Modo de uso

Criando as classes de modelo:

```python
from noseiquela_orm.entity import Model
from noseiquela_orm.key import Key, ParentKey
from noseiquela_orm import properties


class Customer(Model):
    name = properties.StringProperty(required=True)
    age = properties.IntegerProperty(required=True)
    is_deleted = properties.BooleanProperty(default=False, required=True)


class CustomerAddress(Model):
    __kind__ = "Address"
    __parent__ = properties.ParentKey(Customer, required=True)

    number = properties.IntegerProperty(required=True)
    address_one = properties.StringProperty(required=True)
    address_two = properties.StringProperty()
    is_default = properties.BooleanProperty(required=True)
    is_deleted = properties.BooleanProperty(default=False, required=True)
```

Caso precise mudar o projeto, namespace (ou qualquer outro parametro do [`google.cloud.datastore.Client`](https://googleapis.dev/python/datastore/latest/client.html)), basta criar uma classe `Meta` dentro do modelo com as informações desejadas.

```python
class Product(Model):
    quantity = properties.IntegerProperty(required=True)
    name = properties.StringProperty(required=True)
    value = properties.FloatProperty(required=True)

    class Meta:
        namespace = "production"
        project = "products"
```

Criando novas entidades:

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

Buscando no banco:

```python
customer = Customer.query.filter(name="Geraldo Castro").first()
customer_address = Customer.query.filter(parend_id=customer.id)

less_than_or_eq_29 = Customer.query.filter(age__le=29) # age <= 29
more_than_30 = Customer.query.filter(age__gt=30) # age > 30

all_customers = [
    customer.to_dict()
    for customer in Customer.query.all()
]
```

## Autenticação

A biblioteca utiliza-se da maneira padrão de autenticação das bibliotecas da Google ([google-auth-library-python](https://github.com/googleapis/google-auth-library-python)).

A busca por credenciais acontece na seguinte ordem:

1. Se a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS` estiver definida para um caminho de uma service account válida.

2. Se o `Google Cloud SDK` estiver instalado e tiver as credenciais da aplicação a ser utilizada, essas serão carregadas.

3. Se a aplicação estiver rodando no `App Engine standard environment` (primeira geração), então as credenciais e o ID do projeto são pegos do `App Identity Service`.

4. Se a aplicação estiver rodando no `Compute Engine`, `Cloud Run`, `App Engine flexible environment` ou `App Engine standard environment` (segunda geração), então as credenciais e o ID do projeto são pegos do `Metadata Service`.

Mais detalhes nesse [link](https://github.com/googleapis/google-auth-library-python/blob/main/google/auth/_default.py#L356).


