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
    # server_res = requests.post(
    #     ALCHEMY_URL,
    #     allow_redirects=True,
    #     json={
    #         "jsonrpc": "2.0",
    #         "method": "alchemy_getTokenMetadata",
    #         "params": [f'{contract_addr}'],
    #         "id": 42
    #     }
    # )
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

def getMetadataURIs(contract_addr: str) -> list[str]:
    """Given a contract address for an NFT, this function will fetch the metadataURIs for 
    every NFT in the collection

    Args:
        contract_addr (str): Ethereum address of the NFT collection

    Returns:
        list[str]: A list of all the metadata URIs for each NFT in the collection
    """

    
c = getContractNameAndTotalSupply("0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D")
print(c)