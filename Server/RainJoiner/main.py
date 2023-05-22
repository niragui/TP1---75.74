import time
import os

from rain_joiner_worker import RainJoinerWorker


def main():
    time.sleep(10)
    print("Up!")

    filters = int(os.environ["FILTER"])

    worker = RainJoinerWorker(filters)

    worker.run()


if __name__ == "__main__":
    main()
