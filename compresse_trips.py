import shutil

def get_number(text):
    numero = input(text).replace(".", "").replace(",", "")

    while True:
        try:
            return int(numero)
        except:
            numero = input(text+" PLEASE INSERT A NUMBER ").replace(".", "").replace(",", "")

lines = get_number("How Many Likes You'd Like To Save? (0 For ALL)")
city = input("What City?")

read_file = f"{city.lower()}/trips_real.csv"
write_file = f"{city.lower()}/trips.csv"

if lines > 0:
    f = open(read_file, "r")
    f_write = open(write_file, "w")

    lines_written = 0

    for line in f:
        f_write.write(line)
        lines_written += 1
        if lines_written >= lines:
            break

    f.close()
    f_write.close()
else:
    shutil.copy(read_file, write_file)