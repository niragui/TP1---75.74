import time
import os

from montreal_joiner_worker import MontrealJoinerWorker


def main():
    time.sleep(10)
    print("Up!")

    filters = int(os.environ["FILTER"])

    worker = MontrealJoinerWorker(filters)

    worker.run()


if __name__ == "__main__":
    main()
