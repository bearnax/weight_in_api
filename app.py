from flask import Flask, jsonify, request
from weight_in import metal_dict, current_prices, everything, weight_in



app = Flask(__name__)

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




@app.route('/weightin/currentprices', methods=['GET'])
def all_prices():
    return current_prices()



@app.route('/weightin/everything', methods=['GET'])
def return_everything():
    return everything()



@app.route('/weightin/<metal>', methods=['GET'])
def single_metal(metal):
    return weight_in(metal)




if __name__ == '__main__':
    app.run(debug=True)
