# -*- coding: utf-8 -*-
from abc import ABC
from enum import Enum, auto
from typing import Dict, Callable, Set, List, Optional, TypeVar
from random import shuffle

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
        Returns a float which gives a rating to the current state.
        Can be used to compare between two states and decide which one is more
        favorable (The one with a better (higher) attractiveness).
        """
        raise NotImplementedError(
            "The attractive_rate method must be implemented in the inheriting subclass."
        )

class Node:
    state: State
    evaluated_hash: Optional[int] = None

    def __init__(self, state: State):
        self.state = state
    
    def get_arcs(self) -> List[Node]:
        return [Node(next_state) for next_state in self.state.next_states()]
    
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
    RDFS = auto() # Random Depth First Search
    DFSL = auto() # DFS - Depth L
    RDFSL = auto() # RDFS - Depth L
    IDFSL = auto() # Incremental Depth L DFS
    RIDFSL = auto() # Random IDFSL 
    PDFS = auto() # Priority DFS

class Graph:
    start_node: Node
    
    def __init__(self, start_state: State):
        self.start_node = Node(start_state)
    
    def solve_end_state(self, strategy: Strategy, **kwargs) -> List[Node]:
        strategy_map = {
            Strategy.BFS: self.solve_end_state_BFS,
            Strategy.DFS: self.solve_end_state_DFS,
            Strategy.RDFS: self.solve_end_state_RDFS,
            Strategy.DFSL: self.solve_end_state_DFSL,
            Strategy.RDFSL: self.solve_end_state_RDFSL,
            Strategy.IDFSL: self.solve_end_state_IDFSL,
            Strategy.RIDFSL: self.solve_end_state_RIDFSL,
            Strategy.PDFS: self.solve_end_state_PDFS,
        }
        return strategy_map[strategy](**kwargs)
    
    def solve_end_state_BFS(self) -> List[Node]:
        """
        Implementation of BFS on Graph
        Maintains a fifo-queue and spawns more nodes 
        using get_arcs method.
        """
        parent_dict = {}
        fifo_queue = [(self.start_node, 0)]
        while fifo_queue:
            curr_node, depth = fifo_queue.pop(0)
            if curr_node.state.is_end_state():
                path = self.deconstruct_path_from_parent_dict(curr_node, parent_dict)
                return path
            curr_node_arcs = curr_node.get_arcs()
            for node in curr_node_arcs:
                if node in parent_dict:
                    continue
                parent_dict[node] = curr_node
                fifo_queue.append((node, depth + 1))
        
        raise ValueError("No end-state found from base-state.")
    
    def deconstruct_path_from_parent_dict(
            self, 
            end_node: Node, 
            parent_dict: Dict[Node, Node]
    ) -> List[State]:
        path = [end_node]
        curr_node = end_node
        while curr_node != self.start_node:
            curr_node = parent_dict[curr_node]
            path.append(curr_node)
        return [node.state for node in reversed(path)]
        
    
    def dfs_wrapper(
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
    
    @dfs_wrapper
    def solve_end_state_DFS(self):
        """
        Implementation of DFS on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method.
        """
        solved_state_nodes = {self.start_node}
        return self.recursive_solve_end_state_DFS([self.start_node], solved_state_nodes)
    
    def recursive_solve_end_state_DFS(
        self, path: List[Node], solved_state_nodes: Set[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFS
        """
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        node_arcs = curr_node.get_arcs()
        for node in node_arcs:
            if node in solved_state_nodes:
                continue
            solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFS(path, solved_state_nodes):
                return path
            path.pop(-1)
        return None
    
    @dfs_wrapper
    def solve_end_state_RDFS(self):
        """
        Implementation of DFS on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method.
        Uses randomization to create a more equal chance for each node
        instead of relying on deterministic order by hash.
        """
        solved_state_nodes = {self.start_node}
        return self.recursive_solve_end_state_DFS([self.start_node], solved_state_nodes)
    
    def recursive_solve_end_state_RDFS(
        self, path: List[Node], solved_state_nodes: Set[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFS
        """
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        node_arcs = curr_node.get_arcs()
        shuffle(node_arcs)
        for node in node_arcs:
            if node in solved_state_nodes:
                continue
            solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFS(path, solved_state_nodes):
                return path
            path.pop(-1)
        return None
    
    @dfs_wrapper
    def solve_end_state_DFSL(self, depth: int):
        """
        Implementation of DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method.
        """
        solved_state_nodes= {self.start_node}
        return self.recursive_solve_end_state_DFSL(depth, [self.start_node], solved_state_nodes)
    
    def recursive_solve_end_state_DFSL(
            self, depth: int, path: List[Node], solved_state_nodes: Set[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFSL
        """
        if depth < 0:
            return None
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        node_arcs = curr_node.get_arcs()
        for node in node_arcs:
            if node in solved_state_nodes:
                continue
            solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFSL(depth-1, path, solved_state_nodes):
                return path
            solved_state_nodes.remove(node)
            path.pop(-1)
        return None
    
    @dfs_wrapper
    def solve_end_state_RDFSL(self, depth: int):
        """
        Implementation of DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method.
        Uses randomization to create a more equal chance for each node
        instead of relying on deterministic order by hash.
        """
        solved_state_nodes= {self.start_node}
        return self.recursive_solve_end_state_DFSL(depth, [self.start_node], solved_state_nodes)
    
    def recursive_solve_end_state_RDFSL(
            self, depth: int, path: List[Node], solved_state_nodes: Set[Node]
    ) -> Optional[List[Node]]:
        """
        Recursive method which implements solve_end_state_DFSL
        """
        if depth < 0:
            return None
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        node_arcs = curr_node.get_arcs()
        shuffle(node_arcs)
        for node in node_arcs:
            if node in solved_state_nodes:
                continue
            solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_DFSL(depth-1, path, solved_state_nodes):
                return path
            solved_state_nodes.remove(node)
            path.pop(-1)
        return None
    
    def solve_end_state_IDFSL(self) -> Optional[List[State]]:
        """
        Implementation of Incremental DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method. 
        """
        i = 0
        while True:
            try:
                sol = self.solve_end_state(Strategy.DFSL, depth=i)
            except ValueError:
                sol = None
            if sol:
                return sol
            i += 1
    
    def solve_end_state_RIDFSL(self) -> Optional[List[State]]:
        """
        Implementation of Incremental DFSL on Graph
        Maintains path using recursion and spawns pathway 
        using get_arcs method.
        Uses randomization to create a more equal chance for each node
        instead of relying on deterministic order by hash.
        """
        i = 0
        while True:
            try:
                sol = self.solve_end_state(Strategy.RDFSL, depth=i)
            except ValueError:
                sol = None
            if sol:
                return sol
            i += 1
        
    @dfs_wrapper
    def solve_end_state_PDFS(self):
        solved_state_nodes= {self.start_node}
        return self.recursive_solve_end_state_PDFS([self.start_node], solved_state_nodes)
    
    def recursive_solve_end_state_PDFS(
            self, path: List[Node], solved_state_nodes: Set[Node]
    ) -> Optional[List[Node]]:
        curr_node = path[-1]
        if curr_node.state.is_end_state():
            return path
        sorted_nodes = sorted(
                curr_node.get_arcs(), 
                key=lambda node: node.state.attractive_rate(),
                reverse=True
        )
        for node in sorted_nodes:
            if node in solved_state_nodes:
                continue
            solved_state_nodes.add(node)
            path.append(node)
            if self.recursive_solve_end_state_PDFS(path, solved_state_nodes):
                return path
            path.pop(-1)
        return None
