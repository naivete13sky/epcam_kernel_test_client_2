import os
import xlwt
import  psycopg2

# 创建连接
conn = psycopg2.connect(host='10.97.80.119', user='readonly', password='123456', dbname='epdms', port=5432)

#查询路径
fil_dir = r'C:\Users\Administrator\Desktop\贺鸿资料整理\未整理的ODB++\整理中'

# 创建一个workbook 设置编码
workbook = xlwt.Workbook(encoding='utf-8')
# 创建一个sheet名
worksheet = workbook.add_sheet("files")

iter = 0
#循环读取某个路径下的所有文件名，并根据文件名向数据库中查询对应job_id
for root, dirs, files in os.walk(fil_dir):
    for file in files:
        # print(file.split(".", 1)[0])
        # print(os.path.basename(file))

        filename = file.split(".", 1)[0]
        job_name = filename.split("_", 1)[0]
        # print(job_name)
        try:
            # 获取游标
            cursor = conn.cursor()
            # 执行语句
            cursor.execute("SELECT a.id from job_job a where a.job_name ~* '{}'".format(job_name))
            # print("sql:","SELECT a.id from job_job a where a.job_name = '{}'".format(job_name))
            # 获取结果：支持fetchone, fetchall和fetchmany
            job_id = cursor.fetchone()[0]
            print("料号",job_name,"的id是",job_id)
        except Exception as e:
            print(e)
            print("料号",job_name,"在数据库中不存在")
        # print(job_id)

        # name = os.path.join(filename)
        # id = os.path.join(job_id)
        #向工作表中添加文件名和料号id
        worksheet.write(iter, 0, label=filename)
        worksheet.write(iter, 1, label=job_id)
        iter += 1
    # 关闭连接
    conn.close()

#在指定路径下创建filename.xlsx
workbook.save(r'C:\Users\Administrator\Desktop\DMS导入\filename.xlsx')





