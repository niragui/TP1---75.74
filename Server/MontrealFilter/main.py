import time
import os
import signal

from montreal_filter_worker import MontrealFilterWorker


def main():
    time.sleep(10)
    print("Up!")

    parsers = int(os.environ["PARSERS"])
    worker = MontrealFilterWorker(parsers)

    signal.signal(signal.SIGINT, worker.stop)
    worker.run()


if __name__ == "__main__":
    main()
