import time
import pymysql
import pandas as pd
import copy


#database='test'
#graph_name_='冬季图谱'

database='power_test'
graph_name_='冬季图谱'

host_id='192.168.40.27'

conn = pymysql.connect(
        host=host_id,
        port=3306,
        user='power',
        password='ajpower20',
        db=database,
        charset='utf8'
    )

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


sql_graph_id = "select graph_id,start_work_time,end_work_time,strategy_type from graph_info where graph_name='"+graph_name_+"'"
df_graph_id = pd.read_sql(sql_graph_id, con=conn)
print("yououououo")
print(df_graph_id)
n_H_M=time.strptime(df_graph_id['start_work_time'][0],'%H:%M')
offwork_time_H_M=time.strptime(df_graph_id['end_work_time'][0],'%H:%M')
strategy_typee=df_graph_id['strategy_type'][0]



#n点前需要达到指定能量
n=float(n_H_M.tm_hour)


#下班时间

offwork_time=float(offwork_time_H_M.tm_hour)



graph_no=str(df_graph_id['graph_id'][0])
print(graph_no)
sql_electricity = "select start_time,end_time,price from electricity where graph_id='"+graph_no+"'"
df_electricity = pd.read_sql(sql_electricity, con=conn)

data_lenth=len(df_electricity)
electricity_price=[]
electricity_time=[]
#print(df_electricity['price'])
for i in range(len(df_electricity)):
    electricity_price.append(df_electricity['price'][i])
    electricity_time.append([float(df_electricity['start_time'][i].replace(':','.')),float(df_electricity['end_time'][i].replace(':','.'))])

print(electricity_price)
print(electricity_time)

#sql_device = "select cap,device_id,device_name,power,type_id,work_time,conversion_rate,is_predicted from device where graph_id='"+graph_no+"'"
sql_device = "select cap,device_id,device_name,power,type_id,work_time,conversion_rate,is_predicted from device"
df_device = pd.read_sql(sql_device, con=conn)

sql_relationship = "select device_from,device_to,loss_rate,is_share,stgy_code,rel_name from relationship where graph_id='"+graph_no+"'"
df_relationship = pd.read_sql(sql_relationship, con=conn)

print("oioioioioooo")
print(df_relationship)

df_relationship_copy=copy.deepcopy(df_relationship)

sql_graph_dev ="select device_id from graph_dev where graph_id='"+graph_no+"'"
df_graph_dev = pd.read_sql(sql_graph_dev, con=conn)

#读入蓄能放能type表
sql_devicetype = "select type_id,alias,type_name from device_type"
df_devicetype = pd.read_sql(sql_devicetype, con=conn)


conn.close()

'''solar_id=0
for i in range(len(df_device)):
    if '太阳能' in df_device['device_name'][i]:
        solar_id=df_device['device_id'][i]
        df_device = df_device.drop(index=i)

print("太阳能对应编号: ",solar_id)

solar_id_to=0
for i in range(len(df_relationship)):
    if df_relationship['device_from'][i]==solar_id:
        solar_id_to = df_relationship['device_to'][i]
        df_relationship = df_relationship.drop(index=i)
        df_relationship = df_relationship.reset_index(drop=True)

print(df_relationship)
print("solar_to")
ps=str(solar_id_to)
solar_id_to=int(ps)
print(solar_id_to)'''

device_graph_dev_index=[]
for i in df_graph_dev['device_id']:
    device_graph_dev_index.append(i)
print(device_graph_dev_index)

device_is_predicted_index=[]
device_isnot_predicted_index=[]
for i in range(len(df_device)):
    if df_device['is_predicted'][i]==0:
        device_is_predicted_index.append(df_device['device_id'][i])
    else:
        device_isnot_predicted_index.append(df_device['device_id'][i])

print("check if the device is predicted or not")
print(device_is_predicted_index)
print(device_isnot_predicted_index)

df_device_final_index=[]
df_device_final_index_notpredicted=[]
for i in range(len(device_graph_dev_index)):
    for j in range(len(device_is_predicted_index)):
        if device_graph_dev_index[i]==device_is_predicted_index[j]:
            df_device_final_index.append(device_graph_dev_index[i])

for i in range(len(device_graph_dev_index)):
    for j in range(len(device_isnot_predicted_index)):
        if device_graph_dev_index[i]==device_isnot_predicted_index[j]:
            df_device_final_index_notpredicted.append(device_graph_dev_index[i])

print("yoheyouheyouhe")
print(df_device_final_index)
print(df_device_final_index_notpredicted)

df_device_not_predicted=[]

for i in range(len(df_device)):

    #if i<len(df_device):
        if df_device['device_id'][i] not in df_device_final_index:
            #df_device_not_predicted.append(df_device[i])
            df_device= df_device.drop(index=i)

print("---------------")

relationship_not_predicted=[]


for i in range(len(df_relationship)):
    if df_relationship['device_from'][i] not in df_device_final_index or df_relationship['device_to'][i] not in df_device_final_index:
        relationship_not_predicted.append([df_relationship['device_from'][i],df_relationship['device_to'][i]])

        df_relationship=df_relationship.drop(index=i)



print("-----------")
print("-----------")
print(relationship_not_predicted)
print("-----------")
print("-----------")

df_device = df_device.reset_index(drop=True)
df_relationship = df_relationship.reset_index(drop=True)
print("---------------")
print(df_device)
print(df_relationship)
print(df_relationship_copy)

fixed_relationship=[]
green_relationship=[]

for i in range(len(df_relationship_copy)):
    for j in range(len(relationship_not_predicted)):

        if relationship_not_predicted[j][0]==df_relationship_copy['device_from'][i] and relationship_not_predicted[j][1]==df_relationship_copy['device_to'][i]:
            print(df_relationship_copy['rel_name'][i])
            if df_relationship_copy['rel_name'][i] is not None:

                if "太阳能" in df_relationship_copy['rel_name'][i]:
                    green_relationship.append(relationship_not_predicted[j])
                else:
                    fixed_relationship.append(relationship_not_predicted[j])


print("固定策略",fixed_relationship)
print("绿色能源策略",green_relationship)



'''for i in range(len(df_device)):
    if df_device['device_id'][i]==solar_id_to:
        df_device = df_device.drop(index=i)

df_relationship_to_drop_index=[]

for i in range(len(df_relationship)):
    for j in range(len(device_not_in_strategy)):
        if df_relationship['device_from'][i]==device_not_in_strategy[j]:
            df_relationship_to_drop_index.append(i)

print("drop前")
print(df_relationship)
for i in df_relationship_to_drop_index:
    df_relationship=df_relationship.drop(index=i)
df_relationship=df_relationship.reset_index(drop = True)

print("final df_relationship oioioioio")
print(df_relationship)

print("final df_device")
print(df_device)
print(df_device['type_id'])'''


route_power=[]
loss_rate=[]
conversion_rate=[]
working_time=[]
route=[]
type_id=[]


for i in range(len(df_device)):
    for j in range(len(df_relationship)):
        if df_relationship['device_from'][j]==df_device['device_id'][i]:

            route_power.append([df_relationship['device_from'][j],df_device['power'][i]])
            loss_rate.append([df_relationship['device_from'][j],df_relationship['loss_rate'][j]])
            conversion_rate.append([df_relationship['device_from'][j],df_device['conversion_rate'][i]])
            route.append([df_relationship['device_from'][j],df_relationship['device_to'][j]])
        if df_relationship['device_to'][j]==df_device['device_id'][i]:
            working_time.append([df_relationship['device_from'][j], df_device['work_time'][j]])


print("路径功率:",route_power)
print("损失率:",loss_rate)

print("有效率:",conversion_rate)
print("工作时间:",working_time)
print("路径:",route)



relationship_list=[]
relationship=[]
print("wwwwwwwww")
print(df_relationship)
for i in range(len(df_relationship)):
    name = 'relationship_' + str(i)+"_"+str(df_relationship['device_from'][i])+'to'+str(df_relationship['device_to'][i])
    device_from=df_relationship['device_from'][i]
    device_to=df_relationship['device_to'][i]
    relationship_info=df_relationship['rel_name'][i]
    relationship_list.append([name,device_from,device_to,relationship_info])
    relationship.append([name])
print(relationship_list)

for i in range(len(relationship_list)):
    for j in range(len(relationship_list)):
        if relationship_list[i][2]==relationship_list[j][1]:
            for z in range(len(relationship_list)):
                if relationship_list[z][1]==relationship_list[i][1] and relationship_list[z][2]==relationship_list[j][2]:
                    print(relationship_list[i])
                    print(relationship_list[j])
                    print(relationship_list[z])


type_id=0

print("Q^Q^Q")
print(df_devicetype)
for i in range(len(df_devicetype['type_name'])):
    if "储能" in df_devicetype['type_name'][i]:
        type_id = df_devicetype['type_id'][i]

print("kakakaka")

print(int(type_id))
print(relationship_list)

storage_id=''
for i in range(len(df_device['type_id'])):

    if df_device['type_id'][i] == type_id:
        print("============================================")
        print("蓄能设备是"+str(df_device['device_id'][i]))
        storage_id=df_device['device_id'][i]

print("@@@@@@@@@@@@@@@@@@")
print(storage_id)


storage_release_list = []
storage_step=[]
release_step=[]

for i in range(len(relationship_list)):

    if str(relationship_list[i][2])==str(storage_id):
        #蓄能 x->水蓄能
        print("蓄能过程 " + str(relationship_list[i][1]) + "to" + str(relationship_list[i][2]))
        storage_step=[relationship_list[i][1], relationship_list[i][2]]

    if str(relationship_list[i][1])==str(storage_id):
        #放能 水蓄能->y
        print("放能过程 " + str(relationship_list[i][1]) + "to" + str(relationship_list[i][2]))
        release_step=[relationship_list[i][1], relationship_list[i][2]]

storage_release_list.append([storage_step,release_step])
print(storage_release_list)

'''for m in range(len(relationship_list)):
        for n in range(len(relationship_list)):
            for o in range(len(relationship_list)):
                if m != n and n != o and m != o:
                    if relationship_list[m][1] == relationship_list[n][1] and relationship_list[o][1] == \
                            relationship_list[m][2] and relationship_list[o][2] == relationship_list[n][2]:
                        storage_release_list.append([[relationship_list[m][1], relationship_list[o][1]],
                                                     [relationship_list[o][1], relationship_list[o][2]]])
                        print("蓄能过程 " + str(relationship_list[m][1]) + "to" + str(relationship_list[o][1]))
                        print("放能过程 " + str(relationship_list[o][1]) + "to" + str(relationship_list[o][2]))
                        print("蓄能设备", relationship_list[m][1])
                        print("储能设备/放能设备", relationship_list[o][1])
                        print("用能设备", relationship_list[o][2])

print(storage_release_list)'''
print(relationship)

print("固定策略",fixed_relationship)
print("绿色能源策略",green_relationship)
