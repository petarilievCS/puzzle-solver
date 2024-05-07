from bridge import Bridge

class Island(object):
    def __init__(self, x, y, number):
        self.x = x
        self.y = y
        self.number = number
        self.bridges = []

    def add_bridge(self, bridge):
        self.bridges.append(bridge)

    def done(self, bridge_map):
        total_sum = 0
        for bridge_id in self.bridges:
            bridge = bridge_map[bridge_id]
            if bridge.done():
                total_sum += bridge.minimum
        return total_sum == self.number
    
    def over(self, bridge_map):
        total_sum = 0
        for bridge_id in self.bridges:
            bridge = bridge_map[bridge_id]
            if bridge.done():
                total_sum += bridge.minimum
        return total_sum > self.number