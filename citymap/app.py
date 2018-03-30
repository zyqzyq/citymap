# things.py

# Let's get this party started!
import falcon
from city import CityResource, SearchResource, TSPResource

api = application = falcon.API()

city = CityResource()
search = SearchResource()
tsp = TSPResource(city.conn)
api.add_route('/city', city)
api.add_route('/search/{east_longitude}/{north_latitude}', search)
api.add_route('/tsp/{start_east}/{start_north}/{end_east}/{end_north}', tsp)
