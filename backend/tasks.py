import os
import requests
from constants import ALCHEMY_URL, IMAGE_CACHE_DIR, DEFAULT_RATE_LIMIT_COOLDOWN_TIME, MAX_COOLDOWN_TIME, \
    AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME, BUCKET_URL_PREFIX, IS_TESTING
import datetime
import mimetypes
import time
import boto3
import shutil
from db_access import db
from celery import Celery
import logging.config

# Celery config
app = Celery('tasks')
app.config_from_object('celeryconfig')

# Configure AWS S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

# Logging config
logging.config.fileConfig('./logConfig/logging.ini')
logger = logging.getLogger(__name__)

def getContractName(contract_addr: str) -> str:
    """Fetch the name of the contract (if present)

    Args:
        contract_addr (str): Ethereum address of the NFT collection

    Returns:
        str: name of this contract
    """
    # Use the alchemy NFT enchanced API
    server_res = requests.get(
        f'{ALCHEMY_URL}/getContractMetadata',
        params={
            'contractAddress': contract_addr
        },
        allow_redirects=True
    )
    if server_res.status_code != 200 or not server_res.json():
        return ''
    res_json: dict = server_res.json()['contractMetadata']
    name = res_json.get('name', 'NFT Name Unknown')
    logger.debug(f'For contract addr: {contract_addr} we got a name of : {name}')
    return name

def getTokenIdImageURIs(contract_addr: str, _startToken: int = 0, limit: int = 100) -> list[tuple[str, str]]:
    """Given a contract address for an NFT, this function will fetch the imageURIs for 
    every NFT in the collection

    Args:
        contract_addr (str): Ethereum address of the NFT collection

    Returns:
        list[tuple[str, str]]: A list of all the image URIs for each NFT in the collection where each elemnt 
        is a tuple of the form (tokenId: str, ImageURI: str)
    """
    imageURI_list = list()
    # N.B: Enhanced API below only returns up to 100 NFTs at a time, 
    # so we need to paginate through until we get all of the NFTs
    startToken = _startToken
    totalImageURIsFetched = 0
    while True:
        logger.debug(f'Fetching imageURI data from alchemy for {contract_addr} with start token {startToken}')
        server_res = requests.get(
            f'{ALCHEMY_URL}/getNFTsForCollection',
            params={
                'contractAddress': contract_addr,
                'withMetadata': "true",
                'startToken': startToken,
                'limit': min(limit, 100)
            },
            allow_redirects=True
        )

        # if the server return status code of 429, it means we are being rate-limited, so let's stop
        if server_res.status_code == 429:
            logger.info(f'getTokenIdImageURIs received 429 status code for {contract_addr}')
            server_suggested_retry = server_res.headers.get('Retry-After', 0)
            # Wait a max of 4 minutes no matter what
            time_to_sleep = min(MAX_COOLDOWN_TIME, max(server_suggested_retry, DEFAULT_RATE_LIMIT_COOLDOWN_TIME)) 
            logger.info(f'getTokenIdImageURIs sleeping for: {time_to_sleep}')
            time.sleep(time_to_sleep)
            # Use continue to go back to the start of the loop and try downloading this image again
            continue
        
        elif server_res.status_code != 200 or not server_res.json():
            logger.error(f'For contract addr: {contract_addr} in getTokenIdImageURIs we got status code of : {server_res.status_code} \
                when the startToken was: {startToken}')
            return imageURI_list
        
        res_json = server_res.json()
        # Get the image URIs for all the NFTs returned in this response
        for nftData in res_json['nfts']:
            # Cast to int to convert string hex to base 10 number
            tokenId = int(nftData['id']['tokenId'], 16)
            imageUri = nftData['media'][0]['gateway']
            imageURI_list.append((tokenId, imageUri))

        totalImageURIsFetched += len(res_json['nfts'])

        # If the total # of tokens we got is >= limit, then we're done
        if totalImageURIsFetched >= limit or len(res_json['nfts']) == 0:
            break

        # If no next token then we are done
        if not res_json.get('nextToken', None):
            break

        # update start Token (need to convert to decimal number from hex string)
        startToken = int(res_json['nextToken'], 16)

        # Break below is only to prevent pagination during test
        if (IS_TESTING):
            return imageURI_list

    logger.debug(f'Got all image URIs for contract addr: {contract_addr}')
    return imageURI_list

def downloadImagesLocally(tokenIdImageUrlPairList: list[tuple[str, str]]): 
    """Downloads all images in the tokenIdImageUrlPairList locally

    Args:
        tokenIdImageUrlPairList (list[tuple[str, str]]): List of (tokenId, ImageURL) tuples
    """
    # Create image cache folder if it doesn't already exist
    if not os.path.isdir(IMAGE_CACHE_DIR):
        os.makedirs(IMAGE_CACHE_DIR)
    
    # Now let's loop through all the images and download them locally
    i = 0
    while i < len(tokenIdImageUrlPairList):
        tokenId, imageURL = tokenIdImageUrlPairList[i]
        # make the request to the server/gateway
        server_res = requests.get(
            imageURL,
            allow_redirects=True
        )
        # if the server return status code of 429, it means we are being rate-limited, so let's stop
        if server_res.status_code == 429:
            logger.info(f'downloadImagesLocally received 429 status code for tokenId: {tokenId} and imageUrl: {imageURL}')
            server_suggested_retry = server_res.headers.get('Retry-After', 0)
            # Wait a max of 4 minutes no matter what
            time_to_sleep = min(MAX_COOLDOWN_TIME, max(server_suggested_retry, DEFAULT_RATE_LIMIT_COOLDOWN_TIME)) 
            logger.info(f'downloadImagesLocally sleeping for: {time_to_sleep}')
            time.sleep(time_to_sleep)
            # Use continue to go back to the start of the loop and try downloading this image again
            continue

        # Let's guess whether this file is PNG or JPEG using the content header
        contentTypeHeader = server_res.headers.get('content-type', None)
        # Default to .jpg if we content type header doesn't tell us encoding format
        fileExtension = mimetypes.guess_extension(contentTypeHeader) or '.jpg'
        filePath = f'{IMAGE_CACHE_DIR}/{tokenId}{fileExtension}'
        with open(filePath, 'wb') as f:
            f.write(server_res.content)
        i += 1

    # By default, let's sleep for 2 seconds to avoid rate-limiting
    time.sleep(2)
    return

def uploadImagesToS3(contract_addr: str, contractName: str, imageDirectory: str):
    """Uploads all images in 'imageDirectory' to an S3 bucket

    Args:
        contract_addr (str): Address of the contract
        contractMetadata (dict): Name and Total Supply of the contract
        imageDirectory (str): Directory where images are locally downloaded
    """
    nft_dir_name = f'{contractName} ({contract_addr})'
    for rootDir, _, files in os.walk(imageDirectory):
        for file in files:
            try:
                s3.upload_file(Filename=f'{rootDir}/{file}', Bucket=BUCKET_NAME, Key=f'{nft_dir_name}/{file}')
            except Exception as e:
                logger.error(e, exc_info=True)

@app.task
def processNftCollection(contract_addr: str):
    """Given a contract address will fetch images and upload them to S3

    Args:
        contract_addr (str): The address of the contract
    """
    logger.debug(f'Begin processNftCollection for contract address {contract_addr}')
    try:
        dbRecord = db.contracts3link.find_first(
            where={
                'contractAddress': contract_addr
            }
        )
        # In the event this task is re-queued, let's skip images we already uploaded
        i = dbRecord.numImagesUploaded

        contractName = getContractName(contract_addr)
        S3_Link = f'{BUCKET_URL_PREFIX}&prefix={contractName}+%28{contract_addr}%29/&showversions=false'
        logger.debug(f'S3 Link for contract name: {contractName} and contract addr: {contract_addr} is {S3_Link}')
        increment_jump = 50
        while True:
            # Fetch the tokenID and Image URIs
            tokenIdImageUrlPairList = getTokenIdImageURIs(contract_addr, _startToken = i, limit = increment_jump)
            # Break condition - if no more metadata is returned
            if not tokenIdImageUrlPairList:
                break
            # Download images in batches of 'increment_jump' 
            downloadImagesLocally(tokenIdImageUrlPairList)
            # Batch upload the images to S3
            uploadImagesToS3(contract_addr, contractName, IMAGE_CACHE_DIR)
            # Delete the images locally to free up space
            if os.path.isdir(IMAGE_CACHE_DIR):
                shutil.rmtree(IMAGE_CACHE_DIR)
            # Repeat until all images have been uploaded to S3
            i += increment_jump
            logger.debug(f'Finished one batch for {contract_addr} with i:{i}')
            # On every loop, update the current NUM_IMAGES_UPLOADED, so that we can pick up where we left
            # off in the event of having to re-queue this 
            db.contracts3link.update(
                where={
                    'contractAddress': contract_addr
                },
                data={
                    'numImagesUploaded': i,
                    's3Link': S3_Link,
                    'status': 'in-progress'
                }
            )
            logger.debug(f'Uploaded {i} images for contract address: {contract_addr}')

        # Update DB at end to signal that we have uploaded all images in the collection
        db.contracts3link.upsert(
            data={
                'create': {
                    'contractAddress': contract_addr,
                    's3Link': S3_Link,
                    'status': 'finished'
                },
                'update': {
                    'status': 'finished'
                }
            }, 
            where={
                'contractAddress': contract_addr
            }
        )
    except Exception as e:
        logger.error(e, exc_info=True)