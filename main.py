import argparse
import traceback

from MySQLdb._exceptions import OperationalError

from create_graph import CategoryTogheter
from connection_database import Connection
import functions_graph as fun
import json

def check_positive(value):
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return value


def check_category(value):
    if not value.startswith("Category:") or len(value) <= len("Category:"):
        raise argparse.ArgumentTypeError("%s is an invalid string:" % value)
    return value


def check_percentuage(value):
    value = int(value)
    if value < 1 or value > 100:
        raise argparse.ArgumentTypeError("%s is an invalid percentuage value" % value)
    return value

# example: python3 main.py -d 0 -w 100 -c "Category:Africa" -vp
def main():

    parser = argparse.ArgumentParser(
        description="Dato un portale o lista di portali esplora le sotto-categorie e/o pagine. Dati due o piu' portali stampa la loro intersezione")
    parser.add_argument("-v", "--verbose", help="stampa i link, durante l'utilizzo", action="store_true")
    parser.add_argument("-w", "--wikipedia", help="Percentuale di richieste da effettuare a WikiMedia", type=check_percentuage,
                        default=0)
    parser.add_argument("-p", "--page", help="include le pagine nella richiesta", action="store_true")
    parser.add_argument("-t", "--time", help="TEST: tempo massimo di esecuzione del programma, stampa statistiche",
                        type=int)
    parser.add_argument("-d", "--depth", help="profondita' di esplorazione", type=check_positive)
    parser.add_argument("-g", "--graph", help="salva il grafo nel formato gexf, aprire il file con Gephi",
                        action="store_true")
    parser.add_argument("-c", "--category", type=check_category,
                        help="Nome dellla categoria/e da ricercare,col prefisso Category:", nargs='*')

    args = parser.parse_args()
    array_category = []
    conn_database = Connection()
    all_category = ""
    # Controlli
    if args.depth is None:
        parser.error("the argument -d/--depth is required")

    if args.category is None:
        parser.error("the arguments -c/--category is required")

    if args.wikipedia < 100:
        try:
            with open("config.json") as json_data_file:
                data=json.load(json_data_file)
        except FileNotFoundError as e:
            print("File Not Found", e)
            return
        try:
            conn_database.open(data['mysql']['db'], data['mysql']['host'], data['mysql']['user'],
                               data['mysql']['password'])
        except KeyError as e:
            print("Errore variabile nel config.json non trovata:", e)
            return
        except OperationalError as e:
            print(e)
            return

    if args.time:
        if len(args.category) == 1:
            fun.single_test(args.category[0], args.verbose, args.wikipedia, args.time, args.depth, args.page, conn_database)

        elif len(args.category) == 2:
            fun.multi_test(args.category[0], args.category[1], args.verbose, args.wikipedia, args.time, args.depth, args.page, conn_database)
        else:
            parser.error("the argument -t/--test required only one or two Category")
    else:
        for category in args.category:
            d = CategoryTogheter(category)
            d.set_percentuage_wiki(args.wikipedia)
            d.set_connection(conn_database)
            d.search_and_store_graph(category, args.depth, 'null', args.page, args.verbose)
            array_category.append(d)
            all_category = category+"_"+all_category
        if len(args.category) > 1:

            fun.get_common_category(array_category, args.graph, all_category, args.depth)
        elif args.graph:
            fun.save_graph(array_category[0].get_category_graph(), array_category[0].main_cat, args.depth)
    conn_database.close()


if __name__ == "__main__":
    main()
