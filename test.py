import csv
import random
import string
import time

from tree import *


def data_from_file(data_file='data/cities.csv'):
    with open(data_file) as f:
        csv_reader = csv.reader(f)
        cities = [c for city, in csv_reader]
    return cities


def random_generator(n_samples=250,
                     chars=string.ascii_uppercase + string.ascii_lowercase):
    return [''.join(random.choice(chars) for x in range(random.randint(5, 20)))
            for _ in range(n_samples)]


# cities = data_from_file()
cities = random_generator(n_samples=30000)
tree = empty_node()
for city in cities:
    tree_add(tree, city)

n_samples = len(cities)
print(n_samples)
print(cities[:10])


def do_test(n):
    accum = [0.0, 0.0, 0.0]
    for i in range(n):
        target = random.choice(cities)
        #if i%1000 == 0: print(target)

        # Brute force
        start = time.time()
        for city in cities:
            if city == target:
                break
        end = time.time()
        assert city == target
        accum[0] += end - start

        # Min. effort
        start = time.time()
        i = cities.index(target)
        end = time.time()
        assert cities[i] == target
        accum[1] += end - start

        # Custom
        start = time.time()
        t = tree_search(tree, target)
        end = time.time()
        assert root_value(t) == target
        accum[2] += end - start

    print("1) Takes around %f seconds to find a sample" % (accum[0] / (1.0*n)))
    print("2) Takes around %f seconds to find a sample" % (accum[1] / (1.0*n)))
    print("3) Takes around %f seconds to find a sample" % (accum[2] / (1.0*n)))


print("")
n = n_samples/100
print("Try with %d" % n)
do_test(n)
print("")
n = n_samples/10
print("Try with %d" % n)
do_test(n)
print("")
n = n_samples/2
print("Try with %d" % n)
do_test(n)
print("")
n = 2*n_samples/3
print("Try with %d" % n)
do_test(n)
