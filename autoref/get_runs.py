
def main(runs_file):
    with open(runs_file, "r") as fin:
        html = fin.readline()

    temp = html.split("</div>")

    final = []
    for elem in temp:
        try:
            final.append(int(elem[(len(elem)-6):]))
        except ValueError:
            continue

    return final

if __name__ == "__main__":
    print main("Run2018.txt")
