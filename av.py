# get account value from weighted-averaging a few diff webscraped sites with estimated values
#
# for adding new accounts:
#     add new accounts to .env file as "Nickname=topshot_accountname"
# for new estimated value sites:
#     add new value estimatation endpoint in 'url'
#     add new weight to 'weights'
#     create new per site parsing logic
import sys
from dotenv import dotenv_values
from bs4 import BeautifulSoup
import requests
import json

accounts = dict(dotenv_values(".env.av_accounts"))
for name in accounts:
    # a URL for each of the endpoints that is being scraped per account
    url = {'MR': f'https://momentranks.com/topshot/account/{accounts[name]}',
           'OTM': f'https://otmnft.com/account_valuation/?username={accounts[name]}',
           'CS': f'https://api2.cryptoslam.io/api/owners/TS:{accounts[name]}/get-csv-for-owner'}
    # weights for the weighted-average calculation
    weights = (10, 6, 3)
    if len(url) != len(weights):
        print("There must be one assigned weight-factor to each URL")
        sys.exit()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
               "Accept": "text/html,application/xhtml+xml,application/xml"}
    val = {}
    marketspend = 0
    for key in url:
        val[key] = 0
        r = requests.get(url[key], headers=headers)  # need to add headers for cryptoslam.io
        if r.status_code is not requests.codes.ok:
            print(f'{key}:{r.status_code} requesting {url[key]}')
            break
        else:
            soup = BeautifulSoup(r.text, 'html.parser')
            if key == 'MR':
                content = soup.find_all('div', {"class": "AccountView_h3__3V6cV"})
                for i in content[0].find('b'):
                    val[key] = int(str(i.text).split('$')[1].replace(",", "").strip())
                for i in content[5].find('b'):
                    marketspend = int(str(i.text).split('$')[1].replace(",", "").strip())
            elif key == 'OTM':
                content = soup.find('div', {"class": "col-lg-auto my-auto"})
                for i in content.find('h2'):
                    val[key] = int(str(i.text).split('$')[1].replace(",", "").strip())
            elif key == 'CS':
                data = json.loads(soup.contents[0])
                val[key] = int(str(data["csv"]).split('.')[0].strip())
        #print(f'{key}: ${"{:,}".format(val[key])}')  # show individual site values
    wa_numer = sum([list(val.values())[x]*weights[x] for x in range(len(val))])
    wa_denom = sum(weights)
    weighted_average = round(wa_numer/wa_denom)
    print(f'{name}\'s NBA TopShot Collection\n  Est Value: ${"{:,}".format(weighted_average)}'
          f'\n  Marketplace Spend: ${"{:,}".format(int(marketspend))}'
          f'\n  Gain/Loss ($): {"{:+,}".format(int(weighted_average - marketspend))} (ignores pack costs)\n')
