from flask import Flask, request, jsonify, Response
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, this is a REST service for temperature, stock price, and arithmetic expression evaluation.'

@app.route('/temperature')
def get_temperature():
    airport_code = request.args.get('queryAirportTemp')
    if not airport_code:
        return jsonify({'error': 'Missing queryAirportTemp parameter'}), 400

    temperature = query_temperature(airport_code)
    if temperature is None:
        return jsonify({'error': 'Failed to retrieve temperature'}), 500

    return jsonify({'temperature': temperature})

def get_coordinates(airport_code):
    url = f"http://www.airport-data.com/api/ap_info.json?iata={airport_code}"

    try:
        response = requests.get(url)
        response.raise_for_status()  

        airport_data = response.json()
        latitude = airport_data['latitude']
        longitude = airport_data['longitude']

        return latitude, longitude

    except requests.exceptions.RequestException as e:
        print(f"Error while querying coordinates: {e}")
        return None, None

def query_temperature(airport_code):
    
    api_key = 'bc39aa9b9f122dcf9c850d4831bdfeab'
    latitude, longitude = get_coordinates(airport_code)

    if latitude is None or longitude is None:
        print("Failed to get coordinates for the airport.")
        return None


    url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()  
        weather_data = response.json()

        temperature_kelvin = weather_data['main']['temp']
        temperature_celsius = temperature_kelvin - 273.15

        return temperature_celsius

    except requests.exceptions.RequestException as e:
        print(f"Error while querying temperature: {e}")
        return None

@app.route('/stock-price')
def get_stock_price():
    stock_symbol = request.args.get('queryStockPrice')
    if not stock_symbol:
        return jsonify({'error': 'Missing queryStockPrice parameter'}), 400

    price = query_stock_price(stock_symbol)
    if price is None:
        return jsonify({'error': 'Failed to retrieve stock price'}), 500

    return jsonify({'price': price})

def query_stock_price(stock_symbol):
    # URL pro dotaz na aktuální cenu akcie pomocí symbolu
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock_symbol}&apikey=O2HLYPMEI7EU85ZL"

    try:
        # Odeslání GET požadavku na Alpha Vantage API
        response = requests.get(url)
        response.raise_for_status()  # Zkontroluje, zda byl požadavek úspěšný

        # Získání dat o ceně akcie z odpovědi API
        stock_data = response.json()

        # Získání aktuální ceny akcie
        price = float(stock_data['Global Quote']['05. price'])

        return price

    except requests.exceptions.RequestException as e:
        print(f"Error while querying stock price: {e}")
        return None


@app.route('/evaluate')
def evaluate_expression():
    expression = request.args.get('queryEval')
    if not expression:
        return jsonify({'error': 'Missing queryEval parameter'}), 400

    result = eval(expression)
    if result is None:
        return jsonify({'error': 'Failed to evaluate expression'}), 500

    return format_response(result)



def format_response(result):
    if request.accept_mimetypes.accept_json:
        return jsonify({'result': result})
    elif request.accept_mimetypes.accept_xml:
        root = ET.Element('result')
        root.text = str(result)
        return ET.tostring(root)
    else:
        return Response('Unsupported media type', status=406)

if __name__ == '__main__':
    app.run(debug=True)
