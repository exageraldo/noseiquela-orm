## No SeiQueLa ORM
> EM DESENVOLVIMENTO

[🇺🇸 Documentação em Inglês](link.para/arquivo-da-traducao)

**No** **S***ei***Q***ue***L***a* é um ORM pequeno e expressivo para interagir com o Google Datastore inspirado no Django, Mongo-Engine e Peewee.

- python 3.8+
- Suporta multiplos projects/namespaces

## Autenticação

A biblioteca utiliza-se da maneira padrão de autenticação das bibliotecas da Google ([google-auth-library-python](https://github.com/googleapis/google-auth-library-python)).

A busca por credenciais acontece na seguinte ordem:

1. Se a variável de ambiente `GOOGLE_APPLICATION_CREDENTIALS` estiver definida para um caminho de uma service account válida.

<!-- Se a variável de ambiente ``GOOGLE_APPLICATION_CREDENTIALS`` estiver definida para o caminho de uma conta de serviço válida arquivo chave privado JSON, então ele é carregado e devolvido. O ID do projeto devolvido é o ID do projeto definido no arquivo de conta de serviço, se disponível (alguns arquivos mais antigos não conter informações de identificação do projeto). Se a variável ambiente for definida para o caminho de um conta arquivo de configuração JSON (workload identity federation), depois o é usado para determinar e recuperar o arquivo de configuração externo credenciais do ambiente atual (AWS, Azure, etc.). Estas serão então trocadas por fichas de acesso ao Google através do Google STS ponto final. O ID do projeto devolvido neste caso é o que corresponde ao recurso de pool de identidade de carga de trabalho subjacente, se determinável. -->

2. Se o `Google Cloud SDK` estiver instalado e tiver as credenciais da aplicação a ser utilizada, essas serão carregadas.

<!-- Se o `Google Cloud SDK`_ estiver instalado e tiver o aplicativo padrão credenciais são carregadas e devolvidas. -->

3. Se a aplicação estiver rodando no `App Engine standard environment` (primeira geração), então as credenciais e o ID do projeto são pegos do `App Identity Service`.

<!-- Se a aplicação estiver rodando no ambiente "App Engine standard" (primeira geração), então as credenciais e o ID do projeto do Serviço de Identidade da `App'_ são utilizados. -->

4. Se a aplicação estiver rodando no `Compute Engine`, `Cloud Run`, `App Engine flexible environment` ou `App Engine standard environment` (segunda geração), então as credenciais e o ID do projeto são pegos do `Metadata Service`.


<!-- Se a aplicação estiver rodando em `Compute Engine`_ ou `Cloud Run`_ ou o "ambiente flexível do motorApp"_ ou o "padrão do motorApp ambiente`_ (segunda geração) então as credenciais e a identificação do projeto são obtidos do 'Serviço de Metadados'_. -->

Mais detalhes nesse [link](https://github.com/googleapis/google-auth-library-python/blob/main/google/auth/_default.py#L356).

<!-- ### Model Definition -->
## Definição do Modelo

### Conceitos
...

Iniciando as classes de modelo:

```python
from noseiquela_orm.entity import Model, EmbeddedModel, DynamicModel
from noseiquela_orm.key import Key, ParentKey
from noseiquela_orm import properties


class Customer(Model):
    name = properties.StringProperty(required=True)
    age = properties.IntegerProperty(required=True)
    is_deleted = properties.BooleanProperty(default=False, required=True)


class CustomerAddress(Model):
    __kind__ = "Address"
    __parent__ = properties.ParentKey(Customer, required=True, backref='addresses')

    number = properties.IntegerProperty(required=True)
    address_one = properties.StringProperty(required=True)
    address_two = properties.StringProperty()
    is_default = properties.BooleanProperty(required=True)
    is_deleted = properties.BooleanProperty(default=False, required=True)

    class Meta:
        namespace = "some-namespace"
        project = "other-project"
        allow_inheritance = False
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
<!-- Falar sobre os filtros -->
<!-- Falar sobre os operadores (lt, gt, ...) -->
