from tracemalloc import start
from web3 import Web3
from dotenv import load_dotenv
import os
import requests
# Load environment variables in .env
load_dotenv()
ALCHEMY_KEY = os.getenv("ALCHEMY_KEY")

# Ensure that Alchemy URL was set
if not ALCHEMY_KEY:
    print("No ALCHEMY_KEY was configured in .env!")
    exit(0)

# Configure the provider for web3
ALCHEMY_URL = f'https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}'
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

def uploadCollectionToS3(tokenIdImageUrlPairList: list[tuple[str, str]]):
    

    
c = getImageURIs("0x93980f2F30Da266b0667f38A191dc7E92703293F")
print(c)