from importlib.resources import path
import math
import random as rd

class City:
   def __init__(self, name, location):
      self.name = name
      self.location = location
   def get_name(self):
      return self.name
class Route:
   def __init__(self, route, distance_map):
      self.route = route
      self.length = self.set_length(route, distance_map)
   def set_length(self, route, distance_map):
      sum = 0
      for i in range(0, len(route) - 1):
         sum += distance_map.get_distance_btw_countries(route[i], route[i + 1])
      sum += distance_map.get_distance_btw_countries(route[0], route[-1])
      return sum   
   
class DistanceMap:
   def __init__(self, cities):
      self.map = self.create_distance_map(cities)
      
   def create_distance_map(self, cities):
      map = []
      for i in range(len(cities)):
         map.append([])
         cur_city = cities[i]
         for j in range(len(cities)):
            sum = 0
            for k in range(3):
               sum += (cur_city.location[k] - cities[j].location[k]) ** 2
            map[i].append(math.sqrt(sum))
      return map
   def get_distance_btw_countries(self, city1, city2):
      return self.map[city1.get_name()][city2.get_name()]
      
class GA:
   def __init__(self, cities, distance_map, level = 10, populations = 100 ,variant_rate = 0.3, mutation_rate = 0.01, elite_rate = 0.1):
      self.cities = cities
      self.distance_map = distance_map
      self.level = level
      self.populations = populations
      self.variant_rate = variant_rate
      self.mutation_rate = mutation_rate
      self.elite_rate = elite_rate
      self.best_result = self._create_route()
   def _create_route(self):
      route = []
      while self.cities:
         route.append(self.cities.pop(self.cities.index(rd.choice(self.cities))))
      self.cities = route[:]
      return Route(route, self.distance_map)

   def _create_greedy_route(self):
      route = []
      route.append(self.cities.pop(len(self.cities) - 1))
      while self.cities:
         cur_city = route[len(route) - 1]
         self.cities  = sorted(self.cities, key = lambda x: -self.distance_map.get_distance_btw_countries(cur_city, x))
         route.append(self.cities.pop(len(self.cities) - 1))
      self.cities = route[:]
      return Route(route, self.distance_map)

   def _init_routes(self):
      routes = [self._create_greedy_route()]
      
      for _ in range(self.populations -1):
         routes.append(self._create_route())
      return routes

   def _get_next_gen(self, routes):
      routes.sort(key = lambda x: x.length)
      elites_qty = int(self.populations * self.elite_rate)
      for i in range(elites_qty, self.populations):
         routes[i] = self._crossover(routes[i % elites_qty], routes[i])
      self._update_best_gene(routes[0])

   def _crossover(self, elite, child):
      variant_qty = int(self.variant_rate * len(elite.route))
      elite_gene_set = set() 
      new_child = []
      for elite_city in elite.route[:variant_qty]:
         elite_gene_set.add(elite_city)
         new_child.append(elite_city)
      # new_child = elite.route[:variant_qty]
      for city in child.route:
         if city not in elite_gene_set:
            new_child.append(city) 
      return Route(new_child, self.distance_map)
   
   def _mutate(self, routes):
      mutation_qty = int(self.populations * self.mutation_rate)
      for _ in range(0, mutation_qty):
         mutation_route = routes.pop(routes.index(rd.choice(routes)))
         mutation_route.route = mutation_route.route[::-1]
         routes.append(mutation_route)
      
   def _update_best_gene(self, best_route):
      self.best_result = best_route
         
   def _evolve(self):
      routes = self._init_routes()
      for _ in range(self.level):
         self._get_next_gen(routes)
         self._mutate(routes)

   def _get_best_gene(self):
      return self.best_result

def read_all_points_as_cities(filename):
   f = open(filename)
   cities = []
   points = list(map(lambda x: list(map(lambda x: int(x), x.split(" "))), f.readlines()))[1:]
   for index, point in enumerate(points):
      cities.append(City(index, point))
   f.close()
   return cities

def write_all_points(filename, best_route):
   f = open(filename, "w")
   for city in best_route.route:
      line = str(city.location[0]) + " " + str(city.location[1]) + " " + str(city.location[2]) + "\n"
      f.write(line)
   line = str(best_route.route[0].location[0]) + " " + str(best_route.route[0].location[1]) + " " + str(best_route.route[0].location[2])
   f.write(line)
   f.close()

cities = read_all_points_as_cities("input.txt")
distance_map = DistanceMap(cities)
ga_group = GA(cities, distance_map)
ga_group._evolve()
write_all_points("output.txt", ga_group._get_best_gene())
