class Bridge(object):
    def __init__(self, id, start, end, horizontal):
        self.id = id
        self.planks = 0
        self.marked = False
        self.start = start
        self.end = end
        self.horizontal = horizontal
        self.done = False
        self.maximum = 3
        self.minimum = 0

        self.indices = []
        if horizontal:
            for i in range(start[1] + 1, end[1]):
                self.indices.append((start[0], i))
        else:
            for i in range(start[0] + 1, end[0]):
                self.indices.append((i, start[1]))
