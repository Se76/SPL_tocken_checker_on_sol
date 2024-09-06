import requests
import json
import datetime 
from datetime import datetime
from telethon.sync import TelegramClient
from telethon import events
from telethon import TelegramClient, events
from time import sleep
import csv
import asyncio


def nameAndSymbole(address):
    i = 0
    i_max = 25
    url = f"https://api.dexscreener.io/latest/dex/tokens/{address}"
    site = requests.get(url)
    zeitlich = json.loads(site.content.decode("utf-8"))
    while i < i_max and not zeitlich.get("pairs"):
        sleep(5)
        site = requests.get(url)
        zeitlich = json.loads(site.content.decode("utf-8"))
        i += 1
    info_dict = {}

    if zeitlich["pairs"] == None:

        info_dict['DexScreener'] = None

    else:
        info_dict['name'] = zeitlich["pairs"][0]["baseToken"]["name"] # name 
        info_dict['symbol'] = zeitlich["pairs"][0]["baseToken"]["symbol"] # symbol
        info_dict['current_mcap'] = zeitlich["pairs"][0]["fdv"] # market cap
        try:
            utc_createdAt = datetime.utcfromtimestamp(zeitlich["pairs"][0]["pairCreatedAt"]/1000) # pairCreatedAt
            time_now = datetime.utcnow()
            difference = time_now - utc_createdAt
            print(f"Прошло времени: {difference.days} days, {difference.seconds // 3600} часов, {(difference.seconds // 60) % 60} минут.")
        except KeyError:
            info_dict['utc_createdAt'] = None
        
        info_dict['liquidity'] = f"{zeitlich['pairs'][0]['liquidity']['quote']} SOL"

        try:
            zeitlich['pairs'][0]['info']['imageUrl']
        except KeyError:
            info_dict['Socials on DexScreener'] = None
        else:
            info_dict['image on dex'] = True
            info_dict['image on dex url'] = zeitlich['pairs'][0]['info']['imageUrl']
            try:
                zeitlich['pairs'][0]['info']['websites'][0]['url']
            except KeyError and IndexError:
                info_dict['website on dex'] = None
            else:
                info_dict['website on dex'] = True
                info_dict['website on dex url'] = zeitlich['pairs'][0]['info']['websites'][0]['url']
            try:
                for socialNetwork in range(len(zeitlich['pairs'][0]['info']['socials'])):
                    try: 
                        info_dict[zeitlich['pairs'][0]['info']['socials'][socialNetwork]['type']] = True
                        info_dict[f"{zeitlich['pairs'][0]['info']['socials'][socialNetwork]['type']} url"] = zeitlich['pairs'][0]['info']['socials'][socialNetwork]["url"]
                        
                    except KeyError:
                        print("there is no socials")
            except KeyError:
                info_dict['Twiiter'] = False


    return info_dict



def solcanApi(address):

    solscan = { }

    headers = {
    "cookie": "-------------------------------------------------------------------",
    "sol-aut": "B9dls0fK",
    "referer": "https://solscan.io/",
    "origin": "https://solscan.io",
    "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    }



    response_solscan_uri_link = requests.get(f'https://api.solscan.io/v2/account?address={address}', headers=headers) # &cluster
    print(response_solscan_uri_link.status_code)
    print(response_solscan_uri_link.content)
    response_solscan_uri_link_py = json.loads(response_solscan_uri_link.content.decode("utf_8"))

    # uri_link = requests.get(response_solscan_uri_link_py['data']['metadata']['data']['uri'])

    solscan['Authority'] = True
    if response_solscan_uri_link_py["data"]["tokenInfo"]["tokenAuthority"] == None and response_solscan_uri_link_py['data']["tokenInfo"]["freezeAuthority"] == None\
        or response_solscan_uri_link_py["data"]["tokenInfo"]["tokenAuthority"] == '11111111111111111111111111111111' and response_solscan_uri_link_py['data']["tokenInfo"]["freezeAuthority"] == '11111111111111111111111111111111'\
        or response_solscan_uri_link_py["data"]["tokenInfo"]["tokenAuthority"] == '11111111111111111111111111111111' and response_solscan_uri_link_py['data']["tokenInfo"]["freezeAuthority"] == None\
        or response_solscan_uri_link_py["data"]["tokenInfo"]["tokenAuthority"] == None and response_solscan_uri_link_py['data']["tokenInfo"]["freezeAuthority"] == '11111111111111111111111111111111':
            solscan['Authority'] = False

    supply = float(response_solscan_uri_link_py['data']['tokenInfo']['supply'])         
    decimals = float(response_solscan_uri_link_py['data']['tokenInfo']['decimals'])

    #print(supply // (10.0 ** decimals)) # SUPPLY FROM TOKEN
    solscan['supply'] = supply // (10.0 ** decimals)
    global full_supply
    full_supply = solscan['supply']
    

    top_10_supply_res = requests.get(f'https://api.solscan.io/v2/token/holders?token={address}&offset=0&size=10&cluster', headers=headers)
    top_10_supply_py = json.loads(top_10_supply_res.content.decode('utf-8'))
    with open('tg_mes.py', "w") as fp:
            fp.write(str(top_10_supply_py))
    

    # all holders

    solscan['holders'] = top_10_supply_py["data"]["total"]
    
    # top 10 

    top_10 = top_10_supply_py["data"]["result"]
    for person in range(len(top_10)):
        amount_dec = top_10[person]['amount']
        decimals_top10 = top_10[person]['decimals']

        amount = amount_dec // (10 ** decimals_top10)
        percentage = amount / solscan['supply'] * 100

        # Token accounts and owner accounts 

        try:
            token_account = top_10[person]['address']
            owner_account = top_10[person]['owner']
        except KeyError:
            pass

        try: 
            if owner_account == '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1':
                solscan['Raydium Liquidity Pool V4'] = f' {round(percentage, 1)}%'
            else:
                solscan[owner_account] = f' {round(percentage, 1)}%'
        except UnboundLocalError or KeyError:
            pass
        

        

    solscan['updateAuthority'] = response_solscan_uri_link_py['data']['metadata']['updateAuthority']
    if response_solscan_uri_link_py['data']['metadata']['updateAuthority'] == 'TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM':
        print('THE TOKEN IS SCAM, DEV ADDRESS IS TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM or CREATOR IS PUMPFUN')
        #quit()

    uri = response_solscan_uri_link_py['data']['metadata']['data']['uri'] 
    res_uri = requests.get(uri)                                             
    res_uri_py = json.loads(res_uri.content.decode('utf-8'))

    
    try:
        solscan['twitter_solscan_url'] = res_uri_py['twitter']
        solscan['twitter_solscan'] = True
    except KeyError:
        try:
            if res_uri_py["extensions"]["twitter"] != "":
                solscan['twitter_solscan_url'] = res_uri_py['extensions']['twitter']
                solscan['twitter_solscan'] = True
            else:
                solscan['twitter_solscan'] = False
        except KeyError:
            solscan['twitter_solscan'] = False
    
# telegram_solscan checker on solscan

    try:
        solscan['telegram_solscan_url'] = res_uri_py['telegram']
        solscan['telegram_solscan'] = True
    except KeyError:
        try:
            if res_uri_py["extensions"]["telegram"] != "":
                solscan['telegram_solscan_url'] = res_uri_py['extensions']['telegram']
                solscan['telegram_solscan'] = True
            else:
                solscan['telegram_solscan'] = False                
        except KeyError:
            solscan['telegram_solscan'] = False
    
        
# Image checker on solscan

    try:
        if res_uri_py['image']:
            solscan['image_solscan'] = True
            solscan['image_solscan_url'] = res_uri_py['image']
    except KeyError:
        solscan['image_solscan'] = True

# website_solscan checker on sol scan

    try:
        #if res_uri_py['website_solscan'] or res_uri_py["extensions"]["website_solscan"]:
        solscan['website_solscan_url'] = res_uri_py['website']
        solscan['website_solscan'] = True
    except KeyError:
        try: 
            if res_uri_py["extensions"]["website"] != "":
                solscan['website_solscan_url'] = res_uri_py["extensions"]["website"]
                solscan['website_solscan'] = True
            else:
                solscan['website_solscan'] = False
        except KeyError:
            solscan['website_solscan'] = False
    
    # OWNER BALANCE

    owner_balance_res = requests.get(f'https://api.solscan.io/v2/account?address={solscan["updateAuthority"]}&cluster', headers=headers)
    owner_balance_py = json.loads(owner_balance_res.content.decode('utf-8'))
    solscan['owner_sol_balance'] = 0
    try:
        solscan['owner_sol_balance'] = owner_balance_py['data']['lamports'] / (10 ** 9)
    except KeyError:
        solscan['owner_sol_balance'] = 0


    return solscan

    

def lp_checker(token_adress, updateAuthority):
    SolanaInc = False
    LiquidityTokenDec = False
    TokenInc = False
    info_dict = {}
    headers = {
        "cookie": "-------------------------------------------------------------------",
        "referer": "https://solscan.io/",
        "origin": "https://solscan.io",
        # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    }
    offset = 0
    res = requests.get(f'https://api.solscan.io/v2/account/token/txs?address={updateAuthority}&limit=40&offset={offset}&account_type=account_main', headers=headers)
    print(res.status_code)
    print(res.status_code)
    print(res.status_code)
    res_py = json.loads(res.content.decode('utf-8'))
    print(res.content)
    info_dict['BURN STATUS'] = 'NO BURNT'
    total = res_py['data']['tx']['total']
    
    liquidity_token_address = None
    #  res = requests.get(f'https://api.solscan.io/v2/account/token/txs?address={updateAuthority}&limit=1000&offset=0&account_type=non-existence', headers=headers)
    i = 0

    info_dict['RUG'] = False
    if updateAuthority == 'TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM':
        info_dict['LIQUIDITY'] == [' ADDRESS IS TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM']

    
    while total != 0:
        i += 1
        # print(total)
        # print(i)
        txs = res_py['data']['tx']['transactions']
        for tx in range(len(txs))[::-1]:
            # zashlo
            
            if txs[tx]['change']['tokenAddress'] == token_adress:
                if txs[tx]['change']['changeType'] == 'dec' or int(txs[tx]['change']['postBalance']) < int(txs[tx]['change']['preBalance']):
                    temporary_url = f'https://api.solscan.io/v2/transaction-v2?tx={txs[tx]["txHash"]}'
                    temporary_res = requests.get(temporary_url, headers=headers)
                    temporary_py = json.loads(temporary_res.content.decode('utf-8'))
                    for program in temporary_py['data']['programs_involved']:
                        if program == '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8':  # Raydium App adress
                            lp_tx = txs[tx]["txHash"]
                            info_dict['liquidityPool_tx'] = lp_tx

                            for token_change in temporary_py['data']['token_bal_change']:
                                if token_change['token_address'] != token_adress and token_change['token_address'] != 'So11111111111111111111111111111111111111112':
                                    liquidity_token_address = token_change['token_address'] # adress of lp tokens
                         
                                    amount_liquidity_tokens = token_change['post_balance'] # amount of lp tokens
                                    info_dict['liquidity_token_address'] = liquidity_token_address
                                    info_dict['amount_liquidity_tokens'] = amount_liquidity_tokens
                                if token_change['change_type'] == 'dec' and token_change['token_address'] == token_adress \
                                    or token_change['token_address'] == token_adress and int(token_change['post_balance']) < int(token_change['pre_balance']):
                                    transfered_tokens_to_lp = -int(token_change['change_amount']) / (10 ** token_change['decimals'])
                                    info_dict['transfered_tokens_to_lp_var'] = transfered_tokens_to_lp
                         
                                    #global transfered_tokens_to_lp_var
                                    #transfered_tokens_to_lp_var = transfered_tokens_to_lp
                                    # full_supply = 9999975
                                    info_dict['transfered_tokens_to_lp'] = f"{(int(transfered_tokens_to_lp)/int(full_supply))*100}%"
                                    info_dict['transfered_tokens_to_lp_percentage'] = int((int(transfered_tokens_to_lp)/int(full_supply))*100)
                                if token_change['token_address'] == 'So11111111111111111111111111111111111111112' and token_change['owner'] == '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1':
                                    info_dict['transferedSolanaToLp'] = int(token_change['change_amount']) / (10 ** token_change['decimals'])
                                try:                  
                                    key = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"                                    
                                    data = requests.get(key)   
                                    data = data.json() 
                                    sol_price = data['price']
                                    info_dict['launch Market Capitalization'] = ((float(info_dict['transferedSolanaToLp']) * float(sol_price)) / float(info_dict['transfered_tokens_to_lp_var'])) * float(full_supply) # 
                                except (KeyError, ZeroDivisionError) as e: # UnboundLocalError or IndexError or ZeroDivisionError
                                    if e == ZeroDivisionError:
                                        info_dict['RUG'] = True

                               

                                try:
                                    if txs[tx]['change']['changeType'] == 'closedAccount' and txs[tx]['change']['tokenAddress'] == liquidity_token_address\
                                        or txs[tx]['change']['changeType'] == 'dec' and txs[tx]['change']['tokenAddress'] == liquidity_token_address\
                                        or int(txs[tx]['change']['postBalance']) < int(txs[tx]['change']['preBalance']) and txs[tx]['change']['tokenAddress'] == liquidity_token_address:
                                        info_dict['BURN STATUS'] = 'LIQUIDITY BURNT'
                                    elif txs[tx+1]['change']['changeType'] == 'inc' and txs[tx + 1]['change']['tokenAddress'] == token_adress and txs[tx + 1]['txHash'] == txs[tx]['txHash']:
                                    #txs[txs.index(tx) + 1]['change']['changeType'] == 'inc' and txs[txs.index(tx) + 1]['change']['tokenAddress'] == token_adress and txs[txs.index(tx) + 1]['txHash'] == tx['txHash']:
                                        info_dict['RUG'] = 'RUG RUG RUG RUG RUG RUG RUG RUG RUG RUG RUG'
                                except Exception as e:  #UnboundLocalError or IndexError:
                                    pass

            #try:
            elif txs[tx]['change']['tokenAddress'] == liquidity_token_address:
                slot = txs[tx]['slot']
                info_dict['slot'] = slot
                if txs[tx]['change']['changeType'] == 'dec' or int(txs[tx]['change']['postBalance']) < int(txs[tx]['change']['preBalance']):
                    print('CHECK_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST')
                    if txs[tx+1]['change']['tokenAddress'] == token_adress or txs[tx+1]['change']['tokenAddress'] == 'So11111111111111111111111111111111111111112' and \
                    txs[tx]['change']['changeType'] == 'inc' or int(txs[tx]['change']['postBalance']) > int(txs[tx]['change']['preBalance']) or\
                    txs[tx+2]['change']['tokenAddress'] == token_adress or txs[tx+2]['change']['tokenAddress'] == 'So11111111111111111111111111111111111111112' and txs[tx]['slot'] == slot and\
                    txs[tx]['change']['changeType'] == 'inc' or int(txs[tx]['change']['postBalance']) > int(txs[tx]['change']['preBalance']) or\
                    txs[tx-1]['change']['tokenAddress'] == token_adress or txs[tx-1]['change']['tokenAddress'] == 'So11111111111111111111111111111111111111112' and txs[tx]['slot'] == slot and\
                    txs[tx]['change']['changeType'] == 'inc' or int(txs[tx]['change']['postBalance']) > int(txs[tx]['change']['preBalance']) or \
                    txs[tx-2]['change']['tokenAddress'] == token_adress or txs[tx-2]['change']['tokenAddress'] == 'So11111111111111111111111111111111111111112' and txs[tx]['slot'] == slot and\
                    txs[tx]['change']['changeType'] == 'inc' or int(txs[tx]['change']['postBalance']) > int(txs[tx]['change']['preBalance']):
                        print('CHECK_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST')
                        #  if txs[tx+1]['change']['tokenAddress'] == token_adress or txs[tx+1]['change']['tokenAddress'] == 'So11111111111111111111111111111111111111112' and \
                        #     txs[tx]['change']['changeType'] == 'inc' or int(txs[tx]['change']['postBalance']) > int(txs[tx]['change']['preBalance']):
                        # if slot == txs[tx+1]['slot']:
                        txLiquidityPool = txs[tx]['txHash']

                        txLiquidityPoolRes = requests.get(f'https://api.solscan.io/v2/transaction-v2?tx={txLiquidityPool}', headers=headers)
                        txLiquidityPoolResPy = json.loads(txLiquidityPoolRes.content.decode('utf-8'))
                        tokenChanges = txLiquidityPoolResPy['data']['token_bal_change']
                        # print(txLiquidityPool)
                        
                        for tokenChangeNum in range(len(txLiquidityPoolResPy['data']['token_bal_change'])):
                            # print(tokenChangeNum)
                            if tokenChanges[tokenChangeNum]['token_address'] == liquidity_token_address\
                            and tokenChanges[tokenChangeNum]['owner'] == updateAuthority:
                                if tokenChanges[tokenChangeNum]['change_type'] == "dec"\
                                or int(tokenChanges[tokenChangeNum]['post_balance']) < int(tokenChanges[tokenChangeNum]['pre_balance']):
                                    # print(tokenChanges[tokenChangeNum])
                                    LiquidityTokenDec = True
                                    # print('LiquidityTokenDecLiquidityTokenDecLiquidityTokenDecLiquidityTokenDecLiquidityTokenDecLiquidityTokenDec')

                            elif tokenChanges[tokenChangeNum]['token_address'] == token_adress\
                            and tokenChanges[tokenChangeNum]['owner'] == updateAuthority:
                                if tokenChanges[tokenChangeNum]['change_type'] == "inc"\
                                or int(tokenChanges[tokenChangeNum]['post_balance']) > int(tokenChanges[tokenChangeNum]['pre_balance']):
                                    TokenInc = True
                                    # print('TokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenIncTokenInc')

                            elif tokenChanges[tokenChangeNum]['token_address'] == 'So11111111111111111111111111111111111111112'\
                            and tokenChanges[tokenChangeNum]['owner'] == '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1':
                                if tokenChanges[tokenChangeNum]['change_type'] == "dec"\
                                or int(tokenChanges[tokenChangeNum]['post_balance']) < int(tokenChanges[tokenChangeNum]['pre_balance']):
                                    SolanaInc = True
                                    # print('SolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaIncSolanaInc')


                            if LiquidityTokenDec == True and TokenInc == True and SolanaInc == True:
                                info_dict['rug_rug'] = 'rugurugururufdfhkdhjshjdahjdjrugrugrugurugrugurgurgrugrug'
                                info_dict['RUG'] = True
                                # print('CHECK_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST_FIRTST_FIRST_FIRST_FIRST_FIRST')
                                


                            else:
                                info_dict['BURN STATUS'] = 'LIQUIDITY BURNT'
                    else:
                        info_dict['BURN STATUS'] = 'LIQUIDITY BURNT'
        
        offset = offset + 40

        res = requests.get(f'https://api.solscan.io/v2/account/token/txs?address={updateAuthority}&limit=40&offset={offset}&account_type=account_main', headers=headers)
        res_py = json.loads(res.content.decode('utf-8'))
        total = res_py['data']['tx']['total']
        
    return info_dict


def percentage(transfered: float or int, lp_amount: float or int) -> dict:
    res = {
        "percentage": (transfered/lp_amount)*100
    }
    return res
    



global global_address
global_address = None


def functions(afd_hui):
    info = nameAndSymbole(afd_hui)
    for key, val in info.items():
        print(f'{key}: {val}')

    solscan = solcanApi(afd_hui)
    for key1, val1 in solscan.items():
        print(f'{key1}: {val1}')

    dct = lp_checker(afd_hui, solscan['updateAuthority'])
    for key2, val2 in dct.items():
        print(f'{key2}: {val2}')


async def delayed_check(address, updateAuthority):
    await asyncio.sleep(180)  
    
    return lp_checker(address, updateAuthority)
    

def topTransaktionen(address: str) -> dict:
    headers = {
        "cookie": "-------------------------------------------------------------------",
        "sol-aut": "B9dls0fK",
        "referer": "https://solscan.io/",
        "origin": "https://solscan.io",
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    }
    pageNumber = 1
    getLink = f'https://api-v2.solscan.io/v2/token/transfer?address={address}&page={pageNumber}&page_size=50&remove_spam=false&exclude_amount_zero=false'
    getReq = requests.get(getLink, headers=headers)
    getReqPy = json.loads(getReq.content.decode('utf-8'))

    while getReqPy['data'] is not None:
        TransactionList = getReqPy['data']
        for _ in range(len(getReqPy['data'])):
            if TransactionList[_]['activity_type'] == 'ACTIVITY_SPL_TRANSFER':
                pass
    pass


async def process_address(address: str) -> None:
    loop = asyncio.get_event_loop()
    
    info = await loop.run_in_executor(None, nameAndSymbole, address)
    for key, val in info.items():
        print(f'{key}: {val}')

    solscan = await loop.run_in_executor(None, solcanApi, address)
    for key1, val1 in solscan.items():
        print(f'{key1}: {val1}')

    delayed_check_task = asyncio.create_task(delayed_check(address, solscan['updateAuthority']))

    dct = await delayed_check_task
    for keyd, vald in dct.items():
        print(f'{keyd}: {vald}')
    
    res = await loop.run_in_executor(None, percentage, dct['transfered_tokens_to_lp_var'], solscan['supply'])
    for keyy, itemm in res.items():
        print(keyy, itemm)

    if solscan['Authority'] == False and dct['RUG'] == False \
        and solscan['updateAuthority'] != 'TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM'\
        and dct['transferedSolanaToLp'] >= 4.0 and dct['transferedSolanaToLp'] <= 25.0\
        and res['percentage'] >= 60 and res['percentage'] <= 101 : # and int(info['current_mcap']) > 6000



        
        with open("statistikAsyncioNight1.csv", "a") as fp:
            writer = csv.writer(fp)
            row1 = [address ,info['name'], info['symbol'], info['current_mcap'], info['liquidity'], solscan['Authority'], solscan['supply'], solscan['holders'], solscan['updateAuthority'], solscan['twitter_solscan'], solscan['telegram_solscan'], solscan['image_solscan'], solscan['website_solscan'], solscan['owner_sol_balance'], \
                dct['BURN STATUS'], dct['liquidityPool_tx'], dct['transferedSolanaToLp'], dct['transfered_tokens_to_lp'], dct['launch Market Capitalization']]
            writer.writerow(row1)





async def telegram():
    with open("statistikAsyncioNight1.csv", "a") as fp:
        writer = csv.writer(fp)
        row = ["address" ,"name", "symbol", "current_mcap", "liquidity", "Authority",       "supply", "holders", "updateAuthority", "twitter_solscan", \
               "telegram_solscan", "image_solscan", "website_solscan", "owner_sol_balance",           "BURN STATUS", "liquidityPool_tx", \
                "transferedSolanaToLp", "transfered_tokens_to_lp", "launch Market Capitalization"]
        writer.writerow(row)
    api_id = ---------------                       # api id        
    api_hash = '----------'                     # api hash
    phone_number = "-----------------"         # phone number        

    client = TelegramClient('anon', api_id, api_hash)

    @client.on(events.NewMessage(chats=-1002109566555)) # flux  -1002109566555 - -1002109566555    solana scaner - -1002023951506
    async def my_event_handler(event):
        text = event.raw_text
        if "Platform: Raydium" in text:
            parts = text.split("Base: ")
            if len(parts) > 1:
                address = parts[1].split("\nQuote:")[0]
                print(address)
                global global_address
                global_address = address
                await process_address(address)  # Call the synchronous function
        #parts = text.split("🏠 Address: \n")
        # parts = text.split("Base: ")
        #address = parts[1].split("\n")[0]
        # address = parts[1].split("\nQuote:")[0]

        



          # Update the global variable
                

    await client.start(phone_number)
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(telegram())



