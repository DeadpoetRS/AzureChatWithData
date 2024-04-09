import logging
import json
import azure.functions as func
from backend.batch.utilities.helpers.EnvHelper import EnvHelper
from backend.batch.utilities.helpers.AzureBlobStorageHelper import (
    AzureBlobStorageClient,
    create_queue_client,
)

bp_batch_start_processing = func.Blueprint()
env_helper: EnvHelper = EnvHelper()

logger = logging.getLogger(__name__)


@bp_batch_start_processing.route(route="BatchStartProcessing")
def batch_start_processing(req: func.HttpRequest) -> func.HttpResponse:
    return do_batch_start_processing(req)


def do_batch_start_processing(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Requested to start processing all documents received")
    # Set up Blob Storage Client
    azure_blob_storage_client = AzureBlobStorageClient()
    # Get all files from Blob Storage
    files_data = azure_blob_storage_client.get_all_files()
    # Filter out files that have already been processed
    files_data = (
        list(filter(lambda x: not x["embeddings_added"], files_data))
        if req.params.get("process_all") != "true"
        else files_data
    )
    files_data = list(map(lambda x: {"filename": x["filename"]}, files_data))

    # Send a message to the queue for each file
    queue_client = create_queue_client()
    for fd in files_data:
        queue_client.send_message(json.dumps(fd).encode("utf-8"))

    return func.HttpResponse(
        f"Conversion started successfully for {len(files_data)} documents.",
        status_code=200,
    )
