import os, mysql.connector
import matplotlib.pyplot as plt

T_pays = []
abscisse = []
ordonnee = [-1]

directory = '/media/nk-wilfried/NKW/UY1/L3/INF351/TP-1_INF351_Data/TP_INF351_Data'

#Connexion a la bd 
connexion = mysql.connector.connect(user="root", password="", host="localhost", database="TPINF351")

# Creation du curseur
cursor = connexion.cursor()

#   Definition de la fonction de separation
def separation (data : list ,sep : list):
    tab = []
    tab1 = []

    chaine = data [0]
    for i in range (1,len(data)):
        if data[i] != sep:
            if chaine != sep:
                 chaine = chaine + data[i]
            else:
                chaine = data[i]
        else :
            chaine=sep
        tab.append(chaine)

    for j in range (0, len(tab)):
        if tab[j]==sep:
            tab1.append(tab[j-1])
    tab1.append(tab[len(tab)-1])

    return tab1 

#   Definition de la fonction permettant d'effectuer le traitement sur les pays, et eventuellement le \n
def traitement_pays(liste : list):
    #   Retrait du \n
    tailleListe = len(liste)
    tailleLastWord = len(liste[tailleListe-1])

    liste[len(liste)-1] = liste[len(liste)-1][:tailleLastWord-1]

    # Traitement des pays
    for i in range(len(liste)): 
        if liste[i] == ' United States' or liste[i] == ' United state' or liste[i] == ' United State':
            liste[i] = ' USA'
        
        if liste[i] == ' The Netherland' or liste[i] == ' The Netherlands' or liste[i] == ' Netherlands':
            liste[i] = ' Netherland'
    
    return liste

#   Definition de la fonction permettant d'inserer les pays et le nombre d'auteur par pays
def setteur(listAbscisse : list, listOrdonnee : list, pays : list):

    for elt in pays:
        if elt in listAbscisse:
            listOrdonnee[listAbscisse.index(elt)+1] += 1
        else:
            listAbscisse.append(elt)
            listOrdonnee.append(1)

    listOrdonnee.remove(-1)

    return [listAbscisse, listOrdonnee]

#   ----------- Supprimons D'abord les tables afin d'eviter les potentielles erreurs ----------- #
breakForeignKey = "SET FOREIGN_KEY_CHECKS = 0"
AuteurCheck = "TRUNCATE TABLE Auteur"
ArticleCheck = "TRUNCATE TABLE Article"
AffiliationCheck = "TRUNCATE TABLE Affiliation"
AuteurFiliationCheck = "TRUNCATE TABLE AuteurFiliation"
AuteurArticleCheck = "TRUNCATE TABLE AuteurArticle"

try:
    cursor.execute(breakForeignKey)
    cursor.execute(AuteurCheck)
    cursor.execute(ArticleCheck)
    cursor.execute(AffiliationCheck)
    cursor.execute(AuteurFiliationCheck)
    cursor.execute(AuteurArticleCheck)
    connexion.commit()

except:
#   ----------- Creation des tables ----------- #
    create_article_table = """
    CREATE TABLE Article (
    idArticle INT PRIMARY KEY AUTO_INCREMENT,
    titre_article VARCHAR(250)
    )
    """
    create_auteur_table = """
    CREATE TABLE Auteur(
    idAuteur INT PRIMARY KEY AUTO_INCREMENT, 
    nom_encode VARCHAR(50)
    )
    """

    create_affiliation_table = """
    CREATE TABLE Affiliation(
    idAfiliation INT PRIMARY KEY AUTO_INCREMENT,
    etablissement VARCHAR(100),
    ville VARCHAR(100),
    pays VARCHAR(100)
    )
    """

    create_auteurFiliation_table = """
    CREATE TABLE AuteurFiliation(
    idAuteur INT,
    idAfiliation INT,
    FOREIGN KEY (idAuteur) REFERENCES Auteur(idAuteur),
    FOREIGN KEY (idAfiliation) REFERENCES Affiliation(idAfiliation),
    PRIMARY KEY(idAuteur, idAfiliation)
    )
    """

    create_auteurArticle_table = """
    CREATE TABLE AuteurArticle(
    idAuteur INT,
    idArticle INT,
    FOREIGN KEY (idAuteur) REFERENCES Auteur(idAuteur),
    FOREIGN KEY (idArticle) REFERENCES Article(idArticle),
    PRIMARY KEY(idAuteur, idArticle)
    )
    """

    cursor.execute(create_article_table)
    cursor.execute(create_auteur_table)
    cursor.execute(create_affiliation_table)
    cursor.execute(create_auteurFiliation_table)
    cursor.execute(create_auteurArticle_table)

finally:

    for filename in os.listdir(directory):
        file = directory + "/" + filename
        print("=============================================================================")
        print("\n")
        print(file)
        author =[]
        nom = []
        etablissement = []
        ville = []
        pays = []
        auteurs1=[]
        auteurs = []

        with open(file,'r') as t:
            titre = t.readlines()[0]

        with open(file,'r') as g:
            donnees = g.readlines()[1]

        author = separation(donnees,'|')  
        for i in range(len(author)):
            final = separation(author[i], ',')
            tmpNom = separation(final[0], ' ')
            fnom = tmpNom[0][0]+'.'+tmpNom[1]
            fnom = fnom.upper()        
            nom.append(fnom)
            etablissement.append(final[1])
            ville.append(final[2])
            pays.append(final[3])
        pays = traitement_pays(pays)

        for elt in pays:
            T_pays.append(elt)

        print("TITRE : ",titre)
        print("NOMS : ",nom)
        print("ETABLISSEMENTS : ",etablissement)
        print("VILLES : ",ville)
        print("PAYS : ",pays)

        insert_query_titre = "INSERT INTO Article (titre_article) VALUES (%s)"
        for i in range(len(nom)):
            insert_query_noms = "INSERT INTO Auteur (nom_encode) VALUES (%s)"
            insert_query_ets_ville_pays = "INSERT INTO Affiliation (etablissement, ville, pays) VALUES (%s, %s, %s)"

            #donnees à inserer
            data1 = (titre,)
            data2 = (nom[i],)
            data3 = (etablissement[i], ville[i], pays[i])

            #Execution des requetes
            cursor.execute(insert_query_titre, data1)
            cursor.execute(insert_query_noms, data2)
            cursor.execute(insert_query_ets_ville_pays, data3)

            #validation des modifications
            connexion.commit()

#Fermeture du cursor et de la connexion à la bd
    cursor.close()
    connexion.close()

abscisse, ordonnee = setteur(abscisse, ordonnee, T_pays)

plt.xlabel('PAYS')
plt.ylabel('NOMBRE D\'ARTICLE')
plt.title('DIAGRAMME DU NOMBRE D\'ARTICLE PUBLIÉ PAR PAYS')
plt.bar(abscisse,ordonnee, color='#9711ff')
plt.show()