import logging
import json
from js import XMLHttpRequest

from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Esta data la saqué haciendo inspect de https://preciosensurtidor.minem.gob.ar/index/mapa-busqueda-v2

api_url = "https://preciosensurtidor.minem.gob.ar/ws/rest/rest/server.php"
data = {
    "method": "getEmpresasAgrupadasBanderasCombustible",
    "banderas": '["2"]',
    "combustible": "2",
    "bounds": '{"so":{"lat":-31.02066833580396,"lng":-64.16890246056919},"ne":{"lat":-30.951084225109398,"lng":-64.00656818776318}}',
}

price_cache = None


def fetch_fuel_price():
    global price_cache

    if price_cache:
        return price_cache



    req = XMLHttpRequest.new()
    req.open("POST", api_url)
    req.setRequestHeader("Access-Control-Allow-Origin", "*");
    req.send(json.dumps(data))
    output = str(req.response)
    return output

    #response = await http.pyfetch(api_url, data=data, method="POST")

    # https://pyodide.org/en/stable/usage/api/python-api.html#pyodide.http.FetchResponse

    # if not response.ok:
    #     logger.critical(response.status, response.status_text)
    #     return None

    # response_data = response.json()

    # prices = [x["precios"]["2"]["precio"] for x in response_data["resultado"]]
    # price_cache = sum(prices) / response_data["total"]  # Average price
    # logger.info("Computed fuel price: %.2f", price_cache)
    # return price_cache
