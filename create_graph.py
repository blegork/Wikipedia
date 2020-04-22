import networkx as nx
import request_wikipedia as w
import random
MAX_DEPHT = 10
URL = '<a href=%s target="_blank">%s</a>'

class CategoryTogheter:

    # This graph will include all the explored pages
    def __init__(self, main_portal):
        self.category_graph = nx.DiGraph()
        self.main_cat = main_portal
        self.query = 0
        self.connection = None
        self.perc_query_wiki = 0

    #Setta la percentuale di richieste da effettuare a WikiMedia
    def set_percentuage_wiki(self, percentuage):
        self.perc_query_wiki = percentuage

    def get_category_graph(self):
        return self.category_graph

    def set_connection(self, c):
        self.connection = c

    def search_and_store_graph(self, category, subcategory_depth, parent_node, include_pages, verbose):
        """"
        Questa funzione e' chiamata ricorsivamente per esplorare l'albero delle categorie di wikipedia,
        in base alla percentuale di richieste da effettuare all' API di Wikipedia.
            :param category: nome della categoria da cercare
            :param subcategory_depth: profondita esplorazione albero categorie
            :param parent_node: genitore nel grafo
            :param: include_pages: include le pagine nel grafo se e' vero
            :param verbose: se uguale a True, stampa sul terminale per ogni categoria/pagina esplorata <title, URL>
            :return: none
        """

        category_url = ('https://en.wikipedia.org/wiki/' + category.replace(" ", "_"))
        # indent based on the depth of the category: visualisation problems may occur if max_depth is not >>
        # subcategory_depth * 2
        if verbose:
            print(" " * ((MAX_DEPHT) - (subcategory_depth * 2)) + category + " URL: " + category_url)
        # adding the category to t) -( (subcategory_depth-1) * 2)) + page_result[1] + " URL: " + page_result[0])

        # =======Adding and exploring he graph

        category_title = category if category.startswith('Category:') else 'Category:' + category
        new_parent_node = category_title

        # create Graph
        if parent_node != "null":
            self.category_graph.add_edge(parent_node, category_title)
            self.category_graph.add_node(category_title, type='cat', url=URL % (category_url, category_title), size=2, name=self.main_cat)
        else:
            self.category_graph.add_node(category_title, type='main_cat', url=URL % (category_url, category_title), size=3, name=self.main_cat)

        # =========Adding the pages to the categories, if required (generates a very large graph)====
        # Check this website for param structure: https://www.mediawiki.org/wiki/API:Categorymembers

        if include_pages:
            if random.randrange(1, 100) <= self.perc_query_wiki:
                page_results = w.wiki_search_subpage(category_title)
                self.query += 1
            else:
                page_results, number_query = w.db_search_subpage(category_title, self.connection)
                self.query += number_query
            for page_result in page_results:
                self.category_graph.add_node(page_result[1], type="pag", url=URL % (page_result[0],page_result[1]), size=0, name = self.main_cat)
                self.category_graph.add_edge(new_parent_node, page_result[1])
                if verbose:
                    print(" " * ((MAX_DEPHT) -( (subcategory_depth-1) * 2)) + page_result[1] + " URL: " + page_result[0])

        # =======Adding and exploring the subcategories===
        if subcategory_depth > 0:
            if random.randrange(1, 100) <= self.perc_query_wiki:
                subcat_results = w.wiki_search_subcat(category_title)
                self.query +=1
            else:
                subcat_results, number_query = w.db_search_subcat(category_title, self.connection)
                self.query += number_query
            for subcat_result in subcat_results:
                self.search_and_store_graph(subcat_result, subcategory_depth - 1,
                                            new_parent_node, include_pages, verbose)
