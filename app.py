from flask import Flask, jsonify, request
from weightin import current_base_prices, all_metals, single_metal



app = Flask(__name__)



@app.route('/weightin/currentprices', methods=['GET'])
def return_current_base_prices():
    return current_base_prices()



@app.route('/weightin/all_metals', methods=['GET'])
def return_all_metals():
    return all_metals()



@app.route('/weightin/<metal>', methods=['GET'])
def return_single_metal(metal):
    return single_metal(metal)




if __name__ == '__main__':
    app.run(debug=True)
