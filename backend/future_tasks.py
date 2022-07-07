from web3 import Web3
import os
import requests
from constants import ALCHEMY_URL, IMAGE_CACHE_DIR
import mimetypes

# Configure the provider for web3
w3 = Web3(Web3.HTTPProvider(ALCHEMY_URL))

def getContractNameAndTotalSupply(contract_addr: str) -> dict:
    """Fetch the name of the contract (if present) and the total number of NFTs in this collection

    Args:
        contract_addr (str): Ethereum address of the NFT collection

    Returns:
        dict: 'name' of the contract if present (else empty string) and the 'totalSupply'
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
    res_json = server_res.json()['contractMetadata']
    return {
        'name': res_json['name'],
        'totalSupply': res_json['totalSupply']
    }

def getImageURIs(contract_addr: str) -> list[tuple[str, str]]:
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
    startToken = 0
    while True:
        server_res = requests.get(
            f'{ALCHEMY_URL}/getNFTsForCollection',
            params={
                'contractAddress': contract_addr,
                'withMetadata': "true",
                'startToken': startToken
            },
            allow_redirects=True
        )
        
        if server_res.status_code != 200 or not server_res.json():
            return imageURI_list
        res_json = server_res.json()
        # Get the image URIs for all the NFTs returned in this response
        for nftData in res_json['nfts']:
            # Cast to int to convert string hex to base 10 number
            tokenId = int(nftData['id']['tokenId'], 16)
            imageUri = nftData['media'][0]['gateway']
            imageURI_list.append((tokenId, imageUri))

        # If no next token then we are done
        if not res_json['nextToken']:
            break

        # update start Token (need to convert to decimal number from hex string)
        startToken = int(res_json['nextToken'], 16)

        #TODO - break below is only to prevent pagination during test
        if (startToken > 1):
            return res_json

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
    for tokenId, imageURL in tokenIdImageUrlPairList:
        # make the request to the server/gateway
        server_res = requests.get(
            imageURL,
            allow_redirects=True
        )
        # Let's guess whether this file is PNG or JPEG using the content header
        contentTypeHeader = server_res.headers['content-type'] 
        # Default to .jpg if we content type header doesn't tell us encoding format
        fileExtension = mimetypes.guess_extension(contentTypeHeader) or '.jpg'
        filePath = f'{IMAGE_CACHE_DIR}/{tokenId}{fileExtension}'
        with open(filePath, 'wb') as f:
            f.write(server_res.content)

    return


def uploadCollectionToS3(contract_addr: str, contractMetadata: dict, tokenIdImageUrlPairList: list[tuple[str, str]]):
    # Download images in batches of 50 
    # Batch upload the images to S3
    # Delete the images locally 
    # Repeat until all images have been uploaded to S3
    # TODO: Should update the DB updating the contract addr -> S3 bucket URL mapping

    
c = getImageURIs("0x93980f2F30Da266b0667f38A191dc7E92703293F")
print(c)