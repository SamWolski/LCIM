## system 2 - (M,M)->E

nw = Network(network_name)

nw.add_road("Entry 1", 300, priority = 2)
nw.add_road("Entry 2", 50, priority = 2)
nw.add_road("Exit", 50, priority = 1)

nw.roads[0].critical_distance = 2.5
nw.roads[0].critical_distance = 2.5

nw.add_insertion_point(0)
nw.add_insertion_point(1)

nw.add_intersection(2, [0,1])

##