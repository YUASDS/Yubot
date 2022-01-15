# 迷宫生成算法
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image


class Maze_Stack(object):
    def __init__(self, rows, cols) -> None:
        self.rows = rows
        self.cols = cols
        self.M = [[1 for i in range(cols + 2)] for j in range(rows + 2)]
        for i in range(1, rows + 1, 2):
            for j in range(1, cols + 1, 2):
                self.M[i][j] = 0
        self.visited = []
        self.locx = 1
        self.locy = 1
        self.S = []

    def create_maze(self):
        self.visited.append((self.locx, self.locy))
        self.S.append((self.locx, self.locy))
        # rooms = (((self.cols) // 2) + 1) * (((self.rows) // 2) + 1)
        while self.S != []:
            check = []
            # 向右(R=Right)
            if self.locy + 2 <= self.cols and (self.locx, self.locy +
                                               2) not in self.visited:
                check.append('R')
            # 向下(D=Down)
            if self.locx + 2 <= self.rows and (self.locx + 2,
                                               self.locy) not in self.visited:
                check.append('D')
            # 向左(L=Left)
            if self.locy - 2 >= 1 and (self.locx,
                                       self.locy - 2) not in self.visited:
                check.append('L')
            # 向上(U=Up)
            if self.locx - 2 >= 1 and (self.locx - 2,
                                       self.locy) not in self.visited:
                check.append('U')

            if check != []:
                moving_dirction = np.random.choice(check)
                if moving_dirction == 'R':
                    self.M[self.locx][self.locy + 1] = 0  # 凿墙
                    self.visited.append(
                        (self.locx, self.locy + 2))  # 标记改房间已经被访问
                    self.S.append((self.locx, self.locy + 2))  # 将即将访问房间坐标入栈
                    self.locy += 2
                elif moving_dirction == 'D':
                    self.M[self.locx + 1][self.locy] = 0  # 凿墙
                    self.visited.append(
                        (self.locx + 2, self.locy))  # 标记改房间已经被访问
                    self.S.append((self.locx + 2, self.locy))  # 将即将访问房间坐标入栈
                    self.locx += 2
                elif moving_dirction == 'L':
                    self.M[self.locx][self.locy - 1] = 0  # 凿墙
                    self.visited.append(
                        (self.locx, self.locy - 2))  # 标记改房间已经被访问
                    self.S.append((self.locx, self.locy - 2))  # 将即将访问房间坐标入栈
                    self.locy -= 2
                elif moving_dirction == 'U':
                    self.M[self.locx - 1][self.locy] = 0  # 凿墙
                    self.visited.append(
                        (self.locx - 2, self.locy))  # 标记改房间已经被访问
                    self.S.append((self.locx - 2, self.locy))  # 将即将访问房间坐标入栈
                    self.locx -= 2
            else:
                self.locx, self.locy = self.S.pop()  # 否则出栈

    def getm(self):
        return self.M

    def print_maze(self):
        for r in self.M:
            print(r)

    def draw_maze(self):
        picture = np.zeros(((self.rows + 2) * 10, (self.cols + 2) * 10),
                           dtype=np.uint8)
        self.M[0][0] = 0
        self.M[0][1] = 0
        self.M[self.rows + 1][self.cols + 1] = 0
        self.M[self.rows + 1][self.cols] = 0
        for i in range(self.rows + 2):
            for j in range(self.cols + 2):
                # 画墙
                if self.M[i][j] == 0:
                    for k in range((i) * 10, (i + 1) * 10):
                        for p in range((j) * 10, (j + 1) * 10):
                            picture[k][p] = 255
        plt.imshow(picture)
        # 如果你喜欢黑白色的图片，加入一个参数:
        # cmap = plt.cm.Greys_r
        plt.show()


maze = Maze_Stack(rows=4, cols=5)
maze.create_maze()
# maze.print_maze()
# print(maze.getm())
maze.draw_maze()
