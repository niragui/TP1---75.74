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

"""
  filter1:
    build:
      context: ./Server/Filters
      dockerfile: filter.dockerfile
    restart: on-failure
    depends_on:
      - rabbitmq
    links:
      - rabbitmq
    environment:
      - PYTHONUNBUFFERED=1
      - FILTER_ID=1
  
"""

def add_clients(amount, file):
    for i in range(1, amount+1):
        file.write(f"  filter{i}:\n")
        file.write(f"    container_name: filter{i}\n")
        file.write("    image: filter:latest\n")
        file.write("    restart: on-failure\n")
        file.write("    depends_on:\n")
        file.write("      - server\n")
        file.write("      - rabbitmq\n")
        file.write("    links:\n")
        file.write("      - rabbitmq\n")
        file.write("    networks:\n")
        file.write("      - testing_net\n")
        file.write("    environment:\n")
        file.write(f"      - FILTER_ID={i}\n")
        file.write("      - PYTHONUNBUFFERED=1\n")
        file.write("\n"*2)


def main():
    amount = get_number("How Many Clients Would You Like To Add?")

    f = open(DOCKER_FILE, "w")
    add_section(HEADER, f)
    add_clients(amount, f)
    add_section(FOOTER, f)
    f.close()


if __name__ == "__main__":
    main()