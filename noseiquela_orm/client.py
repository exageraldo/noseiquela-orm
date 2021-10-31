from functools import partial

from google.cloud import datastore


class DataStoreClient:
    _instance = None

    def __init__(self) -> None:
        self._client = datastore.Client()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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

    @property
    def project(self):
        return self._client.project

    @property
    def namespace(self):
        return self._client.namespace
