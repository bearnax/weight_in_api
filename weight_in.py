import os
import requests
import datetime
import dateutil.parser as parsedate
from flask import Flask, jsonify, request

# api_key = os.environ['QUANDL_APIKEY']

root_url = 'https://www.quandl.com/api/v3/datasets/'

static_params = (
    ('api_key', 'WsDSG12F6dWzyHV5y_9o'),
    ('column_index', '1'),
    ('limit', '1')
)

metal_dict = {
    'silver': {
        'name': 'Silver',
        'index': 'LBMA',
        'symbol': 'SILVER',
        'units': 'troy_ounce'
    },
    'gold': {
        'name': 'Gold',
        'index': 'LBMA',
        'symbol': 'GOLD',
        'units': 'troy_ounce'
    },
    'ruthenium': {
        'name': 'Ruthenium',
        'index': 'JOHNMATT',
        'symbol': 'RUTH',
        'units': 'troy_ounce'
    },
    'iridium': {
        'name': 'Iridium',
        'index': 'JOHNMATT',
        'symbol': 'IRID',
        'units': 'troy_ounce'
    },
    'rhodium': {
        'name': 'Rhodium',
        'index': 'JOHNMATT',
        'symbol': 'RHOD',
        'units': 'troy_ounce'
    },
    'palladium': {
        'name': 'Palladium',
        'index': 'JOHNMATT',
        'symbol': 'PALL',
        'units': 'troy_ounce'
    },
    'platinum': {
        'name': 'Platinum',
        'index': 'JOHNMATT',
        'symbol': 'PLAT',
        'units': 'troy_ounce'
    }
}


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



def weight_conversion(mass, units):
    if units == "lbs":
        return mass * 14.5833
    elif units == "kg": 
        return mass * 32.151
    else:
        return 0



def price_by_weight(mass, price):
    """ Take the mass in troy ounces and return a computed price
    """

    return mass * price



def current_prices():
    check_pricing(metal_dict)

    response = {
        "status_code": 200,
        "data": metal_dict
    }
    return jsonify(response)



def everything():
    check_pricing(metal_dict)

    weight_in = {}
    weight_in_diff = {}

    try:
        weight = request.args.get('weight', type=int)
        units = request.args.get('units', type=str)
        networth = request.args.get('networth', type=int)

        assert(weight is not None)
        assert(units == "lbs" or units == "kg")
        assert(networth is not None)

        converted_mass = weight_conversion(weight, units)

        for i in metal_dict:
            price = price_by_weight(
                converted_mass,
                metal_dict[i]['spot_price']['price']
            )

            weight_in[metal_dict[i]['name']] = '${:,.2f}'.format(price)
            weight_in_diff[metal_dict[i]['name']] = abs(networth - price)

        response = {
            "status_code": 200,
            "inputs": {
                "weight": weight,
                "units": units,
                "networth": '${:,.2f}'.format(networth)
            },
            "weight_in": weight_in,
            "closest_metal": "Based on your networth, you most closely match your weight in {}".format(
                min(weight_in_diff, key = weight_in_diff.get)
            )
        }
    except AssertionError as error:
        print('Error: invalid args - {}'.format(error))
        response = {
            "status_code": 400,
            "status": "badRequest: invalid arguments"
        }

    return jsonify(response)



def weight_in(metal):
    check_pricing(metal_dict)

    weight_in = {}

    try:
        weight = request.args.get('weight', type=int)
        units = request.args.get('units', type=str)

        assert(metal.lower() in metal_dict.keys())
        assert(weight is not None)
        assert(units == "lbs" or units == "kg")

        converted_mass = weight_conversion(weight, units)
        price = price_by_weight(
                converted_mass,
                metal_dict[metal.lower()]['spot_price']['price']
            )

        weight_in = (metal_dict[metal.lower()]['name'], price)

        response = {
            "status_code": 200,
            "message": "You're weight in {} is ${:,.2f}".format(
                weight_in[0], 
                weight_in[1]
            )
        }

    except AssertionError as error:
        print('Error: invalid args - {}'.format(error))
        response = {
            "status_code": 400,
            "status": "badRequest: invalid arguments"
        }

    return jsonify(response)