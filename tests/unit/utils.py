import os

from google.cloud.datastore.entity import Entity as GEntity
from google.cloud.datastore.key import Key as GKey


def mount_key(kind, id_or_name=None, parent=None):
    key = GKey(
        kind,
        parent=parent,
        project=os.environ['DATASTORE_PROJECT_ID']
    )

    return (
        key.completed_key(id_or_name)
        if id_or_name
        else key
    )


def mount_entity(kind, id_or_name, parent=None, **props):
    """
    Responsible for assisting in the setting up of an entity.

    Parameters:
            kind (str): entity kind
            id_or_name (int|str): entity id

    Returns:
        (GEntity): ``Entity`` instance
    """
    entity = GEntity(
        key=mount_key(kind, id_or_name, parent)
    )
    entity.update(props)
    return entity
