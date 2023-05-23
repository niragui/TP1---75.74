import time
import os
import signal

from montreal_joiner_worker import MontrealJoinerWorker


def main():
    time.sleep(10)
    print("Up!")

    filters = int(os.environ["FILTER"])

    worker = MontrealJoinerWorker(filters)

    signal.signal(signal.SIGINT, worker.stop)
    worker.run()


if __name__ == "__main__":
    main()
