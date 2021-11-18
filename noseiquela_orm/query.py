from typing import Any, Dict, Tuple, Optional, Generator, TYPE_CHECKING
from functools import partial
from google.cloud.datastore.query import Query as GoogleQuery

if TYPE_CHECKING:
    from .entity import Entity

class QueryResult:
    def __init__(
        self,
        query: GoogleQuery,
        entity_instance: 'Entity',
        limit: Optional[int]=None,
        offset: Optional[int]=0,
        retry: Optional[int]=None,
        timeout: Optional[int]=None
    ) -> None:
        self.query = query
        self.limit = limit
        self.offset = offset
        self.retry = retry
        self.timeout = timeout
        self.entity_instance = entity_instance

    def first(self) -> Optional['Entity']:
        result = list(self.query.fetch(
            limit=1,
            retry=self.retry,
            timeout=self.timeout
        ))
        return self.entity_instance._create_from_google_entity(
            result[0]
        ) if result else None

    def _get_query_result(self) -> Generator['Entity', None, None]:
        for entity in self.query.fetch(
            limit=self.limit,
            offset=self.offset,
            retry=self.retry,
            timeout=self.timeout
        ):
            yield self.entity_instance._create_from_google_entity(
                entity
            )

    def __iter__(self) -> Generator['Entity', None, None]:
        return self._get_query_result()

    def __next__(self) -> Generator['Entity', None, None]:
        yield from self._get_query_result()


class Query:
    def __init__(
        self,
        partial_query: partial,
        entity_instance: 'Entity',
    ) -> None:
        self.partial_query = partial_query
        self.entity_instance = entity_instance

    def _mount_query(
        self,
        filters: Optional[Tuple[str, str, Any]]=None,
        order_by: Optional[Tuple[str]]=None,
        projection: Optional[Tuple[str]]=None,
        distinct_on: Optional[Tuple[str]]=None,
        parent_id: Optional[Tuple[str]]=None
    ) -> GoogleQuery:
        return self.partial_query(
            filters=(filters or ()),
            ancestor=(parent_id or None),
            projection=(projection or ()),
            order=(order_by or ()),
            distinct_on=(distinct_on or ()),
        )

    def all(
        self,
        order_by: Optional[Tuple[str]]=None,
        projection: Optional[Tuple[str]]=None
    ) -> 'QueryResult':
        _query = self._mount_query(
            order_by=order_by,
            projection=projection
        )
        return QueryResult(_query, self.entity_instance)

    def filter(
        self,
        order_by: Optional[Tuple[str]]=None,
        projection: Optional[Tuple[str]]=None,
        distinct_on: Optional[Tuple[str]]=None,
        parent_id: Optional[Tuple[str]]=None,
        **kwargs
    ) -> 'QueryResult':
        _query = self._mount_query(
            filters=self._process_filters(kwargs),
            parent_id=parent_id,
            projection=projection,
            order_by=order_by,
            distinct_on=distinct_on,
        )
        return QueryResult(_query, self.entity_instance)

    def _process_filters(self, filter_dict: Dict) -> Tuple[str, str, Any]:
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
