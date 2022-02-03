from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import Contract, ContractFunction
from web3.types import ChecksumAddress, HexBytes, Nonce, TxParams, TxReceipt, Wei
from decimal import Decimal
from typing import Dict, List, NamedTuple, Optional, Set, Tuple
import private
import settings
import time

bsc = "https://bsc-dataseed.binance.org/"
bsc_testnet = 'https://data-seed-prebsc-1-s1.binance.org:8545/'
web3 = Web3(Web3.HTTPProvider(bsc_testnet))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

factory = web3.eth.contract(address=settings.FACTORY, abi=settings.FACTORY_ABI)
router = web3.eth.contract(address=settings.PANCAKE_ROUTER_TESNET, abi=settings.PANCAKE_ABI)
sender_address = web3.toChecksumAddress(private.SENDER_WALLET)

def find_lp_address(
        token_address: ChecksumAddress, base_token_address: ChecksumAddress
    ) -> Optional[ChecksumAddress]:
        pair = factory.functions.getPair(token_address, base_token_address).call()
        if pair == '0x' + 40 * '0':  # not found, don't cache
            return None
        return Web3.toChecksumAddress(pair)

def get_bnb_balance() -> Decimal:
        return Decimal(web3.eth.get_balance(private.SENDER_WALLET)) / Decimal(10 ** 18)

def buy(tokenToBuy : ChecksumAddress, amount):
    sender = Web3.toChecksumAddress(private.SENDER_WALLET)

    transaction = router.functions.swapExactETHForTokens(
    0, # set to 0, or specify minimum amount of token you want to receive - consider decimals!!!
    [Web3.toChecksumAddress(settings.WBNB_TESTNET), tokenToBuy],
    sender,
    (int(time.time()) + 10000)
    ).buildTransaction({
    'from': sender,
    'value': web3.toWei(amount,'ether'), #This is the Token(BNB) amount you want to Swap from
    'gasPrice': web3.toWei('10','gwei'),
    'nonce': web3.eth.get_transaction_count(sender),
    })

    try:
        signed_transaction = web3.eth.account.sign_transaction(transaction, private_key=private.PRIVATE_KEY)
        tx_token = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        print(f"Snipe concluido: {web3.toHex(tx_token)}")

    except Exception as e:
        print(f'Ocorreu um erro na sua transação: {e}')


def main():
    # contract = web3.eth.contract(address=settings.BUSD_TESTNET)
    # print(find_lp_address(Web3.toChecksumAddress(settings.TEZOS), Web3.toChecksumAddress(settings.WBNB)))
    # buy(Web3.toChecksumAddress(settings.BUSD_TESTNET), 0.0001)
    # print(get_bnb_balance())


main()