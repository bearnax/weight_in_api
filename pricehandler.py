import os
import requests
import datetime
import dateutil.parser as parsedate

# api_key = os.environ['QUANDL_APIKEY']

root_url = 'https://www.quandl.com/api/v3/datasets/'

static_params = (
    ('api_key', 'WsDSG12F6dWzyHV5y_9o'),
    ('column_index', '1'),
    ('limit', '1')
)

def return_price(index, symbol):
    new_price = {}

    url = root_url + index + "/" + symbol + "/"
    response = requests.get(url=url, params=static_params)

    if response.status_code == 200:
        new_price['date'] = response.json()['dataset']['data'][0][0]
        new_price['price'] = response.json()['dataset']['data'][0][1]
        return new_price
    else:
        print(response.status_code)
        print("error: bad response from Quandl or improper request")



def check_pricing(metals):
    today = datetime.date.today().isoformat()

    for i in metals:
        try:
            # verify that the metal has a price
            metals[i]['spot_price']

            # verify that the price isn't too old
            price_date = metals[i]['spot_price']['date']
            delta = parsedate.parse(today) - parsedate.parse(price_date)
            assert(delta.days < 7)

            # log success
            print("{} has price, is up to date".format(metals[i]['symbol']))
        except:
            metals[i]['spot_price'] = return_price(
                metals[i]['index'],
                metals[i]['symbol']
            )
            print("Price updated for {}".format(metals[i]['symbol']))