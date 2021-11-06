# -*- coding: utf-8 -*-
from enum import Enum, auto
from dataclasses import dataclass
from typing import  Dict, Tuple, List, Iterable, TypeVar
from graph import State

# Defining this to allow coherent type hints
Maze = TypeVar("Maze")

@dataclass(frozen=True)
class LightBulb(State):
    is_on: bool
    
    def next_states(self) -> List[State]:
        return [LightBulb(not self.is_on)]
    
    def is_end_state(self) -> bool:
        """
        The end state in a light-bulb is being turned on by our definition.
        """
        return self.is_on

@dataclass(frozen=True)
class ModN(State):
    mod: int
    inc: int
    val: int
    
    def next_states(self) -> List[State]:
        return [ModN(self.mod, self.inc, (self.val+self.inc)%self.mod)]
    
    def is_end_state(self) -> bool:
        """
        The end state in ModN is the value being equal to 0.
        """
        return self.val == 0

@dataclass(frozen=True)
class Maze(State):
    class MazeTypes(Enum):
        Pathway = auto()
        Block = auto()
        Exit = auto()
        
    current_pos: Tuple[int, int]
    maze: Tuple[Tuple[MazeTypes]]
    
    def __post_init__(self) -> None:
        """
        Validating that start point is also legal
        """
        if not self.legal_position(self.current_pos): 
            raise ValueError(
                "Start point cannot be inside a block point, or outside maze "
                "dimensions."
            )
    
    def next_states(self) -> List[State]:
        next_states = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if abs(i) + abs(j) != 1:
                    continue
                new_pos = (self.current_pos[0]+i, self.current_pos[1]+j)
                if self.legal_position(new_pos):
                    next_states.append(Maze(new_pos, self.maze))
                
        return next_states
    
    def legal_position(self, position: Tuple[int, int]) -> bool:
        pos_row, pos_col = position
        if (
            pos_row < 0
            or pos_row >= len(self.maze)
            or pos_col < 0
            or pos_col >= len(self.maze[0])
            or (
                self.maze[pos_row][pos_col] == self.MazeTypes.Block
            )
        ): 
            return False
        
        return True
    
    def is_end_state(self) -> bool:
        return (
            self.maze[self.current_pos[0]][self.current_pos[1]] == self.MazeTypes.Exit
        )
    
    def attractive_rate(self) -> float:
        current_pos, exit_pos = self.current_pos, self.exit_pos
        return 1/(1 + abs(current_pos[0] - exit_pos[0]) + abs(current_pos[1] - exit_pos[1]))
        
    @property
    def exit_pos(self) -> Tuple[int, int]:
        row_size, col_size = len(self.maze), len(self.maze[0])
        for i in range(row_size):
            for j in range(col_size):
                if self.maze[i][j] == self.MazeTypes.Exit:
                    return (i,j)
    
    @staticmethod
    def maze_constructor(
        maze_dimensions: Tuple[int, int],
        exit_position: Tuple[int, int],
        block_points: Dict[int, Iterable[int]]
    ):
        """
        maze_dimensions: Tuple[int, int] -  x1 = rows, x2 = cols
        exit_position: The exiting position in the maze
        block_points: a dictionary in which the key points to which row you 
        want to add block-points, and in as the value you specify in which columns.
        
        This constructor initializes the maze and adds the blocks according to
        passed arguments.
        """
        Maze._validate_init_args(
            maze_dimensions=maze_dimensions, 
            exit_position=exit_position, 
            block_points=block_points
        )
        row_size, col_size = maze_dimensions
        maze = [
            [Maze.MazeTypes.Pathway] * row_size
            for i in range(col_size)
        ]
        maze[exit_position[0]][exit_position[1]] = Maze.MazeTypes.Exit
        for row_index in block_points:
            for col_index in block_points[row_index]:
                maze[row_index][col_index] = Maze.MazeTypes.Block
        return tuple(tuple(row) for row in maze)
    
    @staticmethod
    def _validate_init_args(
        maze_dimensions: Tuple[int, int],
        exit_position: Tuple[int, int],
        block_points: Dict[int, Iterable[int]]
    ) -> None:
        """
        Validates that exit point is not inside blocks,
        and that exit and block points exist within the dimensions
        of the maze.
        """
        row_size, col_size = maze_dimensions
        exit_row, exit_col = exit_position
        if (
            (
                exit_row in block_points and exit_col in block_points[exit_row]
            )
            or exit_row < 0
            or exit_row >= row_size
            or exit_col < 0
            or exit_col >= col_size
        ): 
            raise ValueError(
                "Exit point cannot be inside a block point, or outside maze "
                "dimensions."
            )
        
        assert all(
            type(row_index) == int 
            and row_index >= 0 
            and row_index < row_size
            and all(
                type(col_index) == int
                and col_index >= 0
                and col_index < col_size
                for col_index in col_indexes
            )
            for row_index, col_indexes in block_points.items()
        )
    
    @staticmethod
    def pretty_str(sol: List[Maze]) -> str:
        return [state.current_pos for state in sol]

@dataclass(frozen=True)
class Pacman(State):
    
    def __post_init__(self):
        pass