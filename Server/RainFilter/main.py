import time
import os

from rain_filter_worker import RainFilterWorker


def main():
    time.sleep(10)

    parsers = int(os.environ["PARSERS"])
    worker = RainFilterWorker(parsers)

    worker.run()


if __name__ == "__main__":
    main()
