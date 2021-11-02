from typing import Callable, Dict
from functools import partial

from google.cloud import datastore
from google.cloud.datastore.client import _CLIENT_INFO
from google.cloud.datastore.entity import Entity as GoogleEntity


class DataStoreClient:
    def __init__(self,
        project=None,
        namespace=None,
        credentials=None,
        client_info=None,
        client_options=None,
        _http=None,
        _use_grpc=None
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

    def _get_partial_query(self, kind):
        return partial(
            self._client.query,
            kind=kind
        )

    def save(self, entity, retry=None, timeout=None):
        self._client.put_multi(
            entities=[entity],
            retry=retry,
            timeout=timeout
        )
        return entity.key.id

    def _mount_google_entity(self, entity_dict: Dict, key_case: Callable) -> GoogleEntity:
        entity_key = entity_dict.pop("id")
        entity = GoogleEntity(entity_key)
        for key, value in entity_dict.items():
            key_name = key_case(key)
            entity[key_name] = value

        return entity

    @property
    def project(self):
        return self._project or self._client.project

    @property
    def namespace(self):
        return self._namespace or self._client.namespace
