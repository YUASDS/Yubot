from Core import GetMsgQQ, Send
from GlobalVariable import *

# 空白符号
Empty = "　"  # ╋


def CreateChessGame(par):
    if GetMsgQQ() in playerRecord:
        Send("已经存在正在进行或等待的棋局")
        return
    if len(par) < 1 or par[0] == "":
        Send("请输入棋局名称")
        return
    if par[0] in ChessboardRecord:
        Send("棋局名称重复")
        return
    playerRecord[GetMsgQQ()] = par[0]

    # 构建棋局信息
    ChessboardRecord[par[0]] = BuildChessboard()

    # 设置红方为创建者
    ChessboardRecord[par[0]][0]["红方"] = GetMsgQQ()
    Send("创建棋局\"" + par[0] + "\"完成\r你为：红方")
    return


def JoinChessGame(par):
    if GetMsgQQ() in playerRecord:
        Send("已经存在正在进行或等待的棋局，可以选择\"" + "退出棋局" + "\"")
        return
    if len(par) < 1 or par[0] == "":
        Send("请输入棋局名称")
        return
    if par[0] not in ChessboardRecord:
        Send("该棋局不存在")
        return

    if (ChessboardRecord[par[0]][0]["红方"] != ""):
        if (ChessboardRecord[par[0]][0]["黑方"] != ""):
            Send("该棋局人数已满")
            return
        else:
            type = "黑方"
    else:
        type = "红方"

    ChessboardRecord[par[0]][0][type] = GetMsgQQ()

    playerRecord[GetMsgQQ()] = par[0]

    Send("已加入棋局\"" + par[0] + "\"\r你为：" + type)
    return


def QuitChessGame(par):
    if GetMsgQQ() not in playerRecord:
        Send("未有等待中的棋局")
        return
    name = playerRecord[GetMsgQQ()]
    if ChessboardRecord[name][0]["红方"] == GetMsgQQ():
        ChessboardRecord[name][0]["红方"] = ""
        if ChessboardRecord[name][0]["黑方"] == "":
            del ChessboardRecord[name]
            Send("已退出当前棋局,由于棋局内无其他玩家，棋局已自动销毁。")
        else:
            Send("已退出当前棋局，当前局内剩余黑方\"" + ChessboardRecord[name][0]["黑方"] + "\"")
    else:
        ChessboardRecord[name][0]["黑方"] = ""
        if ChessboardRecord[name][0]["红方"] == "":
            del ChessboardRecord[name]
            Send("已退出当前棋局,由于棋局内无其他玩家，棋局已自动销毁。")
        else:
            Send("已退出当前棋局，当前局内剩余红方\"" + ChessboardRecord[name][0]["红方"] + "\"")
    del playerRecord[GetMsgQQ()]


def StartPlayingChess(par):
    if GetMsgQQ() not in playerRecord:
        Send("未有等待中的对局")
        return
    name = playerRecord[GetMsgQQ()]
    if ChessboardRecord[name][0]["回合"] != "":
        Send("当前参与的棋局已经开始")
        return
    if (ChessboardRecord[name][0]["红方"] == ""
            or ChessboardRecord[name][0]["黑方"] == ""):
        Send("人数不足，无法开始")
        return

    ChessboardRecord[name][0]["回合"] = ChessboardRecord[name][0]["红方"]
    Send("对弈开始！\r红方:[@" + ChessboardRecord[name][0]["红方"] + "]\r黑方:[@" +
         ChessboardRecord[name][0]["黑方"] + "]")
    GetCheckerBoard(par)


def CreateChessboard():
    return [["车", Empty, Empty, "卒", Empty, Empty, "兵", Empty, Empty, "車"],
            ["马", Empty, "炮", Empty, Empty, Empty, Empty, "砲", Empty, "馬"],
            ["象", Empty, Empty, "卒", Empty, Empty, "兵", Empty, Empty, "相"],
            ["仕", Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, "士"],
            ["将", Empty, Empty, "卒", Empty, Empty, "兵", Empty, Empty, "帥"],
            ["仕", Empty, Empty, Empty, Empty, Empty, Empty, Empty, Empty, "士"],
            ["象", Empty, Empty, "卒", Empty, Empty, "兵", Empty, Empty, "相"],
            ["马", Empty, "炮", Empty, Empty, Empty, Empty, "砲", Empty, "馬"],
            ["车", Empty, Empty, "卒", Empty, Empty, "兵", Empty, Empty, "車"]]


def AnalyticalCoordinates(str):
    # 解析字符
    if (len(str) < 2 or not str[0].isalpha() or not str[1].isdigit()):
        return -1, -1
    x = min(ord(str[0].upper()) - 65, 8)
    y = min(int(str[1]), 9)
    return x, y


def GetCheckerBoard(par):
    if GetMsgQQ() not in playerRecord:
        Send("未参与任何棋局")
        return
    name = playerRecord[GetMsgQQ()]
    if ChessboardRecord[name][0]["回合"] == "":
        Send("当前参与的棋局未开始")
        return

    #xSymbol = ["Ａ", "Ｂ", "Ｃ", "Ｄ", "Ｅ", "Ｆ", "Ｇ", "Ｈ", "Ｉ"]
    ySymbol = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]

    # 拼合棋盘
    str = "　ＡＢＣＤＥＦＧＨＩ　\r"
    for y in range(10):
        str = str + ySymbol[y]
        for x in range(9):
            str = str + ChessboardRecord[name][1][x][y]
        str = str + ySymbol[y]
        str = str + "\r"

    str = str + "　ＡＢＣＤＥＦＧＨＩ　"
    Send(str)


def PlayChess(par):
    if len(par[0]) != 4:
        return True

    if GetMsgQQ() not in playerRecord:
        return True

    name = playerRecord[GetMsgQQ()]
    if ChessboardRecord[name][0]["回合"] != GetMsgQQ():
        return True

    oldX, oldY = AnalyticalCoordinates(par[0][0:2])
    newX, newY = AnalyticalCoordinates(par[0][2:4])

    # 判断解析的xy坐标
    if newX == -1 or oldX == -1:
        return True

    # 获取落子者属于哪一方
    if ChessboardRecord[name][0]["红方"] == GetMsgQQ():
        PieceList = ["車", "馬", "相", "士", "帥", "砲", "兵"]
        type = "红方"
    else:
        PieceList = ["车", "马", "象", "仕", "将", "炮", "卒"]
        type = "黑方"

    # 被选择棋子和落点
    oldPiece = ChessboardRecord[name][1][oldX][oldY]
    newPiece = ChessboardRecord[name][1][newX][newY]

    # 判断被选择棋子是否有效的棋子
    i = 0
    for piece in PieceList:
        if piece == oldPiece:
            break
        i = i + 1
    else:
        Send("所选棋子有误")
        return False

    # 判断落点是否己方棋子
    if newPiece in PieceList:
        Send("棋子落点有误")
        return False

    # 获取偏移
    offsetX = newX - oldX
    offsetY = newY - oldY

    if i == 0:
        # 车的规则
        # 只允许直线
        if offsetX != 0 and offsetY != 0 or offsetX == 0 and offsetY == 0:
            Send("不符合落子规则A")
            return False

        # 判断路径是否有多余棋子
        if offsetX > 0:
            offset = offsetX
            coefficientX = 1
            coefficientY = 0
            correctX = 1
            correctY = 0
        elif offsetX < 0:
            offset = offsetX
            coefficientX = -1
            coefficientY = 0
            correctX = -1
            correctY = 0
        elif offsetY > 0:
            offset = offsetY
            coefficientX = 0
            coefficientY = 1
            correctX = 0
            correctY = 1
        elif offsetY < 0:
            offset = offsetY
            coefficientX = 0
            coefficientY = -1
            correctX = 0
            correctY = -1
        for j in range(abs(offset) - 1):
            if ChessboardRecord[name][1][oldX + correctX + j * coefficientX][
                    oldY + correctY + j * coefficientY] != Empty:
                Send("不符合落子规则B")
                return False

    if i == 1:
        # 马的规则
        # 只允许走日子
        if not (abs(offsetX) == 2 and abs(offsetY) == 1
                or abs(offsetX) == 1 and abs(offsetY) == 2):
            Send("不符合落子规则C")
            return False

        # 判断是否有绊脚棋
        if offsetY == 2:
            correctionX = 0
            correctionY = 1
        elif offsetY == -2:
            correctionX = 0
            correctionY = -1
        elif offsetX == 2:
            correctionX = 1
            correctionY = 0
        elif offsetX == -2:
            correctionX = -1
            correctionY = 0
        if ChessboardRecord[name][1][oldX + correctionX][oldY +
                                                         correctionY] != Empty:
            Send("不符合落子规则D")
            return False

    if i == 2:
        # 象的规则
        # 只允许走田字
        if not (abs(offsetX) == 2 and abs(offsetY) == 2):
            Send("不符合落子规则E")
            return False

        # 不允许过河
        if type == "红方" and newY < 5 or type == "黑方" and newY > 4:
            Send("不符合落子规则F")
            return False

        # 判断是否有绊脚棋
        if offsetX == 2 and offsetY == 2:
            correctionX = 1
            correctionY = 1
        elif offsetX == -2 and offsetY == 2:
            correctionX = -1
            correctionY = 1
        if offsetX == 2 and offsetY == -2:
            correctionX = 1
            correctionY = -1
        elif offsetX == -2 and offsetY == -2:
            correctionX = -1
            correctionY = -1
        if ChessboardRecord[name][1][oldX + correctionX][oldY +
                                                         correctionY] != Empty:
            Send("不符合落子规则G")
            return False

    if i == 3:
        # 士的规则
        # 只允许斜着走
        if not (abs(offsetX) == 1 and abs(offsetY) == 1):
            Send("不符合落子规则H")
            return False

        # 不允许走出范围
        if (newX < 3 or newX > 5
            ) or type == "红方" and newY < 7 or type == "黑方" and newY > 2:
            Send("不符合落子规则I")
            return False

    if i == 4:
        # 将的规则
        # 判断是否为飞将
        if abs(offsetY) > 3 and offsetX == 0 and (newPiece == "帥"
                                                  or newPiece == "将"):
            # 判断路径是否有多余棋子
            if offsetY > 0:
                coefficientY = 1
                correctY = 1
            elif offsetY < 0:
                coefficientY = -1
                correctY = -1
            for j in range(abs(offsetY) - 1):
                if ChessboardRecord[name][1][oldX][oldY + correctY +
                                                   j * coefficientY] != Empty:
                    Send("不符合落子规则J")
                    return False

        # 只允许走一格
        if not (abs(offsetX) == 1 and abs(offsetY) == 0
                or abs(offsetX) == 0 and abs(offsetY) == 1):
            Send("不符合落子规则K")
            return False

        # 不允许走出范围
        if (newX < 3 or newX > 5
            ) or type == "红方" and newY < 7 or type == "黑方" and newY > 2:
            Send("不符合落子规则L")
            return False

    if i == 5:
        # 炮的规则
        # 只允许走直线
        if offsetX != 0 and offsetY != 0 or offsetX == 0 and offsetY == 0:
            Send("不符合落子规则M")
            return False

        # 判断是否存在炮桩
        if offsetX > 0:
            offset = offsetX
            coefficientX = 1
            coefficientY = 0
            correctX = 1
            correctY = 0
        elif offsetX < 0:
            offset = offsetX
            coefficientX = -1
            coefficientY = 0
            correctX = -1
            correctY = 0
        elif offsetY > 0:
            offset = offsetY
            coefficientX = 0
            coefficientY = 1
            correctX = 0
            correctY = 1
        elif offsetY < 0:
            offset = offsetY
            coefficientX = 0
            coefficientY = -1
            correctX = 0
            correctY = -1

        k = False
        for j in range(abs(offset) - 1):
            if ChessboardRecord[name][1][oldX + correctX + j * coefficientX][
                    oldY + correctY + j * coefficientY] != Empty:
                if k == False:
                    k = True
                else:
                    Send("不符合落子规则N")
                    return False

        # 如果没有炮桩，不允许吃棋
        if k == False and newPiece != Empty:
            Send("不符合落子规则O")
            return False

        # 有炮桩不允许不吃棋
        if k == True and newPiece == Empty:
            Send("不符合落子规则P")
            return False
    if i == 6:
        # 卒的规则
        # 只允许走一格
        if not (abs(offsetX) == 1 and abs(offsetY) == 0
                or abs(offsetX) == 0 and abs(offsetY) == 1):
            Send("不符合落子规则Q")
            return False

        # 不允许后退
        if type == "红方" and offsetY == 1 or type == "黑方" and offsetY == -1:
            Send("不符合落子规则R")
            return False

        # 如果没过河，不允许左右走
        if type == "红方" and (newY > 3 and offsetX != 0) or type == "黑方" and (
                newY < 6 and offsetX != 0):
            Send("不符合落子规则S")
            return False

    # 落子
    ChessboardRecord[name][1][newX][newY] = oldPiece
    ChessboardRecord[name][1][oldX][oldY] = Empty

    sendStr = type + "移动了[" + oldPiece + "]\r[" + \
        par[0][0:2] + "]→[" + par[0][2:4] + "]"
    if newPiece != Empty:
        sendStr = sendStr + "\r[" + newPiece + "]被吃掉了！"
    Send(sendStr)

    # 显示棋盘
    GetCheckerBoard(par)

    # 判断落子位置是否为对方将领
    if type == "红方" and newPiece == "将":
        Send("游戏结束，红方获胜")
        ChessboardRecord[name][0]["回合"] = ""
        ChessboardRecord[1] = CreateChessboard()
    elif type == "黑方" and newPiece == "帥":
        Send("游戏结束，黑方获胜")
        ChessboardRecord[name][0]["回合"] = ""
        ChessboardRecord[1] = CreateChessboard()

    else:
        # 交换回合
        ChessboardRecord[name][0]["回合"] = ChessboardRecord[name][0][
            "黑方" if type == "红方" else "红方"]

    return False


def clear(par):
    # 清理所有棋局，修改为你的QQ
    if GetMsgQQ() != "1454832774":
        return
    ChessboardRecord.clear()
    playerRecord.clear()
    Send("清理完成")
    return


def BuildChessboard():
    # 构建棋局信息
    ret = [{"回合": "", "红方": "", "黑方": ""}, CreateChessboard()]
    return ret
