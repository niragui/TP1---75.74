DOCKER_FILE = "docker-compose-dev.yaml"
HEADER = "header.txt"
FOOTER = "footer.txt"


def add_section(file_name, file):
    f_section = open(file_name, "r")

    for line in f_section:
        file.write(line)

    file.write("\n"*2)

    f_section.close()


def get_number(text):
    numero = input(text)

    while True:
        try:
            return int(numero)
        except:
            numero = input(text+" PLEASE INSERT A NUMBER ")

def add_filter_general(file):
    file.write("    restart: on-failure\n")
    file.write("    depends_on:\n")
    file.write("      rabbitmq:\n")
    file.write("        condition: service_healthy\n")
    file.write("    links:\n")
    file.write("      - rabbitmq\n")
    file.write("    networks:\n")
    file.write("      - testing_net\n")
    file.write("    environment:\n")

def add_rain_filters(amount, parsers, file):
    for i in range(1, amount+1):
        file.write(f"  rainfilter{i}:\n")
        file.write(f"    container_name: rainfilter{i}\n")
        file.write("    image: rainfilter:latest\n")
        add_filter_general(file)
        file.write(f"      - FILTER_ID={i}\n")
        file.write("      - PYTHONUNBUFFERED=1\n")
        file.write(f"      - PARSERS={parsers}\n")
        file.write("\n"*2)

def add_montreal_filters(amount, parsers, file):
    for i in range(1, amount+1):
        file.write(f"  montrealfilter{i}:\n")
        file.write(f"    container_name: montrealfilter{i}\n")
        file.write("    image: montrealfilter:latest\n")
        add_filter_general(file)
        file.write(f"      - FILTER_ID={i}\n")
        file.write(f"      - PARSERS={parsers}\n")
        file.write("      - PYTHONUNBUFFERED=1\n")
        file.write("\n"*2)

def add_year_filters(amount, parsers, file):
    for i in range(1, amount+1):
        file.write(f"  yearfilter{i}:\n")
        file.write(f"    container_name: yearfilter{i}\n")
        file.write("    image: yearfilter:latest\n")
        add_filter_general(file)
        file.write(f"      - FILTER_ID={i}\n")
        file.write(f"      - PARSERS={parsers}\n")
        file.write("      - PYTHONUNBUFFERED=1\n")
        file.write("\n"*2)

def add_parsers(amount, rain, montreal, year, file):
    for i in range(1, amount+1):
        file.write(f"  parser{i}:\n")
        file.write(f"    container_name: parser{i}\n")
        file.write("    image: parser:latest\n")
        add_filter_general(file)
        file.write(f"      - PARSER_ID={i}\n")
        file.write(f"      - RAIN={rain}\n")
        file.write(f"      - MONTREAL={montreal}\n")
        file.write(f"      - YEAR={year}\n")
        file.write("      - PYTHONUNBUFFERED=1\n")
        file.write("\n"*2)


def add_rain_joiner(filters, file):
    file.write("  rainjoiner:\n")
    file.write("    container_name: rainjoiner\n")
    file.write("    image: rainjoiner:latest\n")
    add_filter_general(file)
    file.write(f"      - FILTER={filters}\n")
    file.write("      - PYTHONUNBUFFERED=1\n")
    file.write("\n"*2)


def add_year_joiner(filters, file):
    file.write("  yearjoiner:\n")
    file.write("    container_name: yearjoiner\n")
    file.write("    image: yearjoiner:latest\n")
    add_filter_general(file)
    file.write(f"      - FILTER={filters}\n")
    file.write("      - PYTHONUNBUFFERED=1\n")
    file.write("\n"*2)


def add_montreal_joiner(filters, file):
    file.write("  montrealjoiner:\n")
    file.write("    container_name: montrealjoiner\n")
    file.write("    image: montrealjoiner:latest\n")
    add_filter_general(file)
    file.write(f"      - FILTER={filters}\n")
    file.write("      - PYTHONUNBUFFERED=1\n")
    file.write("\n"*2)


def main():
    parsers = get_number("How Many Parsers Would You Like To Add?")
    f_rain = get_number("How Many Rain Filters Would You Like To Add?")
    f_montreal = get_number("How Many Montreal Filters Would You Like To Add?")
    f_year = get_number("How Many Year Filters Would You Like To Add?")

    f = open(DOCKER_FILE, "w")
    add_section(HEADER, f)
    add_parsers(parsers, f_rain, f_montreal, f_year, f)
    add_rain_filters(f_rain, parsers, f)
    add_montreal_filters(f_montreal, parsers, f)
    add_year_filters(f_year, parsers, f)
    add_rain_joiner(f_rain, f)
    add_year_joiner(f_year, f)
    add_montreal_joiner(f_montreal, f)
    add_section(FOOTER, f)
    f.close()


if __name__ == "__main__":
    main()