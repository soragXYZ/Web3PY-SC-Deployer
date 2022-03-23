import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solcx import compile_source
import solcx
source = "./Carte.sol"
file = "Carte.sol"

from dotenv import load_dotenv
load_dotenv()

if not "PRIVATE_KEY" in os.environ:
    exit("ENV VAR PRIVATE_KEY not defined")
if not "RPC_URL" in os.environ:
    exit("ENV VAR RPC_URL not defined")

PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
RPC_URL     = os.environ.get("RPC_URL")

web3 = Web3(Web3.WebsocketProvider(RPC_URL, websocket_timeout=20))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

# set public address from private key
deployer_address = web3.eth.account.privateKeyToAccount(PRIVATE_KEY).address



spec = {
        "language": "Solidity",
        "sources": {
            file: {
                "urls": [
                    source
                ]
            }
        },
        "settings": {
            "optimizer": {
               "enabled": False
            },
            "outputSelection": {
                "*": {
                    "*": [
                        "metadata", "evm.bytecode", "abi"
                    ]
                }
            }
        }
    }
out = solcx.compile_standard(spec, allow_paths=".",solc_version="0.8.4")
abi = out['contracts']['Carte.sol']['Card']['abi']
bytecode = out['contracts']['Carte.sol']['Card']['evm']['bytecode']['object']



Carte = web3.eth.contract(abi=abi, bytecode=bytecode)

# if deploying to rinkeby, remove gasPrice: 0
# deploy
tx = Carte.constructor(
        "hhhh",
        1,
        "0xF90aCf91BdAB539aAC3093E5C5b207b562354401"
    ).buildTransaction({
        'nonce': web3.eth.getTransactionCount(deployer_address),
        'gasPrice': 0,
        'gas': 10000000
    })
signed_tx  = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
send_tx    = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
receipt_tx = web3.eth.wait_for_transaction_receipt(send_tx)

print(receipt_tx.contractAddress)