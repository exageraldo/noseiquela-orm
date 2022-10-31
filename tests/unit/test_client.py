import os
from unittest import mock

import pytest
from google.cloud.datastore.query import Query as GQuery

from noseiquela_orm.client import DatastoreClient

from .utils import mount_entity


def test_default_datastore_client():
    out = DatastoreClient()

    assert out.project == os.environ['DATASTORE_PROJECT_ID']
    assert out.namespace == None # default


def test_datastore_client_with_custom_project_and_namespace():
    project = 'custom-project'
    namespace = 'custom-namespace'

    out = DatastoreClient(
        project=project,
        namespace=namespace,
    )

    assert (out.project, out.namespace) == (project, namespace)


def test_datastore_client_save():
    entity = mount_entity("some-kind", 1, first_prop=1, second_prop=42)

    with mock.patch(
        'google.cloud.datastore.client.Batch'
    ) as batch:
        DatastoreClient().save(entity)
        batch.return_value.put.assert_called_once_with(entity)


def test_datastore_client_bulk_save():
    entities = [
        mount_entity("some-kind", 1, first_prop=1, second_prop=42),
        mount_entity("some-kind", 2, first_prop=1, second_prop=42),
    ]

    with mock.patch(
        'google.cloud.datastore.client.Batch'
    ) as batch:
        DatastoreClient().bulk_save(entities)
        batch.return_value.call_count == len(entities)
        batch.return_value.put.call_args_list == entities


def test_datastore_client_get_partial_query():
    kind = "some-kind"
    part_query = DatastoreClient().get_partial_query(kind)
    out = part_query()

    assert isinstance(out, GQuery)
    assert out.project == os.environ['DATASTORE_PROJECT_ID']
    assert out.kind == kind
