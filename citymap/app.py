# things.py

# Let's get this party started!
import falcon
from city import CityResource

api = application = falcon.API()

city = CityResource()
api.add_route('/city', city)
