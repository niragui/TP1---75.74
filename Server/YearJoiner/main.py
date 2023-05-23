import time
import os
import signal

from year_joiner_worker import YearJoinerWorker


def main():
    time.sleep(10)
    print("Up!")

    filters = int(os.environ["FILTER"])

    worker = YearJoinerWorker(filters)

    signal.signal(signal.SIGINT, worker.stop)
    worker.run()

if __name__ == "__main__":
    main()
