from fastapi import FastAPI
from tasks import processNftCollection
from db_access import db

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/collections/{contract_addr}')
def handleNftImageRequest(contract_addr: str):
    # First, let's check if this NFT contract address has already been requested and is either queued 
    # up or has finished
    dbRecord = db.contracts3link.find_first(
        where={
            'contractAddress': contract_addr
        }
    )

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
        #TODO Now, let's call the celery task 
        processNftCollection.delay(contract_addr)
        # Return that the job has been queued
        return {'s3Link': 'queued'}

