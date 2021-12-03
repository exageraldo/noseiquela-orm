from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from functools import partial
    from typing import Any, Dict, Tuple, Optional, Generator, Iterable
    from google.cloud.datastore.query import Query as GoogleQuery
    from .entity import Model

class QueryResult:
    def __init__(
        self,
        query: 'GoogleQuery',
        entity_instance: 'Model',
        limit: 'Optional[int]'=None,
        offset: 'Optional[int]'=0,
        retry: 'Optional[int]'=None,
        timeout: 'Optional[int]'=None
    ) -> 'None':
        self.query = query
        self.limit = limit
        self.offset = offset
        self.retry = retry
        self.timeout = timeout
        self.entity_instance = entity_instance

    def _get_fetch_iterator(self):
        return self.query.fetch(
            limit=self.limit,
            offset=self.offset,
            retry=self.retry,
            timeout=self.timeout
        )

    def __iter__(self) -> 'Iterable[Model]':
        for entity in self._get_fetch_iterator():
            yield self.entity_instance._mount_from_google_entity(
                entity
            )


class Query:
    def __init__(
        self,
        partial_query: 'partial',
        entity_instance: 'Model',
    ) -> 'None':
        self.partial_query = partial_query
        self.entity_instance = entity_instance

    def all(
        self,
        order_by: 'Optional[Tuple[str]]'=None,
        projection: 'Optional[Tuple[str]]'=None
    ) -> 'QueryResult':
        query = self.__mount_query(
            order_by=order_by,
            projection=projection
        )
        return QueryResult(query, self.entity_instance)

    def first(
        self,
        order_by: 'Optional[Tuple[str]]'=None,
        projection: 'Optional[Tuple[str]]'=None
    ) -> 'Optional[Model]':
        query = self.__mount_query(
            order_by=order_by,
            projection=projection
        )
        result_iterator = [
            item for item in QueryResult(
                query,
                self.entity_instance,
                limit=1
            )._get_fetch_iterator()
        ]
        return self.entity_instance._mount_from_google_entity(
            result_iterator[0]
        ) if result_iterator else None

    def filter(
        self,
        order_by: 'Optional[Tuple[str]]'=None,
        projection: 'Optional[Tuple[str]]'=None,
        distinct_on: 'Optional[Tuple[str]]'=None,
        parent_id: 'Optional[Tuple[str]]'=None,
        **kwargs
    ) -> 'QueryResult':
        query = self.__mount_query(
            filters=self.__process_filters(kwargs),
            parent_id=parent_id,
            projection=projection,
            order_by=order_by,
            distinct_on=distinct_on,
        )
        return QueryResult(query, self.entity_instance)

    def __mount_query(
        self,
        filters: 'Optional[Tuple[str, str, Any]]'=None,
        order_by: 'Optional[Tuple[str]]'=None,
        projection: 'Optional[Tuple[str]]'=None,
        distinct_on: 'Optional[Tuple[str]]'=None,
        parent_id: 'Optional[Tuple[str]]'=None
    ) -> 'GoogleQuery':
        return self.partial_query(
            filters=(filters or ()),
            ancestor=(parent_id or None),
            projection=(projection or ()),
            order=(order_by or ()),
            distinct_on=(distinct_on or ()),
        )

    def __process_filters(self, filter_dict: 'Dict') -> 'Tuple[str, str, Any]':
        OPERATIONS_TO_QUERY = {
            "eq": "=",
            "gt": ">",
            "ge": ">=",
            "lt": "<",
            "le": "<="
        }
        DEFAULT_QUERY_OPERATION = "eq"

        result = []
        for key, value in filter_dict.items():
            processed_key = key.split("__")
            _key = processed_key[0]
            _operation = processed_key[1] if len(processed_key) > 1 else DEFAULT_QUERY_OPERATION
            _operation = OPERATIONS_TO_QUERY[_operation]
            result.append((self.entity_instance._convert_property_name(_key), _operation, value))

        return tuple(result)
