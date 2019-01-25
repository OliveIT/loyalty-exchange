from django.conf import settings
import web3
from web3 import Web3
from web3.contract import ConciseContract
import json
import os

class Web3Helper:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/" + os.getenv('ADMIN_INFURA_API', '')))
        with open(str( settings.BASE_DIR + '/truffle/build/contracts/LoyaltyExchangeToken.json'), 'r') as abi_definition:
            self.abi = json.load(abi_definition)['abi']
        self.contract_address = "0x229C016C59879d2E9E752BF0B026b88C2Ad342F0"
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.abi)
        self.concise_contract = ConciseContract(self.contract)
        self.admin_account = self.w3.eth.account.privateKeyToAccount(os.getenv('ADMIN_ETH_SECRET', ''))
        pass

    def mint_token(self, address, amount):
        try:
            nonce = self.w3.eth.getTransactionCount(self.admin_account.address)
            mintTx = self.contract.functions.mint(address, amount).buildTransaction({
                'chainId': 3,
                'gas': 100000,
                'gasPrice': self.w3.toWei('500', 'gwei'),
                'nonce': nonce,
            })
            signed_txn = self.w3.eth.account.signTransaction(mintTx, private_key=self.admin_account.privateKey)
            tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
        except:
            return tx_hash
    
    def get_balance(self, address):
        return self.contract.functions.balanceOf(address).call()

    def set_token(self, address, amount):
        try:
            nonce = self.w3.eth.getTransactionCount(self.admin_account.address)
            mintTx = self.contract.functions.control(address, amount).buildTransaction({
                'chainId': 3,
                'gas': 100000,
                'gasPrice': self.w3.toWei('500', 'gwei'),
                'nonce': nonce,
            })
            signed_txn = self.w3.eth.account.signTransaction(mintTx, private_key=self.admin_account.privateKey)
            tx_hash = self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            self.w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)
            return tx_hash
        except:
            return False

web3helper = Web3Helper()


    # def mint_token(self, address, amount):
    #     # tx_hash = self.contract.functions.mint(address, amount).transact({'from': self.w3.eth.accounts[0], 'gas': 1000000, })
    #     tx_hash = self.concise.mint(address, amount, transact={'from': self.w3.eth.accounts[1], 'gas': 100000})
    #     self.w3.eth.waitForTransactionReceipt(tx_hash)
    #     pass
