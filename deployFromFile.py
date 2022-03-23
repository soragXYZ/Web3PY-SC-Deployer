import os
from web3 import Web3
from web3.middleware import geth_poa_middleware
from solcx import compile_source

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

with open("./Greeter.sol", "r") as file:
    Greeter_file = file.read()

compiled_sol = compile_source(Greeter_file, output_values=['abi','bin'])
contract_id, contract_interface = compiled_sol.popitem()
bytecode = contract_interface['bin']
abi      = contract_interface['abi']

Greeter = web3.eth.contract(abi=abi, bytecode=bytecode)

# if deploying to rinkeby, remove gasPrice: 0
# deploy
tx = Greeter.constructor(
        "Hello world"
    ).buildTransaction({
        'nonce': web3.eth.getTransactionCount(deployer_address),
        #'gasPrice': 0
        })
signed_tx  = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
send_tx    = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
receipt_tx = web3.eth.wait_for_transaction_receipt(send_tx)


greeter = web3.eth.contract(address=receipt_tx.contractAddress, abi=abi)

# see what is in greeting in the Smart Contract (lign 5)
print(greeter.functions.greet().call())

# change greeting in the SC
tx = greeter.functions.setGreeting(
        'Bonjour monde'
    ).buildTransaction({
        'nonce': web3.eth.getTransactionCount(deployer_address),
        #'gasPrice': 0
        })
signed_tx  = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
send_tx    = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
receipt_tx = web3.eth.wait_for_transaction_receipt(send_tx)

print(greeter.functions.greet().call())