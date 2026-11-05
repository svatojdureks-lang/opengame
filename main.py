import argparse
import logging

from bs4 import BeautifulSoup

import reference
from client import StopGameClient

from logging_config import BASIC_CONFIG
import difflib
from reference import save_tags, save_platforms
import bs4

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Уровень сообщений в логе",
    )
    parser = argparse.ArgumentParser(
        prog="stopgame",
        description="Каталог игр StopGame из командной строки",
        parents=[common_parser]
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("update", help="скачать справочники жанров и платформ", parents=[common_parser])

    p_genres = subparsers.add_parser("genres", help="показать доступные жанры", parents=[common_parser])
    p_genres.add_argument("--save", metavar="ФАЙЛ", help="записать список в файл")

    p_platforms = subparsers.add_parser("platforms", help="показать доступные платформы", parents=[common_parser])
    p_platforms.add_argument("--save", metavar="ФАЙЛ", help="записать список в файл")

    p_games = subparsers.add_parser("games", help="загрузить игры по фильтрам", parents=[common_parser])
    p_games.add_argument("--genres", nargs="+", metavar="ЖАНР",
                         help="жанры, темы, режимы (как на сайте)", default=[])
    p_games.add_argument("--platforms", nargs="+", metavar="ПЛАТФОРМА",
                         help="платформы (как на сайте)", default=[])
    p_games.add_argument("--pages", type=int, default=1, help="сколько страниц скачать")
    p_games.add_argument("--out", default="games.csv", help="куда сохранить результат")

    return parser


def cmd_update(args):
    logger.info(f"Команда update {args}")
    client = StopGameClient()
    save_tags(client.fetch_tags())
    save_platforms(client.fetch_platforms())


def cmd_genres(args):
    logger.info(f"Выполняем поиск доступных тегов")
    tags22 = reference.load_tags()
    for tag in tags22:
        print(tag.name)


def cmd_platforms(args):
    logger.info(f"Выполняем поиск доступных платформ")
    platforms22 = reference.load_platforms()
    for platform in platforms22:
        print(platform.code)


def cmd_games(args):
    platforms = reference.load_platforms()
    platforms_codes = []
    platform_possibilities = [p.code for p in platforms] + [p.title for p in platforms]
    error = ""
    yes = ""
    for word in args.platforms:
        for platform in platforms:
            if platform.matches(word):
                platforms_codes.append(platform.code)
                break
        else:
            print(f"Не найдена платформа {word}")
            matches = difflib.get_close_matches(word, platforms_codes, cutoff=0.6)
            if matches:
                print(f"Возможно вы имели в виду {matches[0]}")

    tags = reference.load_tags()
    tag_slugs = []
    game_links = []
    all = []
    tag_possibilities = [t.slug for t in tags] + [t.name for t in tags]
    errort = ""
    yest = ""
    have_input_error = True
    for word1 in args.genres:
        for tag in tags:
            if tag.matches(word1):
                tag_slugs.append(tag.slug)
                break
        else:
            print(f"Не найден тег: <<{word1}>>")
            matches1 = difflib.get_close_matches(word1, tag_possibilities, cutoff=0.6)
            if matches1:
                print(f"Возможно вы имели в виду <<{matches1[0]}>>")
    logger.debug(f" {platforms_codes=} {tag_slugs=}")

    client = StopGameClient()
    page = client.fetch_catalog_page(tag_slugs=tag_slugs, platform_codes=platforms_codes)
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all("div")
    for div in divs:
        if div.has_attr("data-key"):
            a = div.find("a")
            game_links.append(a.attrs["href"])
           
    for game_link in game_links:
        platforms = []
        list_tag = []
        resp = client._get(game_link)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("h1", class_="_game-title_1bso0_702").text
        tags_list = soup.find_all("a", class_="_tag_82nn8_724")
        Dt = soup.find("dt", string="Платформы")
        next_dd = Dt.find_next("dd")
        links = next_dd.find_all("a")
        for link in links:
            platforms.append(link.text)
        for tag in tags_list:
            list_tag.append(tag.text)
        year = soup.find("dd").text
    {
        "year": year,
        "tags": list_tag,
        "platforms": platforms,
        "title": title
    }

    games = soup.find_all("div", class_="game")
def main():
    commands = {
        "update": cmd_update,
        "genres": cmd_genres,
        "platforms": cmd_platforms,
        "games": cmd_games,
    }
    parser = build_parser()
    args = parser.parse_args()

    BASIC_CONFIG["level"] = args.log_level
    logging.basicConfig(
        **BASIC_CONFIG,
    )

    func = commands[args.command]  # выбираем функцию по имени команды
    func(args)


if __name__ == "__main__":
    main()
