from fastapi import FastAPI
from tasks import processNftCollection
from db_access import db
import logging.config

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
        return {"s3Link": dbRecord.s3Link}
    # Case 2: DbRecord is found, and status is pending (the job is currently being processed)
    elif dbRecord and dbRecord.status == 'pending':
        return {"s3Link": "pending"}
    # Case 3: No DbRecord is found, we want to kick off a celery task to download the data
    else:
        # First mark that we are queing up this job 
        db.contracts3link.create(
            data={
                'contractAddress': contract_addr,
                's3Link': 'null',
                'status': 'pending',
            }
        )
        logger.debug(f'Starting celery task for {contract_addr}')
        #TODO Now, let's call the celery task 
        processNftCollection.delay(contract_addr)
        # Return that the job has been queued
        return {'s3Link': 'queued'}

