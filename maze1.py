from typing import List
from PIL import Image, ImageDraw


class Node:
    def __init__(self, state, parent, action, path_cost=0):
        self.state = state      # (row, col)
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


class StackFronteir:
    def __init__(self):
        self.frontier: List[Node] = []

    def add(self, node):
        self.frontier.append(node)

    def contains_state(self, state):
        return any(node.state == state for node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("Frontier is empty")

        node = self.frontier[-1]
        self.frontier = self.frontier[:-1]
        return node


class QueueFronteir(StackFronteir):
    def remove(self):
        if self.empty():
            raise Exception("Frontier is empty")

        node = self.frontier[0]
        self.frontier = self.frontier[1:]
        return node


class GreedyBestFirstFronteir(QueueFronteir):

    def __init__(self, goal):
        super().__init__()
        self.goal = goal

    def manhattan_distance(self, s1, s2):
        return abs(s1[0] - s2[0]) + abs(s1[1] - s2[1])

    def remove(self):
        if self.empty():
            raise Exception("Frontier is empty")

        self.frontier.sort(
            key=lambda node: self.manhattan_distance(node.state, self.goal)
        )

        node = self.frontier[0]
        self.frontier = self.frontier[1:]
        return node


class AStarFronteir(GreedyBestFirstFronteir):

    def remove(self):
        if self.empty():
            raise Exception("Frontier is empty")

        def f(node):
            return self.manhattan_distance(node.state, self.goal) + node.path_cost

        self.frontier.sort(key=lambda node: f(node))

        node = self.frontier[0]
        self.frontier = self.frontier[1:]
        return node


class Maze:

    def __init__(self, filename, frontier):
        self.frontier_type = frontier

        with open(filename) as f:
            contents = f.read()

        if contents.count("A") != 1:
            raise Exception("Maze must have exactly one start point")

        if contents.count("B") != 1:
            raise Exception("Maze must have exactly one goal")

        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        self.walls = []

        for i in range(self.height):
            row = []

            for j in range(self.width):

                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)

                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)

                    elif contents[i][j] == " ":
                        row.append(False)

                    else:
                        row.append(True)

                except IndexError:
                    row.append(False)

            self.walls.append(row)

        self.solution = None

    def print(self):

        solution = self.solution[1] if self.solution else None

        print()

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                if col:
                    print("█", end="")

                elif (i, j) == self.start:
                    print("A", end="")

                elif (i, j) == self.goal:
                    print("B", end="")

                elif solution and (i, j) in solution:
                    print("*", end="")

                else:
                    print(" ", end="")

            print()

        print()

    def output_image(self, filename, show_explored=False):

        cell_size = 50
        cell_border = 2

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size),
            "black"
        )

        draw = ImageDraw.Draw(img)

        solution = self.solution[1] if self.solution else None

        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):

                if col:
                    fill = (40, 40, 40)

                elif (i, j) == self.start:
                    fill = (255, 0, 0)

                elif (i, j) == self.goal:
                    fill = (0, 255, 0)

                elif solution and (i, j) in solution:
                    fill = (220, 235, 113)

                elif show_explored and (i, j) in self.explored:
                    fill = (212, 97, 85)

                else:
                    fill = (237, 240, 252)

                draw.rectangle(
                    [
                        (j * cell_size + cell_border, i * cell_size + cell_border),
                        ((j + 1) * cell_size - cell_border,
                         (i + 1) * cell_size - cell_border)
                    ],
                    fill=fill
                )

        img.save(filename)

    def neighbors(self, state):

        row, col = state

        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []

        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width:
                if not self.walls[r][c]:
                    result.append((action, (r, c)))

        return result

    def get_frontier(self):

        if self.frontier_type in [GreedyBestFirstFronteir, AStarFronteir]:
            return self.frontier_type(self.goal)

        return self.frontier_type()

    def solve(self):

        self.num_explored = 0

        start = Node(self.start, None, None)

        frontier = self.get_frontier()
        frontier.add(start)

        self.explored = set()

        while True:

            if frontier.empty():
                raise Exception("No solution")

            node = frontier.remove()

            self.num_explored += 1

            if node.state == self.goal:

                actions = []
                cells = []

                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent

                actions.reverse()
                cells.reverse()

                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):

                if not frontier.contains_state(state) and state not in self.explored:

                    child = Node(
                        state=state,
                        parent=node,
                        action=action,
                        path_cost=node.path_cost + 1
                    )

                    frontier.add(child)


if __name__ == "__main__":

    maze = Maze("maze4.txt", AStarFronteir)

    print("Maze:")
    maze.print()

    print("Solving...")
    maze.solve()

    print("States Explored:", maze.num_explored)

    print("Solution:")
    maze.print()

    maze.output_image("maze.png", show_explored=True)