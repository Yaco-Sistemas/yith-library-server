import uuid


def create_client_id_and_secret(application):
    application['client_id'] = str(uuid.uuid4())
    application['client_secret'] = str(uuid.uuid4())
