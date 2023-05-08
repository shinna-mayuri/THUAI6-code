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
        if 'GameInfo' not in globals().keys(): 
            GameInfo = InformationOfGame()
            GameInfo.upgradeMap(api.GetFullMap()) 

        global Route0
        if 'Route0' not in globals().keys():
            Route0 = Routing()
            Route0.InitialRouteMap(api.GetFullMap())
            Route0.SetClassRooms()
            Route0.SetEndNotes()
        
        global Message
        if 'Message' not in globals().keys():
            Message = MessageInfo()

        '''判断是否同帧部分'''
        GameTime = api.GetGameInfo().gameTime
        FrameCount = round(GameTime/50)
        if not GameInfo.upgradeFrameCount(FrameCount):
            return   #在同一帧则直接返回（可添加函数）
        '''学生信息获取及更新'''
        

        StudentInfo.UpgradeStudentInfo(api)
        Message.SendMessageToOther(StudentInfo, GameInfo, Route0, api)
        Message.ReceiveMessageFromOther(StudentInfo, GameInfo, Route0,api)

        '''控制学生移动'''

        StuPosCell = []
        for i in range(0,4):
            StuPosCell = [AssistFunction.GridToCell(StudentInfo.Students[i].x),
                        AssistFunction.GridToCell(StudentInfo.Students[i].y)]
            if i == StudentInfo.MyID:
                Route0.SetBeginNode(StuPosCell[0],StuPosCell[1])
            else :
                continue
                # Route0.RouteMap[StuPosCell[0]][StuPosCell[1]].NodeType = THUAI6.PlaceType.NullPlaceType #标注其他人的位置，防止互相碰撞

        Route0.UpgradeClassRooms(api)
        Route0.FindRoute(api)

        '''学生能否重叠以及能否两人同时写作业会影响到以下代码的执行'''
        for i in range(0,4):
            if not i == StudentInfo.MyID:
                StuPosCell = [AssistFunction.GridToCell(StudentInfo.Students[i].x),
                        AssistFunction.GridToCell(StudentInfo.Students[i].y)]
                # Route0.RouteMap[StuPosCell[0]][StuPosCell[1]].NodeType = api.GetPlaceType(StuPosCell[0],StuPosCell[1]) #解除位置标注防止影响下一帧寻路
        # for i in range(0,Route0.RouteLenth):
        #     api.Print([Route0.Routes[i].x,Route0.Routes[i].y])
        #     api.Print("-----------------------------------")
        if Route0.RouteLenth:
            NextNode = Route0.GetNextNote()
            if NextNode.NodeType == THUAI6.PlaceType.Window :
                api.SkipWindow()
            else :
                [NodeX,NodeY] = [AssistFunction.CellToGrid(NextNode.x),AssistFunction.CellToGrid(NextNode.y)]
                [Dis,Angle] = CalCulateMove([api.GetSelfInfo().x,api.GetSelfInfo().y],[NodeX,NodeY])
                MoveTime = round(Dis/api.GetSelfInfo().speed*1000)
                api.Print(MoveTime)
                if MoveTime < 5: 
                    MoveTime = 5
                api.Move(MoveTime, Angle)
        elif not api.GetSelfInfo().playerState == THUAI6.PlayerState.Learning: 
            api.StartLearning()

        '''每个学生各自的代码'''
        if self.__playerID == 0:
            
            return

        elif self.__playerID == 1:
            # 玩家1执行操作
            return
        elif self.__playerID == 2:
            # 玩家2执行操作
            return
        elif self.__playerID == 3:
            # 玩家3执行操作
            return
                #可以写成if self.__playerID<2之类的写法

        return

    def TrickerPlay(self, api: ITrickerAPI) -> None:

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
        self.UnfinClassroom : List[RouteNode] = []
        self.FinishedClassrooms : List[RouteNode] = []
        self.UnfinClassroomNum : int


    def InitialRouteMap(self,Map:List[List[THUAI6.PlaceType]]) ->None:
        '''初始化寻路地图'''
        for i in range(0,50):
            self.RouteMap.append([])
            for j in range(0,50):
                Node = RouteNode(i,j)
                Node.NodeType = Map[i][j]
                self.RouteMap[i].append(Node)

    def GetNextNote(self) -> RouteNode:
        '''用于获取下一个需要前往的路径点'''
        return self.Routes[-1]
        
    def SetClassRooms(self) ->None:
        '''初始化教室列表'''
        for i in range(0,50):
            for j in range(0,50):
                if self.RouteMap[i][j].NodeType == THUAI6.PlaceType.ClassRoom:
                    self.UnfinClassroom.append(self.RouteMap[i][j])
        self.UnfinClassroomNum = len(self.UnfinClassroom)

    def UpgradeClassRooms(self,api:IStudentAPI,ClassRooms:List[RouteNode] = []) ->None:
        '''更新作业完成状态,同时也会自动更新终点信息,若输入classroom则会自动移除(不检查输入合法)'''
        if len(ClassRooms):
            for ClassRoom in ClassRooms:
                if api.GetClassroomProgress(ClassRoom.x, ClassRoom.y) == 10000000:
                    continue
                for i in range(self.UnfinClassroomNum-1,-1,-1):  #从列表中删除需要使用倒序循环
                    # api.Print(api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y))
                    if self.UnfinClassroom[i].x == ClassRoom.x and self.UnfinClassroom[i].y == ClassRoom.y:
                        FinishedClassroom = self.UnfinClassroom.pop(i)
                        self.FinishedClassrooms.append(FinishedClassroom)
                        self.RouteMap[FinishedClassroom.x][FinishedClassroom.y].NodeType = THUAI6.PlaceType.NullPlaceType #修改地图使该位置显示为不可越过
                        for j in range(len(self.EndNotes)-1,-1,-1):
                            if ((self.EndNotes[j].x - FinishedClassroom.x)**2 + (self.EndNotes[j].y - FinishedClassroom.y)**2) < 3:
                                self.EndNotes.pop(j)

        else:
            for i in range(self.UnfinClassroomNum-1,-1,-1):  #从列表中删除需要使用倒序循环
                api.Print(api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y))
                if api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y) == 10000000:
                    FinishedClassroom = self.UnfinClassroom.pop(i)
                    self.FinishedClassrooms.append(FinishedClassroom)
                    self.RouteMap[FinishedClassroom.x][FinishedClassroom.y].NodeType = THUAI6.PlaceType.NullPlaceType #修改地图使该位置显示为不可越过
                    for j in range(len(self.EndNotes)-1,-1,-1):
                        if ((self.EndNotes[j].x - FinishedClassroom.x)**2 + (self.EndNotes[j].y - FinishedClassroom.y)**2) < 3:
                            self.EndNotes.pop(j)

        api.Print('ClassRoom Num is ' + str(self.UnfinClassroomNum))
        self.UnfinClassroomNum = len(self.UnfinClassroom)

    def SetEndNotes(self,endnotes :List[RouteNode] = []) ->None:
        '''用于设置终点，不输入参数则默认终点为ClassRoom周围'''
        if not len(endnotes):
            self.EndNotes = []
            for ClassRoom in self.UnfinClassroom:
                [i,j] = [ClassRoom.x,ClassRoom.y]
                for [ii,jj] in [[i + 1,j],    #九宫格内即可
                                [i + 1,j - 1],
                                [i - 1,j + 1],
                                [i - 1,j - 1],
                                [i + 1,j + 1 ],
                                [i - 1,j ],
                                [i ,j + 1],
                                [i ,j - 1]]:
                    if 0 <= ii < 50 and  0 <= jj < 50:
                        Node = RouteNode(ii,jj)
                        Node.NodeType = self.RouteMap[ii][jj].NodeType
                        self.EndNotes.append(Node)
        else:
            self.EndNotes = endnotes

    
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
        self.BeginNode.NodeType = self.RouteMap[x][y].NodeType
        self.BeginNode.Distance = 0

    def FindRoute(self,api:IStudentAPI):
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
        for k in range(0,len(self.EndNotes)):
            if  self.RouteMap[self.EndNotes[k].x][self.EndNotes[k].y].Distance < GoalNode.Distance:
                GoalNode = self.RouteMap[self.EndNotes[k].x][self.EndNotes[k].y]
        
        # api.Print([self.BeginNode.x,self.BeginNode.y])
        # api.Print([GoalNode.x,GoalNode.y])
        # api.Print(GoalNode.Distance)
        # 返回路径
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
        GottenStudents = api.GetStudents()
        api.Print(len(GottenStudents))
        while len(GottenStudents):
            Student = GottenStudents.pop()
            self.Students[Student.playerID] = Student
            self.AddStudentInfo(Student.playerID)       # 添加类中不包含但是可能用到的学生信息

        if self.ViewTricker(api):
            return
        else:
            self.Tricker: List[THUAI6.Tricker] = [THUAI6.Tricker(),]
            #需要声明这些变量否则无法使用
            self.Tricker[0].x = 0
            self.Tricker[0].y = 0
            self.Tricker[0].viewRange = 0 
            self.Tricker[0].trickerType = THUAI6.TrickerType.NullTrickerType
            return


    def UpgradeStudentInfo(self,api:IStudentAPI) ->None:
        Students = api.GetStudents()
        while len(Students):
            Student = Students.pop()
            self.Students[Student.playerID] = Student


    def ViewTricker(self,api:IStudentAPI)->bool:
        Tricker = api.GetTrickers()
        if len(Tricker):
            self.Tricker = Tricker
            return True
        else:
            return False

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



class MessageInfo:

    def __init__(self):
        self.Message: List[str] = ['','','','']
        '''Message include self and others, self is for sending and others for receiving'''

    def SendMessageToOther(self,StudentInfo: InfoOfPlayers,GameInfo:InformationOfGame,Route:Routing,api:IStudentAPI) ->None:
        self.MessageEncode(StudentInfo,GameInfo,Route,api)
        for i in range(0,4):
            if StudentInfo.MyID != i:
                api.SendMessage(i,self.Message[StudentInfo.MyID])
        return

    def MessageEncode(self,StudentInfo:InfoOfPlayers,GameInfo:InformationOfGame,Route:Routing,api:IStudentAPI) ->None:
        '''Important Info In Messages'''
        message = str()
        '''Student Info'''  #这部分貌似被getStudent替代了，问题不大
        # message = message + 'T' + str([self.MyID].studentType.value) + '/'
        # message = message + 'S' + str(self.Students[self.MyID].playerState.value) + '/'
        # message = message + 'X' + str(self.Students[self.MyID].x) + '/'
        # message = message + 'Y' + str(self.Students[self.MyID].y) + '/'
        # message = message + 'G' + str(self.Students[self.MyID].dangerAlert) + '/'
        # # message = message + 'U' + str(self.Students[self.MyID].timeUntilSkillAvailable) + '/'
        # message = message + 'A' + str(self.Students[self.MyID].addiction) + '/'
        # message = message + 'D' + str(self.Students[self.MyID].determination) + '/'
        # message = message + 'E' + str(self.Students[self.MyID].encourageProgress) + '/'
        # message = message + 'R' + str(self.Students[self.MyID].rouseProgress) + '/'
        # message = message + 'B' + str(self.Me.buff) + '/'
        # message = message + 'P' + str(self.Me.prop) + '/'

        '''Tricker Info'''
        if StudentInfo.ViewTricker(api):
            '''能看见才发送，否则不发'''
            message = message + 'C' + str(StudentInfo.Tricker[0].x) + '?' + str(StudentInfo.Tricker[0].y) + '/'

        '''Map Info'''
        if len(Route.FinishedClassrooms):
            for ClassRoom in Route.FinishedClassrooms:
                if api.GetClassroomProgress(ClassRoom.x,ClassRoom.y) == 10000000 :
                    '''只发送看见的部分'''
                    message = message + 'c'+ str(ClassRoom.x) + '?' +  str(ClassRoom.y) + '/'        

        self.Message[StudentInfo.MyID] = message

    def ReceiveMessageFromOther(self,StudentInfo: InfoOfPlayers,GameInfo:InformationOfGame,Route:Routing,api:IStudentAPI) ->None:
        while api.HaveMessage():
            MessageTuple = api.GetMessage()
            self.Message[MessageTuple[0]] = MessageTuple[1]

        for playerID in range(0,4):
            if playerID == StudentInfo.MyID:
                continue 
            else:
                ClassRooms = []
                DecodedMessage = self.Message[playerID].split(sep='/')
                while len(DecodedMessage):
                    MessageUnit :str = DecodedMessage.pop()
                    if len(MessageUnit) == 0: 
                        continue

                        '''Student Info'''
                    # elif MessageUnit[0] == 'T':
                    #     self.Students[playerID].studentType = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'S':
                    #     self.Students[playerID].playerState = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'X':
                    #     self.Students[playerID].x = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'Y':
                    #     self.Students[playerID].y = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'G':
                    #     self.Students[playerID].dangerAlert = float(MessageUnit[1:])
                    # # elif MessageUnit[0] == 'U':
                    # #     self.Students[playerID].timeUntilSkillAvailable = float(MessageUnit[1:])
                    # elif MessageUnit[0] == 'A':
                    #     self.Students[playerID].addiction = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'D':
                    #     self.Students[playerID].determination = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'E':
                    #     self.Students[playerID].encourageProgress = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'R':
                    #     self.Students[playerID].rouseProgress = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'B':
                    #     self.Students[playerID].determination = int(MessageUnit[1:])
                    # elif MessageUnit[0] == 'P':
                    #     self.Students[playerID].determination = int(MessageUnit[1:])

                        '''Tricker Info'''
                    elif MessageUnit[0] == 'C' and not StudentInfo.ViewTricker(api): #'''只有自己看不见的时候才会听别人的'''
                        [x,y] = MessageUnit[1:].split(sep='?')
                        [StudentInfo.Tricker[0].x,StudentInfo.Tricker[0].y] = [int(x),int(y)]

                        '''Map Info'''
                    elif MessageUnit[0] == 'c':
                        [x,y] = MessageUnit[1:].split(sep='?')
                        Node = RouteNode(int(x),int(y))
                        Node.NodeType = THUAI6.PlaceType.NullPlaceType
                        if Route.UpgradeRouteMap(Node) and api.GetClassroomProgress(int(x), int(y)) != -1:   # '''说明之前不知道这里的作业已完成'''
                            ClassRooms.append(Node)

                Route.UpgradeClassRooms(api,ClassRooms)


    '''必须实现的功能'''

    '''学生部分：
    学生信息是完全透明的
    场地信息和对手信息是不透明的，需要相互传递
    对于每份代码应该只有具体的操作不同，所需实例化的对象数目相同，功能基本相同
    尽量保证功能相似的变量不出现两个
    
    Message部分：(接收到的信息存在至少一帧的延时)
    打包可视范围内的信息并广播给队友
    接收队友传来的所有非可视信息（防止延时）
    将这些信息（接收到的和自己看到的）解码并更新
    理论上只要每帧执行一次该部分即可，并且是最先执行
    
    Route部分：
    目前节点所需信息可以认为是最少的，唯一可能需要更新的部分是节点比较函数eq（定义节点相同）--》能简化工作量，先验证可行性
    寻路的关键在于RouteMap，可能对其进行的操作有：
    初始化整个map
    修改map某个节点状态
    寻路过程中记录找到的路径等
    ***此外附加的终点设定应该交给其他函数完成***
    信息的记录与修改应该外包给其他函数
    理论上寻路也只需要每帧执行一次，除非寻路不存在结果（目标不存在或被卡死）

    
    Move部分：
    应当基于Message和Route的共同信息控制Route的寻路方向，并决定具体调用何种函数'''

    


    '''tricker部分逻辑完全不同，写完学生再考虑'''

