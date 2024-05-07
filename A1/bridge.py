class Bridge(object):
    def __init__(self, id, start, end, horizontal):
        self.start = start
        self.end = end
        self.horizontal = horizontal
        self.maximum = 3
        self.minimum = 0
        self.crossings = []

        self.indices = []
        if horizontal:
            for i in range(start[1] + 1, end[1]):
                self.indices.append((start[0], i))
        else:
            for i in range(start[0] + 1, end[0]):
                self.indices.append((i, start[1]))

    def done(self):
        return self.maximum == self.minimum
