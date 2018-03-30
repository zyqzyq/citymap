# things.py

# Let's get this party started!
import falcon
from city import CityResource, SearchResource

api = application = falcon.API()

city = CityResource()
search = SearchResource()
api.add_route('/city', city)
api.add_route('/search/{east_longitude}/{north_latitude}', search)

