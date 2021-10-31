class QueryResult:
    def __init__(self, query, entity_instance, limit=None, offset=0, retry=None, timeout=None) -> None:
        self.query = query
        self.limit = limit
        self.offset = offset
        self.retry = retry
        self.timeout = timeout
        self.entity_instance = entity_instance

    def first(self):
        result = list(self.query.fetch(
            limit=1,
            retry=self.retry,
            timeout=self.timeout
        ))
        return self.entity_instance._create_from_google_entity(
            result[0]
        ) if result else None

    def _get_query_result(self):
        for entity in self.query.fetch(
            limit=self.limit,
            offset=self.offset,
            retry=self.retry,
            timeout=self.timeout
        ):
            yield self.entity_instance._create_from_google_entity(
                entity
            )

    def __iter__(self):
        return self._get_query_result()

    def __next__(self):
        yield from self._get_query_result()


class Query:
    def __init__(self, partial_query, entity_instance) -> None:
        self.partial_query = partial_query
        self.entity_instance = entity_instance

    def all(self, order_by=None, projection=None):
        _query = self.partial_query(
            order=(order_by or ()),
            projection=(projection or ()),
        )
        return QueryResult(_query, self.entity_instance)

    def filter(self, order_by=None, projection=None, distinct_on=None, parent_id=None, **kwargs):
        filter_list = self._process_filters(kwargs)
        _query = self.partial_query(
            filters=filter_list,
            ancestor=parent_id,
            projection=(projection or ()),
            order=(order_by or ()),
            distinct_on=(distinct_on or ()),
        )
        return QueryResult(_query, self.entity_instance)


    def _process_filters(self, filter_dict):
        OPERATIONS_TO_QUERY = {
            "eq": "=",
            "gt": ">",
            "ge": ">=",
            "lt": "<",
            "le": "<="
        }
        DEFAULT_QUERY_OPERATION = "eq"

        OPERATIONS_TO_VALIDATE = {
            "in": None
        }

        result = []
        for key, value in filter_dict.items():
            processed_key = key.split("__")
            _key = processed_key[0]
            _operation = processed_key[1] if len(processed_key) > 1 else DEFAULT_QUERY_OPERATION
            _operation = OPERATIONS_TO_QUERY[_operation]
            result.append((self.entity_instance._convert_property_name(_key), _operation, value))

        return tuple(result)
