import time
import os

from year_filter_worker import YearFilterWorker


def main():
    time.sleep(10)
    print("Up!")

    parsers = int(os.environ["PARSERS"])
    worker = YearFilterWorker(parsers)

    worker.run()


if __name__ == "__main__":
    main()
