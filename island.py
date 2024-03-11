class Island(object):
    def __init__(self, x, y, number):
        self.x = x
        self.y = y
        self.number = number
        self.bridges = []

    def add_bridge(self, bridge):
        self.bridges.append(bridge)