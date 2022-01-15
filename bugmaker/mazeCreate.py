# 迷宫生成算法
from Core import GetMsgQQ
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image
import random
import os
from GlobalVariable import mazeRecord, mazePlayerRecord

data_path = os.path.join(os.getcwd(), "bugmaker\\investigator\\data")
img_path = os.path.join(os.getcwd(), "bugmaker\\investigator\\img")
save_path = os.path.join(os.getcwd(), "bugmaker\\investigator\\save")


class Maze_Stack(object):  # 迷宫对象，初版迷宫生成
    def __init__(self, rows, cols) -> None:
        self.rows = rows
        self.cols = cols
        self.M = [[1 for i in range(cols + 2)] for j in range(rows + 2)]
        print(self.M)
        print("S")
        for i in range(1, rows + 1, 2):
            for j in range(1, cols + 1, 2):
                self.M[i][j] = 0
        print(self.M)
        print("S")
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
        self.M[0][0] = 0
        self.M[0][1] = 0
        self.M[self.rows + 1][self.cols + 1] = 0
        self.M[self.rows + 1][self.cols] = 0

    def getm(self):
        return self.M

    def print_maze(self):
        for r in self.M:
            print(r)

    def draw(self, cube, background):
        return

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


def getRows(QQ=GetMsgQQ()):  # 获取rows
    return 5


def getCols(QQ=GetMsgQQ()):  # 获取cols
    return 5


def AnalyticalCoordinates(str):  # 解析字符
    if (len(str) < 2 or not str[0].isalpha() or not str[1].isdigit()):
        return -1, -1
    x = ord(str[0].upper()) - 65
    y = int(str[1])
    return x, y


def load_image(file, path, sub_dir=None):  # 载入图片，文件名，路径，二级路径
    '''loads an image, prepares it for play'''
    if sub_dir:
        file = Image.open(os.path.join(path, sub_dir, file)).convert('RGBA')
    else:
        file = Image.open(os.path.join(path, file)).convert('RGBA')
    if file:
        return file
    else:
        print("读入图片失败——")
        return False


def CreateMazeImg(
    time,
    M,
    rows,
    cols,
    backgroundName="background77.png",
    img_path=img_path,
    invName="inv.jpg",
    monsName="monster1.png",
    bonName="bonus1.png",
    cubeName="cube.png",
    save__path=save_path,
    QQ="1",
):  # 贴玩家，宝箱，怪物返回保存路径
    background = load_image(file=backgroundName, path=img_path)
    cube = load_image(file=cubeName, path=img_path)
    inv = load_image(file=invName, path=img_path)
    bonus = load_image(file=monsName, path=img_path)
    monster = load_image(file=bonName, path=img_path)
    for y in range(rows + 2):  # 贴棋子
        for x in range(cols + 2):
            if M[x][y]:
                if M[x][y] == 1:
                    x_dir = 40 * x
                    y_dir = 40 * y
                    r, g, b, a = cube.split()
                    background.paste(cube, (y_dir, x_dir), mask=a)
                elif M[x][y] == 2:
                    x_dir = 40 * x
                    y_dir = 40 * y
                    r, g, b, a = inv.split()
                    background.paste(inv, (y_dir, x_dir), mask=a)
                elif M[x][y] == 3:
                    x_dir = 40 * x
                    y_dir = 40 * y
                    r, g, b, a = monster.split()
                    background.paste(monster, (y_dir, x_dir), mask=a)
                elif M[x][y] == 4:
                    x_dir = 40 * x
                    y_dir = 40 * y
                    r, g, b, a = bonus.split()
                    background.paste(bonus, (y_dir, x_dir), mask=a)
    save_path = os.path.join(save__path, QQ)
    if (os.path.exists(save_path)):
        background.save(save_path + "\\%d.PNG" % time)
        img_path = save_path + "\\%d.PNG" % time
    else:
        os.mkdir(save_path)
        background.save(save_path + "\\%d.PNG" % time)
        img_path = save_path + "\\%d.PNG" % time
        # lenth = len(img_path)
    return img_path


def mazeAdd(  # 添加宝箱和怪物，返回添加后的二维数组
        m,  # 添加宝箱和怪物
        rows=5,
        cols=5,
        bonus_rate=5,
        monster_rate=10,
        bonus_num=4,
        monster_num=3):  # 添加宝箱和怪物
    for y in range(rows + 2):
        for x in range(cols + 2):
            if m[x][y] == 0:
                if random.randint(1, 100) < monster_rate:
                    m[x][y] = monster_num
                elif random.randint(1, 100) < bonus_rate:
                    m[x][y] = bonus_num
    m[0][0] = 2
    return m


def change(m, rows=5, cols=5):  # 将迷宫元组赋值到全局变量中，返回
    s = []
    for x in range(rows + 2):
        s.append([])
        for y in range(cols + 2):
            s[x].append(m[x][y])
    return s


def mazeCreat(rows=5, cols=5):  # 输入，长宽，迷宫构建函数，返回构建好的迷宫二维数组
    maze = Maze_Stack(rows=rows, cols=cols)
    maze.create_maze()
    # maze.print_maze()
    mz = mazeAdd(m=maze.M, rows=rows, cols=cols)
    print(maze.M)
    print(mz)
    return mz


# 此处class maze可能和全局变量出现意外的问题


def mazeStart(par, QQ=GetMsgQQ()):  # 用于构造每个玩家的迷宫，无返回值

    if QQ not in mazeRecord:
        x = getRows()
        y = getCols()
        maz = mazeCreat(rows=x, cols=y)
        mazeRecord[QQ] = maz
        mazePlayerRecord[QQ] = {}
        mazePlayerRecord[QQ]["x"] = 0
        mazePlayerRecord[QQ]["y"] = 0
        print("CREAT OK")
        print(maz)

    else:
        maz = mazeRecord[QQ]
        print(maz)


# 开始游戏方法


def mazePlay(par, QQ=GetMsgQQ()):  # 用于进行游戏，通过调用playChange方法进行位置变换
    # 当playerChange返回false表示不响应
    if len(par[0]) != 2:
        return True

    if QQ not in mazeRecord:
        return True
    playerChange(par=par, QQ=QQ)


# 进行游戏方法


def accident(num, x, y):  # 用于前进过程中遭遇突发情况处理
    # 成功前进返回ture，无法前进返回false，num为输入事件代号，x为x坐标，y为y坐标
    if num == 1:
        print("移动过程中有墙壁")
        return False
    if num == 3:
        print("你在%s%s遭遇了怪物" % (x, y))
        return True
    if num == 4:
        print("你在%s%s发现了宝箱" % (x, y))
        bonus(QQ=GetMsgQQ())
        return True


def bonus(QQ=GetMsgQQ()):

    return


def playerChange(par, QQ=GetMsgQQ):
    oldx = mazePlayerRecord[QQ]["x"]
    oldy = mazePlayerRecord[QQ]["y"]
    newx, newy = AnalyticalCoordinates(par[0])
    print(newx, newy)
    # 判断解析的xy坐标
    if newx == -1:
        return True
    offsetx = newx - oldx
    offsety = newy - oldy
    if (offsetx) and (offsety):
        print("无法斜线移动")
        return
    if (not offsetx) and (not offsety):
        print("没有移动")
        return
    print(offsetx, offsety)

    if (offsetx):
        if offsetx > 0:
            for i in range(oldx, newx + 1):
                if mazeRecord[QQ][oldy][i]:
                    if accident(num=mazeRecord[QQ][oldy][i], x=oldy, y=i):
                        mazePlayerRecord[QQ]["x"] = i
                        mazeRecord[QQ][oldy][oldx] = 0
                        mazeRecord[QQ][oldy][i] = 2
                        return mazeRecord[QQ]
                    else:
                        return False
            mazeRecord[QQ][oldy][oldx] = 0
            mazePlayerRecord[QQ]["x"] = newx
            mazeRecord[QQ][oldy][newx] = 2
            maz = mazeRecord[QQ]
            print(maz)
        else:
            i = 0
            while i > offsetx:
                i = i - 1
                if mazeRecord[QQ][oldy][oldx + i]:
                    if accident(num=mazeRecord[QQ][oldy][oldx + i],
                                x=oldx + i,
                                y=oldy):
                        mazePlayerRecord[QQ]["x"] = oldx + i
                        mazeRecord[QQ][oldy][oldx] = 0
                        mazeRecord[QQ][oldy][oldx + i] = 2
                        return mazeRecord[QQ]
                    else:
                        return False
            mazeRecord[QQ][oldy][oldx] = 0
            mazePlayerRecord[QQ]["x"] = newx
            mazeRecord[QQ][oldy][newx] = 2
            maz = mazeRecord[QQ]
            # 此处为正常前进，无事件发生函数
            print(maz)

    else:
        if offsety > 0:
            for i in range(oldy, newy + 1):
                if mazeRecord[QQ][i][oldx]:
                    if accident(num=mazeRecord[QQ][i][oldx], x=i, y=oldx):
                        mazePlayerRecord[QQ]["y"] = i
                        mazeRecord[QQ][oldx][oldy] = 0
                        mazeRecord[QQ][i][oldx] = 2
                        return mazeRecord[QQ]
                    else:
                        return False
            mazeRecord[QQ][oldy][oldx] = 0
            mazePlayerRecord[QQ]["y"] = newy
            mazeRecord[QQ][newy][oldx] = 2
            maz = mazeRecord[QQ]
            print(maz)
        else:
            i = 0
            while i > offsety:
                i = i - 1
                if mazeRecord[QQ][oldy + i][oldx]:
                    if accident(num=mazeRecord[QQ][oldy + i][oldx],
                                x=oldx,
                                y=oldy + i):
                        mazePlayerRecord[QQ]["y"] = oldy + i
                        mazeRecord[QQ][oldy][oldx] = 0
                        mazeRecord[QQ][oldy + i][oldx] = 2
                        return mazeRecord[QQ]
                    else:
                        return False
            mazeRecord[QQ][oldy][oldx] = 0
            mazePlayerRecord[QQ]["y"] = newy
            mazeRecord[QQ][newy][oldx] = 2
            maz = mazeRecord[QQ]
            print(maz)

    return


def clearMaze(par):
    mazeRecord.clear()
    mazePlayerRecord.clear()
    print("清理完成")
    return


def printMaze(par=1, QQ=GetMsgQQ()):
    maz = mazeRecord[QQ]
    print(mazePlayerRecord[QQ]["y"])
    print(mazePlayerRecord[QQ]["x"])
    print(maz)


maze = Maze_Stack(rows=5, cols=5)
maze.create_maze()
maze.print_maze()
mz = mazeAdd(change(m=maze.M))
print(mz)
print(maze.M)
# print(maze.getm())
CreateMazeImg(M=mz, time=13, rows=5, cols=5)
# maze.draw_maze()
