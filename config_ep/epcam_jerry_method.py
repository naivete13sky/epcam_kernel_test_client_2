import json
import os
import shutil
import sys
import time
import urllib
from pathlib import Path

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import RunConfig
from epkernel import Configuration, Input, GUI,BASE,Output
from epkernel.Edition import Job,Matrix,Layers
from epkernel.Action import Information,Selection

class Pretreatment(object):
    def __init__(self,*,job):
        pass
        self.job = job

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