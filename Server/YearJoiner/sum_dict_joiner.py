class SumDictJoiner():
    def __init__(self):
        self.sums = {}

    def check_update_value(self, new_value):
        if len(new_value) != 2:
            error = "AverageJoiner Expect A Tuple (Str, Int/Float)"
            error += f"{new_value} is not this"
            raise Exception(error)

        if not isinstance(new_value[0], str):
            error = "AverageJoiner Expect A Tuple (Str, Int/Float)"
            error += f"{new_value} is not this"
            raise Exception(error)

        if not isinstance(new_value[1], int) and not isinstance(new_value[1], float):
            error = "AverageJoiner Expect A Tuple (Str, Int/Float)"
            error += f"{new_value} is not this"
            raise Exception(error)

    def update(self, new_value):
        self.check_update_value(new_value)

        key = new_value[0]
        value = new_value[1]

        before = self.sums.get(key, 0)
        new = before + value
        self.sums.update({key: new})

    def get_value(self):
        return self.sums
