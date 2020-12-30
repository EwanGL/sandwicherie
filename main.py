#Author: Ewan GRIGNOUX LEVERT
import sqlite3
import csv
import sys
from tkinter import *
from tkinter.messagebox import showinfo
from datetime import datetime

# Connexion à la base de données
connect = sqlite3.connect('aux_deux_amis_creer.db')

#Créer les tables de la base de données
def CreateTables():
    
    # Création d'un curseur de lecture de cette base
    cur = connect.cursor()

    # Exécution d'une requête sur la base en langage SQL
    cur.execute("CREATE TABLE 'clients' ('id'    INTEGER,'nom'   TEXT NOT NULL,'prenom'    TEXT,'adresse'   TEXT,'num_tel'   TEXT NOT NULL,PRIMARY KEY('id' AUTOINCREMENT));")
    cur.execute("CREATE TABLE 'sandwichs' ('id'    INTEGER,'nom'   TEXT NOT NULL,'prix'    INTEGER,PRIMARY KEY('id' AUTOINCREMENT));")
    cur.execute("CREATE TABLE 'commandes' ('id'    INTEGER,'idClient'   TEXT NOT NULL,'date'    TEXT NOT NULL,PRIMARY KEY('id' AUTOINCREMENT));")
    cur.execute("CREATE TABLE 'contenu' ('idCommande'    INTEGER,'idSandwichs'   TEXT NOT NULL, 'quantite' TEXT NOT NULL);")

    # Fermeture du curseur
    cur.close()
    connect.commit()
    return

#Importations des données de clients.csv et de sandwichs.csv vers le base de donées
def ImportData():
    cur = connect.cursor()
    with open ('clients.csv', newline='') as fichier:
        lireClients = csv.DictReader(fichier)
        for ligne in lireClients:
            cur.execute(f"INSERT INTO clients ('nom', 'prenom', 'num_tel', 'adresse') VALUES ('{ligne['nom']}', '{ligne['prénom']}', '{ligne['téléphone']}', '{ligne['adresse']}');")
    fichier.close()

    cur.execute("UPDATE clients SET adresse = '2 vielles rue' WHERE nom = 'Sud';")
    
    with open ('sandwichs.csv', newline='') as fichier:
        lireClients = csv.DictReader(fichier)
        for ligne in lireClients:
            cur.execute(f"INSERT INTO sandwichs ('nom', 'prix') VALUES ('{ligne['nom']}', '{ligne['prix']}');")
    fichier.close()

    cur.close()
    connect.commit()
    return

# Passer une commande
def commander():
    list_widget_commander = []

    def enregister():
        client =list_clients.get()
        client = client.split(' ')
        
        cur = connect.cursor()

        cur.execute(f"SELECT id FROM clients WHERE nom='{client[0]}' AND prenom='{client[1]}';")
        idClient = int(cur.fetchone()[0])
        
        idSandwichs=''
        for key in contenu_commande.keys():
            cur.execute(f"SELECT id FROM sandwichs WHERE nom='{key}';")
            idSandwichs += str(cur.fetchone()[0])+','
        
        quantites = ''
        for value in contenu_commande.values():
            quantites+=str(value)+','
        
        now = datetime.now()
        current_date = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        
        cur.execute(f"INSERT INTO commandes ('idClient', 'date') VALUES ('{idClient}', '{current_date}');")
        connect.commit()
        
        cur.execute(f"SELECT id FROM commandes WHERE idClient='{idClient}' AND date='{current_date}';")
        idCommande = int(cur.fetchone()[0])

        cur.execute(f"INSERT INTO contenu ('idCommande', 'idSandwichs', 'quantite') VALUES ({idCommande}, '{idSandwichs}','{quantites}');")
        connect.commit()

        showinfo('Prix', f'Votre commande as bien été enregistrée.\nVotre numéro de commande est: {idCommande}')
        fermer()
        return
    
    def ajouter():
        
        list_widget_ajouter = []
        def fermer():
            for i in list_widget_ajouter:
                i.destroy()
                list_widget_ajouter.remove(i)
            return

        def valider_ajout():
            global prix_total

            contenu_commande[list_sandwichs.get()] = choix_quantite.get()
            
            for key, value in contenu_commande.items():
                for i in sandwichs_db:
                    if key == i[0]:
                        prix_total+=i[1]*int(value)
                    if key == list_sandwichs.get():
                        prix=i[1]*int(value)
            
        
            produits.append(Label(commander_window, text=f'{list_sandwichs.get()}     {choix_quantite.get()}     {prix}€'))
            afficher_produits()
            fermer()
            return

        ajouter_window = Toplevel()
        ajouter_window.title('Ajouter un produit')
        ajouter_window.geometry("300x120+500+200")
        list_widget_ajouter.append(ajouter_window)
        
        choix_sandwich = OptionMenu(ajouter_window, list_sandwichs, *nom_sandwichs)
        choix_sandwich.pack(padx=5, pady=5)
        list_widget_ajouter.append(choix_sandwich)

        choix_quantite = Spinbox(ajouter_window, from_=1, to=10)
        choix_quantite.pack(padx=5, pady=5)
        list_widget_ajouter.append(choix_quantite)

        bas = Frame(ajouter_window)
        bas.pack(side=BOTTOM)
        list_widget_ajouter.append(bas)

        annuler_button = Button(bas, text='Annuler', command=fermer)
        annuler_button.pack(side=LEFT)
        list_widget_ajouter.append(annuler_button)

        valider_button = Button(bas, text='Valider', command=valider_ajout)
        valider_button.pack(side=RIGHT)
        list_widget_ajouter.append(valider_button)
    
    def fermer():
        for i in list_widget_commander:
            i.destroy()
            list_widget_commander.remove(i)
        return
    
    contenu_commande = {}
    
    commander_window = Toplevel()
    commander_window.title('Passer une commande')
    commander_window.geometry("300x300+500+200")
    
    list_widget_commander.append(commander_window)
    
    client_choix = OptionMenu(commander_window, list_clients, *clients)
    client_choix.pack(padx=5, pady=5)
    list_widget_commander.append(client_choix)

    valider_button = Button(commander_window, text='Valider la commande', command=enregister)
    valider_button.pack(padx=5, pady=5, side=BOTTOM)
    list_widget_commander.append(valider_button)
    
    ajouter_button = Button(commander_window, text='ajouter un produit', command=ajouter)
    ajouter_button.pack(padx=5, pady=5, side=BOTTOM)
    list_widget_commander.append(ajouter_button)
 
    colonnes_label = Label(commander_window, text= 'Produit        Quantité        Prix')
    colonnes_label.pack(padx=5, pady=5)
    list_widget_commander.append(colonnes_label)
    
    produits=[]
    def afficher_produits():
        for i in produits:
            if i != None:
                i.pack(padx=5, pady=5)
    
    afficher_produits()

    global prix_total
    prix_total= 0
    prix = Label(commander_window, text=f'Total: {prix_total}€')
    prix.pack(padx=5, pady=5, side=BOTTOM)
    list_widget_commander.append(prix)

    return

# Consulter une commande
def consulter():
    def afficher_commande():
        idCommande = choix_idCommande.get()

        cur.execute(f"SELECT idSandwichs, quantite FROM contenu WHERE idCommande = {idCommande};")
        contenu_db = cur.fetchall()[0]
        
        idSandwichs= contenu_db[0].split(',')[:-1]
        quantite = contenu_db[1].split(',')[:-1]

        contenue = {}
        j=0
        for i in idSandwichs:
            cur.execute(f"SELECT nom FROM sandwichs WHERE id={int(i)};")
            sandwichs_nom = cur.fetchone()[0]
            contenue[sandwichs_nom] = quantite[j]
            j+=1

        cur.execute(f"SELECT idClient FROM commandes WHERE id={idCommande};")
        idClient = int(cur.fetchone()[0])
        cur.execute(f"SELECT nom, prenom FROM clients WHERE id={idClient};")
        client_name = ' '.join(cur.fetchall()[0])
        
        commande_window = Toplevel()
        commande_window.title('Consulter votre commande')
        commande_window.geometry('300x300+500+200')
        
        client_label = Label(commande_window, text=client_name)
        client_label.pack(side=TOP, padx=5, pady=5)

        for keys, values in contenue.items():
            Label(commande_window, text=keys+'  x'+values).pack(padx=5, pady=5)
    
    recherche_window = Toplevel()
    recherche_window.title('Rechercher une commande')
    recherche_window.geometry("300x100+500+200")

    cur.execute("SELECT id FROM commandes;")
    idMax = cur.fetchall()[-1][0]

    choix_idCommande = Spinbox(recherche_window, from_=1, to=int(idMax))
    choix_idCommande.pack(padx=5, pady=5)

    recherche_button = Button(recherche_window, text='Rechercher la commande', command=afficher_commande)
    recherche_button.pack(padx=5, pady=5)
    
# CreateTables()
# ImportData()

#Récupérer les nom et prénoms des clients depuis la base de données
cur = connect.cursor()
cur.execute("SELECT nom, prenom FROM clients;")
clients_db = cur.fetchall()
clients = []
for i in clients_db:
    clients.append(str(i[0]+' '+i[1]))

cur.execute("SELECT nom, prix FROM sandwichs;")
sandwichs_db = cur.fetchall()
nom_sandwichs=[]
for i in sandwichs_db:
    nom_sandwichs.append(i[0])
cur.close

#Mon Interface graphique
maFenetre = Tk()
maFenetre.title('Aux deux Amis')
maFenetre.geometry("300x300+500+200")

#Variables concernant l'interface
list_clients = StringVar(maFenetre)
list_clients.set(clients[0])
list_sandwichs = StringVar(maFenetre)
list_sandwichs.set(nom_sandwichs[0])

#Widgets

Button(maFenetre, text='Passer une commande', command=commander).pack(padx=5, pady=5)

Button(maFenetre, text='Consulter une commande', command=consulter).pack(padx=5, pady=5)

maFenetre.mainloop()
connect.close()
sys.exit()