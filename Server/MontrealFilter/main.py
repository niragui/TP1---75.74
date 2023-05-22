import time
import os

from montreal_filter_worker import MontrealFilterWorker


def main():
    time.sleep(10)

    parsers = int(os.environ["PARSERS"])
    worker = MontrealFilterWorker(parsers)

    worker.run()


if __name__ == "__main__":
    main()
