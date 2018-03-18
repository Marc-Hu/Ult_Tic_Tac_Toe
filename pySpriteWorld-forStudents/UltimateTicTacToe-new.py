# -*- coding: utf-8 -*-

# Nicolas, 2015-11-18

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game, check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random
import numpy as np
import sys
import time

sys.path.insert(0, '../1-rechercheHeuristique/')
from grid2D import ProblemeGrid2D
from probleme import *
from UltimateTicTacToeGame import UTTTGame


def getPath(node, path):
    if node != None:
        getPath(node.pere, path)
        path.append(node.etat)


# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

uttt_game = UTTTGame()


def init(_boardname=None):
    global player, game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'tictactoeBis'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 30  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    # player = game.player


def main():
    # for arg in sys.argv:
    iterations = 500  # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print("Iterations: ")
    print(iterations)

    init()

    # -------------------------------
    # Initialisation
    # -------------------------------

    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    # score = [0]*nbPlayers
    # fioles = {} # dictionnaire (x,y)->couleur pour les fioles

    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print("Init states:", initStates)

    # on localise tous les objets ramassables
    # goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    # print ("Goal states:", goalStates)

    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    # et la zone de jeu pour le tic-tac-toe
    tictactoeStates = [(x, y) for x in range(3, 16) for y in range(3, 16)]
    # print ("Wall states:", wallStates)

    # les coordonnees des tiles dans la fiche
    tile_fiole_jaune = (19, 1)
    tile_fiole_bleue = (20, 1)

    # listes des objets fioles jaunes et bleues

    fiolesJaunes = [f for f in game.layers['ramassable'] if f.tileid == tile_fiole_jaune]
    fiolesBleues = [f for f in game.layers['ramassable'] if f.tileid == tile_fiole_bleue]
    all_fioles = (fiolesJaunes, fiolesBleues)
    fiole_a_ramasser = (0, 0)  # servira à repérer la prochaine fiole à prendre

    # renvoie la couleur d'une fiole
    # potentiellement utile

    def couleur(o):
        if o.tileid == tile_fiole_jaune:
            return 'j'
        elif o.tileid == tile_fiole_bleue:
            return 'b'

    def get_grid():
        grid = np.ones((20, 20), dtype=bool)
        for c in wallStates:
            grid[c[0]][c[1]] = False

        autre_player = posPlayers[(j + 1) % 2]
        grid[autre_player[0]][autre_player[1]] = False
        return grid

    # -------------------------------
    # Placement aleatoire d'une fioles de couleur 
    # -------------------------------

    def put_next_fiole(j, t, move=None):
        o = all_fioles[j][t]

        # et on met cette fiole qqpart au hasard
        if move is None:
            x = random.randint(1, 19)
            y = random.randint(1, 19)

            while (x, y) in tictactoeStates or (x, y) in wallStates:  # ... mais pas sur un mur
                x = random.randint(1, 19)
                y = random.randint(1, 19)
        else:
            x, y = move
        o.set_rowcol(x, y)
        # on ajoute cette fiole dans le dictionnaire
        # fioles[(x,y)]=couleur(o)

        game.layers['ramassable'].add(o)
        game.mainiteration()
        return (x, y)

    posPlayers = initStates

    def get_next_fiole(j, t, target=None):
        grid = get_grid()

        pos = posPlayers[j]
        if target is None:
            target = all_fioles[j][t].get_rowcol()
        print("target", target)
        p2 = ProblemeGrid2D(pos, target, grid, 'manhattan')
        node = astar(p2, False, False)
        path = []
        getPath(node, path)
        return path

    # -------------------------------
    # Boucle principale de déplacements, un joueur apres l'autre
    # -------------------------------

    tour = 0
    j = 0  # le joueur 0 commence
    # on place la premiere fiole jaune      

    fiole_a_ramasser = put_next_fiole(0, tour)
    no_fiols = len(all_fioles[j])
    state = True
    # get_fiol is a boolean that indicates what ever we're going to find a fiol or to depose it somewhere
    get_fiol = True
    target = None
    while (state):
        # bon ici on fait juste plusieurs random walker pour exemple...
        if get_fiol:
            path = get_next_fiole(j, tour)
        else:
            path = get_next_fiole(j, tour, target)

        for step in path:
            row, col = posPlayers[j]

            x_inc, y_inc = step
            next_row = x_inc
            next_col = y_inc
            # and ((next_row,next_col) not in posPlayers)
            if ((next_row,
                 next_col) not in wallStates) and next_row >= 0 and next_row <= 19 and next_col >= 0 and next_col <= 19:
                players[j].set_rowcol(next_row, next_col)
                # print("pos :", j, next_row, next_col)
                game.mainiteration()

                col = next_col
                row = next_row
                posPlayers[j] = (row, col)

        if get_fiol:
            # si on trouve la fiole par un grand hasard...
            o = players[j].ramasse(game.layers)  # on la ramasse
            game.mainiteration()
            print("Objet de couleur ", couleur(o), " trouvé par le joueur ", j)

            # ici il faudrait aller la mettre a la position choisie
            # pour jouer a ultimate tic-tac-toe
            # et verifier que la position est legale etc.

            # we play a move
            state, board_move, cell_move = uttt_game.play()
            # we calculate the coordinates according to the game plan
            target = 4 + board_move[0] * 4 + cell_move[0], 4 + board_move[1] * 4 + cell_move[1]
            # on active le joueur suivant
            # et on place la fiole suivante

            # get fiol to False since we want to depose the fiol that we got
            get_fiol = False

            # break
        else:
            # on depose la fiole
            players[j].depose(game.layers)
            game.mainiteration()
            # next round
            j = (j + 1) % 2
            if j == 0:
                tour += 1
            fiole_a_ramasser = put_next_fiole(j, tour)
            get_fiol = True

    time.sleep(120)
    pygame.quit()


if __name__ == '__main__':
    main()
