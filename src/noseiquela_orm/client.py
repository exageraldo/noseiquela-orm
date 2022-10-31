from typing import TYPE_CHECKING
from functools import partial

if TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Union, List

    from google.cloud.datastore.key import Key as GKey
    from google.cloud.datastore.entity import Entity as GEntity
    from google.auth.credentials import Credentials as GoogleCredentials
    from google.api_core.gapic_v1.client_info import ClientInfo as GoogleClientInfo
    from google.api_core.client_options import ClientOptions as GoogleClientOptions
    from google.api_core.retry import Retry as GoogleRetry
    from requests import Session as HttpSession


class DatastoreClient:
    def __init__(self,
        project: 'Optional[str]'=None,
        namespace: 'Optional[str]'=None,
        credentials: 'Optional[GoogleCredentials]'=None,
        client_info: 'Optional[GoogleClientInfo]'=None,
        client_options: 'Optional[GoogleClientOptions]'=None,
        _http: 'Optional[HttpSession]'=None,
        _use_grpc: 'Optional[bool]'=None
    ) -> 'None':
        from google.cloud.datastore import Client
        from google.cloud.datastore.client import _CLIENT_INFO

        self._project = project
        self._namespace = namespace
        self._client = Client(
            project=project,
            namespace=namespace,
            credentials=credentials,
            client_info=(client_info or _CLIENT_INFO),
            client_options=client_options,
            _http=_http,
            _use_grpc=_use_grpc
        )

    def get_partial_query(self, kind: 'Union[str, int]') -> 'partial':
        return partial(
            self._client.query,
            kind=kind
        )

    def save(
        self,
        entity: 'GEntity',
        retry: 'Optional[GoogleRetry]'=None,
        timeout: 'Optional[float]'=None
    ) -> 'GEntity':
        self._client.put_multi(
            entities=[entity],
            retry=retry,
            timeout=timeout
        )
        return entity

    def bulk_save(
        self,
        entities: 'List[GEntity]',
        retry: 'Optional[GoogleRetry]'=None,
        timeout: 'Optional[float]'=None
    ) -> 'List[GEntity]':
        self._client.put_multi(
            entities=entities,
            retry=retry,
            timeout=timeout
        )

        return entities

    def mount_partial_g_key(
        self,
        kind: str,
        parent: 'Optional[GKey]'=None,
    ) -> 'GKey':
        return self._client.key(kind, parent=parent)

    def mount_complete_g_key(
        self,
        kind: 'str',
        id_or_name: 'Union[str, int]',
        parent: 'Optional[GKey]'=None,
    ) -> 'GKey':
        if parent and parent.is_partial:
            raise Exception("Parent deve ter uma chave completa!")

        return self.mount_partial_g_key(
            kind,
            parent=parent
        ).completed_key(id_or_name)

    @property
    def project(self) -> 'str':
        return self._project or self._client.project

    @property
    def namespace(self) -> 'str':
        return self._namespace or self._client.namespace
