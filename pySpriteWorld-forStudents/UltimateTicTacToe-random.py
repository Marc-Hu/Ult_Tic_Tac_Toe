# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
from time import sleep
import pygame
import glo

import random 
import numpy as np
import sys

sys.path.insert(0, '../1-rechercheHeuristique/')
from  grid2D import ProblemeGrid2D
from probleme import *

def getPath(node,path):
    if node != None:
        getPath(node.pere,path)
        path.append(node.etat)


    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 60  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 500 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
       
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    #score = [0]*nbPlayers
    #fioles = {} # dictionnaire (x,y)->couleur pour les fioles
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets ramassables
    #goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x,y) for x in range(3,16) for y in range(3,16)]
    #print ("Wall states:", wallStates)
    
    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19,1)
    tile_fiole_bleue = (20,1)
    
    # listes des objets fioles jaunes et bleues
    
    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid==tile_fiole_bleue]   
    all_fioles = (fiolesJaunes,fiolesBleues) 
    fiole_a_ramasser = (0,0) # servira à repérer la prochaine fiole à prendre
    
    # renvoie la couleur d'une fiole
    # potentiellement utile
    
    def couleur(o):
        if o.tileid==tile_fiole_jaune:
            return 'j'
        elif o.tileid==tile_fiole_bleue:
            return 'b'
    
    
    #-------------------------------
    # Placement aleatoire d'une fioles de couleur 
    #-------------------------------
    
    def put_next_fiole(j,t):
        o = all_fioles[j][t]
    
        # et on met cette fiole qqpart au hasard
    
        x = random.randint(1,19)
        y = random.randint(1,19)
    
        while (x,y) in tictactoeStates or (x,y) in wallStates: # ... mais pas sur un mur
            x = random.randint(1,19)
            y = random.randint(1,19)
        o.set_rowcol(x,y)
        # on ajoute cette fiole dans le dictionnaire
        #fioles[(x,y)]=couleur(o)
    
        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x,y)
    
    posPlayers = initStates
    ultimate_board=['-']*9 #L'état du morpion général initialisé avec des '-'
    ultimate_board_nb_fiol=[0]*9 #Nombre de fiole dans chaque case du morpion ultime
    fioles_position=[]#La liste des positions des fioles, pour éviter qu'on pose une fiole dans une case qui contient dàja une fiole
    w, h = 9, 9
    player1_fiole = [[0 for x in range(w)] for y in range(h)] #9 listes qui sont respectivement les 9 case du morpion ultime, chaque liste contient 9 valeur à 0, on met 1 si le joueur pose une fiole sur la case
    player2_fiole = [[0 for x in range(w)] for y in range(h)]
    #Premier coup dans un board au hasard 
    boardnum=random.randint(1,9)
    
    # Fonction qui va renvoyer la prochaine destination d'un joueur
    #j = le joueur en question
    #t= la fiole
    #forFiole = boolean pour savoir si c'est pour une fiole qu'on veut trouver la prochaine destination
    #boardnum = si c'est pas pour une fiole alors c'est pour indiquer la prochaine case du morpion ultime
    def get_next_target(j,t, forFiole, boardnum):
        grid = np.ones((20, 20), dtype=bool)
        for c in wallStates:
            grid[c[0]][c[1]] = False
        
        autre_player = posPlayers[(j+1)%2]
        grid[autre_player[0]][autre_player[1]] = False
        
        pos = posPlayers[j]
        # print("position:",pos)
        if forFiole :
            target = all_fioles[j][t].get_rowcol() 
        else :
            #On choisit une autre case si celle-ci est déjà gagné par un joueur
            while ultimate_board[boardnum-1]=='X' or ultimate_board[boardnum-1]=='O' :
                boardnum=random.randint(0, 9)
            #Dans la case, on va choisir aléatoirement une case
            x1, x2, y1, y2=random_board(boardnum)
            x = random.randint(x1,x2)
            y = random.randint(y1,y2)
            #Si la case qu'on a choisit aléatoirement est déjà utilisé
            while (x, y) in fioles_position:
                #Alors on refait un tirage aléatoire
                x = random.randint(x1,x2)
                y = random.randint(y1,y2)
            target = (x,y)
            fioles_position.append((x, y))#Si la place est libre on le rajoute dans fioles_position
            #On incrémente le nombre de fiole dans la case du morpion ultime
            ultimate_board_nb_fiol[boardnum-1]=ultimate_board_nb_fiol[boardnum-1]+1 
            print(ultimate_board_nb_fiol)
            nextboard=get_next_board(x1, y1, x, y) #On récupère le numéro de la prochaine case pour le joueur suivant
            if j==0: #Si c'est le joueur un (ou 0)
                # print(boardnum, nextboard-1)
                player1_fiole[boardnum-1][nextboard-1]=1 #Alors on passe à 1 la valeur de la case du player1
            else :
                player2_fiole[boardnum-1][nextboard-1]=1
            boardnum=nextboard
            # print(game.layers['ramassable'])
        # print("target",target)
        p3 = ProblemeGrid2D(pos,target,grid,'manhattan')
        node = astar(p3,True,False);
        path = []
        getPath(node,path)
        
        return path, boardnum
    
    def random_board(num):
        if num==1:
            return 4, 6, 4, 6
        if num==2:
            return 8, 10, 4, 6
        if num==3:
            return 12, 14, 4, 6
        if num==4:
            return 4, 6, 8, 10
        if num==5:
            return 8, 10, 8, 10
        if num==6:
            return 12, 14, 8, 10
        if num==7:
            return 4, 6, 12, 14
        if num==8:
            return 8, 10, 12, 14
        return 12, 14, 12, 14

    def get_next_board(x1, y1, x, y):
        return 1+x-x1+(y-y1)*3

    def go_to_next_target(j, tour, boardnum):
        path_to_middle, boardnum = get_next_target(j,tour, False, boardnum);
        for step_mid in path_to_middle:
            row,col = posPlayers[j]

            x_inc,y_inc = step_mid
            next_row = x_inc
            next_col = y_inc
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                # print ("pos :", j, next_row,next_col)
                game.mainiteration()

                col=next_col
                row=next_row
                posPlayers[j]=(row,col)
        players[j].depose(game.layers)
        return (next_row, next_col), boardnum
        
    #Fonction qui va évaluer les cases du morpion ultime
    def evaluate_player_line():
        for i in range (len(player1_fiole)):
            #Si le joueur 1 à fait une ligne sur une case i du morpion ultime
            if player1_fiole[i][0] and player1_fiole[i][1] and player1_fiole[i][2] or player1_fiole[i][3] and player1_fiole[i][4] and player1_fiole[i][5] or player1_fiole[i][6] and player1_fiole[i][7] and player1_fiole[i][8] or player1_fiole[i][0] and player1_fiole[i][4] and player1_fiole[i][8] or player1_fiole[i][2] and player1_fiole[i][4] and player1_fiole[i][6] or player1_fiole[i][0] and player1_fiole[i][3] and player1_fiole[i][6] or player1_fiole[i][1] and player1_fiole[i][4] and player1_fiole[i][7] or player1_fiole[i][2] and player1_fiole[i][5] and player1_fiole[i][8]:
                ultimate_board[i]='X' #Il a gagné la case
            elif player2_fiole[i][0] and player2_fiole[i][1] and player2_fiole[i][2] or player2_fiole[i][3] and player2_fiole[i][4] and player2_fiole[i][5] or player2_fiole[i][6] and player2_fiole[i][7] and player2_fiole[i][8] or player2_fiole[i][0] and player2_fiole[i][4] and player2_fiole[i][8] or player2_fiole[i][2] and player2_fiole[i][4] and player2_fiole[i][6] or player2_fiole[i][0] and player2_fiole[i][3] and player2_fiole[i][6] or player2_fiole[i][1] and player2_fiole[i][4] and player2_fiole[i][7] or player2_fiole[i][2] and player2_fiole[i][5] and player2_fiole[i][8]:
                ultimate_board[i]='O' #Sinon si c'est le joueur 2, alors il gagne la case
            #Si une case est pleine et que personne ne gagne alors on compte le nombre de fiole dans la case
            elif ultimate_board_nb_fiol[i]==9: 
                #Si le joueur 1 à plus de fiole que le joueur 2 alors qui remporte la case
                if np.sum(player1_fiole[i])>np.sum(player2_fiole[i]) :
                    ultimate_board[i]='X'
                else: #Sinon c'est le joueur 2
                    ultimate_board[i]='O'
        print(ultimate_board)

    #Fonction qui va savoir si la partie est remporté ou non
    def win():
        evaluate_player_line() #On met à jour les lignes
        #On regarde si le joueur 1 gagne
        if ultimate_board[0]=='X' and ultimate_board[1]=='X' and ultimate_board[3]=='X' or ultimate_board[3]=='X' and ultimate_board[4]=='X' and ultimate_board[5]=='X' or ultimate_board[6]=='X' and ultimate_board[7]=='X' and ultimate_board[8]=='X' or ultimate_board[0]=='X' and ultimate_board[4]=='X' and ultimate_board[8]=='X' or ultimate_board[2]=='X' and ultimate_board[4]=='X' and ultimate_board[6]=='X' or ultimate_board[0]=='X' and ultimate_board[3]=='X' and ultimate_board[6]=='X' or ultimate_board[1]=='X' and ultimate_board[4]=='X' and ultimate_board[7]=='X' or ultimate_board[2]=='X' and ultimate_board[5]=='X' and ultimate_board[8]=='X':
            return True, 0
        #On regarde si le joueur 2 gagne
        if ultimate_board[0]=='O' and ultimate_board[1]=='O' and ultimate_board[3]=='O' or ultimate_board[3]=='O' and ultimate_board[4]=='O' and ultimate_board[5]=='O' or ultimate_board[6]=='O' and ultimate_board[7]=='O' and ultimate_board[8]=='O' or ultimate_board[0]=='O' and ultimate_board[4]=='O' and ultimate_board[8]=='O' or ultimate_board[2]=='O' and ultimate_board[4]=='O' and ultimate_board[6]=='O' or ultimate_board[0]=='O' and ultimate_board[3]=='O' and ultimate_board[6]=='O' or ultimate_board[1]=='O' and ultimate_board[4]=='O' and ultimate_board[7]=='O' or ultimate_board[2]=='O' and ultimate_board[5]=='O' and ultimate_board[8]=='O':
            return True, 1
        #On regarde si c'est un match nul
        if len(fioles_position)==81:
            return True, -1
        #False sinon (on continue de jouer)
        return False, -1
    #-------------------------------
    # Boucle principale de déplacements, un joueur apres l'autre
    #-------------------------------
    

    tour = 0    
    j = 0 # le joueur 0 commence
    # on place la premiere fiole jaune      

    fiole_a_ramasser = put_next_fiole(0,tour)    
    no_fiols = len(all_fioles[j])

    while(tour<=no_fiols):
        # bon ici on fait juste plusieurs random walker pour exemple...
        path, boardnum = get_next_target(j,tour, True, boardnum);
        for step in path:
            row,col = posPlayers[j]

            x_inc,y_inc = step
            next_row = x_inc
            next_col = y_inc
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,next_col) not in wallStates) and next_row>=0 and next_row<=19 and next_col>=0 and next_col<=19:
                players[j].set_rowcol(next_row,next_col)
                # print ("pos :", j, next_row,next_col)
                game.mainiteration()

                col=next_col
                row=next_row
                posPlayers[j]=(row,col)

            # si on trouve la fiole par un grand hasard...
            if (row,col)==fiole_a_ramasser:
                o = players[j].ramasse(game.layers) # on la ramasse
                game.mainiteration()
                # print ("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)

                # ici il faudrait aller la mettre a la position choisie
                # pour jouer a ultimate tic-tac-toe
                # et verifier que la position est legale etc.            

                res, boardnum=go_to_next_target(j, tour, boardnum)
                player_win, joueur=win()
                if player_win:
                    if not joueur==-1 :
                        print("Le joueur : ", joueur , " à gagné.")
                    else :
                        print("Match nul.")
                    sleep(120)
                    pygame.quit()
                # on active le joueur suivant
                # et on place la fiole suivante
                j = (j+1)%2     
                if j == 0:
                    tour+=1

                fiole_a_ramasser=put_next_fiole(j,tour)    
    
                
                #break
            
    
    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    


