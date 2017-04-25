#!/usr/bin/python3

from game import *
import  random
import time
import socket
import select
import sys






""" generate a random valid configuration """
def randomConfiguration(clients_connectes):
    boats = [];
    while not isValidConfiguration(boats):
        boats=[]
        tab = []
        for i in range(5):
            x = random.randint(0,9)
            y = random.randint(0,9)
            isHorizontalint = random.randint(0,1)
            isHorizontal = isHorizontalint == 0
            boats = boats + [Boat(x+1,y+1,LENGTHS_REQUIRED[i],isHorizontal)]
            tab = tab + [ x , y , isHorizontalint]
    for i in range (len(tab)):
        clients_connectes[0].sendall(str(tab[i]).encode('utf-8'))
        clients_connectes[1].sendall(str(tab[i]).encode('utf-8'))
            
    return boats

def randomConfiguration2():
    boats = [];
    while not isValidConfiguration(boats):
        boats=[]
        for i in range(5):
            x = random.randint(1,10)
            y = random.randint(1,10)
            isHorizontal = random.randint(0,1) == 0
            boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    return boats


    

def displayConfiguration(boats, shots=[], showBoats=True):
    Matrix = [[" " for x in range(WIDTH+1)] for y in range(WIDTH+1)]
    for i  in range(1,WIDTH+1):
        Matrix[i][0] = chr(ord("A")+i-1)
        Matrix[0][i] = i

    if showBoats:
        for i in range(NB_BOATS):
            b = boats[i]
            (w,h) = boat2rec(b)
            for dx in range(w):
                for dy in range(h):
                    Matrix[b.x+dx][b.y+dy] = str(i)

    for (x,y,stike) in shots:
        if stike:
            Matrix[x][y] = "X"
        else:
            Matrix[x][y] = "O"


    for y in range(0, WIDTH+1):
        if y == 0:
            l = "  "
        else:
            l = str(y)
            if y < 10:
                l = l + " "
        for x in range(1,WIDTH+1):
            l = l + str(Matrix[x][y]) + " "
        print(l)

""" display the game viewer by the player"""
def displayGame(game, player):
    otherPlayer = (player+1)%2
    displayConfiguration(game.boats[player], game.shots[otherPlayer], showBoats=True)
    displayConfiguration([], game.shots[player], showBoats=False)



""" Play a new random shot """
def randomNewShot(shots):
    (x,y) = (random.randint(1,10), random.randint(1,10))
    while not isANewShot(x,y,shots):
        (x,y) = (random.randint(1,10), random.randint(1,10))
    return (x,y)

def receiveBoat(client):
    boats = []
    for i in range(5):
        x = int(client.recv(1)) + 1
        y = int(client.recv(1)) + 1
        isHorizontal = int(client.recv(1))
        isHorizontal = isHorizontal == 0
        boats = boats + [Boat(x,y,LENGTHS_REQUIRED[i],isHorizontal)]
    
    return boats
def main_robot():
	boats1 = randomConfiguration2()
	boats2 = randomConfiguration2()
	game = Game(boats1, boats2)
	displayGame(game, 0)
	print("======================")
	currentPlayer = 0
	displayGame(game, currentPlayer)
	while gameOver(game) == -1:
		print("======================")
		if currentPlayer == J0:
			x_char = input ("quelle colonne ? ")
			x_char.capitalize()
			x = ord(x_char)-ord("A")+1
			y = int(input ("quelle ligne ? "))
		else:
			(x,y) = randomNewShot(game.shots[currentPlayer])
			time.sleep(1)
		addShot(game, x, y, currentPlayer)
		displayGame(game, 0)
		currentPlayer = (currentPlayer+1)%2
	print("game over")
	print("your grid :")
	displayGame(game, J0)
	print("the other grid :")
	displayGame(game, J1)

	if gameOver(game) == J0:
		print("You win !")
	else:
		print("you loose !")

def main_client(x):
    choix = (input ("Voulez vous jouer en réseau <N>on <O>ui ?"))
    if (choix == 'O'):
    	main_robot()
    	return
    #Création de la socket TCP/IP
    client = socket.socket(family = socket.AF_INET6, type = socket.SOCK_STREAM, proto = 0, fileno = None)

    #On connecte la nouvelle socket client au port où le server "écoute"
    server_address = (x,7777)
    print("Connection au server distant sur le port 7777")
    client.connect(server_address)
    print("Vous êtes connecté au serveur de jeu")
    print("Attente de joueur ...")

    Player_Number = client.recv(1)
    print("Joueur trouvé")
    boats1 = receiveBoat(client)
    boats2 = receiveBoat(client)
    game = Game(boats1, boats2)
    
    print("======================")

    
    print("your player number is %d" % int(Player_Number))
    
    displayGame(game, int(Player_Number))
    currentPlayer = int(Player_Number)
    while gameOver(game) == -1:
        print("======================")
        if currentPlayer == J0:
            x_char = input ("quelle colonne ? ")
            x_char.capitalize()
            x = ord(x_char)-ord("A")  + 1
            y = int(input ("quelle ligne ? "))  
            client.send(str(x-1).encode('utf-8'))
            client.send(str(y-1).encode('utf-8'))
            print(currentPlayer)
            addShot(game, x, y, int(Player_Number))
        else:
            print("L'autre joueur joue son coup ...")
            x = client.recv(1) 
            y = client.recv(1) 
            time.sleep(1)
            print(currentPlayer)
            addShot(game, int(x)+1, int(y)+1, (int(Player_Number)+1)%2)
        displayGame(game, int(Player_Number))
        currentPlayer = (currentPlayer+1)%2
    print("game over")
    print("your grid :")
    displayGame(game, J0)
    print("the other grid :")
    displayGame(game, J1)

    if gameOver(game) == J0:
        print("You win !")
    else:
        print("you loose !")


def main():

    if len(sys.argv) >1:
        main_client(sys.argv[1])
        return
    
    #création de socket TCP
    server = socket.socket(family = socket.AF_INET6, type = socket.SOCK_STREAM, proto = 0, fileno = None)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Bind la socket au port 7777
    print("Lancement du serveur sur le port 7777")
    server.bind(('::',7777))
    # "Ecoute" pour les demandes de connections entrantes
    server.listen(5)

 
    #Attente de connexion
    clients_connectes = []
    
    print("Attente de joueur(s) ..")
    while True:
        # Attente d'une connexion
        #On récupère les sockets disponibles en lecture
        connexions_demandees, wlist, xlist = select.select([server],[], [])
        print("1 joueur s'est connecté")
    
        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            # On ajoute la socket connecté à la liste des clients
            clients_connectes.append(connexion_avec_client)

        #Les premiers clients connectés sont les joueurs on leur renvoit les infos sur la table de jeux et leur numero de joueurs
        if len(clients_connectes) == 2:
            clients_connectes[0].sendall(str(0).encode('utf-8'))
            clients_connectes[1].sendall(str(1).encode('utf-8'))
            boats1 = randomConfiguration(clients_connectes)
            boats2 = randomConfiguration(clients_connectes)
            game = Game(boats1, boats2)
            print("%s joueur(s) connecté(s)" % len(clients_connectes))
            
            
            #Pour commencer on defini le joueur du serveur à 0 
            currentPlayer = 0
            
            
            while gameOver(game) == -1:        
                if (currentPlayer == J0):
                    #Si c'est le tour du joueur 0 on attend les coordonées qu il a joue et on les envoie au joueur 1
                    x = clients_connectes[0].recv(1)
                    y = clients_connectes[0].recv(1)
                    addShot(game, int(x), int(y), currentPlayer)
                    clients_connectes[1].send(x)
                    clients_connectes[1].send(y)
                    currentPlayer = (currentPlayer+1)%2
                else:
                    #Si c'est le tour du joueur 1 on attend les coordonées qu il a joue et on les envoie au joueur 0
                    x = clients_connectes[1].recv(1)
                    y = clients_connectes[1].recv(1)
                    addShot(game, int(x), int(y), currentPlayer)
                    clients_connectes[0].send(x)
                    clients_connectes[0].send(y)
                    currentPlayer = (currentPlayer+1)%2
            
            #Fin du jeu et fermeture des connexions
            for client in clients_connectes:
                client.close()
            server.close()

            
    
main()
