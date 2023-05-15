class AverageDictJoiner():
    def __init__(self):
        self.averages = {}
        self.amounts = {}

    def check_update_value(self, new_value):
        if len(new_value) != 2:
            error = "AverageJoiner Expect A Tuple (Str, Int)"
            error += f"{new_value} is not this"
            raise Exception(error)

        if not isinstance(new_value[0], str):
            error = "AverageJoiner Expect A Tuple (Str, Int)"
            error += f"{new_value} is not this"
            raise Exception(error)

        if not isinstance(new_value[1], int):
            error = "AverageJoiner Expect A Tuple (Str, Int)"
            error += f"{new_value} is not this"
            raise Exception(error)

    def update(self, new_value):
        self.check_update_value(new_value)

        key = new_value[0]
        value = new_value[1]

        average = self.averages.get(key, 0)
        amount = self.amounts.get(key, 0)

        if amount == 0:
            self.averages.update({key: value})
            self.amounts.update({key: 1})
            return

        prev_total = average * amount
        new_total = prev_total + new_value
        amount += 1
        average = new_total / amount

        self.averages.update({key: average})
        self.amounts.update({key: amount})

    def get_value(self):
        return self.averages
