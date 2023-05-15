class AverageJoiner():
    def __init__(self):
        self.average = None
        self.amount = 0
        super().__init__()

    def update(self, new_value):
        if not isinstance(new_value, int):
            error = "AverageJoiner Expect An Int, "
            error += f"{new_value} is {type(new_value)}"
            raise Exception(error)
        if self.amount == 0:
            self.amount = 1
            self.average = new_value
            return

        prev_total = self.average * self.amount
        new_total = prev_total + new_value
        self.amount += 1
        self.average = new_total / self.amount

    def get_value(self):
        return self.average
