from fastapi import FastAPI
from tasks import processNftCollection
from db_access import db
from constants import IS_TESTING
import logging.config
from datetime import datetime, timezone

# Logging config
logging.config.fileConfig('./logConfig/logging.ini')
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/collections/{contract_addr}')
def handleNftImageRequest(contract_addr: str):
    # First, let's check if this NFT contract address has already been requested and is either queued 
    # up or has finished
    logger.debug(f'API endpoint hit for contract address: {contract_addr}')
    dbRecord = db.contracts3link.find_first(
        where={
            'contractAddress': contract_addr
        }
    )
    logger.debug(f'DB Queried for contract addr: {contract_addr} || and it found a record of {dbRecord}')

    # Case 1: DbRecord is found, and status is finished (we have the S3 link we can return)
    if dbRecord and dbRecord.status == 'finished':
        return {"s3Link": dbRecord.s3Link, 'status': dbRecord.status}

    # Case 2: DbRecord is found, and status is in-progress (the job has been picked up by a worker node)
    # and some images (but not all) have been uploaded
    if dbRecord and dbRecord.status == 'in-progress':
        return {"s3Link": dbRecord.s3Link, 'status': dbRecord.status}

    # Case 3: DbRecord is found, and status is pending (the job is currently in the celery queue OR
    # has been picked up by a worker node but no images have been uploaded to S3 yet for that collection)
    elif dbRecord and dbRecord.status == 'pending':
        #  If the task has been pending for more than 2 hour, allow for queueing it again
        timeNow = datetime.now(timezone.utc)
        secondsElapsedSincePending = (timeNow - dbRecord.updatedAt).total_seconds()
        if secondsElapsedSincePending > 2*3600:
            logger.error(f'Task for contract addr: {contract_addr} has been queued for \
            {secondsElapsedSincePending} amount of time. We will requeue this task')
        else:
            return {"s3Link": dbRecord.s3Link, 'status': dbRecord.status}

    # Case 4: No DbRecord is found, we want to kick off a celery task to download the data
    else:
        # First mark that we are queing up this job
        newDbRecord = db.contracts3link.upsert(
            data={
                'create': {
                    'contractAddress': contract_addr,
                    's3Link': 'null',
                    'status': 'pending',
                },
                'update': {
                    's3Link': 'null',
                    'status': 'pending',
                }
            },
            where={
                'contractAddress': contract_addr
            }
        )
        logger.debug(f'Starting celery task for {contract_addr}')
        # Now, let's call the celery task 
        processNftCollection.delay(contract_addr)
        # Return that the job has been queued
        return {"s3Link": newDbRecord.s3Link, 'status': newDbRecord.status}

