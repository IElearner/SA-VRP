import pandas as pd
import math
import random
import copy
#实例信息
class Instance():
    def __init__(self):
        self.best_method=None
        self.point_list=[]
        self.point_order=[]
        self.depot=None
        self.pointamount=0
        self.maxLoad=0
#方案包括节点序列、最优值、路线
class Method():
    def __init__(self):
        self.pointarray=None     #整列信息
        self.value=None
        self.routes=None         #切割路线
#每个点模型，包括其坐标、需求量
class Point():
    def __init__(self):
        self.array=0
        self.x=0
        self.y=0
        self.demand=0
#生成一个原始序列
def OriginalPointsSequence(point_array):
    point_sequence=copy.deepcopy(point_array)
    random.seed(0)
    random.shuffle(point_sequence)
    return point_sequence
#确定改进搜索点位（在整个长序列上，前面某点与后半段相应位置某点交换）
def ExchangingPoints(Point_number):
    exchangepoint=[]
    exnumber=Point_number//2
    for i in range(0, exnumber, 2):
        exchangepoint.append([i, i + exnumber])
    return exchangepoint
#开始搜索
def Improve_Search(points_seq, exchange_points):
    points_seq=copy.deepcopy(points_seq)
    P1 = exchange_points[0]
    P2 = exchange_points[1]
    x=points_seq[P1]
    points_seq[P1]=points_seq[P2]
    points_seq[P2]=x
    return points_seq
#将整个点序列切割成可行序列
def routescutting(point_seq, instance):
    num_vehicle = 0                    #定义载具（路线）数量
    whole_lines = []                   #总路径集
    single_line = []                   #单路径
    rest_load = instance.maxLoad       #剩余载货量
    for point_no in point_seq:
        if rest_load - instance.point_list[point_no].demand >= 0:
            single_line.append(point_no)
            rest_load = rest_load - instance.point_list[point_no].demand
        else:
            whole_lines.append(single_line)
            single_line = [point_no]           #以point_no该点为新路线起点
            num_vehicle = num_vehicle + 1      #载具加一
            rest_load = instance.maxLoad - instance.point_list[point_no].demand
    whole_lines.append(single_line)
    return num_vehicle,whole_lines             #返回载具数、具体线路
#计算两点距离
def calDistance(line, instance):
    distance=0
    depot=instance.depot
    for i in range(len(line) - 1):
        front_point=instance.point_list[line[i]]
        back_point=instance.point_list[line[i + 1]]
        distance+=round(math.sqrt((front_point.x - back_point.x) ** 2 + (front_point.y - back_point.y) ** 2),3)
    inception=instance.point_list[line[0]]
    destination=instance.point_list[line[-1]]
    distance+=round(math.sqrt((depot.x - inception.x) ** 2 + (depot.y - inception.y) ** 2),3)
    distance+=round(math.sqrt((depot.x - destination.x) ** 2 + (depot.y - destination.y) ** 2),3)
    return distance
#发车成本＋行驶距离（100*车数+总距离）
def calCost(points_seq, model):
    num_vehicle, vehicle_routes = routescutting(points_seq, model)
    distance=0
    for route in vehicle_routes:
        distance+=calDistance(route,model)
        return (distance+100*num_vehicle),vehicle_routes
#读取instance的各点信息（id与坐标与数量）
def import_data(filepath, instance):
    point_id = -1
    df = pd.read_excel(filepath)
    for i in range(df.shape[0]):
        point=Point()
        point.array=point_id
        point.x= df['X坐标'][i]
        point.y= df['Y坐标'][i]
        point.demand=df['需求量'][i]
        if df['需求量'][i] == 0:
            instance.depot=point
        else:
            instance.point_list.append(point)
            instance.point_order.append(point_id)
        point_id= point_id + 1
    instance.pointamount=len(instance.point_list)
def SA(filepath, tem_threshold, max_load):
    model=Instance()
    model.maxLoad=max_load
    import_data(filepath, model)
    exchangelist=ExchangingPoints(model.pointamount)
    method_cur=Method()
    method_cur.pointarray=OriginalPointsSequence(model.point_order)   #生成初始序列
    method_cur.value, method_cur.routes=calCost(method_cur.pointarray, model) #切割，形成初始可行方案
    model.best_method=copy.deepcopy(method_cur)                       #定义最佳方案
    T0=method_cur.value                                               #初始温度即初始目标值
    current_temper=T0                                                 #当前温度
    expattern=len(exchangelist)  #搜索改进种类数量
    print("初始温度：%s，初始解:%s" % (current_temper, method_cur.value ))
    while current_temper>=tem_threshold:
        for i in range(expattern):
            method_new = Method()
            method_new.pointarray = Improve_Search(method_cur.pointarray, exchangelist[i])
            method_new.value, method_new.routes = calCost(method_new.pointarray, model)
            value_dif= method_new.value - method_cur.value                         #计算（Zn-Zc）
            if value_dif<0 or math.exp(-value_dif/current_temper)>random.random(): #两种情况采用新方案
                method_cur=copy.deepcopy(method_new)                               #确定value(current)
            if method_cur.value<model.best_method.value:
                model.best_method=copy.deepcopy(method_cur)                        #确定value(best)
            current_temper=round(current_temper*0.90,6)                                          #更新温度
            print("当前温度：%s，当前解:%s最优解: %s" % (current_temper, method_cur.value, model.best_method.value))
    print("最佳路径是：")
    for line in model.best_method.routes:
        print("0-",end="")
        for i in line:
            print(f"{i+1}-", end='')
        print("0",end="\n")
    print(f"最佳距离行驶成本与固定成本之和是：{model.best_method.value}")

if __name__=='__main__':
    datapath="./homework2.xlsx"
    SA(filepath=datapath, tem_threshold=0.001, max_load=250)