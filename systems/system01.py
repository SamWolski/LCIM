## system 1 - (H,L)->E

nw = Network(network_name)

nw.add_road("High Priority Entry", 300, priority = 3)
nw.add_road("Low Priority Entry", 50, priority = 2)
nw.add_road("Exit", 50, priority = 1)

nw.roads[1].critical_distance = 5.0
nw.roads[1].speed_limiter = 0.67

nw.add_insertion_point(0)
nw.add_insertion_point(1)

nw.add_intersection(2, [0,1])

##