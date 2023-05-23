import time
import os
import signal

from rain_filter_worker import RainFilterWorker


def main():
    time.sleep(10)
    print("Up!")

    parsers = int(os.environ["PARSERS"])
    worker = RainFilterWorker(parsers)

    signal.signal(signal.SIGINT, worker.stop)
    worker.run()


if __name__ == "__main__":
    main()
