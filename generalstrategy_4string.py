import copy
import datetime
from scipy.optimize import minimize

from generalstrategy_3generate import electricity_all
from generalstrategy_3generate import final_x
from generalstrategy_3generate import relationship_list
from generalstrategy_2readdata import storage_step
from generalstrategy_2readdata import release_step
from generalstrategy_2readdata import n
from generalstrategy_2readdata import offwork_time
from generalstrategy_2readdata import fixed_relationship
from generalstrategy_2readdata import df_relationship_copy

from generalstrategy_1predict import date


#date="20210309"

print("================node+stratrgy_output======================")
print("================node+stratrgy_output======================")
print("================node+stratrgy_output======================")

print(storage_step)
print(final_x)
print("info")
print(relationship_list)
print(electricity_all)



def generate_dynamic_node_path(final_x, relationship_list):

    fixed_node=[]
    fixed_path=[]

    for i in range(len(fixed_relationship)):
            fixed_node.append(fixed_relationship[i][0])
            fixed_node.append(fixed_relationship[i][1])
            fixed_path.append(str(fixed_relationship[i][0])+"#"+str(fixed_relationship[i][1]))

    print("固定策略node")
    print(fixed_node)
    print("固定策略path")
    print(fixed_path)

    node = []
    path = []

    for i in range(len(final_x)):
        print(final_x[i][0][0])
        print(relationship_list[i][0])
        if final_x[i][0][0]==relationship_list[i][0]:
                if max(final_x[i][1][:-1])!=0:
                    node.append(relationship_list[i][1])
                    node.append(relationship_list[i][2])

                    print(node)
                    path.append(str(relationship_list[i][1])+"#"+str(relationship_list[i][2]))

    node=node+fixed_node
    path=path+fixed_path
    node = list(set(node))

    str_node = ''
    str_path = ''
    for i in node:
        str_node = str_node + str(i) + ','
    str_node = str_node[:-1]

    for i in path:
        str_path = str_path + i + ','

    str_path = str_path[:-1]

    return str_node, str_path

str_node,str_path=generate_dynamic_node_path(final_x,relationship_list)
print("@@@@@@@@@@@@@")
print("node",str_node)
print("path",str_path)

def preparation_data_for_strategy(final_x, relationship_list,electricity_all):
    final_relationship_list=[]
    for i in range(len(relationship_list)):
        if [relationship_list[i][1],relationship_list[i][2]]==storage_step:
            final_relationship_list.append([final_x[i][0],final_x[i][1][:-1],final_x[i][1][-1],
                                            [relationship_list[i][1],relationship_list[i][2]],relationship_list[i][3],
                                            "storage"])
        elif [relationship_list[i][1],relationship_list[i][2]]==release_step:
            final_relationship_list.append([final_x[i][0], final_x[i][1][:-1], final_x[i][1][-1],
                                            [relationship_list[i][1], relationship_list[i][2]], relationship_list[i][3],
                                            "release"])

        else:
            final_relationship_list.append([final_x[i][0], final_x[i][1][:-1], final_x[i][1][-1],
                                            [relationship_list[i][1], relationship_list[i][2]], relationship_list[i][3],
                                            "others"])

    print(final_relationship_list)

    def period_in_workingtime_is_full(electricity_all_i, final_relationship_list):
        each_electricity_sum=[]

        for i in range(len(final_relationship_list)):
                each_electricity_sum.append(final_relationship_list[i][1][electricity_all_i])
        return each_electricity_sum

    device_working_time=[]
    for i in range(len(electricity_all)):
        #print(period_in_workingtime_is_full(i, final_relationship_list))
        device_working_time.append(sum(period_in_workingtime_is_full(i, final_relationship_list)))



    electricity_period=[]
    for i in range(len(electricity_all)):
        electricity_period.append(electricity_all[i][0][1]-electricity_all[i][0][0])



    strategy_add_simple=[]

    for i in range(len(electricity_period)):
        if device_working_time>=strategy_add_simple:
            #策略串单纯相加
            strategy_add_simple.append(1)
        else:
            #是否为最后一个时间段
            if i==len(electricity_period)-1:
                #是，该段时间开头直接加period
                strategy_add_simple.append(1)
            else:
                #否，查看是否在工作时间内

                if electricity_all[i][0][0]>=n and electricity_all[i][0][1]<=offwork_time:
                    #在工作时间内，padding
                    strategy_add_simple.append("padding")
                else:
                    strategy_add_simple.append(1)



    return device_working_time,electricity_period,strategy_add_simple,final_relationship_list


device_working_time,electricity_period,strategy_add_simple,final_relationship_list=preparation_data_for_strategy(final_x, relationship_list,electricity_all)

print(electricity_all)


print("每个时间段内所有设备工作时间总和")
print(device_working_time)
print("每个时间段时间总长")
print(electricity_period)
print("策略总和相加方式")
print(strategy_add_simple)
for i in range(len(final_relationship_list)):
    print(final_relationship_list[i])

def transfer_float_electrcity_all_to_time(electricity_all):
    string_start_time=[]
    string_end_time=[]

    for i in range(len(electricity_all)):
        start_time=electricity_all[i][0][0]
        end_time = electricity_all[i][0][1]
        start_time_int=int(start_time)
        start_time_float=int((start_time-start_time_int)*60)

        end_time_int = int(end_time)
        end_time_float = int((end_time - end_time_int) * 60)
        if start_time<0:
            start_time_int=start_time_int+24

        start_time=start_time_int+start_time_float
        end_time = end_time_int + end_time_float


        start_time_string=str(start_time_int)+":"+str(start_time_float)
        end_time_string = str(end_time_int) + ":" + str(end_time_float)


        start_time_datetime= datetime.datetime.strptime(start_time_string,"%H:%M")
        end_time_datetime = datetime.datetime.strptime(end_time_string, "%H:%M")

        string_start_time.append(start_time)
        string_end_time.append(end_time)

    return string_start_time,string_end_time

string_start_time,string_end_time=transfer_float_electrcity_all_to_time(electricity_all)
print(string_start_time)
print(string_end_time)

print("oyouoyou1111")
print(final_relationship_list)


def deal_with_data(final_relationship_list):
    for i in range(len(final_relationship_list)):
        for j in range(len(electricity_all)):
            if final_relationship_list[i][-1]=='storage' and final_relationship_list[i][1][-1]!=0:
                #当主机在下午蓄能时:将下午蓄能补到提前前面
                final_relationship_list[i][1][0]=final_relationship_list[i][1][-1]
                final_relationship_list[i][1][-1]=0
            #print(type(final_relationship_list[i][1][j]))
            #print(type(device_working_time[i]))
            if final_relationship_list[i][1][j]>0 and final_relationship_list[i][1][j]<0.08*electricity_period[j]:
                #check矩阵里是否有过小的数，如果有且下一个时间段为0，则置为0
                #print("o1o1o1o1o")
                #print(final_relationship_list[i][1][j])
                #print(electricity_period[j])
                if j+1<len(electricity_all):
                    if final_relationship_list[i][1][j+1]==0:
                        final_relationship_list[i][1][j]=float(0)
            ######???????######
            if final_relationship_list[i][1][j]>0.9*electricity_period[j]:
                #check矩阵里是否有约等于整个时间区间的值，如果有且下一个时间段为0，则置为0
                #20210309??为何要做此步？？？
                final_relationship_list[i][1][j]=electricity_period[j]


    return final_relationship_list

final_relationship_list=deal_with_data(final_relationship_list)

print("oyouyouyou22222")
print(final_relationship_list)

def how_many_device_working_in_one_period(electrcity_all_i, final_relationship_list):
    flag = 0
    for j in range(len(final_relationship_list)):

        if final_relationship_list[j][1][electrcity_all_i] != 0:
            flag = flag + 1

    return flag


flag_one_device_working_in_one_period = []

for i in range(len(electricity_all)):
    flag = how_many_device_working_in_one_period(i, final_relationship_list)
    flag_one_device_working_in_one_period.append(flag)

print("how many devices work in one period?")
print(flag_one_device_working_in_one_period)

for i in range(len(final_relationship_list)):
    print((final_relationship_list[i]))

def generate_string(final_relationship_list,electricity_all):
    strategy_output=[]
    strategy_output_1device=[]
    strategy_output_morethan1device=[]

    predict_date = datetime.datetime.strptime(date, "%Y%m%d")
    zeroToday = predict_date - datetime.timedelta(hours=predict_date.hour, minutes=predict_date.minute, seconds=predict_date.second,
                                           microseconds=predict_date.microsecond)

    def generate_clock(start_hour,start_mins,end_hour):
        if start_hour<=offwork_time and end_hour<=offwork_time:
            clock_start=zeroToday + datetime.timedelta(hours=start_hour, minutes=start_mins, seconds=0)

        else:
            clock_start = zeroToday - datetime.timedelta(days=1) + datetime.timedelta(hours=start_hour, minutes=start_mins, seconds=0)
        hour_clock_start = clock_start.strftime('%H:%M')

        return clock_start,hour_clock_start

    def generate_clockend_by_clockstart(clock_start,period_hour,period_mins):
        clock_end=clock_start + datetime.timedelta(hours=period_hour, minutes=period_mins, seconds=0)
        hour_clock_end=clock_end.strftime('%H:%M')

        return clock_end,hour_clock_end

    def generate_clockstart_by_clockend(clock_end,period_hour,period_mins):
        clock_start=clock_end - datetime.timedelta(hours=period_hour, minutes=period_mins, seconds=0)
        hour_clock_start=clock_start.strftime('%H:%M')

        return clock_start,hour_clock_start

    def generate_clock_for_electrical_all(electricity_all):
        #将所有的时间段的开始和结束都转成clock_start/clock_end和 hour_clock_start/hour_clock_end

        for i in range(len(electricity_all)):
            #判断某一个时间段是在predict_date的前一天还是predict_date当天本天
            #check 开始时间<0且结束时间>0
            for j in range(len(electricity_all[i][0])):
                if electricity_all[i][0][j]<=0:
                    electricity_all[i][0][j]=electricity_all[i][0][j]+24

        #print(electricity_all)
        clock=[]
        hour_clock=[]
        for i in range(len(electricity_all)):
            # 将所有的时间段的开始和结束都转成clock_start/clock_end和 hour_clock_start/hour_clock_end
                start_hour=int(electricity_all[i][0][0])
                start_mins=int((electricity_all[i][0][0] - int(electricity_all[i][0][0]))*60)
                end_hour = int(electricity_all[i][0][1])
                end_mins = int((electricity_all[i][0][1] - int(electricity_all[i][0][1])) * 60)
                clock_start,hour_clock_start=generate_clock(start_hour,start_mins,end_hour)
                clock_end, hour_clock_end = generate_clock(end_hour, end_mins,end_hour)

                clock.append([clock_start,clock_end])
                hour_clock.append([hour_clock_start, hour_clock_end])

        return clock,hour_clock

    #clock对应的是电价时间段的起点/终点
    #clock_start,clock_end对应的设备的工作起点/终点
    clock,hour_clock=generate_clock_for_electrical_all(electricity_all)


    for i in range(len(final_relationship_list)):
        for j in range(len(electricity_all)):
            if flag_one_device_working_in_one_period[j]==0:
                #该时间段内无设备工作
                strategy_output=strategy_output

            if flag_one_device_working_in_one_period[j]==1:
                #该时间段内仅有一种设备工作
                #判断是否要和下一个时间段前后连接
                #如果j+1 ！=0，说明下一段时间该设备也在工作，那么j从尾端开始减
                if final_relationship_list[i][1][j] != 0:

                    if j+1<len(electricity_all):
                        #除了最后一个时间段的所有时间段
                        #该句已经默认j+1存在

                        if final_relationship_list[i][1][j]!=0 and final_relationship_list[i][1][j+1]==0:
                            #print(final_relationship_list[i][1])
                            #print(final_relationship_list[i][1][j])
                            #print(final_relationship_list[i][1][j + 1])

                            #该段时间内仅有一种设备工作，且下一段时间内该设备不工作
                            # j!=0 j+1!=0 那么 j的end time=start time + period
                            period_hour=int(final_relationship_list[i][1][j])
                            #print('period_hour',period_hour)
                            period_mins=int((final_relationship_list[i][1][j]-period_hour)*60)
                            #print("period_mins",period_mins)
                            clock_end, hour_clock_end=generate_clockend_by_clockstart(clock[j][0],period_hour,period_mins)

                            strategy_output_1device.append([final_relationship_list[i][2], hour_clock[j][0] + "~" + hour_clock_end+ " "+str(final_relationship_list[i][4]), clock[j][0], clock_end,final_relationship_list[i][2]])


                        if final_relationship_list[i][1][j]!=0 and final_relationship_list[i][1][j+1]!=0:
                            #j!=0 j+1!=0 那么 j的start time=end time - period

                            #该段时间内仅有一种设备工作，且下一段时间内该设备工作
                            period_hour=int(final_relationship_list[i][1][j])
                            #print('period_hour',period_hour)
                            period_mins=int((final_relationship_list[i][1][j]-period_hour)*60)
                            #print(final_relationship_list[i][1][j])
                            #print(period_hour)
                            #print("period_mins",period_mins)
                            clock_start, hour_clock_start=generate_clockstart_by_clockend(clock[j][1],period_hour,period_mins)

                            #clock_start,hour_clock_start=generate_clock_start(hour_clock,start_mins)
                            strategy_output_1device.append([final_relationship_list[i][3], hour_clock_start + "~" + hour_clock[j][1] + " "+str(final_relationship_list[i][4]),clock_start,clock[j][1],final_relationship_list[i][2]])

                    else:
                        #最后一个时间段的处理
                        period_hour = int(final_relationship_list[i][1][j])
                        # print('period_hour',period_hour)
                        period_mins = int((final_relationship_list[i][1][j] - period_hour) * 60)
                            # print("period_mins",period_mins)
                        clock_end, hour_clock_end = generate_clockend_by_clockstart(clock[j][0], period_hour, period_mins)

                        strategy_output_1device.append(
                            [final_relationship_list[i][3], hour_clock[j][0] + "~" + hour_clock_end + " " + str(final_relationship_list[i][4]),
                            clock[j][0], clock_end,final_relationship_list[i][2]])



            if flag_one_device_working_in_one_period[j] >=2:

                #该段时间有两种及以上设备工作

                #不存在[在时间段j中，ab串联工作，在时间段j+1中，ab继续串联工作],因为
                #存在[在时间段j中，ab并联工作，在时间段j+1中，ab继续并联工作]
                #只要a[i]+b[j]>time[j]，就说明改段时间仅一个设备工作提供不了所需要的能量
                #只要a[i]+b[j]>time[j](当矩阵工作正常没有溢出时）,就说明该段时间内两个设备可以共同使用，这时两个设备并联

                # 先判断多个设备是如何链接的
                if final_relationship_list[i][1][j] != 0:

                    if device_working_time[j]<=electricity_period[j]*1.2:
                        #print("多个设备串联")
                        #多个设备串联
                        #时间上：水蓄能>水放能,其它设备
                        if final_relationship_list[i][-1]=='storage':
                            period_hour = int(final_relationship_list[i][1][j])
                            # print('period_hour',period_hour)
                            period_mins = int((final_relationship_list[i][1][j] - period_hour) * 60)
                            # print("period_mins",period_mins)
                            clock_end, hour_clock_end = generate_clockend_by_clockstart(clock[j][0], period_hour,period_mins)
                            strategy_output_morethan1device.append([final_relationship_list[i][3], hour_clock[j][0] + "~" + hour_clock_end + " " + str(final_relationship_list[i][4]),
                                clock[j][0], clock_end,final_relationship_list[i][2]])
                            #print("strategy_output_morethan1device，蓄能")
                            #print(strategy_output_morethan1device)

                        else:
                            if strategy_output_morethan1device!=[]:

                                clock_start=strategy_output_morethan1device[-1][-2]
                                hour_clock_start=clock_start.strftime('%H:%M')

                                period_hour = int(final_relationship_list[i][1][j])
                                # print('period_hour',period_hour)
                                period_mins = int((final_relationship_list[i][1][j] - period_hour) * 60)
                                # print("period_mins",period_mins)

                                clock_end, hour_clock_end = generate_clockend_by_clockstart(clock_start, period_hour,period_mins)

                                strategy_output_morethan1device.append([final_relationship_list[i][3], hour_clock_start + "~" + hour_clock_end + " " + str(final_relationship_list[i][4]),
                                clock_start, clock_end,final_relationship_list[i][2]])
                                #print("if")
                                #print(strategy_output_morethan1device)

                            if strategy_output_morethan1device == []:
                                period_hour = int(final_relationship_list[i][1][j])
                                # print('period_hour',period_hour)
                                period_mins = int((final_relationship_list[i][1][j] - period_hour) * 60)
                                # print("period_mins",period_mins)
                                clock_end, hour_clock_end = generate_clockend_by_clockstart(clock[j][0], period_hour,
                                                                                        period_mins)
                                strategy_output_morethan1device.append(
                                [final_relationship_list[i][3], hour_clock[j][0] + "~" + hour_clock_end + " " + str(final_relationship_list[i][4]),
                                 clock[j][0], clock_end,final_relationship_list[i][2]])

                                #print("else")
                                #print(strategy_output_morethan1device)

                    else:
                        print("多个设备并联")
                    #所有设备的开始时间都是从电价起始时间开始往后加的

                        period_hour = int(final_relationship_list[i][1][j])
                        # print('period_hour',period_hour)
                        period_mins = int((final_relationship_list[i][1][j] - period_hour) * 60)
                        # print("period_mins",period_mins)
                        clock_end, hour_clock_end = generate_clockend_by_clockstart(clock[j][0], period_hour,period_mins)

                        strategy_output_morethan1device.append([final_relationship_list[i][3], hour_clock[j][0] + "~" + hour_clock_end + " " + str(final_relationship_list[i][4]),clock[j][0], clock_end,final_relationship_list[i][2]])

                        print(strategy_output_morethan1device)

    strategy_output=strategy_output_1device+strategy_output_morethan1device


    #按某段策略开始时间排序
    #冒泡排序法

    for i in range(len(strategy_output)):
        for j in range(1, len(strategy_output) - i):
            if strategy_output[j - 1][2] > strategy_output[j][2]:
                strategy_output[j - 1], strategy_output[j] = strategy_output[j], strategy_output[j - 1]

    '''
    for i in range(len(strategy_output)):
        print(strategy_output[i])
    '''

    return strategy_output


strategy_output=generate_string(final_relationship_list,electricity_all)



def find_index_in_finalrelationshiplist_accordingto_element(x,y,final_relationship_list):
    #eg:
    #x为startegy_output某条策略中的[20,36]
    #y为x[20,36]在final_relationship_list中某个设备
    #返回的i是[20,36]在final_relationship_list的第i个设备矩阵当中
    for i in range(len(final_relationship_list)):
        if x==final_relationship_list[i][y]:

            return i

#index=find_element_in_finalrelationshiplist_accordingto_element([3,36],3,final_relationship_list)

print("chu=====")
for i in range(len(strategy_output)):
        print(strategy_output[i])
print("chu=====")

def combine_strategy_output(strategy_output):
    strategy_output_new=[]
    m = len(strategy_output)
    for i in range(len(strategy_output)):
        if i+1<m:

            if strategy_output[i+1][0]==strategy_output[i][0]:
                if (strategy_output[i + 1][2] - strategy_output[i][3]).total_seconds() <=60*5:
                    # 相差<=5mins，可以合并
                    #print("yoyo")
                    print(str(strategy_output[i])+"和"+str(strategy_output[i+1])+"可以合并!")

                    #print("yoyo")
                    hour_combine_start= strategy_output[i][2].strftime('%H:%M')
                    hour_combine_end =strategy_output[i+1][3].strftime('%H:%M')


                    combine_string_index=find_index_in_finalrelationshiplist_accordingto_element(strategy_output[i][0],3,final_relationship_list)
                    combine_string=final_relationship_list[combine_string_index][4]

                    strategy_output.insert(i+2,[strategy_output[i][0], hour_combine_start + "~" + hour_combine_end + " " + combine_string,strategy_output[i][2], strategy_output[i+1][3],strategy_output[i+1][-1]])
                    #strategy_output_new.append([strategy_output[i][0], hour_combine_start + "~" + hour_combine_end + " " + combine_string,strategy_output[i][2], strategy_output[i+1][3]])
                    #print("new------")
                    #print(strategy_output)
                    del (strategy_output[i])
                    #print(strategy_output)
                    del (strategy_output[i])
                    #print(strategy_output)
                    #strategy_output.remove(strategy_output[i])
                    #strategy_output.remove(strategy_output[i+1])
                    #print("删除后")
                    #print(strategy_output)
                    m=m-2

                #strategy_output_new.append(strategy_output[i])


    return strategy_output


strategy_output_upload=combine_strategy_output(strategy_output)



for i in range(len(strategy_output_upload)):
    for j in range(len(df_relationship_copy)):
            '''print(strategy_output_upload[i][0][0])
            print(type(strategy_output_upload[i][0][0]))
            print(df_relationship_copy['device_from'][j])
            print(type(df_relationship_copy['device_from'][j]))'''

            if strategy_output_upload[i][0][0]==df_relationship_copy['device_from'][j] and strategy_output_upload[i][0][1]==df_relationship_copy['device_to'][j]:
                #print("Yesss!!!")
                #print(strategy_output_upload[i][0])
                #print(df_relationship_copy['stgy_code'][j])
                strategy_output_upload[i].append(df_relationship_copy['stgy_code'][j])
                print(strategy_output_upload[i])

print(final_x)

print(str_node)
print(str_path)

