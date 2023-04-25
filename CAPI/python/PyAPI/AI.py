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
        return [THUAI6.StudentType.Athlete, THUAI6.StudentType.Teacher, THUAI6.StudentType.StraightAStudent, THUAI6.StudentType.Sunshine]

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
        # 公共操作
        if self.__playerID == 0:
            Route0 = Routing()
            StudentPosition = [AssistFunction.GridToCell(api.GetSelfInfo().x)
            ,AssistFunction.GridToCell(api.GetSelfInfo().y)]
            api.Print(StudentPosition)
            Route0.SetMap(api.GetFullMap())
            Route0.SetBeginNode(StudentPosition[0], StudentPosition[1])
            Route0.FindRoute()
            if Route0.RouteLenth:
                NextNode = Route0.GetNextNote()
                if NextNode.NodeType == THUAI6.PlaceType.Window :
                    api.SkipWindow()
                else :
                    [NodeX,NodeY] = [AssistFunction.CellToGrid(NextNode.x),AssistFunction.CellToGrid(NextNode.y)]
                    [Dis,Angle] = CalCulateMove([api.GetSelfInfo().x,api.GetSelfInfo().y],[NodeX,NodeY])
                    api.Move(round(Dis/api.GetSelfInfo().speed*1000), Angle)
            else: 
                api.StartLearning()
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
        # 可以写成if self.__playerID<2之类的写法
        # 公共操作
        return

    def TrickerPlay(self, api: ITrickerAPI) -> None:
        selfInfo = api.GetSelfInfo()
        api.PrintSelfInfo()
        #api.Move(random.randint(500,1000),random.randint(0,100))
        return


def CalCulateMove(Begin: List[int],Goal: List[int]) -> List:
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
    x: int
    y: int 
    prex: int
    prey: int 
    IsRouted: bool
    Distance: int
    NodeType: THUAI6.PlaceType

    def __init__(self,x: int = 0,y: int = 0,dis: int = 114514) -> None:
        self.x = x
        self.y = y
        self.IsRouted = False
        self.prex = x
        self.prey = y
        self.Distance :int = dis
        self.NodeType = THUAI6.PlaceType(0)

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




class Routing:
    Routes: List[RouteNode]
    Map: List[List[THUAI6.PlaceType]]
    BeginNode : RouteNode
    EndNotes :List[RouteNode]
    RouteMap :List[List[RouteNode]]
    RouteLenth: int
    RouteIsNewest: bool
    
    def __init__(self):
        self.RouteIsNewest = False
        self.RouteLenth = 114514
        self.BeginNode = RouteNode()
        self.EndNotes :List[RouteNode] = []
        self.Routes :List[RouteNode] = []
        self.RouteMap :List[List[RouteNode]]= []

    def GetNextNote(self) -> RouteNode:
        return self.Routes[-1]
        
    def SetMap(self,map:List[List[THUAI6.PlaceType]]) ->None:
        self.Map = map
        for i in range(0,50) :
            for j in range(0,50) :
                if self.Map[i][j] == THUAI6.PlaceType.ClassRoom:
                    Node = RouteNode(i,j)
                    Node.NodeType = self.Map[i][j]
                    self.EndNotes.append(Node)

    def SetRouteMap(self) ->None:
        for i in range(0,50):
            self.RouteMap.append([])
            for j in range(0,50):
                Node = RouteNode(i,j)
                Node.NodeType = self.Map[i][j]
                self.RouteMap[i].append(Node)

    def SetBeginNode(self,x: int,y: int):
        self.BeginNode.x = x
        self.BeginNode.y = y
        self.BeginNode.NodeType = self.Map[x][y]
        self.BeginNode.Distance = 0

    def FindRoute(self):
        self.SetRouteMap() 

        q = queue.PriorityQueue()
        q.put(self.BeginNode)
        self.RouteMap[self.BeginNode.x][self.BeginNode.y].IsRouted = True
        self.RouteMap[self.BeginNode.x][self.BeginNode.y].Distance = 0
        while not q.empty():
            Node :RouteNode = q.get()
            if Node.Distance > 2500:
                break

                #算出所有点到起点的距离
            for [i,j] in [[Node.x - 1,Node.y ],[Node.x + 1,Node.y ],[Node.x ,Node.y - 1],[Node.x ,Node.y + 1]]:
            # 遍历四个方向

                if 0 <= i < 50 and  0 <= j < 50 and self.RouteMap[i][j].IsRouted == False :
                        self.RouteMap[i][j].IsRouted = True
                        #判断该点路径是否已经确定
                        if [THUAI6.PlaceType.Land,THUAI6.PlaceType.Window,THUAI6.PlaceType.Grass].count(self.Map[i][j]): 
                            self.RouteMap[i][j].Distance = Node.Distance + 1
                            self.RouteMap[i][j].prex = Node.x
                            self.RouteMap[i][j].prey = Node.y
                            q.put(self.RouteMap[i][j])
   
        
        Q = queue.PriorityQueue()
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
                if 0 <= i < 50 and  0 <= j < 50:
                    NeighberNode : RouteNode = self.RouteMap[i][j]
                    Q.put(NeighberNode)

        PreNode = self.RouteMap[18][40]
        # PreNode = Q.get()

        while PreNode.Distance :
            self.Routes.append(PreNode)
            PreNode = self.RouteMap[PreNode.prex][PreNode.prey]

        self.RouteLenth = len(self.Routes)