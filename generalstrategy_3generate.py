import copy
import datetime
from scipy.optimize import minimize

from generalstrategy_2readdata import relationship

from generalstrategy_2readdata import conversion_rate
from generalstrategy_2readdata import loss_rate
from generalstrategy_2readdata import relationship_list

from generalstrategy_2readdata import storage_release_list

from generalstrategy_2readdata import storage_step
from generalstrategy_2readdata import df_device
from generalstrategy_2readdata import df_relationship
from generalstrategy_2readdata import electricity_price
from generalstrategy_2readdata import electricity_time
from generalstrategy_2readdata import working_time
from generalstrategy_2readdata import route_power
from generalstrategy_2readdata import n
from generalstrategy_2readdata import offwork_time

from generalstrategy_1predict import Y_all
from generalstrategy_1predict import Y_before_8


#总能量
#Y_all=1800
#下班时间
#offwork_time = 17
#offwork_time=float(offwork_time)
#n点前需要达到指定能量
#n=8
#n点前需要达到指定能量大小
Y_before_n_oclock=Y_before_8


#中午分段
noon=12


print("开始传参")
print(electricity_price)
print(electricity_time)

########electricity_price和electricity_time进行处理########


def multiply_matrix(c, t):
    result = 0
    for i in range(len(c)):
        result = result + c[i] * t[i]
    return result

'''
for i in range(len(relationship_origin_1)):
    for j in range(len(electricity_price) + 1):
        relationship_origin_1[i].append([j + i * (len(electricity_price) + 1)])


power = []
for i in range(len(relationship_origin_1)):
    power.append(relationship_origin_1[i][-1])
    del (relationship_origin_1[i][0])

print("----------relationship_origin_1[-1][-1][0]----------")
print(relationship_origin_1)
print(relationship_origin_1[-1][-1][0])

ini_len=relationship_origin_1[-1][-1][0]+1


ini=np.zeros(ini_len)

ini[0] = 6  #1
ini[1] = 1  #2
ini[2] = 3  #3
ini[3] = 6  #4
ini[4] = 6  #5
ini[5] = 180  #power


ini[6] = 5  # 23：00-8:00
ini[7] = 0  # 07：00-8:00
ini[8] = 0  # 08：00-11:00
ini[9] = 0  # 11：00-17:00
ini[10] = 0  # 17：00-23:00
ini[11] = 180  # power


ini[12] = 6  # 7：00-8:00主机直供冷
ini[13] = 1  # 8：00-11:00主机直供冷
ini[14] = 3  # 11：00-17:00主机直供冷
ini[15] = 6  # 11：00-17:00主机直供冷
ini[16] = 6  # 21:00-7:00主机直供冷
ini[17] = 180  # 21:00-7:00主机直供冷

ini[18] = 6  # 7：00-8:00主机直供冷
ini[19] = 1  # 8：00-11:00主机直供冷
ini[20] = 3  # 11：00-17:00主机直供冷
ini[21] = 6  # 7：00-8:00主机直供冷
ini[22] = 6  # 8：00-11:00主机直供冷
ini[23] = 180  # 11：00-17:00主机直供冷

ini[24] = 6  # 7：00-8:00主机直供冷
ini[25] = 1  # 8：00-11:00主机直供冷
ini[26] = 3  # 11：00-17:00主机直供冷
ini[27] = 6  # 7：00-8:00主机直供冷
ini[28] = 6  # 8：00-11:00主机直供冷
ini[29] = 180  # 11：00-17:00主机直供冷'''

start_list = []
end_list = []
electricity_all = []
loss_rate_all = []

print("=========start==========")
print(electricity_all)
print(electricity_time)

for i in range(len(electricity_time)):
    electricity_all.append([electricity_time[i], electricity_price[i]])
for i in range(len(loss_rate)):
    loss_rate_all.append([df_relationship['device_from'][i], df_relationship['device_to'][i], loss_rate[i][1]])

print("loss_rate")
print(loss_rate_all)

print("-------------------electricity_all---------------------------")
print(electricity_all)
print("---------------electricity_all processing--------------------")

#######将electrcity_time进行筛选，遍历list中所有值，用n o'clock和offwork_time去卡#######

def bubble_sort_electricity_table_by_starttime(electricity_table):
    #冒泡排序法，以electricity_table[i][0][0]为key来排序

    for i in range(len(electricity_table)):
        for j in range(1, len(electricity_table) - i):
            if electricity_table[j - 1][0][0] > electricity_table[j][0][0]:
                electricity_table[j - 1], electricity_table[j] = electricity_table[j], electricity_table[j - 1]

    return electricity_table

def resort_electricity_table_by_offworktime(electricity_table,offwork_time):
    '''
    将电价时间和电价价格组成的新的list:electricity_all按照下班时间重新分割
    :param electricity_table:
    :param offwork_time:
    :return:
    '''
    #input=[[[23.0, 7.0], 0.4338], [[7.0, 8.0], 0.6778], [[8.0, 11.0], 0.9888], [[11.0, 17.0], 0.6778], [[17.0, 23.0], 0.9888]]
    #outpu=[[[15.0, 17.0], 0.6778], [[23.0, 7.0], 0.4338], [[7.0, 8.0], 0.6778], [[8.0, 11.0], 0.9888], [[17.0, 23.0], 0.9888], [[11.0, 15.0], 0.6778]]
    for i in range(len(electricity_table)):
        if electricity_table[i][0][0] == offwork_time and electricity_table[i][0][1] > offwork_time:
            start_list = electricity_table[i]
            electricity_table.insert(0, start_list)
            del electricity_table[i+1]

        elif electricity_table[i][0][0] < offwork_time and electricity_table[i][0][1] > offwork_time:
            end_list = [[electricity_table[i][0][0], offwork_time], electricity_table[i][1]]
            start_list = [[offwork_time, electricity_table[i][0][1]], electricity_table[i][1]]
            del electricity_table[i]
            electricity_table.append(end_list)
            electricity_table.insert(0, start_list)

        else:
            electricity_table=electricity_table

    # 将电价时间和电价价格组成的新的list:electricity_all按照下班时间重新分段
    # 假设下班时间为15点
    # output as following:
    # electricity1 = [[[15.0, 17.0], 0.6778], [[17.0, 23.0], 0.9888], [[23.0, 7.0], 0.4338]]
    # electricity2 = [[[7.0, 8.0], 0.6778], [[8.0, 11.0], 0.9888], [[11.0, 15.0], 0.6778]]
    electricity_1=[]
    electricity_2=[]
    for i in range(len(electricity_table)):
        if electricity_table[i][0][0]>=offwork_time:
            electricity_1.append(electricity_table[i])
        else:
            electricity_2.append(electricity_table[i])

    #分别对两组时间段从小到大排序
    electricity_1 = bubble_sort_electricity_table_by_starttime(electricity_1)
    electricity_2 = bubble_sort_electricity_table_by_starttime(electricity_2)

    electricity_table=electricity_1+electricity_2

    return electricity_table

def resort_electricity_table_by_n_oclock(n, electricity_table):
    # 如果需要计算n点前能量需求，需要将时间段用n分段
    # input=[[],[],[]]
    # output=[[],[],[]]/[[],[],[],[]]


    for i in range(len(electricity_table)):
        # n==某个时间段的结束时间，break
        # n>开始时间 and n<结束时间
        if n == electricity_table[i][0][1]:
            break

        elif n > electricity_table[i][0][0] and n < electricity_table[i][0][1]:
            origin_start = electricity_table[i][0][0]
            origin_end = electricity_table[i][0][1]
            origin_price = electricity_table[i][1]

            electricity_table.insert(i, [[origin_start, n], origin_price])
            electricity_table.insert(i + 1, [[n, origin_end], origin_price])
            del (electricity_table[i+2])
            break
        else:
            electricity_table=electricity_table

    index=0
    for i in range(len(electricity_table)):
        if electricity_table[i][0][0] <= n and electricity_table[i][0][1]>n:
            #print("n点在electricity table哪个时间段里")
            #print(electricity_table[i])
            index=i

    before_n_electricity_table = []
    after_n_electricity_table=[]
    for i in range(len(electricity_table)):
        if i<index:
            before_n_electricity_table.append(electricity_table[i])
        else:
            after_n_electricity_table.append(electricity_table[i])


    #print(before_n_electricity_table)

    return electricity_table,before_n_electricity_table,after_n_electricity_table

def distribute_electricity_table_to_am_and_pm(noon, electricity_table):
    # 如果需要计算n点前能量需求，需要将时间段用n分段
    # input=[[],[],[]]
    # output=[[],[],[]]/[[],[],[],[]]


    for i in range(len(electricity_table)):
        # n==某个时间段的结束时间，break
        # n>开始时间 and n<结束时间
        if noon == electricity_table[i][0][1]:
            break

        elif noon > electricity_table[i][0][0] and noon < electricity_table[i][0][1]:
            origin_start = electricity_table[i][0][0]
            origin_end = electricity_table[i][0][1]
            origin_price = electricity_table[i][1]

            electricity_table.insert(i, [[origin_start, noon], origin_price])
            electricity_table.insert(i + 1, [[noon, origin_end], origin_price])
            del (electricity_table[i+2])
            break
        else:
            electricity_table=electricity_table

    index=0
    for i in range(len(electricity_table)):
        if electricity_table[i][0][0] <= noon and electricity_table[i][0][1]>noon:
            #print("n点在electricity table哪个时间段里")
            #print(electricity_table[i])
            index=i

    before_noon_electricity_table = []
    after_noon_electricity_table = []
    for i in range(len(electricity_table)):
        if i<index:
            before_noon_electricity_table.append(electricity_table[i])
        else:
            after_noon_electricity_table.append(electricity_table[i])

    print(before_noon_electricity_table)

    return electricity_table,before_noon_electricity_table,after_noon_electricity_table

def delet_offwork_electricity_table(electricity_table):
    #将>下班时间的时间段删除
    #如果
    for i in range(len(electricity_table)):
        if i >= len(electricity_table):
            break
        else:
            if electricity_table[i][0][0] >= offwork_time and electricity_table[i][0][1] >= offwork_time:
                del (electricity_table[i])

    return electricity_table

electricity_all=resort_electricity_table_by_offworktime(electricity_all,offwork_time)

print("resort_electricity_table_by_offworktime")
print(electricity_all)

#electricity_all=delet_offwork_electricity_table(electricity_all)

electricity_all,electricity_before_n,electricity_after_n=resort_electricity_table_by_n_oclock(float(n), electricity_all)
print("resort_electricity_table_by_ntime")
print(electricity_all)
print(electricity_before_n)
print(electricity_after_n)

#-----------------------------------#
electricity_price = []
electricity_time = []

electricity_price_before_n = []
electricity_time_before_n = []

electricity_price_after_n = []
electricity_time_after_n = []

for i in range(len(electricity_all)):
    electricity_price.append(electricity_all[i][1])
    electricity_time.append(electricity_all[i][0])
    
for i in range(len(electricity_before_n)):
    electricity_price_before_n.append(electricity_before_n[i][1])
    electricity_time_before_n.append(electricity_before_n[i][0])

for i in range(len(electricity_after_n)):
    electricity_price_after_n.append(electricity_after_n[i][1])
    electricity_time_after_n.append(electricity_after_n[i][0])

print("===============final electricity related===================")
print(electricity_time)
print(electricity_price)

print(electricity_time_before_n)
print(electricity_price_before_n)

print(electricity_time_after_n)
print(electricity_price_after_n)

print("再分层")


electricity_after_n,electricity_am,electricity_pm=resort_electricity_table_by_n_oclock(float(11), electricity_after_n)

print(electricity_after_n)
print(electricity_am)
print(electricity_pm)

electricity_price_am = []
electricity_time_am = []

electricity_price_pm = []
electricity_time_pm = []

for i in range(len(electricity_am)):
    electricity_price_am.append(electricity_am[i][1])
    electricity_time_am.append(electricity_am[i][0])

for i in range(len(electricity_pm)):
    electricity_price_pm.append(electricity_pm[i][1])
    electricity_time_pm.append(electricity_pm[i][0])

print(electricity_time_am)
print(electricity_price_am)

print(electricity_time_pm)
print(electricity_price_pm)

electricity_time_am_i=[]
for i in electricity_time_am:
    for j in i:
        electricity_time_am_i.append(j)
print(electricity_time_am_i)

electricity_time_pm_i=[]
for i in electricity_time_pm:
    for j in i:
        electricity_time_pm_i.append(j)
print(electricity_time_pm_i)



print("===========================================================")



'''for i in range(len(electricity_time)):
    if electricity_time[i][0]==offwork_time and electricity_time[i][1]>offwork_time:
        start_list=electricity_time[i]
        electricity_time.insert(0, start_list)
        del electricity_time[-1]
    if electricity_time[i][0]<offwork_time and electricity_time[i][1]>offwork_time:
        end_list = [electricity_time[i][0],offwork_time]
        start_list = [offwork_time,electricity_time[i][1]]
        del electricity_time[-1]
        electricity_time.insert(0, start_list)
        electricity_time.append(end_list)'''


electricity = [None] * len(working_time)


print("working time is", working_time)

for i in range(len(working_time)):
    electricity[i] = str(working_time[i][1]).split('-')
    electricity[i].insert(0, working_time[i][0])

print("+++++++++++++++++++++")
print(electricity)


def sort_list(list, i):
    def takeSecond(elem):
        return elem[i]

    # 指定第二个元素排序
    list.sort(key=takeSecond)

    return list


for i in range(len(electricity)):
    electricity[i][1] = int(electricity[i][1])
    electricity[i][2] = int(electricity[i][2])

print("electricity",electricity)

electricity = sort_list(electricity, 0)

print("+++++++++++++++++++++")
print(electricity)

# print("electricity",electricity)

print("中间量111111",electricity_time)
for i in range(len(electricity_time)):
    if electricity_time[i][0] > electricity_time[i][1]:
        electricity_time[i][0] = electricity_time[i][0] - 24

print("electricity_time", electricity_time)

w, h = len(electricity_time), len(electricity)
ini = [[0] * w for i in range(h)]

print(ini)

print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
print("electricity", electricity)

print("sunsunsunshilv")
print(loss_rate)


def objective_cost_effective(x):
    relationship_objective = copy.deepcopy(relationship)
    # print("---------------objective----------------")

    # print(x)
    for i in range(len(relationship_objective)):
        for j in range(len(electricity_price) + 1):
            relationship_objective[i].append(x[j + i * (len(electricity_price) + 1)])

    # ['relationship_0', x[0], x[1], x[2], x[3], x[4], x[5]]
    # ['relationship_1', x[6], x[7], x[8], x[9], x[10], x[11]]
    # print("1.objective")
    # print(relationship_objective)
    # print(len(relationship_objective))

    power = []
    for i in range(len(relationship_objective)):
        power.append(relationship_objective[i][-1])
        del (relationship_objective[i][0])
        del (relationship_objective[i][-1])
    # print("objective relationship~~~~~")
    # print(relationship_objective)
    cost_list = []
    for i in range(len(relationship_objective)):
        # print("objective~~~~~~")
        # print(electricity_price)
        # print(relationship_objective)
        # print(power)
        # print(efficiency_rate)

        ccc = multiply_matrix(electricity_price, relationship_objective[i]) * power[i] / conversion_rate[i][1]*(1+loss_rate_all[i][2])

        cost_list.append(ccc)

    sum = 0
    for i in range(len(cost_list)):
        sum = sum + cost_list[i]

    '''print("-----------------------------------------")
    print(cost_list)
    print("-----------------------------------------")'''

    return sum

def objective_power_effective(x):
    relationship_objective = copy.deepcopy(relationship)
    # print("---------------objective----------------")

    # print(x)
    for i in range(len(relationship_objective)):
        for j in range(len(electricity_price) + 1):
            relationship_objective[i].append(x[j + i * (len(electricity_price) + 1)])

    power = []
    for i in range(len(relationship_objective)):
        power.append(relationship_objective[i][-1])
        del (relationship_objective[i][0])
        del (relationship_objective[i][-1])

    # print("ro is",relationship_objective)
    # print("power is",power)
    sum = 0
    for i in range(len(relationship_objective)):
        for j in range(len(electricity_time)):
            sum = sum + int(relationship_objective[i][j]) * (1 - float(loss_rate[i][1])) * int(power[i]) / \
                  conversion_rate[i][1]

    return sum


# 所有设备供的能量>=Y_all(√)
def constraint1(x):
    #print("----------constraints1 start---------------")

    relationship_constraint1 = copy.deepcopy(relationship)
    for i in range(len(relationship_constraint1)):
        for j in range(len(electricity_price) + 1):

            relationship_constraint1[i].append(x[j + i * (len(electricity_price) + 1)])

    #print(relationship_constraint1)

    power = []
    for i in range(len(relationship_constraint1)):
        power.append(relationship_constraint1[i][-1])
        del (relationship_constraint1[i][0])

    release = 0
    storage=0

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == \
                    storage_release_list[n][1][1]:
                release = relationship_list[m]
            if relationship_list[m][1] == storage_release_list[n][0][0] and relationship_list[m][2] == \
                    storage_release_list[n][0][1]:
                storage = relationship_list[m]

    index_release = relationship_list.index(release)
    index_storage = relationship_list.index(storage)

    if relationship_constraint1 != []:
        del (relationship_constraint1[index_storage])
        #del (relationship_constraint1[index_release])
    sum = 0

    # print(relationship_constraint1)

    for i in range(len(relationship_constraint1)):
        for j in range(len(electricity_price)):

            ''' 
            print(relationship_constraint1)
            print(relationship_constraint1[i][j])
            print(relationship_constraint1[i][-1])
            '''
            sum = sum + relationship_constraint1[i][j] * relationship_constraint1[i][-1]


    return sum - Y_all


# 能量守恒限定:储能=放能(√)
def constraint2(x):
    relationship_constraint2 = copy.deepcopy(relationship)
    for i in range(len(relationship_constraint2)):
        for j in range(len(electricity_price) + 1):
            relationship_constraint2[i].append(x[j + i * (len(electricity_price) + 1)])
    # print("constraints2~~~~")
    # print(relationship_constraint2)

    for i in range(len(relationship_constraint2)):
        del (relationship_constraint2[i][0])
    # print(relationship_constraint2)

    storage = []
    release = []

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][0][0] and relationship_list[m][2] == \
                    storage_release_list[n][0][1]:
                storage = relationship_list[m]
                # storage.append(relationship_list[m])
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == \
                    storage_release_list[n][1][1]:
                # release.append(relationship_list[m])
                release = relationship_list[m]
    '''print("储能")
    print(storage)
    print("放能")
    print(release)
    print("enddddd")'''
    index_storage = relationship_list.index(storage)
    index_release = relationship_list.index(release)

    # print(relationship_list[index_storage])
    # print(relationship_list[index_release])

    sum_storage = 0
    sum_release = 0

    for i in range(len(relationship_constraint2[index_storage]) - 1):
        # print(relationship_constraint2[index_storage])
        # print("-------------")
        # print(relationship_constraint2[index_storage][-1])
        # print(i)

        sum_storage = relationship_constraint2[index_storage][i] * relationship_constraint2[index_storage][-1] + sum_storage

    for i in range(len(relationship_constraint2[index_release]) - 1):
        # print("yoyoyoyo")
        # print(relationship_constraint2[index_storage][-1])
        # print(i)

        sum_release = relationship_constraint2[index_release][i] * relationship_constraint2[index_release][-1] + sum_release


    #return sum_storage*0.9 - sum_release
    return sum_storage- sum_release/(1-loss_rate[index_release][1])


# 蓄能量上限(√)
def constraint3(x):
    relationship_constraint3 = copy.deepcopy(relationship)

    storage_device = ""
    storage_limitation = 0
    storage_relationship = str(storage_step[0]) + "to" + str(storage_step[1])
    storage_index = 0

    for i in range(len(relationship_constraint3)):
        if storage_relationship in relationship_constraint3[i][0]:
            storage_device = storage_step[1]
            storage_index = i
    for i in range(len(df_device)):

        if str(df_device['device_id'][i]) == str(storage_device):
            storage_limitation = int(df_device['cap'][i])

    #print("蓄能能量总上限")
    #print(storage_limitation)

    for i in range(len(relationship_constraint3)):
        for j in range(len(electricity_price) + 1):
            relationship_constraint3[i].append(x[j + i * (len(electricity_price) + 1)])

    for i in range(len(relationship_constraint3)):
        del (relationship_constraint3[i][0])

    # print("relationship_constraint3")
    # print(relationship_constraint3[storage_index])
    storage_limitation_sum = 0

    for i in range(len(electricity_time)):
        storage_limitation_sum = storage_limitation_sum + relationship_constraint3[storage_index][i] * \
                                 relationship_constraint3[storage_index][-1]

    return storage_limitation - storage_limitation_sum


# 所有设备不能同时供能(√)
def constraint4(x):

    relationship_constraint4 = copy.deepcopy(relationship)

    for i in range(len(relationship_constraint4)):
        for j in range(len(electricity_price) + 1):
            relationship_constraint4[i].append(x[j + i * (len(electricity_price) + 1)])
    #print(relationship_constraint4)

    for i in range(len(relationship_constraint4)):
        del (relationship_constraint4[i][0])
        del (relationship_constraint4[i][-1])
    #print(relationship_constraint4)

    '''sum=[]
    for i in range(len(electricity_time)):
        sum.append([])
    print(sum)'''
    #sum = [[], [], [], [], []]

    '''for m in range(len(relationship_constraint4)):
        for n in range(len(electricity_time)):
            sum[n].append(relationship_constraint4[m][n])
    print(sum)'''

    sum_seperate =[]
    for i in range(len(electricity_time)):
        sum_seperate.append(0)
    #sum_seperate = [0, 0, 0, 0, 0]

    for i in range(len(electricity_time)):
        for j in range(len(relationship_constraint4)):
            sum_seperate[i] = sum_seperate[i] + relationship_constraint4[j][i]

    #print(sum_seperate)
    list = ()
    for i in range(len(sum_seperate)):

        list = list + (abs(int(electricity_time[i][1]) - int(electricity_time[i][0])) - sum_seperate[i],)

        #print("lllllist",list)
    # return abs(int(electricity_time[0][1])-int(electricity_time[0][0]))-sum_seperate[0],abs(int(electricity_time[1][1])-int(electricity_time[1][0]))-sum_seperate[1],abs(int(electricity_time[2][1])-int(electricity_time[2][0]))-sum_seperate[2],abs(int(electricity_time[3][1])-int(electricity_time[3][0]))-sum_seperate[3],abs(int(electricity_time[4][1])-int(electricity_time[4][0]))-sum_seperate[4]
    return list


#n点前需要的能量(√)
def constraint5(x):

    relationship_constraint5 = copy.deepcopy(relationship)
    #print(relationship_constraint5)
    #print(electricity_price)
    #print(electricity_price_before_n)
    for i in range(len(relationship_constraint5)):
        for j in range(len(electricity_price)+1):
            if j<len(electricity_price_before_n):
                relationship_constraint5[i].append(x[j + i * (len(electricity_price)+1)])
            elif j>=len(electricity_price_before_n) and j<len(electricity_price):
                relationship_constraint5[i].append(0.0)
            else:
                relationship_constraint5[i].append(x[j + (len(electricity_price)+1)])
    #print("con5")
    #print(relationship_constraint5)

    power = []
    for i in range(len(relationship_constraint5)):
        power.append(relationship_constraint5[i][-1])
        del (relationship_constraint5[i][0])

    release = 0
    storage=0

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == storage_release_list[n][1][1]:
                release = relationship_list[m]

            if relationship_list[m][1] == storage_release_list[n][0][0] and relationship_list[m][2] == storage_release_list[n][0][1]:
                storage = relationship_list[m]

    index_storage = relationship_list.index(storage)


    #删除relationship_constraint中蓄能部分
    #relationship_constraint=[主机直供,水蓄能放]
    if relationship_constraint5 != []:
        del (relationship_constraint5[index_storage])

    sum_before_n_oclock = 0

    for i in range(len(relationship_constraint5)):
        for j in range(len(electricity_price_before_n)):
            ''' 
            print(relationship_constraint1)
            print(relationship_constraint1[i][j])
            print(relationship_constraint1[i][-1])
            '''
            #print(relationship_constraint5[i][j])
            #print(relationship_constraint5[i][-1])
            sum_before_n_oclock = sum_before_n_oclock + relationship_constraint5[i][j] * relationship_constraint5[i][-1]


    return Y_before_n_oclock-sum_before_n_oclock
    #return Y_before_n_oclock - sum_before_n_oclock

#n点后需要的能量(待改,未调用)
def constraint6(x):

    relationship_constraint6 = copy.deepcopy(relationship)
    print(relationship_constraint6)

    for i in range(len(relationship_constraint6)):
        for j in range(len(electricity_price)+1):
            if j<len(electricity_price_before_n):
                #relationship_constraint6[i].append(x[j + i * (len(electricity_price)+1)])
                relationship_constraint6[i].append(0.0)
            elif j>=len(electricity_price_before_n) and j<len(electricity_price):
                #relationship_constraint6[i].append(0.0)
                relationship_constraint6[i].append(x[j + i * (len(electricity_price) + 1)])
            else:
                relationship_constraint6[i].append(x[j + (len(electricity_price)+1)])

    print("yokoyou")
    print(relationship_constraint6)

    power = []
    for i in range(len(relationship_constraint6)):
        power.append(relationship_constraint6[i][-1])
        del (relationship_constraint6[i][0])

    print(relationship_constraint6)

    release = 0

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == storage_release_list[n][1][1]:
                release = relationship_list[m]

    index_release = relationship_list.index(release)

    if relationship_constraint6 != []:
        del (relationship_constraint6[index_release])

    sum_after_n_oclock = 0

    for i in range(len(relationship_constraint6)):
        for j in range(len(electricity_price_before_n)):
            ''' 
            print(relationship_constraint1)
            print(relationship_constraint1[i][j])
            print(relationship_constraint1[i][-1])
            '''
            print(relationship_constraint6[i][j])
            print(relationship_constraint6[i][-1])
            sum_after_n_oclock = sum_after_n_oclock + relationship_constraint6[i][j] * relationship_constraint6[i][-1]

    #return 3000-sum_after_n_oclock
    return Y_before_n_oclock - sum_after_n_oclock

#上午需要的能量(√)
def constraint7(x):

    relationship_constraint7 = copy.deepcopy(relationship)

    for i in range(len(relationship_constraint7)):
        for j in range(len(electricity_price)+1):
            if j<(len(electricity_price_before_n)+len(electricity_price_am)) and j>=len(electricity_price_before_n):
                relationship_constraint7[i].append(x[j + i * (len(electricity_price) + 1)])
            if j==len(electricity_price):
                relationship_constraint7[i].append(x[j + i * (len(electricity_price) + 1)])
            else:
                relationship_constraint7[i].append(0.0)

    power = []
    for i in range(len(relationship_constraint7)):
        power.append(relationship_constraint7[i][-1])
        del (relationship_constraint7[i][0])

    release = 0
    storage=0

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == storage_release_list[n][1][1]:
                release = relationship_list[m]

            if relationship_list[m][1] == storage_release_list[n][0][0] and relationship_list[m][2] == storage_release_list[n][0][1]:
                storage = relationship_list[m]

    index_storage = relationship_list.index(storage)


    #删除relationship_constraint中蓄能部分
    #relationship_constraint=[主机直供,水蓄能放]
    if relationship_constraint7 != []:
        del (relationship_constraint7[index_storage])

    sum_am = 0

    for i in range(len(relationship_constraint7)):
        for j in range(len(electricity_price)):
            ''' 
            print(relationship_constraint1)
            print(relationship_constraint1[i][j])
            print(relationship_constraint1[i][-1])
            '''
            #print(relationship_constraint5[i][j])
            #print(relationship_constraint5[i][-1])
            sum_am = sum_am + relationship_constraint7[i][j] * relationship_constraint7[i][-1]
    #print("oy")

    #print((max(electricity_time_am_i)-min(electricity_time_am_i))/(max(electricity_time_am_i)-min(electricity_time_am_i)+max(electricity_time_pm_i)-min(electricity_time_pm_i)-1))

    #print(len(electricity_price_pm))
    #print((len(electricity_price_am))/(len(electricity_price_am)+len(electricity_price_pm)))

    return sum_am-(Y_all-Y_before_n_oclock)*(max(electricity_time_am_i)-min(electricity_time_am_i))/(max(electricity_time_am_i)-min(electricity_time_am_i)+max(electricity_time_pm_i)-min(electricity_time_pm_i)-1)
    #return sum_am-(Y_all-Y_before_n_oclock)*3/7

#蓄能矩阵里不为0的序号必须小于放能矩阵里不为0的矩阵
def constraint8(x):
    relationship_constraint8 = copy.deepcopy(relationship)
    for i in range(len(relationship_constraint8)):
        for j in range(len(electricity_price) + 1):
            relationship_constraint8[i].append(x[j + i * (len(electricity_price) + 1)])
    # print("constraints2~~~~")
    # print(relationship_constraint2)

    for i in range(len(relationship_constraint8)):
        del (relationship_constraint8[i][0])
    # print(relationship_constraint2)

    storage = []
    release = []

    for m in range(len(relationship_list)):
        for n in range(len(storage_release_list)):
            if relationship_list[m][1] == storage_release_list[n][0][0] and relationship_list[m][2] == \
                    storage_release_list[n][0][1]:
                storage = relationship_list[m]
                # storage.append(relationship_list[m])
            if relationship_list[m][1] == storage_release_list[n][1][0] and relationship_list[m][2] == \
                    storage_release_list[n][1][1]:
                # release.append(relationship_list[m])
                release = relationship_list[m]

    index_storage = relationship_list.index(storage)
    index_release = relationship_list.index(release)


    storage_notzero_index = []
    release_notzero_index = []
    #length-1是因为最后一个元素是power


    for i in range(len(relationship_constraint8[index_storage]) - 1):
        if relationship_constraint8[index_storage][i]!=0:
            storage_notzero_index.append(i)


    for i in range(len(relationship_constraint8[index_release]) - 1):
        if relationship_constraint8[index_release][i]!=0:
            release_notzero_index.append(i)


    while release_notzero_index!=[] and storage_notzero_index!=[]:

        print(min(release_notzero_index)-max(storage_notzero_index))

        return min(release_notzero_index)-max(storage_notzero_index)




    #print("放能index", release_notzero_index,min_release_notzero_index)
    #print("储能index", storage_notzero_index,max_storage_notzero_index)


def generate_inis(ini, electricity, electricity_time):
    for i in range(len(electricity)):
        print(electricity[i])
        if electricity[i][1] != electricity[i][2]:
            # print("qqqqqqqqqqqqqqqqq")
            # print("electricity[i]",electricity[i])

            # example:['103to104', '0', '17'] electricity[i][1]=0 electricity[i][2]=17 0!=17
            for j in range(len(electricity_time)):
                # electricity_time=[[17.0, 23.0], [-1.0, 7.0], [7.0, 8.0], [8.0, 11.0], [11.0, 17.0]]

                if electricity[i][2] <= electricity_time[j][0]:

                    print(electricity[i])
                    print(electricity_time[j])
                    # print("electricity[i][2]",electricity[i][2])
                    # print("electricity_time[j][1]",electricity_time[j][0])
                    # electricity[i][2]=17<electricity_time[i][0]
                    ini[i][j] = 0

                if electricity[i][1] > electricity_time[j][0] and electricity[i][1] < electricity_time[j][1]:
                    print("666666")
                    # electricity[i][2]=17<electricity_time[i][0]
                    ini[i][j] = electricity_time[j][1] - electricity[i][1]
                if electricity[i][1] <= electricity_time[j][0] and electricity[i][2] > electricity_time[j][1]:
                    # electricity[i][1]=0   <=   electricity_time[j][0]=7,8,11
                    # electricity[i][2]=17  >=   electricity_time[j][1]=8,11,17
                    print("777777")
                    print(electricity[i][1],electricity[i][2])
                    print(electricity_time[j][0],electricity_time[j][1])
                    ini[i][j] = electricity_time[j][1] - electricity_time[j][0]
                    print(ini[i][j])

        if electricity[i][1] == electricity[i][2]:


            # example:['106to103', '23', '23'] electricity[i][1]=23 electricity[i][2]=23

            for j in range(len(electricity_time)):
                ini[i][j] = electricity_time[j][1] - electricity_time[j][0]

    return ini

print("中间量~~~~~")
print(electricity)
print(electricity_time)
inis = generate_inis(ini, electricity, electricity_time)
ini = []
for i in range(len(inis)):
    inis[i].append(route_power[i][1])
    for j in range(len(inis[i])):
        ini.append(inis[i][j])

print("-------------generate inis are--------------")
print(inis)
print(ini)

bnds = []

for i in ini:
    bnds.append((0, i))

print(bnds)

#bnds=[(0, 6.0), (0, 7.0), (0, 1.0), (0, 3.0), (0, 6.0), (0, 700.0), (0, 6.0), (0, 7.0), (0, 1.0), (0.0, 3.0), (0.0, 6.0), (0, 700.0), (0, 6.0), (0, 7.0), (0, 1.0), (0.0, 3.0), (0.0, 6.0), (0, 700.0)]
con1 = {'type': 'ineq', 'fun': constraint1}
con2 = {'type': 'eq', 'fun': constraint2}
con3 = {'type': 'ineq', 'fun': constraint3}
con4 = {'type': 'ineq', 'fun': constraint4}
con5 = {'type': 'eq', 'fun': constraint5}
con7 = {'type': 'ineq', 'fun': constraint7}
con8 = {'type': 'ineq', 'fun': constraint8}
cons = ([con1,con2,con3,con4,con5,con7])

#cons = ([con2,con1,con3,con4,con5])

solution = minimize(objective_cost_effective, ini, method='SLSQP', bounds=bnds, constraints=cons)

x = solution.x

new = []
for i in x:
    i = round(i + 0.001, 2)
    new.append(i)

print("new: ",new)
final_x=[]
for i in range(0, len(new), len(electricity_all)+1):
    print([new[i:i + len(electricity_all)+1]])
    final_x.append([new[i:i + len(electricity_all)+1]])

print("final_x: ",final_x)
print(str(objective_cost_effective(x)))

x_with_relation=[]
for i in range(len(relationship)):
    final_x[i].insert(0, relationship[i])


print(final_x)
print(relationship_list)
print("final cost")
print(objective_power_effective(x))
print(electricity_all)
print("relationship is yoyoyo",relationship)



