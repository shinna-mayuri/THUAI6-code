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
        
        '''每个学生各自的代码'''
        if self.__playerID == 0:
            # global Route0
            # if 'Route0' not in globals().keys():
            #     Route0 = Routing()
            #     Route0.InitialRouteMap(api.GetFullMap())
            # StudentPosition = [AssistFunction.GridToCell(api.GetSelfInfo().x),AssistFunction.GridToCell(api.GetSelfInfo().y)]
            # Route0.SetBeginNode(StudentPosition[0], StudentPosition[1])
            # Route0.SetEndNotes()
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

            api.GetStudents()
            api.Print("Current Root:")
            for i in range(0,Route0.RouteLenth):
                api.Print([Route0.Routes[i].x,Route0.Routes[i].y])
            api.Print("-----------------------------------")
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
        
    def SetEndNotes(self) ->None:
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

        