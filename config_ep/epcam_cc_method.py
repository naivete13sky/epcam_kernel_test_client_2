import json
import os
import shutil
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import RunConfig
from epkernel import Configuration, Input, GUI,BASE,Output
from epkernel.Edition import Job,Matrix,Layers
from epkernel.Action import Information,Selection
import re



from cc.cc_method import StringMehtod,DMS,Print

Configuration.init(RunConfig.ep_cam_path)
Configuration.set_sysattr_path(os.path.join(RunConfig.ep_cam_path,r'config\attr_def\sysattr'))
Configuration.set_userattr_path(os.path.join(RunConfig.ep_cam_path,r'config\attr_def\userattr'))

def f1():
    pass
    Input.open_job("eni40021", r"C:\job\test\odb")
    GUI.show_layer("eni40021", "orig", "top")

class MyInput(object):

    def __init__(self,*,folder_path,job,step,job_id,save_path=None):
        self.folder_path = folder_path
        self.job = job
        self.step = step
        self.job_id = job_id
        self.save_path = save_path
        #层名称处理
        self.fix_layer_name_same_to_g()
        #从DMS获取层别信息
        self.get_job_layer_info_from_dms()
        self.input_folder()

    def fix_layer_name_same_to_g(self):
        print('fix_layer_name_same_to_g'.center(190,'-'))
        folder_path = self.folder_path
        # 开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        file_list = [x for x in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, x))]

        unknown_index = 1

        for file in file_list:
            # 把特殊字符替换成‘-’，比如空格、(、)等。
            os.rename(os.path.join(folder_path, file),os.path.join(folder_path, file.replace(' ', '-').replace('(', '-').replace(')', '-')))
            file = file.replace(' ', '-').replace('(', '-').replace(')', '-')
            # 把含有中文字符名称的文件改名成unknown1\unknown2等
            if StringMehtod.is_chinese(file):
                suffix_of_file = os.path.splitext(file)[1]
                os.rename(os.path.join(folder_path,file), os.path.join(folder_path,'unknown' + str(unknown_index) + suffix_of_file))
                # file = 'unknown' + str(unknown_index)
                unknown_index = unknown_index + 1

    def get_job_layer_info_from_dms(self):
        job_id = self.job_id
        sql = '''SELECT a.* from eptest_layer a where a.job_id = {}'''.format(job_id)
        engine = create_engine('postgresql+psycopg2://readonly:123456@{}/epdms'.format(RunConfig.dms_ip))
        pd_job_layer_info = pd.read_sql(sql=sql, con=engine)
        self.pd_job_layer_info = pd_job_layer_info

    def input_folder(self):
        '''
        函数：把指定路径下的所有Gerber274X或Excello2文件全部转换到指定名称的料号，并保存到指定路径。
        命名关键字参数save_path，用来保存料号的路径，未传此参数时，默认路径为'C:/job/test/odb'。
        '''

        folder_path = self.folder_path
        job = self.job
        step = self.step
        save_path = self.save_path

        #如果未指定保存路径,默认路径为r'C:\job\test\odb'。
        save_path = r'C:\job\test\odb' if not save_path else save_path

        # job若存在则删除
        shutil.rmtree(os.path.join(save_path, job)) if os.path.exists(os.path.join(save_path, job)) else True

        # 创建一个空料号
        Job.create_job(job)

        #创建一个空step
        Matrix.create_step(job, step)

        #开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        file_list = [x for x in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path,x))]

        offsetFlag = False
        offset1 = 0
        offset2 = 0

        for each_file in file_list:

            result_each_file_identify = Input.file_identify(os.path.join(folder_path,each_file))
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']
            print("orig min_1,min_2:",min_1,":",min_2)
            #如果是孔的话，需要从DMS读取导入参数。是不是孔文件，以及相关参数信息都从DMS获取信息。孔参数信息是要人工确认过的，即层信息状态是published的。
            try:
                pd_job_layer_info_cuurent_layer = self.pd_job_layer_info[(self.pd_job_layer_info['layer'] == each_file)]
                print("layer_file_type_value:".center(192,'-'))
                print(pd_job_layer_info_cuurent_layer['layer_file_type'].values[0])

                if pd_job_layer_info_cuurent_layer['status'].values[0] ==  'published' and pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] ==  'excellon2' or \
                        pd_job_layer_info_cuurent_layer['status'].values[0] ==  'published' and pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] ==  'excellon1':
                    print('need to set the para for drill excellon2'.center(190,'-'))
                    print('原来导入参数'.center(190,'-'))
                    print(result_each_file_identify)
                    result_each_file_identify['parameters']['units'] = pd_job_layer_info_cuurent_layer['units'].values[0]
                    result_each_file_identify['parameters']['zeroes_omitted'] = pd_job_layer_info_cuurent_layer['zeroes_omitted'].values[0]
                    result_each_file_identify['parameters']['Number_format_integer'] = int(pd_job_layer_info_cuurent_layer['number_format_A'].values[0])
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(pd_job_layer_info_cuurent_layer['number_format_B'].values[0])
                    result_each_file_identify['parameters']['tool_units'] = pd_job_layer_info_cuurent_layer['tool_units_ep'].values[0]
                    print('现在导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                if pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'gerber274X' \
                        or pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'else' \
                        or pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'dxf':
                    if result_each_file_identify["format"] == "Gerber274x":
                        # print("hihihi1:", each_file)
                        print("我不是孔类型")
                        print('orig para'.center(190, '-'))
                        print(result_each_file_identify)
                        print("offsetFlag:", offsetFlag)
                        if (offsetFlag == False) and (abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
                            # print("hihihi2:",each_file)
                            offset1 = min_1
                            offset2 = min_2
                            offsetFlag = True
                        result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1, 'second': offset2}
                    elif result_each_file_identify["format"] == "DXF":
                        # print("hihihi1:", each_file)
                        print("我是dxf呀")
                        print('dxf para'.center(190, '-'))
                        print(result_each_file_identify)
                        if pd_job_layer_info_cuurent_layer['status'].values[0] == 'published':
                            result_each_file_identify['parameters']['units'] = pd_job_layer_info_cuurent_layer['units'].values[0]
                        result_each_file_identify['parameters']['scale'] = 1  # 改参数在kernel1.9版本中添加
                    print('now para'.center(190, '-'))
                    print(result_each_file_identify)

            except Exception as e:
                print(e)
                print("有异常情况发生")
            Input.file_translate(path=os.path.join(folder_path,each_file),job=job, step='orig', layer=each_file, param=result_each_file_identify['parameters'])

        #保存料号
        BASE.save_job_as(job, save_path)

class MyOutput(object):
    def __init__(self,*,temp_path:str,job:str,job_id,step = 'orig',layer_info_from_obj='dms',customer_para:dict):
        pass
        self.temp_path = temp_path
        self.job = job
        self.job_id = job_id
        self.step = step
        self.layer_info_from_obj = layer_info_from_obj

        self.get_current_job_layer_type(layer_info_from_obj)

        self.set_para_default()

        self.set_para_customer(customer_para)

        self.out_put()

    def set_para_default(self):

        # 设置导出参数
        with open(RunConfig.config_my_settings, 'r') as cfg:
            infos_ = json.load(cfg)['epcam']['output_paras']   # (json格式数据)字符串 转化 为字典

            self.para = {}
            # self.para['_type'] = infos_['type']
            self.para['resize'] = infos_['resize']
            self.para['angle'] = infos_['angle']
            self.para['scalingX'] = infos_['scalingX']
            self.para['scalingY'] = infos_['scalingY']
            self.para['mirror'] = infos_['mirror']
            self.para['rotate'] = infos_['rotate']
            self.para['scale'] = infos_['scale']
            self.para['cw'] = infos_['cw']
            self.para['mirrorpointX'] = infos_['mirrorpointX']
            self.para['mirrorpointY'] = infos_['mirrorpointY']
            self.para['rotatepointX'] = infos_['rotatepointX']
            self.para['rotatepointY'] = infos_['rotatepointY']
            self.para['scalepointX'] = infos_['scalepointX']
            self.para['scalepointY'] = infos_['scalepointY']
            self.para['mirrorX'] = infos_['mirrorX']
            self.para['mirrorY'] = infos_['mirrorY']

            # excellon2的默认参数
            self.para['numberFormatL'] = infos_['numberFormatL']
            self.para['numberFormatR'] = infos_['numberFormatR']


    def set_para_customer(self,customer_para:dict):
        pass
        print('customer_para:',customer_para)
        for each in customer_para:
            print(each)
            self.para[each] = customer_para[each]
        print(self.para)
        print("cc")

    def get_current_job_layer_type(self,layer_info_from_obj):
        self.layers = Information.get_layers(self.job)
        print('self.layers:', self.layers)

        print('layer_info_from_obj:', layer_info_from_obj)
        if layer_info_from_obj == "dms":
            self.drill_layers = [each.lower() for each in DMS().get_job_layer_drill_from_dms_db_pandas_one_job(self.job_id)['layer']]
            self.rout_layers = [each.lower() for each in DMS().get_job_layer_rout_from_dms_db_pandas_one_job(self.job_id)['layer']]
        if layer_info_from_obj == 'job_tgz_file':
            self.drill_layers = list(map(lambda x:x['name'],Information.get_layer_info(self.job, context='board', type=['drill'])))
            self.rout_layers = list(map(lambda x: x['name'], Information.get_layer_info(self.job, context='board', type=['rout'])))

        print('self.drill_layers:', self.drill_layers)
        print('self.rout_layers:', self.rout_layers)

    def out_put(self):
        out_put = []
        job_result = {}
        out_json = ''

        # 建立output_gerber文件夹，里面用来放epcam输出的gerber。
        temp_out_put_gerber_path = os.path.join(self.temp_path, 'output_gerber')
        # if os.path.exists(temp_out_put_gerber_path):
        #     shutil.rmtree(temp_out_put_gerber_path)
        # os.mkdir(temp_out_put_gerber_path)
        os.mkdir(temp_out_put_gerber_path) if not os.path.exists(temp_out_put_gerber_path) else None



        para = self.para

        layers = Information.get_layers(self.job)
        file_path = os.path.join(temp_out_put_gerber_path, self.job)
        file_path_file = Path(file_path)
        # if file_path_file.exists():
        #     shutil.rmtree(file_path_file)  # 已存在gerber文件夹删除掉，再新建
        # os.mkdir(file_path)
        os.mkdir(file_path) if not file_path_file.exists() else None




        # step = 'orig'
        step = self.step
        value = {}
        # 开始时间
        start_time = (int(time.time()))
        # 创建料的step文件夹
        step_path = os.path.join(file_path, step)
        os.mkdir(step_path)

        drill_layers = self.drill_layers
        rout_layers = self.rout_layers

        common_layers_list = []
        layer_result = {}

        for each_layer in layers:
            if each_layer not in drill_layers:
                common_layers_list.append(each_layer)

        # 输出gerber
        for layer in common_layers_list:
            layer_stime = (int(time.time()))
            filename = os.path.join(step_path, layer)  # 当前step下的每个层的gerber文件路径
            ret = Output.save_gerber(self.job, step, layer, filename, **para)
            layer_etime = (int(time.time()))
            layer_time = layer_etime - layer_stime
            value[layer] = layer_time

        # 输出excellon2
        for drill_layer in drill_layers:

            layer_stime = (int(time.time()))

            drill_out_path = os.path.join(step_path, drill_layer)

            if drill_layer in rout_layers:
                Print.print_with_delimiter("我是rout")
                print(drill_layer)
                Matrix.change_matrix_row(self.job, drill_layer, 'board', 'rout', drill_layer)
                # GUI.show_layer(self.job, 'orig', drill_layer)
                # drill_info = Output.save_rout(self.job, step, drill_layer, drill_out_path, number_format_l=2,
                #                               number_format_r=4, zeroes=2, unit=0,
                #                               tool_unit=1, x_scale=1, y_scale=1, x_anchor=0, y_anchor=0,
                #                               break_arcs=False)
                print("rout输出参数：",self.job, step, drill_layer, drill_out_path, self.para['numberFormatL'], self.para['numberFormatR'])
                drill_info = BASE.rout2file(self.job, step, drill_layer,drill_out_path,number_format_l=self.para['numberFormatL'],number_format_r=self.para['numberFormatR'],
                    zeroes=2,unit=0,tool_unit=1,x_scale=1,y_scale=1,x_anchor=0,y_anchor=0, partial_order = 0
                    , num_in_x = 0, num_in_y = 0, order_type = 0, serial_no = 0, break_arcs = False)


            else:
                Print.print_with_delimiter("我是drill啊")
                Matrix.change_matrix_row(self.job, drill_layer, 'board', 'drill', drill_layer)
                drill_info = Output.save_excellon2(self.job, step, drill_layer, drill_out_path,
                                                   number_format_l=self.para['numberFormatL'], number_format_r=self.para['numberFormatR'], zeroes=2, unit=0,
                                                   tool_unit=1, x_scale=1, y_scale=1, x_anchor=0, y_anchor=0)
                # drill_info = Output.save_drill(self.job, step, drill_layer, drill_out_path, isMetric=False,
                #                                number_format_l=self.para['numberFormatL'], number_format_r=self.para['numberFormatR'], zeroes=2, unit=0, tool_unit=1,
                #                                x_scale=1, y_scale=1, x_anchor=0, y_anchor=0)
                # drill_info = BASE.drill2file(self.job, step, drill_layer, drill_out_path, isMetric=False,
                #                              number_format_l=2, number_format_r=4,
                #                              zeroes=2, unit=0, x_scale=1, y_scale=1, x_anchor=0, y_anchor=0,
                #                              manufacator='', tools_order=[])
                # print("drill_info:",drill_info)
            layer_etime = (int(time.time()))
            layer_time = layer_etime - layer_stime
            value[layer] = layer_time

        # 记录下输出step的时间
        end_time = (int(time.time()))
        time_time = end_time - start_time
        value["step_time"] = time_time
        job_result[step] = value
        print('job_result:', job_result)
        out_put.append(job_result)
        print('out_put:', out_put)
        out_path = os.path.join(temp_out_put_gerber_path, 'out_put' + '.json')
        if out_json == '':
            with open(out_path, 'w+') as f:  # 不能是a,w+会覆盖原有的，a只会追加
                f.write(json.dumps(out_put, sort_keys=True, indent=4, separators=(',', ': ')))
        else:
            with open(out_json, 'r') as h:
                ret_json = json.load(h)
                ret_json.append(job_result)
                with open(out_json, 'w+') as hh:
                    hh.write(json.dumps(ret_json, sort_keys=True, indent=4, separators=(',', ': ')))

        # GUI.show_layer(job_ep, "orig", "layer")
        # Job.close_job(self.job)

        Print.print_with_delimiter('输出gerber完成')


class Pretreatment(object):
    def __init__(self,*,job, job_id):
        pass
        self.job = job
        self.job_id = job_id

    def change_layer_attribute(self,attributes:dict):
        """
        修改层别名称，定义属性，重新排序
        # 字典格式
        attrbutes:
        [
        'layer_name'(string,原稿层名):['board'(string,新的层别属性)，'signal'(string,新的层别类型)，'new_name'(string,新的层名)，new_row(int,新的层别顺序)]
        ]
        """
        pass
        # 得到原稿层名
        all_layers_list_job_ep = Information.get_layers(self.job)
        try:
            for layer_name in all_layers_list_job_ep:
                # 修改层别名称，定义层别属性
                Matrix.change_matrix_row(self.job,layer_name,attributes[layer_name][0],attributes[layer_name][1],attributes[layer_name][2],True)
                # 获取层别信息
                informations = Information.get_layer_information(self.job)
                # 遍历层别信息
                for information in informations:
                    # 如果informations中的层名等于atrributes字典中的层名，获取该层名在information中的row值
                    if information['name'] == attributes[layer_name][2]:
                        # 获取information中的row值
                        row = information['row']
                        # 重新排序
                        Matrix.move_layer(self.job, row, attributes[layer_name][3])
        except Exception as e:
            print("错误异常：",e)

    # 复制一个新的step，并创建一个新层
    def copy2step(self, step_old, step_new, layer_new):
        pass
        step_name = Matrix.copy_step(self.job, step_old)
        Matrix.change_matrix_column(self.job, step_name, step_new)
        Matrix.create_layer(self.job, layer_new, -1)

    # def select_delete(self, step, layers, feature_ids):

    # 将线路层正、负片合并
    def signal_layers_contourize(self, step, signal_layers):
        pass
        # 设置筛选器物件类型，选中所有负极性物件
        Selection.set_featuretype_filter(0, 1, 1, 1, 1, 1, 1)
        Selection.select_features_by_filter(self.job, step, signal_layers)
        # 设置筛选器物件类型，选中所有征集性surface
        Selection.set_featuretype_filter(1, 0, 0, 1, 0, 0, 0)
        Selection.select_features_by_filter(self.job, step, signal_layers)
        # 执行congtourize，将正、负片合并
        Layers.contourize(self.job, step, signal_layers, 6350, True, 7620, 0)
        # 重置筛选器
        Selection.reset_select_filter()

    # 将防焊层非pad物件转成pad
    def solder_mask_layers2pad(self, step, solder_mask_layers):
        pass
        Selection.set_featuretype_filter(1, 1, 1, 1, 1, 1, 0)
        Selection.select_features_by_filter(self.job, step, solder_mask_layers)
        # 执行contour2pad，将surface转成pad
        Layers.contour2pad(self.job, step, solder_mask_layers, 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
        # 重置筛选器
        Selection.reset_select_filter()

    # 修改物件属性
    def change_attribute(self, step, layer, attributes, select_types, locations, ids, points):
        pass
        # Selection.select_feature_by_id(self.job, step, layer, ids)
        self.select_feature_type(step, layer, select_types, locations, ids, points)
        if Information.has_selected_features(self.job, step, layer):
            # GUI.show_layer(self.job, step, layer)
            BASE.modify_attributes(self.job, step, [layer], 1, attributes)
            # GUI.show_layer(self.job, step, layer)
        else:
            print("没有选中物件！")

    # 根据物件类型选择change_symbol接口
    def change_symbol(self, step, layer, feature_types, select_type, locations, ids, points):
        pass
        self.select_feature_type(step, layer, select_type, locations, ids, points)
        if Information.has_selected_features(self.job, step, layer):
            for type in feature_types:
                if type == 'arc': # 将指定得arc转成line
                    Layers.arc2lines(self.job, step, [layer], 1, True)
                    # GUI.show_layer(self.job, step, layer)
                elif type == 'line': # 将指定的line转成surface
                    Layers.contourize(self.job, step, [layer], 6350, True, 7620, 1)
                    # GUI.show_layer(self.job, step, layer)
                elif type == 'surface': # 将指定的surface转成pad
                    Layers.contour2pad(self.job, step, [layer], 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
                    # GUI.show_layer(self.job, step, layer)
                else:
                    print("type不存在")
        else:
            print("没有选中物件！")

    # 根据选择类型调用select_feature接口
    def select_feature_type(self, step, layer, select_types:list, locations, ids, points ):
        pass
        for type in select_types:
            print("=type=:",type)
            if type == 'locations': #根据坐标选择物件
                for location_x, location_y in locations:
                    Selection.select_feature_by_point(self.job, step, layer, location_x, location_y)
            elif type == 'ids': #根据index选择物件
                Selection.select_feature_by_id(self.job, step, layer, ids)
            elif type == 'points': #根据框选范围选择物件
                Selection.select_feature_by_polygon(self.job, step, layer, points)
            else:
                print("type不存在")

    def get_job_layer_info_from_dms(self):
        job_id = self.job_id
        sql = '''SELECT a.* from eptest_layer a where a.job_id = {}'''.format(job_id)
        engine = create_engine('postgresql+psycopg2://readonly:123456@{}/epdms'.format(RunConfig.dms_ip))
        pd_job_layer_info = pd.read_sql(sql=sql, con=engine)
        # self.pd_job_layer_info = pd_job_layer_info
        return pd_job_layer_info

    def input_folder(self, temp_gerber_path, save_path):
        '''
        函数：把指定路径下的所有Gerber274X或Excello2文件全部转换到指定名称的料号，并保存到指定路径。
        命名关键字参数save_path，用来保存料号的路径，未传此参数时，默认路径为r'C:/job/test/odb'。
        '''
        # folder_path = self.folder_path
        job = self.job
        # step = self.step
        # save_path = self.save_path
        step = 'orig'
        folder_path = temp_gerber_path
        # folder_path = os.

        #如果未指定保存路径,默认路径为r'C:\job\test\odb'。
        save_path = r'C:\job\test\odb' if not save_path else save_path

        # job若存在则删除
        shutil.rmtree(os.path.join(save_path, job)) if os.path.exists(os.path.join(save_path, job)) else True

        # 创建一个空料号
        # Job.create_job(job)
        BASE.create_job(save_path,job)
        #创建一个空step
        Matrix.create_step(job, step)

        #开始识别文件夹中各个文件的类型，此方只识别单层文件夹中的内容
        file_list = [x for x in os.listdir(folder_path + '\\' + job.split("_ep")[0]) if os.path.isfile(os.path.join(folder_path + '\\' + job.split("_ep")[0],x))]
        # print("folder_path",folder_path + "\\" + job.split("_ep")[0])
        # print("file_list",file_list)
        # file_list = []
        # for root, dirs, files in os.walk(folder_path):
        #     for file in files:
        #         file_list.append(file)
        print("list",file_list)

        offsetFlag = False
        offset1 = 0
        offset2 = 0
        for each_file in file_list:
            print(each_file)
            # result_each_file_identify = Input.file_identify(os.path.join(folder_path,each_file))
            result_each_file_identify = Input.file_identify(folder_path + '\\' + job.split("_ep")[0] + '\\' + each_file)
            print("result_each_file_identify",result_each_file_identify)
            min_1 = result_each_file_identify['parameters']['min_numbers']['first']
            min_2 = result_each_file_identify['parameters']['min_numbers']['second']
            print("orig min_1,min_2:",min_1,":",min_2)
            #如果是孔的话，需要从DMS读取导入参数。是不是孔文件，以及相关参数信息都从DMS获取信息。孔参数信息是要人工确认过的，即层信息状态是published的。
            try:
                pd_job_layer_info = self.get_job_layer_info_from_dms()
                pd_job_layer_info_cuurent_layer = pd_job_layer_info[(pd_job_layer_info["layer"] == each_file)]
                print("layer_file_type_value:".center(192,'-'))
                print(pd_job_layer_info_cuurent_layer['layer_file_type'].values[0])

                if pd_job_layer_info_cuurent_layer['status'].values[0] ==  'published' and pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] ==  'excellon2' or \
                        pd_job_layer_info_cuurent_layer['status'].values[0] ==  'published' and pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] ==  'excellon1':
                    print('need to set the para for drill excellon2'.center(190,'-'))
                    print('原来导入参数'.center(190,'-'))
                    print(result_each_file_identify)
                    result_each_file_identify['parameters']['units'] = pd_job_layer_info_cuurent_layer['units'].values[0]
                    result_each_file_identify['parameters']['zeroes_omitted'] = pd_job_layer_info_cuurent_layer['zeroes_omitted'].values[0]
                    result_each_file_identify['parameters']['Number_format_integer'] = int(pd_job_layer_info_cuurent_layer['number_format_A'].values[0])
                    result_each_file_identify['parameters']['Number_format_decimal'] = int(pd_job_layer_info_cuurent_layer['number_format_B'].values[0])
                    result_each_file_identify['parameters']['tool_units'] = pd_job_layer_info_cuurent_layer['tool_units_ep'].values[0]
                    print('现在导入参数'.center(190, '-'))
                    print(result_each_file_identify)

                if pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'gerber274X' or pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'else' \
                        or pd_job_layer_info_cuurent_layer['layer_file_type'].values[0] == 'dxf':
                    if result_each_file_identify["format"] == "Gerber274x":
                        # print("hihihi1:", each_file)
                        print("我不是孔类型")
                        print('orig para'.center(190, '-'))
                        print(result_each_file_identify)
                        print("offsetFlag:", offsetFlag)
                        if (offsetFlag == False) and (abs(min_1 - sys.maxsize) > 1e-6 and abs(min_2 - sys.maxsize) > 1e-6):
                            # print("hihihi2:",each_file)
                            offset1 = min_1
                            offset2 = min_2
                            offsetFlag = True
                        result_each_file_identify['parameters']['offset_numbers'] = {'first': offset1, 'second': offset2}
                    elif result_each_file_identify["format"] == "DXF":
                        # print("hihihi1:", each_file)
                        print("我是dxf呀")
                        print('dxf para'.center(190, '-'))
                        print(result_each_file_identify)
                        if pd_job_layer_info_cuurent_layer['status'].values[0] == 'published':
                            result_each_file_identify['parameters']['units'] = \
                            pd_job_layer_info_cuurent_layer['units'].values[0]
                        result_each_file_identify['parameters']['scale'] = 1  # 改参数在kernel1.9版本中添加
                    print('now para'.center(190, '-'))
                    print(result_each_file_identify)

            except Exception as e:
                print(e)
                print("有异常情况发生")
            Input.file_translate(path=folder_path + '\\' + job.split("_ep")[0] + '\\' + each_file, job=job, step='orig', layer=each_file,
                                 param=result_each_file_identify['parameters'])

        #保存料号
        BASE.save_job(job)


class GetInfo:
    pass


if __name__ == "__main__":
    pass


