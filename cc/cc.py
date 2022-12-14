import json
import os
import sys

from epkernel import Input, GUI, BASE
from epkernel.Edition import Job, Matrix
from sqlalchemy import create_engine
import pandas as pd

from config import RunConfig


def my_print():
    # '^'字符表示中心
    print('{0:*^198}'.format('MENU'))
    print('{0:*^198}'.format('你好啊，你在哪里啊啊发发！'))
    print('MENU'.center(198, '*'))

class DMS(object):

    def get_job_layer_info_from_dms(self,job_id):

        sql = '''SELECT a.* from eptest_layer a where a.job_id = {}'''.format(job_id)
        engine = create_engine('postgresql+psycopg2://readonly:123456@10.97.80.119/epdms')
        pd_job_layer_info = pd.read_sql(sql=sql, con=engine)
        self.pd_job_layer_info = pd_job_layer_info
        return pd_job_layer_info



def pp():
    pass
    print('abc')


def open_job():
    from epkernel import Configuration
    Configuration.init(RunConfig.ep_cam_path)
    Configuration.set_sys_attr_path(os.path.join(RunConfig.ep_cam_path, r'config\attr_def\sysattr'))
    Configuration.set_user_attr_path(os.path.join(RunConfig.ep_cam_path, r'config\attr_def\userattr'))

    job = 'nca11611_g2'
    job_path = r'C:\cc\share\temp_3068_1670480974\g2'

    # job = 'nca11611_g'
    # job_path = r'C:\cc\share\temp_3068_1670481538\g\nca11611_g'

    Input.open_job(job, job_path)
    GUI.show_layer(job, 'orig', 'top')


def input_gerber274x():
    pass
    print("abc")
    from epkernel import Configuration
    Configuration.init(RunConfig.ep_cam_path)
    Configuration.set_sys_attr_path(os.path.join(RunConfig.ep_cam_path, r'config\attr_def\sysattr'))
    Configuration.set_user_attr_path(os.path.join(RunConfig.ep_cam_path, r'config\attr_def\userattr'))

    job = 'test'
    step = 'orig'
    layer = '123'

    # 创建一个空料号
    Job.create_job(job)

    # 创建一个空step
    Matrix.create_step(job, step)

    result_each_file_identify = Input.file_identify(os.path.join(r'C:\Users\cheng.chen\Desktop\hige001a', r'BOTTOM.art'))
    print('result_each_file_identify:',result_each_file_identify)

    offsetFlag = False
    offset1 = 0
    offset2 = 0

    min_1 = result_each_file_identify['parameters']['min_numbers']['first']
    min_2 = result_each_file_identify['parameters']['min_numbers']['second']
    print('原来导入参数'.center(190, '-'))
    print(result_each_file_identify)
    if (offsetFlag == False) and (abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
        offset1 = min_1
        offset2 = min_2
        offsetFlag = True
    result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1, 'second': offset2}


    # offsetFlag = False
    # ret = Input.file_identify(os.path.join(r'C:\Users\cheng.chen\Desktop\hige001a', r'BOTTOM.art'))
    # file_format = ret['format']
    # file_param = ret['parameters']
    # file_minNum = file_param['min_numbers']
    # min_1 = file_minNum['first']
    # min_2 = file_minNum['second']
    # if (offsetFlag == False) and (abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
    #     offset1 = min_1
    #     offset2 = min_2
    #     offsetFlag = True
    # file_param['offset_numbers'] = {'first': offset1, 'second': offset2}
    #re = Input.file_translate(os.path.join(r'C:\Users\cheng.chen\Desktop\hige001a', r'BOTTOM.art'), job, step, layer, result_each_file_identify)  # translate

    Input.file_translate(path=os.path.join(r'C:\Users\cheng.chen\Desktop\hige001a',r'BOTTOM.art'), job=job, step='orig', layer=layer,
                         param=result_each_file_identify['parameters'])

    GUI.show_layer(job,step,layer)


    print('finish')


if __name__ == '__main__':
    pass
    # cc = DMS()
    # df = cc.get_job_layer_info_from_dms(997)
    # data = df[(df['layer'] == 'Znn-2786693_.drl')]
    # print(data)
    # data1 =  df[(df['layer'] == 'Znn-2786693_.drl')]['units_ep'].values[0]
    # print(data1)
    # print(data1)
    # open_job()

    input_gerber274x()

