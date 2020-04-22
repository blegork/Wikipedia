import os.path
import networkx as nx
import csv
import time
from datetime import timedelta
from create_graph import CategoryTogheter
import random
import request_wikipedia as w

FILE_SINGLE_TEST = "SingleTest.csv"
FILE_MULTI_TEST = "MultiTest.csv"


def save_graph(g, name_portal, subcategory_depth):
    graph_file_name = name_portal + '_D' + str(subcategory_depth) + '_category_graph.gexf'
    nx.write_gexf(g, graph_file_name)
    print('Gephi graph saved in ' + graph_file_name)


def get_common_category(array_cat, save, all_category, depth):
    nodes_set = []
    graph_merge = nx.DiGraph()
    for cat in array_cat:
        nodes_set.append(list(cat.get_category_graph().node))
        graph_merge.add_nodes_from(cat.get_category_graph().nodes(data=True))
        graph_merge.add_edges_from(cat.get_category_graph().edges())

    nodes_set = set(nodes_set[0]).intersection(*nodes_set[1:])

    for node in nodes_set:
        print("Title:", node, "URL:", array_cat[0].get_category_graph().node[node]['url'])
        if node.startswith("Category:"):
            graph_merge.add_node(node, name="merge_cat", size=2)
        else:
            graph_merge.add_node(node, name="merge_pag", size=1)

    if save:
        print("save graph")
        save_graph(graph_merge, all_category, depth)


def store_subcat(d, wikipedia, conn_database, include_page, verbose, search_cat, max_time, start_time):
    """"
            Questa funzione e' di supporto ai Test. Ricerce le sottocatgorie e/o pagine di una categoria foglia, e le aggiunge al grafo
            in base alla percentuale di richieste da effettuare all' API di Wikipedia.
                :param d: grafo
                :param wikipedia: profondita esplorazione albero categorie
                :param conn_database: genitore nel grafo
                :param: include_pages: include le pagine nel grafo se e' vero
                :param verbose: se uguale a True, stampa sul terminale per ogni categoria/pagina esplorata <title, URL>
                :search_cat: nome della categoria foglia
                :max_time: tempo massimo del test
                :start_time: tempo di avvio del Test
                :return: restituisce un lista delle sotto-categorie aggiunte al grafo
            """

    newleafs = []
    if random.randrange(1, 100) <= wikipedia:
        subcat_results = w.wiki_search_subcat(search_cat)
        d.query += 1
    else:
        subcat_results, number_query = w.db_search_subcat(search_cat, conn_database)
        d.query += number_query

    for cat in subcat_results:
        if max_time > int(time.time() - start_time):
            d.search_and_store_graph(cat, subcategory_depth=0, parent_node=search_cat, include_pages=include_page,
                                     verbose=verbose)
            newleafs.append(cat)
        else:
            return newleafs
    return newleafs


def single_test(portal, verbose, wikipedia, e_time, max_depth, include_page, conn_database):
    # variabili
    start_time = time.time()
    e_time = e_time * 60
    depth_arrive = 0
    leafs = [portal]

    # creazione e settaggio grafo
    d = CategoryTogheter(portal)
    d.set_percentuage_wiki(wikipedia)
    d.set_connection(conn_database)
    d.search_and_store_graph(portal, subcategory_depth=0, parent_node='null', include_pages=include_page,
                             verbose=verbose)

    while e_time > int(time.time() - start_time) and depth_arrive < max_depth:
        newleafs = []
        for leaf in leafs:
            if e_time > int(time.time() - start_time):
                newleafs.extend(
                    store_subcat(d, wikipedia, conn_database, include_page, verbose, leaf, e_time, start_time))
            else:
                # time out
                break
        leafs = newleafs
        depth_arrive = depth_arrive + 1

    nodes_category_only = [n for n in d.get_category_graph().nodes if n.startswith('Category:')]
    temp = time.time() - start_time

    # crea file se non esiste, altrimenti fa un append dei dati
    file_exists = os.path.isfile(FILE_SINGLE_TEST)
    f = open(FILE_SINGLE_TEST, 'a+')
    with f:
        fnames = ['Categoria', 'Query', 'Numero di nodi', 'Numero di edges', 'Numero di categorie', 'Numero di pagine',
                  'Query/Sec', 'Time', 'Depth', 'Percentuale']
        writer = csv.DictWriter(f, fieldnames=fnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({'Categoria': portal, 'Query': d.query, 'Numero di nodi': len(d.get_category_graph().node),
                         'Numero di edges': len(d.get_category_graph().edges),
                         'Numero di categorie': len(nodes_category_only),
                         'Numero di pagine': len(d.get_category_graph().node) - len(nodes_category_only),
                         'Query/Sec': d.query / temp, 'Time': str(timedelta(seconds=temp)), 'Depth': depth_arrive - 1,
                         'Percentuale': wikipedia})
    f.close()

    # stampo risultati
    print("Query:", '{:,}'.format(d.query))
    print("Number of node:", '{:,}'.format(len(d.get_category_graph().node)))
    print("Number of categories:", '{:,}'.format(len(nodes_category_only)))
    print("Number of pages:", '{:,}'.format(len(d.get_category_graph().node) - len(nodes_category_only)))
    print("Query/sec:", d.query / temp)
    print("Time:" + str(timedelta(seconds=temp)))
    print("Depth:", depth_arrive - 1)
    print("Numero di edges", '{:,}'.format(len(d.get_category_graph().edges)))


def multi_test(category_name1, category_name2, verbose, wikipedia, e_time, max_depth, include_page, conn_database):
    start_time = time.time()
    e_time = e_time * 60
    depth_arrive = 0
    common_pages = []

    d1 = CategoryTogheter(category_name1)
    d2 = CategoryTogheter(category_name2)
    d1.set_percentuage_wiki(wikipedia)
    d2.set_percentuage_wiki(wikipedia)
    d1.set_connection(conn_database)
    d2.set_connection(conn_database)
    newleafs1 = []
    newleafs2 = []

    d1.search_and_store_graph(category_name1, subcategory_depth=0, parent_node='null',
                              include_pages=include_page, verbose=verbose)
    d2.search_and_store_graph(category_name2, subcategory_depth=0, parent_node='null',
                              include_pages=include_page, verbose=verbose)
    if max_depth > 0:
        leaf1 = [category_name1]
        leaf2 = [category_name2]
        break_while = False
        while e_time > int(time.time() - start_time) and depth_arrive < max_depth and not break_while:
            depth_arrive += 1
            for i in range(min(len(leaf1), len(leaf2))):
                # esploro edges1
                if e_time > int(time.time() - start_time):
                    newleafs1.extend(
                        store_subcat(d1, wikipedia, conn_database, include_page, verbose, leaf1[i], e_time, start_time))
                else:
                    #tempo scaduto
                    break_while = True
                    break

                # esploro edges2
                if e_time > int(time.time() - start_time):
                    newleafs2.extend(
                        store_subcat(d2, wikipedia, conn_database, include_page, verbose, leaf2[i], e_time, start_time))
                else:
                    break_while = True
                    break
            # continuo a esplorare edges1
            while i < len(leaf1) and not break_while:
                if e_time > int(time.time() - start_time):
                    newleafs1.extend(
                        store_subcat(d1, wikipedia, conn_database, include_page, verbose, leaf1[i], e_time, start_time))
                else:
                    break_while = True
                    break
                i += 1
            # continuo a esplorare edges2
            while i < len(leaf2) and not break_while:
                if e_time > int(time.time() - start_time):
                    newleafs2.extend(
                        store_subcat(d2, wikipedia, conn_database, include_page, verbose, leaf2[i], e_time, start_time))
                else:
                    break_while = True
                    break
                i += 1
            leaf1 = newleafs1
            leaf2 = newleafs2

    # crea file se non esiste, altrimenti fa un append dei dati
    file_exists = os.path.isfile(FILE_MULTI_TEST)
    f = open(FILE_MULTI_TEST, 'a+')
    with f:
        fnames = ['Categorie','Query', 'Numero di nodi', 'Numero di edges', 'Numero di categorie',
                  'Numero di pagine',
                  'Query/Sec', 'Time', 'Depth', 'Percentuale', 'Pagine in comune']
        writer = csv.DictWriter(f, fieldnames=fnames)
        if not file_exists:
            writer.writeheader()
        #writer.writerow({'Categoria': category_name1+'-'+category_name2, 'Query': d.query, 'Numero di nodi': len(d.get_category_graph().node),
        #                  'Numero di edges': len(d.get_category_graph().edges),
        #                  'Numero di categorie': len(nodes_category_only),
        #                  'Numero di pagine': len(d.get_category_graph().node) - len(nodes_category_only),
        #                  'Query/Sec': d.query / temp, 'Time': str(timedelta(seconds=temp)), 'Depth': depth_arrive,
        #                  'Percentuale': wikipedia, 'Categorie esplorate': (category, '/', full_category)})
    f.close()
    common_pages.extend(set(d1.get_category_graph().nodes).intersection(set(d2.get_category_graph().nodes)))
    temp = time.time() - start_time
    print(len(d1.get_category_graph().nodes))
    print(len(d2.get_category_graph().nodes))
    print("Pagine in comune: ", common_pages, "len: ", len(set(common_pages)))
    print("Time: " + str(timedelta(seconds=temp)))
