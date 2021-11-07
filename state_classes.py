# -*- coding: utf-8 -*-
from enum import Enum, auto
from dataclasses import dataclass
from typing import  Set, Dict, Tuple, List, Iterable, TypeVar, FrozenSet
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
    row_size: int
    col_size: int
    pacman_position: Tuple[int, int]
    pacman_enemy_positions: FrozenSet[Tuple[int, int]]
    points: FrozenSet[Tuple[int, int]]
    blocks: FrozenSet[Tuple[int, int]]
    skip_post_init: bool = False
    
    def __post_init__(self) -> None:
        """
        Validating that input is legal.
        
        Added the ability to skip post init checks to ease the creation
        of new instances based on original copy.
        Do NOT skip post init unless you know what you are doing.
        
        NOTE: I've isolated some of the assertions for more precise error
        message. (line level)
        """
        if self.skip_post_init:
            return
        
        # Loading all arguments
        (
            row_size,
            col_size,
            pacman_position,
            pacman_enemy_positions,
            points,
            blocks
        ) = (
            self.row_size,
            self.col_size,
            self.pacman_position,
            self.pacman_enemy_positions,
            self.points,
            self.blocks
        )
            
        # Validate dimensions
        assert row_size > 0 and col_size > 0
        
        # Validate pacman cords
        assert (
            0 <= pacman_position[0] < row_size 
            and 0 <= pacman_position[1] < col_size
        )
        assert pacman_position not in pacman_enemy_positions
        assert pacman_position not in points
        assert pacman_position not in blocks
        
        # Validate enemies cords
        for enemy_position in pacman_enemy_positions:
            assert (
                0 <= enemy_position[0] < row_size
                and 0 <= enemy_position[1] < col_size
            )
            assert enemy_position not in blocks
        
        # Validate points cords
        for point in points:
            assert (
                0 <= point[0] < row_size
                and 0 <= point[1] < col_size
            )
            assert point not in blocks
            
        # Validate block cords
        for block in blocks:
            assert (
                0 <= block[0] < row_size
                and 0 <= block[1] < col_size
            )
        
    def next_states(self) -> List[State]:
        new_enemy_positions = self.get_next_enemy_positions()
        possible_pacman_positions = self.get_possible_pacman_positions(new_enemy_positions)
        next_states = []
        for pacman_position in possible_pacman_positions:
            curr_points = self.points
            if pacman_position in curr_points:
                curr_points = frozenset(
                    [
                        point 
                        for point in curr_points 
                        if point != pacman_position
                    ]
                )
            next_states.append(
                Pacman(
                    row_size=self.row_size,
                    col_size=self.col_size,
                    pacman_position=pacman_position,
                    pacman_enemy_positions=new_enemy_positions,
                    points=curr_points,
                    blocks=self.blocks,
                    skip_post_init=True                    
                )
            )
        return next_states
    
    def is_end_state(self) -> bool:
        """
        The end state in pacman is that all points have been consumed
        """
        return not self.points
                
    def get_possible_pacman_positions(
            self, enemy_positions: FrozenSet[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        pacman_row, pacman_col = self.pacman_position
        possible_positions = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                next_pacman_move = (pacman_row + i, pacman_col + j)
                if (
                    abs(i) + abs(j) != 1
                    or next_pacman_move[0] < 0
                    or next_pacman_move[0] >= self.row_size
                    or next_pacman_move[1] < 0 
                    or next_pacman_move[1] >= self.col_size
                    or next_pacman_move in self.blocks
                    or next_pacman_move in self.pacman_enemy_positions
                    or next_pacman_move in enemy_positions
                ):
                    continue
                possible_positions.append(next_pacman_move)
        
        return possible_positions
        
    
    def get_next_enemy_positions(self) -> FrozenSet[Tuple[int, int]]:
        """
        Calculates for each enemy it's next move.
        This is calculated prior to Pacman's move, giving Pacman
        an advantage (Pacman is aware of their next move).
        
        The enemy moves by the following rules:
            * An enemy cannot move to a block where an enemy was previously
            * An enemy cannot move to a block that has been allocated for 
            another enemy's next move.
            * An enemy would always prefer to move closer to pacman.
            * An enemy would always move unless it cannot move to a different
            block by the rules stated above.
        """
        pacman_position = self.pacman_position
        current_enemy_positions = self.pacman_enemy_positions
        next_enemy_positions = set()
        
        for enemy_position in current_enemy_positions:
            def move_rating(new_pos: Tuple[int, int]) -> int:
                """
                The rating is decided as follows:
                    * If the movement is getting away from pacman - It is unfavored at all.
                    * If the movement is towards pacman, we would prefer the movement which 
                    closes the biggest gap.
                """
                if not (
                    abs(pacman_position[0] - enemy_position[0]) > abs(pacman_position[0] - new_pos[0])
                    or abs(pacman_position[1] - enemy_position[1]) > abs(pacman_position[1] - new_pos[1])
                ):
                    return 0
                
                return (
                    abs(new_pos[0] - enemy_position[0]) * abs(pacman_position[0] - enemy_position[0])
                    + abs((new_pos[1] - enemy_position[1])) * abs(pacman_position[1] - enemy_position[1])
                )
                
            possible_next_enemy_positions = (
                self.generate_single_enemy_positions(
                    current_position=enemy_position,
                    allocated_enemy_positions=next_enemy_positions
                )
            )
            if not possible_next_enemy_positions:
                next_enemy_positions.add(enemy_position)
                continue
            next_enemy_positions.add(
                sorted(
                    possible_next_enemy_positions,
                    key=move_rating,
                    reverse=True
                )[0]
            )
        
        return frozenset(next_enemy_positions)
                
    
    def generate_single_enemy_positions(
            self,
            current_position: Tuple[int, int],
            allocated_enemy_positions: Set[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        enemy_row, enemy_col = current_position
        possible_positions = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                next_enemy_move = (enemy_row + i, enemy_col + j)
                if (
                    abs(i) + abs(j) != 1
                    or next_enemy_move[0] < 0
                    or next_enemy_move[0] >= self.row_size
                    or next_enemy_move[1] < 0 
                    or next_enemy_move[1] >= self.col_size
                    or next_enemy_move in self.blocks
                    or next_enemy_move in self.pacman_enemy_positions
                    or next_enemy_move in allocated_enemy_positions
                ):
                    continue
                possible_positions.append(next_enemy_move)
        
        return possible_positions
        
        
        
        
    
    