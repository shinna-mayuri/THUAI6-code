import PyAPI.structures as THUAI6
from PyAPI.Interface import IStudentAPI, ITrickerAPI, IAI
from typing import Union, Final, cast, List
from PyAPI.constants import Constants
import queue

import time

# 以下为自行添加的库
import math
import random
# import functools 


class Setting:
    # 为假则play()期间确保游戏状态不更新，为真则只保证游戏状态在调用相关方法时不更新
    @staticmethod
    def asynchronous() -> bool:
        return True

    # 选手需要依次将player0到player4的职业都定义
    @staticmethod
    def studentType() -> List[THUAI6.StudentType]:
        return [THUAI6.StudentType.Athlete, THUAI6.StudentType.Athlete, THUAI6.StudentType.Athlete, THUAI6.StudentType.Athlete]

    @staticmethod
    def trickerType() -> THUAI6.TrickerType:
        return THUAI6.TrickerType.Assassin


# 辅助函数
numOfGridPerCell: Final[int] = 1000


class AssistFunction:

    @staticmethod
    def CellToGrid(cell: int) -> int:
        return cell * numOfGridPerCell + numOfGridPerCell // 2

    @staticmethod
    def GridToCell(grid: int) -> int:
        return grid // numOfGridPerCell


# -------------------分割线-----------------

class AI(IAI):
    def __init__(self, pID: int):
        self.__playerID = pID

    def StudentPlay(self, api: IStudentAPI) -> None:
        
        '''初始化部分'''
        global StudentInfo
        if 'StudentInfo' not in globals().keys():
            StudentInfo = InfoOfPlayers(api)

        global  GameInfo 
        GameTime = api.GetGameInfo().gameTime
        FrameCount = round(GameTime/50)
        if 'GameInfo' not in globals().keys(): 
            GameInfo = InformationOfGame()
            GameInfo.upgradeMap(api.GetFullMap()) 
            GameInfo.upgradeFrameCount(FrameCount)
        else :
            if not GameInfo.upgradeFrameCount(FrameCount):
                return   #在同一帧则直接返回（可添加函数）
        
        StudentInfo.UpgradeSelfView(api)
        StudentInfo.SendSelfMessage(api)
        StudentInfo.UpdateOthersInfo(api)
        api.Print([StudentInfo.Tricker[0].x,StudentInfo.Tricker[0].y])

        '''每个学生各自的代码'''
        if self.__playerID == 0:
            # global Route0
            # if 'Route0' not in globals().keys():
            #     Route0 = Routing()
            #     Route0.InitialRouteMap(api.GetFullMap())
            # StudentPosition = [AssistFunction.GridToCell(api.GetSelfInfo().x),AssistFunction.GridToCell(api.GetSelfInfo().y)]
            # Route0.SetBeginNode(StudentPosition[0], StudentPosition[1])
            # Route0.InitialEndNotes()
            # Route0.FindRoute()
            # if Route0.RouteLenth:
            #     NextNode = Route0.GetNextNote()
            #     if NextNode.NodeType == THUAI6.PlaceType.Window :
            #         api.SkipWindow()
            #     else :
            #         [NodeX,NodeY] = [AssistFunction.CellToGrid(NextNode.x),AssistFunction.CellToGrid(NextNode.y)]
            #         [Dis,Angle] = CalCulateMove([api.GetSelfInfo().x,api.GetSelfInfo().y],[NodeX,NodeY])
            #         api.Move(round(Dis/api.GetSelfInfo().speed*1000), Angle)
            # else: 
            #     api.StartLearning()

            # api.Print("Current Root:")
            # for i in range(0,Route0.RouteLenth):
            #     api.Print([Route0.Routes[i].x,Route0.Routes[i].y])
            # api.Print("-----------------------------------")
            return

        elif self.__playerID == 1:
            # 玩家1执行操作
            return
        elif self.__playerID == 2:
            api.Move(1,1)
            # 玩家2执行操作
            return
        elif self.__playerID == 3:
            # 玩家3执行操作
            return
                #可以写成if self.__playerID<2之类的写法

        return

    def TrickerPlay(self, api: ITrickerAPI) -> None:
        selfInfo = api.GetSelfInfo()
        api.PrintSelfInfo()
        api.Print(api.GetFrameCount())
        return


def CalCulateMove(Begin: List[int],Goal: List[int]) -> List:  
    '''没有问题的直角坐标转极坐标函数，返回目标点间dis和angle
    '''
    Dis = math.sqrt((Begin[0] - Goal[0])**2 + (Begin[1] - Goal[1])**2)
    if Goal[0] - Begin[0] == 0:
        if Goal[1] - Begin[1] > 0: 
            Angle = math.pi/2 
        else: 
            Angle = -math.pi/2
    else : 
        Angle = math.atan((Goal[1] - Begin[1])/(Goal[0] - Begin[0])) 
        if Goal[0] - Begin[0] < 0:
            Angle = Angle + math.pi
    return [Dis,Angle]


# 用于计算最短路径
class RouteNode:  

    def __init__(self,x: int = 0,y: int = 0,dis: int = 114514) -> None:
        self.x :int= x
        self.y :int= y
        self.IsRouted :bool= False
        ''' 由于每帧都需要做一次更新，因此该变量不保持为定值，而是在二值变换'''
        self.prex :int= x
        self.prey :int= y
        self.Distance :int = dis
        self.NodeType :THUAI6.PlaceType= THUAI6.PlaceType(0)

    # 以下重载运算符函数用于优先队列   更改可能导致报错
    def __gt__(self,other):
        if isinstance(other, RouteNode):
            return self.Distance > other.Distance
        elif isinstance(other, Number):
            return self.Distance > other
        else:
            raise AttributeError("The of other is incorrect!")

    def __eq__(self, other):
        if isinstance(other, RouteNode):
            return self.Distance == other.Distance
        elif isinstance(other, Number):
            return self.Distance == other
        else:
            raise AttributeError("The of other is incorrect!")

    def __lt__(self,other): 
        if isinstance(other, RouteNode):
            return self.Distance < other.Distance
        elif isinstance(other, Number):
            return self.Distance < other
        else:
            raise AttributeError("The of other is incorrect!")


# 用于寻路的类
class Routing:

    def __init__(self):
        self.RouteIsNewest = False
        self.RouteLenth = 114514
        self.BeginNode = RouteNode()
        self.EndNotes :List[RouteNode] = []
        self.Routes :List[RouteNode] = []
        self.RouteMap :List[List[RouteNode]]= []

    
    def GetNextNote(self) -> RouteNode:
        '''用于获取下一个需要前往的路径点'''
        return self.Routes[-1]
        
    def InitialEndNotes(self) ->None:
        '''用于初始化终点'''
        for i in range(0,50) :
            for j in range(0,50) :
                if self.RouteMap[i][j].NodeType == THUAI6.PlaceType.ClassRoom:
                    Node = RouteNode(i,j)
                    Node.NodeType = THUAI6.PlaceType.ClassRoom
                    self.EndNotes.append(Node)

    def InitialRouteMap(self,Map:List[List[THUAI6.PlaceType]]) ->None:
        '''初始化寻路地图'''
        for i in range(0,50):
            self.RouteMap.append([])
            for j in range(0,50):
                Node = RouteNode(i,j)
                Node.NodeType = Map[i][j]
                self.RouteMap[i].append(Node)
    
    def UpgradeRouteMap(self,mapnode: RouteNode) ->bool:
        '''返回真表明有更新，否则没有'''
        [x,y] = [mapnode.x,mapnode.y]
        if self.RouteMap[x][y].NodeType == mapnode.NodeType:
                return False
        else :
            self.RouteMap[x][y].NodeType = mapnode.NodeType
            return True

    def SetBeginNode(self,x: int,y: int):
        self.BeginNode.x = x
        self.BeginNode.y = y
        self.BeginNode.NodeType = self.RouteMap[x][y]
        self.BeginNode.Distance = 0

    def FindRoute(self):
        '''
        使用的寻路方法为从起点向周围扩散并最终得到所有点到起点的最短距离

        可能出现的问题：
        在寻找最近的目标点时必定收敛，但是寻找最远点或者次元点未必收敛
        （可能在两个位置间来回振荡，因为进行的是动态优化）
        
        如何进行躲闪？

        可以进行改进的地方：由于加入了极坐标方向系统，所以没必要一定得走中间
        (可以添加拐弯函数来优化最后的路线) 
        (只要观察从目前位置 到终点前的 某一个点是否能拉直线就行)

        Length 之后可以用来调节权重

        '''

        q = queue.PriorityQueue()
        q.put(self.BeginNode)
        BeginNodeState = ~self.RouteMap[self.BeginNode.x][self.BeginNode.y].IsRouted
        self.RouteMap[self.BeginNode.x][self.BeginNode.y].IsRouted = BeginNodeState #取反即可
        self.RouteMap[self.BeginNode.x][self.BeginNode.y].Distance = 0
        while not q.empty():
            Node :RouteNode = q.get()
            # if Node.Distance > 2500:
            #     break
                #算出所有点到起点的距离
            for [i,j] in [[Node.x - 1,Node.y ],[Node.x + 1,Node.y ],[Node.x ,Node.y - 1],[Node.x ,Node.y + 1]]:
            # 遍历四个方向
                if 0 <= i < 50 and  0 <= j < 50 and self.RouteMap[i][j].IsRouted != BeginNodeState:
                        self.RouteMap[i][j].IsRouted = BeginNodeState
                        #判断该点路径是否已经确定
                        if [THUAI6.PlaceType.Land,THUAI6.PlaceType.Window,THUAI6.PlaceType.Grass].count(self.RouteMap[i][j].NodeType): 
                            self.RouteMap[i][j].Distance = Node.Distance + 1
                            self.RouteMap[i][j].prex = Node.x
                            self.RouteMap[i][j].prey = Node.y
                        else:
                            self.RouteMap[i][j].Distance = 114514  #认为该点不可经过，但是需要入栈以保证最终所有点的IsRouted 与 BeginNodeState 保持一致
                            # 只追求计算速度而忽略稳定性时可删除该部分
                        q.put(self.RouteMap[i][j])
        
        # 用来确定去哪一个教室旁边
        GoalNode = self.RouteMap[0][0] #肯定无法到达的点
        for k in range(0,10):
            ClassRoom :RouteNode = self.EndNotes[k]  
            for [i,j] in [[ClassRoom.x + 1,ClassRoom.y],    #九宫格内即可
            [ClassRoom.x + 1,ClassRoom.y - 1],
            [ClassRoom.x - 1,ClassRoom.y + 1],
            [ClassRoom.x - 1,ClassRoom.y - 1],
            [ClassRoom.x + 1,ClassRoom.y + 1 ],
            [ClassRoom.x - 1,ClassRoom.y ],
            [ClassRoom.x ,ClassRoom.y + 1],
            [ClassRoom.x ,ClassRoom.y - 1]]:
                if 0 <= i < 50 and  0 <= j < 50 and self.RouteMap[i][j].Distance < GoalNode.Distance:
                    GoalNode = self.RouteMap[i][j]

        self.Routes = []
        PreNode = GoalNode
        while PreNode.Distance :
            self.Routes.append(PreNode)
            PreNode = self.RouteMap[PreNode.prex][PreNode.prey]
        self.RouteLenth = len(self.Routes)

class InformationOfGame:

    def __init__(self): 
        self.FrameCount :int = 0
        self.Map :List[List[THUAI6.PlaceType]] = []
        self.GameState :int = 0

    def upgradeFrameCount(self,framecount:int) -> bool:
        ''' 返回真表明帧数有更新，否则没有'''
        if self.FrameCount == framecount:
            return False
        else :
            self.FrameCount = framecount
            return True

    def upgradeMap(self,map) -> bool:
        ''' 可输入某个地图的点或整个地图
        输入点时格式为[x,y,MapType]
        输入地图时格式为List[List[THUAI6.PlaceType]]
        返回真表明有更新，否则没有'''
        if len(map) == 3:
            [x ,y ,MapType] = map
            if self.Map[x][y] == MapType:
                return False
            else :
                self.Map[x][y] = MapType
                return True

        else: 
            if self.Map == map:
                return False
            else:
                self.Map = map
                return True

class InfoOfPlayers:
    ''' Save the info of students including myself,and tricker(if can see)'''
    def __init__(self,api: IStudentAPI):
        self.Students : List[THUAI6.Student] = [None,None,None,None]
        self.MyID :int = api.GetSelfInfo().playerID
        self.Students[self.MyID] = api.GetSelfInfo()
        self.AddStudentInfo(self.MyID)
        StudentsViewed = api.GetStudents()
        while len(StudentsViewed):
            Student = StudentsViewed.pop()
            self.Students[Student.playerID] = Student

        if len(api.GetTrickers()):
            self.Tricker = api.GetTrickers()
            self.CanViewTricker = True
        else:
            self.Tricker: List[THUAI6.Tricker] = [THUAI6.Tricker(),]
            #需要声明这些变量否则无法使用
            self.Tricker[0].x = 0
            self.Tricker[0].y = 0
            self.Tricker[0].viewRange = 0 
            self.Tricker[0].trickerType = THUAI6.TrickerType.NullTrickerType
            self.CanViewTricker = False
        
        self.Message: List[str] = ['','','','']
        '''Message include self and others, self is for sending and others for receiving'''


    def UpgradeSelfView(self,api:IStudentAPI)->None:
        '''在接收消息前先自己看一眼，优先以自己看到的为准'''
        Tricker = api.GetTrickers()
        if len(Tricker):
            self.Tricker = Tricker
            self.CanViewTricker = True
        else:
            self.CanViewTricker = False

    def SendSelfMessage(self,api: IStudentAPI) ->None:
        self.MessageEncode(api)
        for i in range(0,4):
            if self.MyID != i:
                api.SendMessage(i,self.Message[self.MyID])

    def UpdateOthersInfo(self,api:IStudentAPI) ->bool:
        '''if receive message will return true'''
        if api.HaveMessage():
            while api.HaveMessage():
                [stuid,stustr] = api.GetMessage()
                self.Message[stuid] = stustr
                self.MessageDecode(stuid)
            return True
        else:
            return False

    def MessageDecode(self,playerID:int) ->None:
        DecodedMessage = self.Message[playerID].split(sep='/')
        while len(DecodedMessage):
            MessageUnit :str = DecodedMessage.pop()
            if len(MessageUnit) == 0: 
                continue
            elif MessageUnit[0] == 'T':
                self.Students[playerID].studentType = int(MessageUnit[1:])
            elif MessageUnit[0] == 'S':
                self.Students[playerID].playerState = int(MessageUnit[1:])
            elif MessageUnit[0] == 'X':
                self.Students[playerID].x = int(MessageUnit[1:])
            elif MessageUnit[0] == 'Y':
                self.Students[playerID].y = int(MessageUnit[1:])
            elif MessageUnit[0] == 'G':
                self.Students[playerID].dangerAlert = float(MessageUnit[1:])
            # elif MessageUnit[0] == 'U':
            #     self.Students[playerID].timeUntilSkillAvailable = float(MessageUnit[1:])
            elif MessageUnit[0] == 'A':
                self.Students[playerID].addiction = int(MessageUnit[1:])
            elif MessageUnit[0] == 'D':
                self.Students[playerID].determination = int(MessageUnit[1:])
            elif MessageUnit[0] == 'E':
                self.Students[playerID].encourageProgress = int(MessageUnit[1:])
            elif MessageUnit[0] == 'R':
                self.Students[playerID].rouseProgress = int(MessageUnit[1:])
            # elif MessageUnit[0] == 'B':
            #     self.Students[playerID].determination = int(MessageUnit[1:])
            # elif MessageUnit[0] == 'P':
            #     self.Students[playerID].determination = int(MessageUnit[1:])

            elif MessageUnit[0] == 'C' and  not self.CanViewTricker:
                '''只有自己看不见的时候才会听别人的'''
                if MessageUnit[1] == 'X':
                    self.Tricker[0].x =  int(MessageUnit[2:])
                elif MessageUnit[1] == 'Y':
                    self.Tricker[0].y =  int(MessageUnit[2:])

        
        self.AddStudentInfo(playerID) 
        # 添加类中不包含但是可能用到的学生信息

        
        
        return

    def MessageEncode(self,api:IStudentAPI) ->None:
        '''Important Info In Messages'''
        message = str()
        message = message + 'T' + str(self.Students[self.MyID].studentType.value) + '/'
        message = message + 'S' + str(self.Students[self.MyID].playerState.value) + '/'
        message = message + 'X' + str(self.Students[self.MyID].x) + '/'
        message = message + 'Y' + str(self.Students[self.MyID].y) + '/'
        message = message + 'G' + str(self.Students[self.MyID].dangerAlert) + '/'
        # message = message + 'U' + str(self.Students[self.MyID].timeUntilSkillAvailable) + '/'
        message = message + 'A' + str(self.Students[self.MyID].addiction) + '/'
        message = message + 'D' + str(self.Students[self.MyID].determination) + '/'
        message = message + 'E' + str(self.Students[self.MyID].encourageProgress) + '/'
        message = message + 'R' + str(self.Students[self.MyID].rouseProgress) + '/'
        # message = message + 'B' + str(self.Me.buff) + '/'
        # message = message + 'P' + str(self.Me.prop) + '/'

        '''Tricker Info'''
        if self.CanViewTricker:
            '''能看见才发送，否则不发'''
            message = message + 'CX'+ str(self.Tricker[0].x) + '/'
            message = message + 'CY'+ str(self.Tricker[0].y) + '/'

        self.Message[self.MyID] = message

        return

    def AddStudentInfo(self,playerID:int) -> None:
        if self.Students[playerID].studentType == THUAI6.StudentType.Teacher:
            self.Students[playerID].encourageSpeed = 80
            self.Students[playerID].learningSpeed = 0
            self.Students[playerID].radius = 400
            self.Students[playerID].speed = 2700
            self.Students[playerID].viewRange = 9000

            self.Students[playerID].maxDetermination = 30000000
            self.Students[playerID].maxAddition = 600000
            self.Students[playerID].hiddingRate = 0.5
            self.Students[playerID].dangerRange = 7500
            self.Students[playerID].openDoorSpeed = 4000
            self.Students[playerID].skipWindowSpeed = 1270
            self.Students[playerID].skipBoxSpeed = 1000

        elif self.Students[playerID].studentType== THUAI6.StudentType.Athlete :
            self.Students[playerID].encourageSpeed = 90
            self.Students[playerID].learningSpeed = 73
            self.Students[playerID].radius = 400
            self.Students[playerID].speed = 3150
            self.Students[playerID].viewRange = 11000

            self.Students[playerID].maxDetermination = 3000000
            self.Students[playerID].maxAddition = 54000
            self.Students[playerID].hiddingRate = 0.9
            self.Students[playerID].dangerRange = 15000
            self.Students[playerID].openDoorSpeed = 4000
            self.Students[playerID].skipWindowSpeed = 3048
            self.Students[playerID].skipBoxSpeed = 1000
        
        elif self.Students[playerID].studentType== THUAI6.StudentType.StraightAStudent:
            self.Students[playerID].encourageSpeed = 100
            self.Students[playerID].learningSpeed = 135
            self.Students[playerID].radius = 400
            self.Students[playerID].speed = 2880
            self.Students[playerID].viewRange = 9000

            self.Students[playerID].maxDetermination = 3300000
            self.Students[playerID].maxAddition = 78000
            self.Students[playerID].hiddingRate = 0.9
            self.Students[playerID].dangerRange = 13500
            self.Students[playerID].openDoorSpeed = 4000
            self.Students[playerID].skipWindowSpeed = 2116
            self.Students[playerID].skipBoxSpeed = 1000

        elif self.Students[playerID].studentType== THUAI6.StudentType.Sunshine:
            self.Students[playerID].encourageSpeed = 120
            self.Students[playerID].learningSpeed = 123
            self.Students[playerID].radius = 400
            self.Students[playerID].speed = 3000
            self.Students[playerID].viewRange = 10000

            self.Students[playerID].maxDetermination = 3200000
            self.Students[playerID].maxAddition = 66000
            self.Students[playerID].hiddingRate = 0.8
            self.Students[playerID].dangerRange = 15000
            self.Students[playerID].openDoorSpeed = 2800
            self.Students[playerID].skipWindowSpeed = 2540
            self.Students[playerID].skipBoxSpeed = 900





