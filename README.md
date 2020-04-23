# WikiScan 

WikiScan è uno strumento esterno a wikipedia che data una specifica categoria, ricerca le sue sottocategorie e pagine.
Può anche essere utilizzato per trovare tutte le pagine che appartengono a due o piu' categorie specifiche (intersezione).
Opzionalmente genera in output un file .gexf, che contiene il grafo/i che hai espolorato.

Outuput(opzionale): salva il grafo in un file .gexf


(Tested on Ubuntu 19.10)

---------------------------------
I - Istruzioni di installazione 
---------------------------------

1. Installa Python 3.7.5 [Download](https://www.python.org/downloads/release/python-375)

2. Installa MySql (opzionale)

    a. Apri il terminale(Ctrl+Alt+T)
    ```bash
    sudo apt update
    sudo apt install mysql-server
    sudo mysql_secure_installation
    ```
    b. Crea il DataBase
    ```bash
    mysql -u root -p
    ```
    ```mysql
    CREATE DATABASE db_wikipedia;
    exit;
    ```
    c. Vai su
    [Wikipedia English dump](https://ftp.acc.umu.se/mirror/wikimedia.org/dumps/enwiki/). Clicca sull'ultimo dump disponibile                     cerca e scarica pages.sql.gz e categorylinks.sql.gz. [Info dump](https://dumps.wikimedia.org/)

    d. Importa i file nel database mysql
    ```bash
    gunzip enwiki-YYYYMMDD-page.sql.gz | mysql -u root -p --database=db_wikipedia
    gunzip enwiki-YYYYMMDD-categorylinks.sql.gz | mysql -u root -p --database=db_wikipedia
    ```
 3.Scarica Gephi per la visualizzazione del grafo [Download](https://gephi.org/users/download/)

 ---------------------------------
 R - Running Wikipedia
 ---------------------------------

 1. Effettua il download del file zip dalla repository di wikipedia [Download](https://github.com/blegork/wikipedia/archive/master.zip)

 2. Estrai il file

 3. Setta il file config.json, inserendo password, user, ip e nome del database.

 4. Posizionati sulla cartella Wikipedia e dal terminale apri il programma con:
      pyton main.py -OPTION
	a. Usa le seguenti opzioni:

	| Opzione | Descrizione |
	| ------ | ------ |
	| -c [CATEGORY [CATEGORY ...]], --category [CATEGORY [CATEGORY ...]] | Nome della categoria/e da ricercare, col prefisso "Category:"|
	| -p --page | Include le pagine nella richiesta |
	| -w WIKIPEDIA --wikipedia WIKIPEDIA| Percentuale di richieste da effettuare on-line. Valore compreso da 1 - 100. Default effettua solo richieste al DataBase |
	| -v --verbose | Stampa tutti i link durante la ricerca |
	| -d DEPTH, --depth DEPTH | Profondita di esplorazione |
	| -g --graph | Salva il grafo nel formato .gexf |
	| -t TIME --time TIME | Tempo massimo di esecuzione del programma, stampa e salva statistiche nei file MultiTest.CSV o SingleTest.CSV. Test eseguito su singola categorie o coppie di categorie|
 ---------------------------------
 G - Gephi
 ---------------------------------

 1. Posizionati sulla cartella Gephi e dal terminale apri il programma con:

 ```bash
 ./bin/gephi
 ```
 2. Apri File
	File-> Open -> file.gexf

 3. Layout grafo: 
	Layout -> YifanHu -> Run

 4. Colorazione nodi:
 
 	a. Grafo singolo:
		  Colora in modo diverso: Categoria padre, sotto-categorie, pagine
 		  Nodes -> Color -> Partion -> type -> Apply
		  
      ![](https://github.com/blegork/Wikipedia/blob/master/screen/SingleNodeColor.png)
     	
	b. Intersezione grafi:
		  Colora in modo diverso: ogni grafo, categorie e/o pagine in comune
		  Nodes -> Color -> Partion-> name -> Apply
		  
	![](https://github.com/blegork/Wikipedia/blob/master/screen/MultiNodeColor.png)
		  
	 
 5. Dimensione nodi:
		Nodes -> Size -> Ranking -> size -> Apply
		
	![](https://github.com/blegork/Wikipedia/blob/master/screen/NodeSize.png)

 6. Esportazione grafo:
	File -> Export -> Sigma.js template
	Questa operazione crea la cartella network

 7. Posizionati sulla cartella network e dal terminale apri un web server:
	```bash
	python3 -m http.server
	```
 8. Apri il browser e vai all'indirizzo localhost:8000. Questo visulizzera' il grafo
 
 	![](https://github.com/blegork/Wikipedia/blob/master/screen/Category:Agriculture%7CAfrica.png)
 
 	Esempio: intersezione Category:Africa e Category:Agriculture, in verde le pagine in comune(Profondita' 1).

