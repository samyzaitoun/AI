# -*- coding: utf-8 -*-
"""
Created on Sat Nov  6 19:47:31 2021

@author: Samy
"""
from graph import Graph, Strategy
from state_classes import Maze

if __name__ == "__main__":
    print("Hello World")
    m = Maze((0,0), Maze.maze_constructor((30,30), (29,29), {}))
    g = Graph(m)
    print(Maze.pretty_str(g.solve_end_state(Strategy.PDFS)))