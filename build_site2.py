import csv
import os
from dataclasses import asdict
# считать csv с данными об играх
# в цикле перебрать строки из файла и дополнить их
# html егами
# <tr><td>/game/acro_fs</td>
# 3. открыть шаблон страницы catalog.html
# 4. вставить туда новый html код
# 5. сохранить html файл catalogue.html

def read_csv_file():
    games = []
    with open('./out/games.csv', "r", encoding="UTF-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            games.append(row)
        return games

def build_row(game: dict):
    tdst = []
    tds = ""
    for cell in game.values():
        tdst += f"<td>{cell}</td>"
    tr = f"<tr>{tdst}</tr>"
    return tr


def main():
    data = read_csv_file()
    rows = []
    for game in data:
        row = build_row(game)
        rows.append(row)
    html = "\n".join(rows)
    with open("site/catalog.html", "r", encoding="UTF-8") as f:
        catalog = f.read()
    html_out = catalog.replace("{{DATA}}", html)
    with open("site/catalog.html", "w", encoding="UTF-8") as f:
        f.write(html_out)


if __name__ == "__main__":
    main()