import PyAPI.structures as THUAI6
from PyAPI.Interface import IStudentAPI, ITrickerAPI, IAI
from typing import Union, Final, cast, List
from PyAPI.constants import Constants
import queue

import time

# 以下为自行添加的库

import random
import queue



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


# 自定义类部分

class Routing:
    Routes: List[RouteNode]
    Map: List[List[THUAI6.PlaceType]]
    BeginNode : RouteNode
    EndNotes : List[RouteNode]
    RouteMap: List[List[RouteNode]]
    RouteLenth: int
    RouteIsNewest: bool


    def __init__(self):
        self.RouteIsNewest = False
        self.RouteLenth = 114514

       
        
    def SetMap(self,map:List[List[THUAI6.PlaceType]]) ->None:
        self.Map = map
        for i in range(0,49) :
            for j in range(0,49) :
                if self.Map[i][j] == THUAI6.PlaceType.ClassRoom :
                    Node = RouteNode(i,j)
                    Node.NodeType = self.Map[i][j]
                    self.EndNotes.append(Node)
                else : continue

    def SetBeginNode(self,x: int,y: int):
        self.BeginNode.x = x
        self.BeginNode.y = y
        self.BeginNode.NodeType = self.Map[x][y]

    def FindRoute(self):
        for i in range(0,49):
            for j in range(0,49):
                self.RouteMap[i].append(RouteNode(i,j))
        q = queue.PriorityQueue()
        q.put((0,self.BeginNode))
        while q.not_empty():
            Node :RouteNode = q.get()[1]
            if Node.Distance > 2500:
                break
                #算出所有点到起点的距离
            
            for [i,j] in [[Node.x - 1,Node.y - 1],[Node.x - 1,Node.y + 1],[Node.x + 1,Node.y - 1],[Node.x + 1,Node.y + 1]]:
            # 遍历四个方向

                if 0 <= i < 50 and  0 <= j < 50 and self.RouteMap[i][j].IsRouted == False :
                    #判断该点路径是否已经确定

                    if List[THUAI6.PlaceType.Land,THUAI6.PlaceType.Window,THUAI6.PlaceType.Grass].count(self.Map[i][j]): 
                        q.put((Node.Distance+1,RouteNode(i,j,Node.Distance+1)))
                        self.RouteMap[i][j].prex = Node.x
                        self.RouteMap[i][j].prey = Node.y
                    else:
                        q.put((114514,RouteNode(i,j,114514)))

                    self.RouteMap[i][j].IsRouted = True
        
        Q = queue.PriorityQueue()
        for ClassRoom in self.EndNotes:
            for [i,j] in [[ClassRoom.x - 1,ClassRoom.y - 1],
            [ClassRoom.x - 1,ClassRoom.y - 1],
            [ClassRoom.x - 1,ClassRoom.y - 1],
            [ClassRoom.x - 1,ClassRoom.y - 1]]:
                if 0 <= i < 50 and  0 <= j < 50:
                    Q.put((self.RouteMap[i][j].Distance,self.RouteMap[i][j]))

        PreNode :RouteNode = q.get()[1]

        while PreNode.x != self.BeginNode.x or PreNode.y != self.BeginNode.y :
            self.Routes.append(PreNode)
            PreNode = self.RouteMap[PreNode.prex][PreNode.prey]

        self.RouteLenth = len(self.Routes)

        

            

                        



# 自定义函数部分


    # NullPlaceType = 0
    # Land = 1
    # Wall = 2
    # Grass = 3
    # ClassRoom = 4
    # Gate = 5
    # HiddenGate = 6
    # Window = 7
    # Door3 = 8
    # Door5 = 9
    # Door6 = 10
    # Chest = 11

    #1，3，7一定能走
    #2，4，5，6，11为障碍
    #8910为条件障碍
    #为目标（实际目标设置在其旁边）

def StudentFindMap(api:IStudentAPI) -> None:
    Map = api.GetFullMap()
    StudentPosition = [AssistFunction.GridToCell(api.GetSelfInfo().x)
    ,AssistFunction.GridToCell(api.GetSelfInfo().y)]

    # while 
    # StudentPosition[1]
    # for x in 1:50 :
    #     for y in 1:50 :

    #     end
    # end

    #以上经过测试即可生成矩阵版地图
    #api.Print(StudentPosition)
    #目前只需要简单的0-1地图即可，不需要加权的最短路径

    
    
    return

    


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
        self.Distance = dis
        self.NodeType = THUAI6.PlaceType(0)






# -------------------分割线-----------------

class AI(IAI):
    def __init__(self, pID: int):
        self.__playerID = pID

    def StudentPlay(self, api: IStudentAPI) -> None:
        # 公共操作
        if self.__playerID == 0:
            StudentFindMap(api)
            # 玩家0执行操作
            return
        elif self.__playerID == 1:
            api.Move(1,1)
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


