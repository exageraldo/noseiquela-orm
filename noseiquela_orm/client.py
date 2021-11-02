from typing import Callable, Dict, Optional, Union
from functools import partial

from google.cloud import datastore
from google.cloud.datastore.client import _CLIENT_INFO
from google.cloud.datastore.entity import Entity as GoogleEntity
from google.auth.credentials import Credentials as GoogleCredentials
from google.api_core.gapic_v1.client_info import ClientInfo as GoogleClientIngo
from google.api_core.client_options import ClientOptions as GoogleClientOptions
from google.api_core.retry import Retry as GoogleRetry
from requests import Session


class DataStoreClient:
    def __init__(self,
        project:Optional[str]=None,
        namespace:Optional[str]=None,
        credentials:Optional[GoogleCredentials]=None,
        client_info:Optional[GoogleClientIngo]=None,
        client_options:Optional[GoogleClientOptions]=None,
        _http:Optional[Session]=None,
        _use_grpc:Optional[bool]=None
    ) -> None:
        self._project = project
        self._namespace = namespace
        self._client = datastore.Client(
            project=project,
            namespace=namespace,
            credentials=credentials,
            client_info=(client_info or _CLIENT_INFO),
            client_options=client_options,
            _http=_http,
            _use_grpc=_use_grpc
        )

    def _get_partial_query(self, kind: Union[str, int]) -> Callable:
        return partial(
            self._client.query,
            kind=kind
        )

    def save(self, entity:GoogleEntity, retry:Optional[GoogleRetry]=None, timeout:Optional[float]=None) -> Union[str, int]:
        self._client.put_multi(
            entities=[entity],
            retry=retry,
            timeout=timeout
        )
        return entity.key.id

    @staticmethod
    def _mount_google_entity(entity_dict: Dict, key_case: Callable) -> GoogleEntity:
        entity_key = entity_dict.pop("id")
        entity = GoogleEntity(entity_key)
        for key, value in entity_dict.items():
            key_name = key_case(key)
            entity[key_name] = value

        return entity

    @property
    def project(self) -> str:
        return self._project or self._client.project

    @property
    def namespace(self) -> str:
        return self._namespace or self._client.namespace
