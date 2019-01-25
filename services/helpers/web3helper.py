from django.conf import settings
import web3
from web3 import Web3
from web3.contract import ConciseContract
import json
import os

class Web3Helper:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
        with open(str( settings.BASE_DIR + '/truffle/build/contracts/LEToken.json'), 'r') as abi_definition:
            self.abi = json.load(abi_definition)['abi']
        self.contract_address = "0xA44C1aE4A46193d8373355849D3fFebf68A8143F"
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi)
        self.concise_contract = ConciseContract(self.contract)

        self.admin_account = self.w3.eth.account.privateKeyToAccount(os.getenv('ADMIN_ETH_SECRET', ''))
        pass

    def mint_token(self, address, amount):
        nonce = self.w3.eth.getTransactionCount(self.admin_account.address)
        mintTx = self.contract.functions.mint(address, amount).buildTransaction({
            'chainId': 3,
            'gas': 70000,
            'gasPrice': self.w3.toWei('1', 'gwei'),
            'nonce': nonce,
        })
        signed_txn = self.w3.eth.account.signTransaction(mintTx, private_key=self.admin_account.privateKey)
        self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        pass

web3helper = Web3Helper()
