import time
import os

from parser import Parser


def main():
    # Wait for rabbitmq to come up
    time.sleep(10)

    consumer_id = os.environ["PARSER_ID"]
    rains = int(os.environ["RAIN"])
    montreals = int(os.environ["MONTREAL"])
    years = int(os.environ["YEAR"])

    parser = Parser(consumer_id, rains, montreals, years)
    parser.run()


if __name__ == "__main__":
    main()
