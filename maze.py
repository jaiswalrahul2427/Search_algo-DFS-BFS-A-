from typing import List


class Node:
    def __init__(self,state,parent,action,path_cost=0):
        """
        Not keeping track of the path cost. This is because the
         path cost can be calculated at the end.
        """
        