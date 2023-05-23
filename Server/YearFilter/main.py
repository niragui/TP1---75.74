import time
import os
import signal

from year_filter_worker import YearFilterWorker


def main():
    time.sleep(10)
    print("Up!")

    parsers = int(os.environ["PARSERS"])
    worker = YearFilterWorker(parsers)
    
    signal.signal(signal.SIGINT, worker.stop)
    worker.run()


if __name__ == "__main__":
    main()
