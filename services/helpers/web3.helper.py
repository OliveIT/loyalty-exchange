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

        self.admin_account = self.w3.eth.account.privateKeyToAccount(os.getenv('admin_secret_key', ''))
        pass

    def mint_token(self, address, amount):
        nonce = self.w3.eth.getTransactionCount(self.admin_account.address)
        self.contract.functions.mint(adderss, amount).buildTransaction({
            'chainId': 3,
            'gas': 70000,
            'gasPrice': self.w3.toWei('1', 'gwei'),
            'nonce': nonce,
        })
        signed_txn = w3.eth.account.signTransaction(unicorn_txn, private_key=private_key)
        
        admin_private = "0xaaaaaaaaaaaaaaaaaaaaa"
        # tx_hash = self.contract.functions.mint(address, amount).transact({'from': self.w3.eth.accounts[0], 'gas': 1000000, })
        tx_hash = self.concise.mint(address, amount, transact={'from': self.w3.eth.accounts[1], 'gas': 100000})
        self.w3.eth.waitForTransactionReceipt(tx_hash)
        pass
