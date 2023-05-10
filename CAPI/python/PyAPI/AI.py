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
        
        '''初始化'''
        global StudentInfo
        if 'StudentInfo' not in globals().keys():
            StudentInfo = InfoOfPlayers(api)

        global  GameInfo 
        if 'GameInfo' not in globals().keys(): 
            GameInfo = InfoOfGame(api)

        global Route0
        if 'Route0' not in globals().keys():
            Route0 = Routing()
            Route0.InitialRouteMap()
        
        global Message
        if 'Message' not in globals().keys():
            Message = MessageInfo()

        '''判断是否同帧部分'''
        if not GameInfo.upgradeFrameCount(api):
            return   #在同一帧则直接返回（可添加函数）
        '''学生信息更新'''
        StudentInfo.UpgradeStudentInfo(api)
        

        '''Tircker&Map信息更新'''
        StudentInfo.ViewTricker(api)
        finclassroom = []
        for [x,y] in GameInfo.UnFinClassRooms:
            if api.GetClassroomProgress(x,y) == 10000000:
                finclassroom.append([x,y])
        GameInfo.upgradeClassRooms(finclassroom)
        

        '''信息发送及接收'''
        Message.SendMessageToOther(StudentInfo, GameInfo, api)
        Message.ReceiveMessageFromOther(StudentInfo, GameInfo,api)

        '''控制学生移动'''

        StuPosCell = []
        for Student in StudentInfo.Students:
            StuPosCell = [AssistFunction.GridToCell(Student.x),
                        AssistFunction.GridToCell(Student.y)]
            if Student.playerID == StudentInfo.MyID:
                Route0.SetBeginNode(StuPosCell[0],StuPosCell[1])
            else :
                continue
                # Route0.RouteMap[StuPosCell[0]][StuPosCell[1]].NodeType = THUAI6.PlaceType.NullPlaceType #标注其他人的位置，防止互相碰撞

        Route0.SetEndNotes(GameInfo)
        Route0.FindRoute(GameInfo.Map)
        api.Print(Route0.RouteLenth)

        # '''学生能否重叠以及能否两人同时写作业会影响到以下代码的执行'''
        # for i in range(0,4):
        #     if not i == StudentInfo.MyID:
        #         StuPosCell = [AssistFunction.GridToCell(StudentInfo.Students[i].x),
        #                 AssistFunction.GridToCell(StudentInfo.Students[i].y)]
                # Route0.RouteMap[StuPosCell[0]][StuPosCell[1]].NodeType = api.GetPlaceType(StuPosCell[0],StuPosCell[1]) #解除位置标注防止影响下一帧寻路
        # for i in range(0,Route0.RouteLenth):
        #     api.Print([Route0.Routes[i].x,Route0.Routes[i].y])
        #     api.Print("-----------------------------------")
        if Route0.RouteLenth:
            NextNode = Route0.GetNextNote()
            [NextX,NextY] = [NextNode.x,NextNode.y]
            if GameInfo.Map[NextX][NextY] == THUAI6.PlaceType.Window and api.GetSelfInfo().playerState != THUAI6.PlayerState.Climbing:
                api.SkipWindow()
            else :
                [NodeX,NodeY] = [AssistFunction.CellToGrid(NextNode.x),AssistFunction.CellToGrid(NextNode.y)]
                [Dis,Angle] = CalCulateMove([api.GetSelfInfo().x,api.GetSelfInfo().y],[NodeX,NodeY])
                MoveTime = round(Dis/api.GetSelfInfo().speed*1000)
                api.Print(MoveTime)
                if MoveTime < 5: 
                    MoveTime = 5
                api.Move(MoveTime, Angle)
        elif api.GetSelfInfo().playerState != THUAI6.PlayerState.Learning: 
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


class InfoOfGame:

    def __init__(self,api:IStudentAPI): 
        self.FrameCount :int = 0
        self.Map :List[List[THUAI6.PlaceType]] = api.GetFullMap()
        self.GameInfo = api.GetGameInfo()
        self.UnFinClassRooms : List[[int,int]] = []
        self.FinClassRooms : List[[int,int]] = []
        self.FinClassRoomNum : int = 0
        self.InitClassRooms()

    def upgradeFrameCount(self,api:IStudentAPI) -> bool:
        GameTime = api.GetGameInfo().gameTime
        framecount = round(GameTime/50)
        ''' 返回真表明帧数有更新，否则没有'''
        if self.FrameCount == framecount:
            return False
        else :
            self.FrameCount = framecount
            return True

    def upgradeMap(self,map:[int,int,THUAI6.PlaceType]) -> bool:
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

    def InitClassRooms(self) ->None:
        '''依据地图更新教室所在地点'''
        for x in range(0,50):
            for y in range(0,50):
                if self.Map[x][y] == THUAI6.PlaceType.ClassRoom:
                    self.UnFinClassRooms.append([x,y])
    
    def upgradeClassRooms(self,ClassRooms:[[int,int]]) ->bool:
        '''将传入列表中的教室设定为已完成并同时更改地图，有变化返回True'''
        if len(ClassRooms) == 0:
            return False
        else:
            change = 0
            for ClassRoom in ClassRooms:
                if self.UnFinClassRooms.count(ClassRoom):
                    i = self.UnFinClassRooms.index(ClassRoom)
                    self.UnFinClassRooms.pop(i)
                    self.FinClassRooms.append(ClassRoom)
                    self.upgradeMap([ClassRoom[0],ClassRoom[1],THUAI6.PlaceType.Wall]) #认为已完成的作业为wall
                    change = change +1 
            self.FinClassRoomNum = len(self.FinClassRooms)
            return (change==0)

class InfoOfPlayers:
    
    ''' Save the info of students including myself,and tricker(if can see)'''
    def __init__(self,api: IStudentAPI):
        self.Students : List[THUAI6.Student] = api.GetStudents()
        '''注意顺序并不按照player排，是随机的'''
        self.MyID :int = api.GetSelfInfo().playerID

        self.ViewTricker(api)
        if  self.CanViewTricker == True:
            return
        else:
            '''主要是Tricker没有定义init函数，超麻烦'''
            self.Tricker: List[THUAI6.Tricker] = [THUAI6.Tricker(),]
            #需要声明这些变量否则无法使用
            self.Tricker[0].x = 0
            self.Tricker[0].y = 0
            self.Tricker[0].viewRange = 0 
            self.Tricker[0].trickerType = THUAI6.TrickerType.NullTrickerType
            return


    def UpgradeStudentInfo(self,api:IStudentAPI) ->None:
        self.Students = api.GetStudents()
        
    def ViewTricker(self,api:IStudentAPI)->None:
        '''函数会自动更新Tricker信息,该函数应当在每帧开头调用一次'''
        Tricker = api.GetTrickers()
        if len(Tricker):
            self.Tricker = Tricker
            self.CanViewTricker = True
        else:
            self.CanViewTricker = False

class MessageInfo:

    def __init__(self):
        self.Message: List[str] = ['','','','']
        '''message按照studentID储存，自己为发送，别人为接收'''

    def SendMessageToOther(self,StudentInfo: InfoOfPlayers,GameInfo:InfoOfGame,api:IStudentAPI) ->None:
        self.MessageEncode(StudentInfo,GameInfo)
        for i in range(0,4):
            if StudentInfo.MyID != i:
                api.SendMessage(i,self.Message[StudentInfo.MyID])
        return

    def MessageEncode(self,StudentInfo:InfoOfPlayers,GameInfo:InfoOfGame) ->None:
        '''Important Info In Messages'''
        message = str()
        '''Student Info'''  #这部分貌似被getStudent替代了，问题不大

        '''Tricker Info'''
        if StudentInfo.CanViewTricker:
            '''能看见才发送，否则不发'''
            message = message + 'T' + str(StudentInfo.Tricker[0].x) + '?' + str(StudentInfo.Tricker[0].y) + '/'

        '''Map Info'''
        if len(GameInfo.FinClassRooms):
            for ClassRoom in GameInfo.FinClassRooms:  #只发送已完成的教室
                message = message + 'C'+ str(ClassRoom[0]) + '?' +  str(ClassRoom[1]) + '/'        

        self.Message[StudentInfo.MyID] = message

    def ReceiveMessageFromOther(self,StudentInfo: InfoOfPlayers,GameInfo:InfoOfGame,api:IStudentAPI) ->None:
        while api.HaveMessage():
            MessageTuple = api.GetMessage()
            self.Message[MessageTuple[0]] = MessageTuple[1]
            self.MessageDecode(StudentInfo, GameInfo, MessageTuple[0])

    def MessageDecode(self,StudentInfo: InfoOfPlayers,GameInfo:InfoOfGame,playerID:int)->None:

        ClassRooms = []

        DecodedMessage = self.Message[playerID].split(sep='/')
        while len(DecodedMessage):
            MessageUnit :str = DecodedMessage.pop()
            if len(MessageUnit) == 0: 
                continue
                '''Tricker Info'''
            elif MessageUnit[0] == 'T' and not StudentInfo.CanViewTricker: #只有自己看不见的时候才会听别人的
                [x,y] = MessageUnit[1:].split(sep='?')
                [StudentInfo.Tricker[0].x,StudentInfo.Tricker[0].y] = [int(x),int(y)]

                '''Map Info'''
            elif MessageUnit[0] == 'C':
                [x,y] = MessageUnit[1:].split(sep='?')
                ClassRooms.append([x,y])

        GameInfo.upgradeClassRooms(ClassRooms)


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

    # 以下重载运算符函数用于优先队列以及判断两点坐标是否相同   更改可能导致报错
    def __gt__(self,other):
        if isinstance(other, RouteNode):
            return self.Distance > other.Distance
        elif isinstance(other, Number):
            return self.Distance > other
        else:
            raise AttributeError("The of other is incorrect!")

    def __eq__(self, other):
        if isinstance(other, RouteNode):
            return self.x == other.x and self.y == other.y
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
        self.RouteLenth = 114514
        self.BeginNode = RouteNode()
        self.EndNotes :List[RouteNode] = []
        self.Routes :List[RouteNode] = []
        self.RouteMap :List[List[RouteNode]]= []

    def InitialRouteMap(self) ->None:
        '''初始化寻路地图'''
        for i in range(0,50):
            self.RouteMap.append([])
            for j in range(0,50):
                Node = RouteNode(i,j)
                self.RouteMap[i].append(Node)

    def GetNextNote(self) -> RouteNode:
        '''用于获取下一个需要前往的路径点'''
        return self.Routes[-1]
        
    # def SetClassRooms(self) ->None:
    #     '''初始化教室列表'''
    #     for i in range(0,50):
    #         for j in range(0,50):
    #             if self.RouteMap[i][j].NodeType == THUAI6.PlaceType.ClassRoom:
    #                 self.UnfinClassroom.append(self.RouteMap[i][j])
    #     self.UnfinClassroomNum = len(self.UnfinClassroom)

    # def InitClassRoomss(self,api:IStudentAPI,ClassRooms:List[RouteNode] = []) ->None:
    #     '''更新作业完成状态,同时也会自动更新终点信息,若输入classroom则会自动移除(不检查输入合法)'''
    #     if len(ClassRooms):
    #         for ClassRoom in ClassRooms:
    #             if api.GetClassroomProgress(ClassRoom.x, ClassRoom.y) == 10000000:
    #                 continue
    #             for i in range(self.UnfinClassroomNum-1,-1,-1):  #从列表中删除需要使用倒序循环
    #                 # api.Print(api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y))
    #                 if self.UnfinClassroom[i].x == ClassRoom.x and self.UnfinClassroom[i].y == ClassRoom.y:
    #                     FinishedClassroom = self.UnfinClassroom.pop(i)
    #                     self.FinishedClassrooms.append(FinishedClassroom)
    #                     self.RouteMap[FinishedClassroom.x][FinishedClassroom.y].NodeType = THUAI6.PlaceType.NullPlaceType #修改地图使该位置显示为不可越过
    #                     for j in range(len(self.EndNotes)-1,-1,-1):
    #                         if ((self.EndNotes[j].x - FinishedClassroom.x)**2 + (self.EndNotes[j].y - FinishedClassroom.y)**2) < 3:
    #                             self.EndNotes.pop(j)

    #     else:
    #         for i in range(self.UnfinClassroomNum-1,-1,-1):  #从列表中删除需要使用倒序循环
    #             api.Print(api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y))
    #             if api.GetClassroomProgress(self.UnfinClassroom[i].x, self.UnfinClassroom[i].y) == 10000000:
    #                 FinishedClassroom = self.UnfinClassroom.pop(i)
    #                 self.FinishedClassrooms.append(FinishedClassroom)
    #                 self.RouteMap[FinishedClassroom.x][FinishedClassroom.y].NodeType = THUAI6.PlaceType.NullPlaceType #修改地图使该位置显示为不可越过
    #                 for j in range(len(self.EndNotes)-1,-1,-1):
    #                     if ((self.EndNotes[j].x - FinishedClassroom.x)**2 + (self.EndNotes[j].y - FinishedClassroom.y)**2) < 3:
    #                         self.EndNotes.pop(j)

    #     api.Print('ClassRoom Num is ' + str(self.UnfinClassroomNum))
    #     self.UnfinClassroomNum = len(self.UnfinClassroom)

    def SetEndNotes(self,GameInfo:InfoOfGame,endnotes :List[RouteNode] = []) ->None:
        '''用于设置终点，不输入参数则默认终点为ClassRoom周围'''
        if not len(endnotes):
            self.EndNotes = []
            for [i,j] in GameInfo.UnFinClassRooms:
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
                        self.EndNotes.append(Node)
        else:
            self.EndNotes = endnotes

    
    # def UpgradeRouteMap(self,mapnode: RouteNode) ->bool:
    #     '''返回真表明有更新，否则没有'''
    #     [x,y] = [mapnode.x,mapnode.y]
    #     if self.RouteMap[x][y].NodeType == mapnode.NodeType:
    #             return False
    #     else :
    #         self.RouteMap[x][y].NodeType = mapnode.NodeType
    #         return True

    def SetBeginNode(self,x: int,y: int):
        self.BeginNode.x = x
        self.BeginNode.y = y
        self.BeginNode.Distance = 0

    def FindRoute(self,map:List[List[THUAI6.PlaceType]]):
        '''
        使用的寻路方法为从起点向周围扩散并最终得到所有点到起点的最短距离

        可能出现的问题：
        在寻找最近的目标点时必定收敛，但是寻找最远点或者次元点未必收敛
        （可能在两个位置间来回振荡，因为进行的是动态优化）

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
                        if [THUAI6.PlaceType.Land,THUAI6.PlaceType.Window,THUAI6.PlaceType.Grass].count(map[i][j]): 
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
        
        # 返回路径
        self.Routes = []
        PreNode = GoalNode
        while PreNode.Distance :
            self.Routes.append(PreNode)
            PreNode = self.RouteMap[PreNode.prex][PreNode.prey]
        self.RouteLenth = len(self.Routes)


                    

                

        
        '''必须实现的功能'''

        '''学生部分：
        学生信息是完全透明的
        场地信息和对手信息是不透明的，需要相互传递
        对于每份代码应该只有具体的操作不同，所需实例化的对象数目相同，功能基本相同
        尽量保证功能相似的变量不出现两个
        目前重点：关于信息是否可视部分应该在哪个部分做
        大约在学生信息更新后和message前

        GameControl部分：
        处理和控制帧数，并调用和控制其他模块执行

        Message部分：(接收到的信息存在至少一帧的延时)
        使用View函数观察并打包所有可视信息
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
        应当基于Message和Route的共同信息控制Route的寻路方向，并决定具体调用何种函数
        '''


