# -*- coding: utf-8 -*-
from abc import ABC
from enum import Enum, auto
from typing import Callable, Set, List, Optional, TypeVar

# Defining this to allow coherent type hints
State = TypeVar("State")
Node = TypeVar("Node")
Graph = TypeVar("Graph")

class State(ABC):
    def __init__(self):
        raise NotImplementedError(
            "You cannot instantiate the base class State directly. "
            "Please create an inheriting class and implement it."
        )
    
    def next_states(self) -> List[State]:
        """
        Returns all possible next states from the current state.
        """
        raise NotImplementedError(
            "The next_state method must be implemented in the inheriting subclass."
        )
    
    def is_end_state(self) -> bool:
        """
        Returns true if this instance of state is considered an end-state.
        """
        raise NotImplementedError(
            "The is_end_state method must be implemented in the inheriting subclass."
        )
    
    def attractive_rate(self) -> float:
        """
        Returns a float between 0 to 1 which represents how close this current
        state is to the end state.
        """
        raise NotImplementedError(
            "The attractive_rate method must be implemented in the inheriting subclass."
        )

class Node:
    state: State
    arcs: List[Node]
    evaluated_hash: Optional[int] = None

    def __init__(self, state: State):
        self.state = state
        self.arcs = []
    
    def add_arcs(self) -> List[Node]:
        if not self.arcs:
            for next_state in self.state.next_states():
                self.arcs.append(Node(next_state))
                
        return self.arcs
    
    def get_arcs(self) -> List[Node]:
        return self.arcs or self.add_arcs()
    
    def __eq__(self, obj: Node) -> bool:
        return self.state == obj.state
    
    def __hash__(self) -> int:
        self.evaluated_hash = (
            self.evaluated_hash or hash(self.state)
        )
        return self.evaluated_hash 

class Strategy(Enum):
    BFS = auto() # Breadth First search
    DFS = auto() # Depth First Search
    DFSL = auto() # DFS - Depth L
    IDFSL = auto() # Incremental Depth L DFS
    PDFS = auto() # Priority DFS

class Graph:
    start_node: Node
    solved_state_nodes: Set[Node]
    
    def __init__(self, start_state: State):
        self.start_node = Node(start_state)
        self.solved_state_nodes = {self.start_node}
    
    def solve_end_state(self, strategy: Strategy, **kwargs) -> List[Node]:
        strategy_map = {
            Strategy.BFS: self.solve_end_state_BFS,
            Strategy.DFS: self.solve_end_state_DFS,
            Strategy.DFSL: self.solve_end_state_DFSL,
            Strategy.IDFSL: self.solve_end_state_IDFSL,
            Strategy.PDFS: self.solve_end_state_PDFS,
        }
        self.solved_state_nodes = {self.start_node}
        return strategy_map[strategy](**kwargs)
    
    def solve_end_state_BFS(self) -> List[Node]:
        """
        Implementation of BFS on Graph
        Maintains a fifo-queue and spawns more nodes 
        using add_arcs method.
        """
        fifo_queue = [(self.start_node, 0)]
        while fifo_queue:
            curr_node, depth = fifo_queue.pop(0)
            if curr_node.state.is_end_state():
                path = self.solve_end_state(Strategy.DFSL, depth=depth)
                return path
            curr_node_arcs = curr_node.add_arcs()
            for node in curr_node_arcs:
                if node in self.solved_state_nodes:
                    continue
                self.solved_state_nodes.add(node)
                fifo_queue.append((node, depth + 1))
        
        raise ValueError("No end-state found from base-state.")
    
    def DFS_decorator(
            dfs_method: Callable[[Graph], Optional[List[Node]]]
    ) -> Callable[[Graph], List[State]]:
        def wrapper(*args, **kwargs):
            path_sol = dfs_method(*args, **kwargs)
            if not path_sol:
                raise ValueError("No end-state found from base-state.")
            return [
                node.state for node in path_sol
            ]
        return wrapper
    
    @DFS_decorator
    def solve_end_state_DFS(self):
        """
        Implementation of DFS on Graph
        Maintains path using recursion and spawns pathway 
        using add_arcs method.
        """
        return self.recursive_solve_end_state_DFS([self.start_node])
    
    def recursive_solve_end_state_DFS(
        self, path: List[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFS
        """
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        for node in curr_node.add_arcs():
            if node in self.solved_state_nodes:
                continue
            self.solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFS(path):
                return path
            self.solved_state_nodes.remove(node)
            path.pop(-1)
        return None
    
    @DFS_decorator
    def solve_end_state_DFSL(self, depth: int):
        """
        Implementation of DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using add_arcs method.
        """
        return self.recursive_solve_end_state_DFSL(depth, [self.start_node])
    
    def recursive_solve_end_state_DFSL(
            self, depth: int, path: List[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFSL
        """
        if depth < 0:
            return None
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        for node in curr_node.add_arcs():
            if node in self.solved_state_nodes:
                continue
            self.solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFSL(depth-1, path):
                return path
            self.solved_state_nodes.remove(node)
            path.pop(-1)
        return None
    
    def solve_end_state_IDFSL(self) -> Optional[List[State]]:
        """
        Implementation of Incremental DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using add_arcs method. 
        """
        i = 0
        while True:
            try:
                sol = self.solve_end_state(Strategy.DFSL, depth=i)
            except ValueError:
                pass
            if sol:
                return sol
            i += 1
        
    @DFS_decorator
    def solve_end_state_PDFS(self):
        return self.recursive_solve_end_state_PDFS([self.start_node])
    
    def recursive_solve_end_state_PDFS(
            self, path: List[Node]
    ) -> Optional[List[Node]]:
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        sorted_nodes = sorted(
                curr_node.add_arcs(), 
                key=lambda node: node.state.attractive_rate(),
                reverse=True
        )
        for node in sorted_nodes:
            if node in self.solved_state_nodes:
                continue
            self.solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_PDFS(path):
                return path
            self.solved_state_nodes.remove(node)
            path.pop(-1)
        return None
