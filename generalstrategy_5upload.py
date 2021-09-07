from generalstrategy_4string import strategy_output_upload
from generalstrategy_4string import str_node
from generalstrategy_4string import str_path
from generalstrategy_2readdata import graph_no
from generalstrategy_2readdata import strategy_typee
from generalstrategy_1predict import host_id

from generalstrategy_1predict import date
from generalstrategy_3generate import final_x
from generalstrategy_2readdata import storage_step
from generalstrategy_2readdata import release_step



import pymysql
import datetime

date_datetime = datetime.datetime.strptime(date, "%Y%m%d")

print(final_x)
print(strategy_output_upload)
print(storage_step)
print(release_step)


def upload_strategy_winter_historydata2():
    conn = pymysql.connect(
        host=host_id,
        port=3306,
        user='power',
        password='ajpower20',
        db='power_test',
        charset='utf8'
    )

    cur = conn.cursor()


    sql_1 = "INSERT INTO history_data (alias,data,date,strategy_type,graph_id) VALUES(%s, %s, %s, %s,%s)"

    data_list_1 = []
    for i in range(0, 1):
            # 插入具体的假数据,需要与上方的sql语句的元素对应

            result1 = ("node", str_node, date_datetime, strategy_typee,graph_no)
            result2 = ("path", str_path, date_datetime, strategy_typee,graph_no)
            print("2222")

            '''result3 = ("shuiXuNengXu", str_zhujixu, date_datetime, strategy_typee,graph_no)
            result4 = ("shuiXuNengFang", str_zhujifang, date_datetime, strategy_typee,graph_no)
            result5 = ("zhuJi", str_zhujizhigong, date_datetime, strategy_typee,graph_no)
            result6 = ("solar", str_solar, date_datetime, strategy_typee,graph_no)'''

            data_list_1.append(result1)
            data_list_1.append(result2)
            '''
            data_list_1.append(result3)
            data_list_1.append(result4)
            data_list_1.append(result5)
            data_list_1.append(result6)
            '''

    cur.executemany(sql_1, data_list_1)
    conn.commit()
    conn.close()

    #except Exception as e:
        #print("upload error for 1~~~")
        #conn.close()


def upload_strategy_winter_strategy_output2():
    conn = pymysql.connect(
        host=host_id,
        port=3306,
        user='power',
        password='ajpower20',
        db='power_test',
        charset='utf8'
    )

    cur = conn.cursor()

    sql_2 = "INSERT INTO strategy_output (code,start_time,end_time,power,info,graph_id,strategy_type) VALUES(%s,%s,%s,%s,%s,%s,%s)"
    data_list_2 = []

    for x in range(0, 1):
        for i in range(len(strategy_output_upload)):
                # print("youhouhou")
                # print(strategy_output[i][2])

            print(type(strategy_output_upload[i][-1]))
            #print(type(strategy_output_upload[i][2]))
            #print(type(strategy_output_upload[i][3]))
            #strategy_output_upload[i][4]=int(strategy_output_upload[i][4])
            #print(type(strategy_output_upload[i][1]))
            #print(graph_no, strategy_typee)

            result1 = (str(strategy_output_upload[i][-1]), strategy_output_upload[i][2], strategy_output_upload[i][3], int(strategy_output_upload[i][4]),str(strategy_output_upload[i][1]), str(graph_no), str(strategy_typee))

            data_list_2.append(result1)

    print(data_list_2)
    cur.executemany(sql_2, data_list_2)

    conn.commit()
    conn.close()

#upload_strategy_winter_historydata2()
upload_strategy_winter_strategy_output2()

for i in range(len(final_x)):
    final_x[i].append([int(final_x[i][0][0].split('_')[-1].split('to')[0]),int(final_x[i][0][0].split('_')[-1].split('to')[1])])

#判断该段时间是不是蓄能
def generate_add_predict_dl(final_x,strategy_output_upload):
    #电量：蓄能部分需要在原有基础上加上一定阈值（很多）
    predict_dl_add_storage=[0.0]*24
    #电量：放能部分需要在原有基础上加上一定阈值（很少）
    #predict_dl_add_release=[0.0]*24

    time_start_storage=0
    time_span_storage=0

    storage_time_period_before_today=0
    for m in range(len(final_x)):
        for n in range(len(strategy_output_upload)):
            if final_x[m][-1]==storage_step and strategy_output_upload[n][0]==storage_step:
                time_span_storage=final_x[m]
                time_start_storage=strategy_output_upload[n][2]

    if time_start_storage<date_datetime:
        #蓄能从前一天开始
        storage_time_period_before_today=(date_datetime-time_start_storage).seconds/3600

    time_period_storage=0
    for i in range(len(time_span_storage[1])-1):
        if time_span_storage[1][i]!=0:
            time_period_storage=time_span_storage[1][i]

    #如果蓄能从前一天开始
    storage_time_today=time_period_storage-storage_time_period_before_today
    for i in range(int(storage_time_today)):
        predict_dl_add_storage[i]=170
    predict_dl_add_storage[int(storage_time_today)]=170*(storage_time_today-int(storage_time_today))

    return predict_dl_add_storage

predict_dl_add_array=generate_add_predict_dl(final_x,strategy_output_upload)
print(predict_dl_add_array)
def generate_predict_power():

    # 能量：除了蓄能以外其他能量都需要加
    print(final_x)

    for m in reversed(range((len(final_x)))):
        for n in range(len(strategy_output_upload)):
            if final_x[m][-1] == storage_step and strategy_output_upload[n][0] == storage_step:
                del final_x[m]
                return
    print(final_x)

print(generate_predict_power())




