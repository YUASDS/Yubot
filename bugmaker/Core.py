def GetMsgQQ():
    return "1"


def GetMsgSource():
    return ""


def GetMsgType():
    return 0


def GetMsgRobot():
    return ""


def Send(str_msg):
    return


def SendEx(str_msg, int_msgType, str_sendTarget, str_Robot, bool_triggerEvent):
    return


def Read(str_tableName, str_appName, str_keyName):
    return ""


def Write(str_tableName, str_appName, str_keyName, str_value):
    return False


def Delete(str_tableName, str_appName, str_keyName):
    return False


def AppList(str_tableName):
    return []


def KeyList(str_tableName, str_appName):
    return []


def SQLExec(str_SQL):
    return False


def SQLPrepare(str_SQL):
    return {}


def SQLiteBegin():
    return False


def SQLiteCommit():
    return False


def SQLiteRollback():
    return False
