import os
import requests
import datetime
import dateutil.parser as parsedate
from flask import jsonify, request



QUANDL_ROOT_URL = 'https://www.quandl.com/api/v3/datasets/'

# parameters needed for the correct quandl calls
quandl_request_params = (
    ('api_key', os.environ['QUANDL_APIKEY']),
    ('column_index', '1'),
    ('limit', '1')
)

# all metals and their listing data needed to make successful quandl calls
metal_commodities = {
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


def get_price(index, symbol):
    """ get the price for a single security from quandl

    [args]
        index (str): shortcode for the security index
        symbol (str): 4 letter shortcode symbol for the security
    """

    new_price = {}

    # concatenate the index and symbol to the base Quandl URL
    url = QUANDL_ROOT_URL + index + "/" + symbol + "/"

    # make the request with your fancy new url
    response = requests.get(url=url, params=quandl_request_params)

    # if the request is successful, parse the response, return the new price
    if response.status_code == 200:
        new_price['date'] = response.json()['dataset']['data'][0][0]
        new_price['price'] = response.json()['dataset']['data'][0][1]

        return new_price
    
    # if the call fails, log the error
    else:
        print(response.status_code)
        print("error: bad response from Quandl or improper request")
        
        # TODO: do more than log the error, return something that is passed to the user




def update_prices(commodities):
    """ Request and add pricing for all commodities in a properly formatted
    dictionary

    [args]
        commodities (dict): dict must include --
            "commodity_id" : {
                'name': user friendly name,
                'index': index_id from quandl,
                'symbol': commodity_id from quandl,
                'units': 'troy_ounce'
            }
    """

    today = datetime.date.today().isoformat()

    for i in commodities:
        try:
            # verify that the metal has a price
            commodities[i]['spot_price']

            # verify that the price isn't too old
            price_date = commodities[i]['spot_price']['date']
            delta = parsedate.parse(today) - parsedate.parse(price_date)
            assert(delta.days < 7)

            # log success
            print("{} has price, is up to date".format(
                commodities[i]['symbol'])
            )

        except:
            # if the price doesn't exist, or is too old - update/add it.
            commodities[i]['spot_price'] = get_price(
                commodities[i]['index'],
                commodities[i]['symbol']
            )
            print("Price updated for {}".format(commodities[i]['symbol']))



def weight_conversion(mass, units):
    """ Convert a users weight to troy ounces

    [args]
        mass (int): the user's total mass
        units (str): must be 'lbs' or 'kg'
    """

    if units == "lbs":
        return mass * 14.5833
    elif units == "kg": 
        return mass * 32.151
    else:
        return 0



def price_by_weight(mass, price):
    """ Take the mass in troy ounces and return a computed price

    [args]
        mass (int or float): must be in troy ounces for the correct results
        price (float): price should be taken from a commodity
    """

    return mass * price



def current_base_prices():
    """ return the current prices for all commodities

    [args]
        none
    """

    update_prices(metal_commodities)

    response = {
        "code": 200,
        "status": "success",
        "data": metal_commodities
    }

    return jsonify(response)



def all_metals():
    """ compare the user's weight and networth to all metals
    to determine the metal that most closely matches their weight
    in that metal.

    [args]
        none
    """

    update_prices(metal_commodities)

    weight_in = {}
    weight_in_diff = {}

    try:
        # parse and check that params from the request are valid
        weight = request.args.get('weight', type=int)
        units = request.args.get('units', type=str)
        networth = request.args.get('networth', type=int)

        assert(weight is not None)
        assert(units == "lbs" or units == "kg")
        assert(networth is not None)

        converted_mass = weight_conversion(weight, units)

        # get the price for the user's mass in each metal
        for i in metal_commodities:
            price = price_by_weight(
                converted_mass,
                metal_commodities[i]['spot_price']['price']
            )

            # determine the closest metal in the user's mass 
            # to the user's networth
            weight_in[metal_commodities[i]['name']] = '${:,.2f}'.format(price)
            weight_in_diff[metal_commodities[i]['name']] = abs(networth - price)

        response = {
            "code": 200,
            "status": "success",
            "data": {
                "inputs": {
                    "weight": weight,
                    "units": units,
                    "networth": '${:,.2f}'.format(networth)
                },
                "weight_in": weight_in,
                "closest_metal": ("Based on your networth, you most closely "        "match your weight in {}".format(
                    min(weight_in_diff, key = weight_in_diff.get)
                    )
                )
            }
        }

    except AssertionError as error:
        print('Error: invalid args - {}'.format(error))
        response = {
            "code": 400,
            "status": "Fail",
            "message": "badRequest: invalid or missing arguments"
        }

    return jsonify(response)



def single_metal(metal):
    """ return the user's value by their weight, for a single metal

    [args]
        metal (str): must be included in the request url
    """

    update_prices(metal_commodities)

    weight_in = {}

    try:
        # parse and check that params from the request are valid
        weight = request.args.get('weight', type=int)
        units = request.args.get('units', type=str)

        assert(metal.lower() in metal_commodities.keys())
        assert(weight is not None)
        assert(units == "lbs" or units == "kg")

        converted_mass = weight_conversion(weight, units)

        price = price_by_weight(
                converted_mass,
                metal_commodities[metal.lower()]['spot_price']['price']
            )

        weight_in = (metal_commodities[metal.lower()]['name'], price)

        response = {
            "code": 200,
            "status": "Success",
            "data": {
                "message": "You're weight in {} is ${:,.2f}".format(
                    weight_in[0], 
                    weight_in[1]
                )
            }
        }

    except AssertionError as error:
        print('Error: invalid args - {}'.format(error))
        response = {
            "code": 400,
            "status": "Fail",
            "message": "badRequest: invalid or missing arguments"
        }

    return jsonify(response)