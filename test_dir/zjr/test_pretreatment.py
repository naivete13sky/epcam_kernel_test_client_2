import pytest,os, time,json,shutil,sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput,MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI,BASE,Guide,Analysis
from epkernel.Action import Information,Selection
from epkernel.Edition import Layers,Matrix
from epkernel.Output import save_job
import re

class TestPretreatment:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Pretreatment'))
    def test_pretreatment(self, job_id, g, prepare_test_job_clean_g):
        '''
        id:11633,本用例测试Gerber274X自动化模拟人工做料，到前处理
        '''
        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_gerber_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')
        # temp_g2_path = os.path.join(temp_path, 'g2')


        # ----------悦谱转图。先下载并解压原始gerber文件,拿到解压后的文件夹名称，此名称加上_ep就是我们要的名称。然后转图。-------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='rar')
        # print('job_ep:',job_ep)
        MyInput(folder_path=os.path.join(temp_gerber_path, os.listdir(temp_gerber_path)[0].lower()),
                job=job_ep, step=r'orig', job_id=job_id, save_path=temp_ep_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        print("all_layers_list_job_ep1:",all_layers_list_job_ep)

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')
        Input.open_job(job_yg, temp_g_path)  # 用悦谱CAM打开料号
        all_layers_list_job_yg = Information.get_layers(job_yg)

        step_orig = 'orig'

        if (job_id == 11633):
            """-----------修改层别名称，定义层别属性，重新排序-----------"""
            new_attribute = {
                        '0114-1240-1-10.drl': ['board','drill', 'drl1-10', 1, 18],
                        'bottom.art': ['board','signal','bot', 1, 15],
                        'bot_mask.art': ['board','solder_mask','smb', 1, 15],
                        'bot_past.art': ['board','solder_paste','spb', 1, 15],
                        'bot_silk.art': ['board', 'silk_screen', 'ssb', 1, 14],
                        'drill.art': ['misc', 'signal', 'map', 1, 18],
                        'top.art': ['board', 'signal', 'top', 9, 1],
                        'top_mask.art': ['board', 'solder_mask', 'smt', 14, 1],
                        'top_past.art': ['board', 'solder_paste', 'spt', 15, 1],
                        'top_silk.art': ['board', 'silk_screen', 'sst', 18, 2],
                        'layer2.art': ['board', 'signal', 'l2', 5, 5],
                        'layer3.art': ['board', 'signal', 'l3', 6, 6],
                        'layer4.art': ['board', 'signal', 'l4', 7, 7],
                        'layer5.art': ['board', 'signal', 'l5', 8, 8],
                        'layer6.art': ['board', 'signal', 'l6', 9, 9],
                        'layer7.art': ['board', 'signal', 'l7', 10, 10],
                        'layer8.art': ['board', 'signal', 'l8', 11, 11],
                        'layer9.art': ['board', 'signal', 'l9', 12, 12]
                        }
            for layer_name in all_layers_list_job_ep:
                Matrix.change_matrix_row(job_ep, layer_name, new_attribute[layer_name][0], new_attribute[layer_name][1], new_attribute[layer_name][2], True)
                Matrix.move_layer(job_ep, new_attribute[layer_name][3], new_attribute[layer_name][4])
            # GUI.show_matrix(job_ep)

            """"----------定原点（没有专门的函数，可以试用move2same_layer代替）----------"""

            """----------复制orig到step----------"""
            step_net = 'net'
            step_name =  Matrix.copy_step(job_ep,step_orig)
            Matrix.change_matrix_column(job_ep,step_name,step_net)
            outline = 'outline'
            Matrix.create_layer(job_ep,outline,-1)
            # GUI.show_matrix(job_ep)

            #获取top层外框线
            ret = BASE.classify_polyline(job_ep, step_net, 'top')
            info = json.loads(ret)['paras']['polygons']
            indexList = []
            items = [1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955,
                     1956, 1957, 1958, 1959]
            for item in info:
                if item[0]['feature_index'] in items:
                    pattern = re.compile(r''''feature_index': \d+,''')  # 正则
                    result = pattern.findall(str(item))
                    pattern2 = re.compile(r'''\d+''')
                    for each in result:
                        result2 = pattern2.findall(each)
                        indexList.append(int(result2[0]))
                    break
            #将top层的外框线选中
            Selection.select_feature_by_id(job_ep, step_net, 'top', indexList)
            # GUI.show_layer(job_ep, step_net, 'top')
            #将选中的外框线复制到outline层
            Layers.copy2other_layer(job_ep,step_net,'top',outline,False,0,0,0,0,0,0,0)
            # GUI.show_layer(job_ep, step_net, outline)

            """-----------创建profile线-----------"""
            #打开筛选器
            Selection.set_featuretype_filter(1,1,1,1,1,1,1)
            #根据筛选器设置条件选中物件
            Selection.select_features_by_filter(job_ep,step_net,['outline'])
            #创建profile线
            Layers.create_profile(job_ep, step_net, 'outline')
            # GUI.show_layer(job_ep,step_net,'outline')

            """--------去除板外杂物----------"""
            layers = ['spt','smt','top','l2','l3','l4','l5','l6','l7','l8','l9','bot','smb','spb','drl1-10']
            #clip_area功能，删除板外杂物
            Layers.clip_area_use_profile(job_ep,step_net,layers,0,0,0,1,1,1,1,0)
            # GUI.show_layer(job_ep, step_net, 'spt')
            #选中执行层中的指定坐标物件，并执行删除
            for layer in layers:
                if layer != 'drl1-10':
                    locations = [4 * 1000000, 21.5 * 1000000], [2 * 1000000, 20.9 * 1000000], [2 * 1000000, 17.7 * 1000000], [2 * 1000000, 16.5 * 1000000] \
                        , [2 * 1000000, 6 * 1000000], [2 * 1000000, 4.8 * 1000000], [2 * 1000000, 1.1 * 1000000], [4 * 1000000, 0.25 * 1000000], [3.67 * 1000000, 1 * 1000000]
                    #连续选中物件
                    Selection.set_selection(False,True,True,True,True,True)
                    for location_x, location_y in locations:
                        Selection.select_feature_by_point(job_ep, step_net, layer, location_x, location_y)
                    #判断是否有物件选中，有选中执行删除
                    if Information.has_selected_features(job_ep, step_net, layer):
                        Layers.delete_feature(job_ep, step_net, [layer])
                        # GUI.show_layer(job_ep, step_net, layer)
                    else:
                        print("没有选中物件！")
                    Selection.reset_selection()

            # 获取sst、ssb层外框线
            layers = ['sst','ssb']
            Selection.set_selection(False, True, True, True, True, True)
            for layer in layers:
                if layer == 'sst':
                    sstIds = [3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757,
                               3758, 3759, 3760, 3761, 3762, 3763, 3766, 3765, 3764]
                    Selection.select_feature_by_id(job_ep,step_net,layer,sstIds)
                elif layer == 'ssb':
                    ssbIds = [4870, 4871, 4872, 4873, 4874, 4875, 4876, 4877, 4878, 4879, 4880, 4881, 4882, 4883, 4884,
                               4885, 4886, 4887, 4888, 4889]
                    Selection.select_feature_by_id(job_ep, step_net, layer, ssbIds)

                points = []
                points.append([68 * 1000000, -15 * 1000000])
                points.append([68 * 1000000, -11 * 1000000])
                points.append([85 * 1000000, -11 * 1000000])
                points.append([85 * 1000000, -15 * 1000000])
                Selection.select_feature_by_polygon(job_ep, step_net, layer, points)
            if Information.has_selected_features(job_ep,step_net,layer):
                Layers.delete_feature(job_ep, step_net, layers)
            else:
                print("没有选中物件！")
            Selection.reset_selection()
            # GUI.show_layer(job_ep, step_net, layer)

            """"----------将线路层正、负片合并----------"""
            layers = ['top','l2','l3','l4','l5','l6','l7','l8','l9','bot']
            # 设置筛选器物件类型，选中所有负极性物件
            Selection.set_featuretype_filter(0, 1, 1, 1, 1, 1, 1)
            Selection.select_features_by_filter(job_ep,step_net,layers)
            # 设置筛选器物件类型，选中所有征集性surface
            Selection.set_featuretype_filter(1, 0, 0, 1, 0, 0, 0)
            Selection.select_features_by_filter(job_ep, step_net, layers)
            # 执行congtourize，将正、负片合并
            Layers.contourize(job_ep,step_net,layers,6350,True,7620,0)
            # 重置筛选器
            Selection.reset_select_filter()

            """----------孔层定属性----------"""
            # 自动定义孔层属性
            layers = ['drl1-10']
            drill_plated = 'drill-plated'
            drill_via = 'drill-via'
            Matrix.create_layer(job_ep, drill_plated, -1)
            Matrix.create_layer(job_ep, drill_via, -1)

            BASE.auto_classify_attribute(job_ep,step_net,layers)
            #按物件属性copy，验证
            Selection.set_attribute_filter(0,[{'.drill':'plated'}])
            Selection.select_features_by_filter(job_ep, step_net, layers)
            Layers.copy2other_layer(job_ep, step_net, 'drl1-10', drill_plated, False, 0, 0, 0, 0, 0, 0, 0)
            Selection.reset_select_filter()
            Selection.set_attribute_filter(0, [{'.drill': 'via'}])
            Selection.select_features_by_filter(job_ep, step_net, layers)
            Layers.copy2other_layer(job_ep, step_net, 'drl1-10', drill_via, False, 0, 0, 0, 0, 0, 0, 0)
            Selection.reset_select_filter()
            # GUI.show_layer(job_ep, step_net, drill_plated)

            """将防焊层非pad物件转成pad"""
            # 设置筛选器物件类型，选中smt和smb层的非pad物件
            layers = ['smt','smb']
            Selection.set_featuretype_filter(1,1,1,1,1,1,0)
            Selection.select_features_by_filter(job_ep,step_net,layers)
            # 执行contour2pad，将surface转成pad
            Layers.contour2pad(job_ep,step_net,layers,1*25400,5*25400,99999*25400,'+++')
            # 重置筛选器
            Selection.reset_select_filter()
            # GUI.show_layer(job_ep,step_net,'smt')

            """检查外层SMD PAD"""
            layers = ['top','bot']
            ids = {'top':2403, 'bot':1305}
            #将指定的arc转成line
            for layer in layers:
                print("=ids[layer]=",ids[layer])
                Selection.select_feature_by_id(job_ep, step_net, layer, [ids[layer]])
                # GUI.show_layer(job_ep, step_net, layer)
                if Information.has_selected_features(job_ep, step_net, layer):
                    # GUI.show_layer(job_ep, step_net, layer)
                    Layers.arc2lines(job_ep, step_net, layers, 1, True)
                    # GUI.show_layer(job_ep, step_net, layer)
                else:
                    print("没有选中物件！")

            #将指定的line转成surface
            points = []
            points.append([58.25 * 1000000, 19.60 * 1000000])
            points.append([57.57 * 1000000, 20.14 * 1000000])
            points.append([57.97 * 1000000, 20.87 * 1000000])
            points.append([58.77 * 1000000, 20.66 * 1000000])
            points.append([58.81 * 1000000, 20.01 * 1000000])
            for layer in layers:
                Selection.select_feature_by_polygon(job_ep,step_net,layer,points)
                if Information.has_selected_features(job_ep, step_net, layer):
                    # GUI.show_layer(job_ep, step_net, layer)
                    Layers.contourize(job_ep, step_net, [layer], 6350, True, 7620, 1)
                    # GUI.show_layer(job_ep, step_net, layer)
                else:
                    print("没有选中物件！")

            #将指定的surface转成pad
            for layer in layers:
                Selection.select_feature_by_id(job_ep, step_net, layer, [ids[layer]])
                if Information.has_selected_features(job_ep, step_net, layer):
                    # GUI.show_layer(job_ep, step_net, layer)
                    Layers.contour2pad(job_ep, step_net, [layer], 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
                    # GUI.show_layer(job_ep, step_net, layer)
                else:
                    print("没有选中物件！")

            # GUI.show_layer(job_ep, step_net, 'bot+++')

            """----------复制net到pre----------"""
            step_pre = 'pre'
            Matrix.copy_step(job_ep, step_net)
            Matrix.change_matrix_column(job_ep, 'net+1', step_pre)
            # BASE.save_job(job_ep)
            # Matrix.create_layer(job_ep, 'outline', -1)
            # GUI.show_matrix(job_ep)

            """---------线路层自动定属性,手动检查是否定正确----------"""
            # 自动定义线路层属性
            layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'bot']
            BASE.auto_classify_attribute(job_ep, step_pre, layers)
            # GUI.show_matrix(job_ep)
            #修改错误属性
            for layer in layers:
                if layer == 'top':
                    ids = [668, 671, 669, 670, 667]
                    Selection.select_feature_by_id(job_ep, step_pre, layer, ids)
                    if Information.has_selected_features(job_ep, step_pre, layer):
                        # GUI.show_layer(job_ep, step_pre, layer)
                        BASE.modify_attributes(job_ep, step_pre, [layer], 1,[{'.fiducial_name': 'cle'}, {'.smd': ''}])
                        # GUI.show_layer(job_ep, step_pre, layer)
                    else:
                        print("没有选中物件！")
                elif layer == 'bot':
                    ids = [104, 105, 106, 107, 154, 183, 204, 205]
                    Selection.select_feature_by_id(job_ep, step_pre, layer, ids)
                    if Information.has_selected_features(job_ep, step_pre, layer):
                        # GUI.show_layer(job_ep, step_pre, layer)
                        BASE.modify_attributes(job_ep, step_pre, [layer], 1, [{'.via': 'pad'}])
                        # GUI.show_layer(job_ep, step_pre, layer)
                    else:
                        print("没有选中物件！")

            """----------孔层补偿----------"""
            layers = ['drl1-10']
            #via孔补偿2条,npt孔补偿2条，pt孔补偿4条，补完取刀径值（看刀径表）
            Selection.reset_select_filter()
            # Selection.set_featuretype_filter(1, 0, 0, 0, 0, 0, 1)
            Selection.set_include_symbol_filter(['r7.87'])
            Selection.select_features_by_filter(job_ep, step_pre, layers)
            Layers.resize_global(job_ep, step_pre, layers, 0, 1.973 * 25400)
            Selection.reset_select_filter()
            # Selection.set_featuretype_filter(1, 0, 0, 0, 0, 0, 1)
            Selection.set_include_symbol_filter(['r19.681','r102.358'])
            Selection.select_features_by_filter(job_ep, step_pre, layers)
            Layers.resize_global(job_ep, step_pre, layers, 0, 3.941 * 25400)
            Selection.reset_select_filter()
            Selection.set_include_symbol_filter(['r19.685'])
            Selection.select_features_by_filter(job_ep, step_pre, layers)
            Layers.resize_global(job_ep, step_pre, layers, 0, 3.937 * 25400)
            Selection.reset_select_filter()
            # GUI.show_layer(job_ep, step_pre, 'drl1-10')

            layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'bot', 'drl1-10']
            for layer in layers:
                BASE.split_layer_with_attribute(job_ep, step_pre, layer)
            # GUI.show_layer(job_ep, step_pre, 'top')



            """----------分析钻孔（看看有没有重复孔，touch孔，孔太近这些问题）"""
            # path = r'C:\cc\ep_local\product\EP-CAM\version\EP-CAM_release_1.1.5.1_2_jiami\Release\rangesconfig\DrillChecks\DrillRanges.json'
            # with open(path, 'r', encoding='utf8')as fp:
            #     json_data = json.load(fp)
            #
            # data = json_data['rangesList']
            # for i in range(len(data)):
            #     data[i]['RedLv'] = float(data[i]['RedLv'])
            #     data[i]['YellowLv'] = float(data[i]['YellowLv'])
            #     data[i]['GreenLv'] = float(data[i]['GreenLv'])
            # ranges = {'rangesList' : data}
            #
            # rett = BASE.drill_check(job_ep,step_pre,['drl1-10'],'',5080000,True,True,True,True,True,True,True,False,True,2,ranges)
            # print(rett)
            # GUI.show_layer(job_ep, step_pre, 'drl1-10')
            #
            #
            # GUI.show_layer(job_ep,'orig','top')
            # Input.file_identify()
            save_job(job_ep, temp_ep_path)

        elif (job_id == 0):
            """-----------修改层别名称，定义层别属性，重新排序-----------"""
            for layer_name in all_layers_list_job_ep:
                if layer_name == 'bottom.art':
                    Matrix.change_matrix_row(job_ep, 'bottom.art', 'board', 'signal', 'bot', True)
                    Matrix.move_layer(job_ep, 1, 11)
                elif layer_name == 'drill-1-6.art':
                    Matrix.change_matrix_row(job_ep, 'drill-1-6.art', 'misc', 'signal', 'map', True)
                    Matrix.move_layer(job_ep, 1, 15)
                elif layer_name == 'dual720pdisp_p0-1-6.drl':
                    Matrix.change_matrix_row(job_ep, 'dual720pdisp_p0-1-6.drl', 'board', 'drill', 'drl1-6', True)
                    Matrix.move_layer(job_ep, 1, 14)
                elif layer_name == 'l2_gnd1.art':
                    Matrix.change_matrix_row(job_ep, 'l2_gnd1.art', 'board', 'signal', 'l2', True)
                    Matrix.move_layer(job_ep, 1, 5)
                elif layer_name == 'l3_sig.art':
                    Matrix.change_matrix_row(job_ep, 'l3_sig.art', 'board', 'signal', 'l3', True)
                    Matrix.move_layer(job_ep, 1, 5)
                elif layer_name == 'l4_pwr2.art':
                    Matrix.change_matrix_row(job_ep, 'l4_pwr2.art', 'board', 'signal', 'l4', True)
                    Matrix.move_layer(job_ep, 1, 5)
                elif layer_name == 'l5_gnd2.art':
                    Matrix.change_matrix_row(job_ep, 'l5_gnd2.art', 'board', 'signal', 'l5', True)
                    Matrix.move_layer(job_ep, 1, 5)
                elif layer_name == 'outline.art':
                    Matrix.change_matrix_row(job_ep, 'outline.art', 'misc', 'signal', 'outline', True)
                    Matrix.move_layer(job_ep, 5, 15)
                elif layer_name == 'paste_bot.art':
                    Matrix.change_matrix_row(job_ep, 'paste_bot.art', 'board', 'solder_paste', 'spb', True)
                    Matrix.move_layer(job_ep, 5, 10)
                elif layer_name == 'paste_top.art':
                    Matrix.change_matrix_row(job_ep, 'paste_top.art', 'board', 'solder_paste', 'spt', True)
                    Matrix.move_layer(job_ep, 5, 1)
                elif layer_name == 'silk_bot.art':
                    Matrix.change_matrix_row(job_ep, 'silk_bot.art', 'board', 'silk_screen', 'ssb', True)
                    Matrix.move_layer(job_ep, 7, 9)
                elif layer_name == 'silk_top.art':
                    Matrix.change_matrix_row(job_ep, 'silk_top.art', 'board', 'silk_screen', 'sst', True)
                    Matrix.move_layer(job_ep, 7, 2)
                elif layer_name == 'solder_bot.art':
                    Matrix.change_matrix_row(job_ep, 'solder_bot.art', 'board', 'solder_mask', 'smb', True)
                    Matrix.move_layer(job_ep, 10, 8)
                elif layer_name == 'solder_top.art':
                    Matrix.change_matrix_row(job_ep, 'solder_top.art', 'board', 'solder_mask', 'smt', True)
                    Matrix.move_layer(job_ep, 11, 3)
                elif layer_name == 'top.art':
                    Matrix.change_matrix_row(job_ep, 'top.art', 'board', 'signal', 'top', True)
                    Matrix.move_layer(job_ep, 15, 4)
            """"----------定原点（没有专门的函数，可以试用move2same_layer代替）----------"""
            layers = Information.get_layers(job_ep)
            Selection.select_features_by_filter(job_ep,step_orig,layers)
            Layers.move2same_layer(job_ep,step_orig,layers,0,-5000000)
            # BASE.show_layer(job_ep,step_orig,'outline')

            """----------复制orig到step----------"""
            BASE.save_job(job_ep)
            step_net = 'net'
            step_name = Matrix.copy_step(job_ep, step_orig)
            Matrix.change_matrix_column(job_ep, step_name, step_net)
            BASE.save_job(job_ep)
            outline = 'outline+1'
            Matrix.create_layer(job_ep, outline, -1)
            BASE.save_job(job_ep)
            # GUI.show_matrix(job_ep)

            # 获取outline层外框线
            # Selection.se
            ret = BASE.classify_polyline(job_ep, step_net, 'outline')
            info = json.loads(ret)['paras']['polygons']
            indexList = []
            items = [6, 7, 8, 9, 10, 11, 12, 13]
            for item in info:
                if item[0]['feature_index'] in items:
                    pattern = re.compile(r''''feature_index': \d+,''')  # 正则
                    result = pattern.findall(str(item))
                    pattern2 = re.compile(r'''\d+''')
                    for each in result:
                        result2 = pattern2.findall(each)
                        indexList.append(int(result2[0]))
                    break
            # 将top层的外框线选中
            Selection.select_feature_by_id(job_ep, step_net, 'outline', indexList)
            # GUI.show_layer(job_ep, step_net, 'outline')
            # 将选中的外框线复制到outline层
            Layers.copy2other_layer(job_ep, step_net, 'outline', outline, False, 0, 0, 0, 0, 0, 0, 0)
            # GUI.show_layer(job_ep, step_net, outline)

            """-----------创建profile线-----------"""
            # 打开筛选器
            Selection.set_featuretype_filter(1, 1, 1, 1, 1, 1, 1)
            # 根据筛选器设置条件选中物件
            Selection.select_features_by_filter(job_ep, step_net, [outline])
            # 创建profile线
            Layers.create_profile(job_ep, step_net, outline)
            # GUI.show_layer(job_ep,step_net,outline)

            """--------去除版外杂物----------"""
            layers = ['spt','sst','smt','top','l2','l3','l4','l5','bot','smb','ssb','spb','drl1-6']
            Layers.clip_area_use_profile(job_ep, step_net, layers, False, False, 0, 1, 1, 1, 1, 1)
            # GUI.show_layer(job_ep, step_net, 'spt')
            for layer in layers:
                if layer != 'drl1-10':
                    Selection.select_feature_by_point(job_ep, step_net, layer, 0 * 1000000, 2 * 1000000)
                    if(Information.has_selected_features(job_ep, step_net, layer)) == True :
                        Layers.delete_feature(job_ep, step_net, [layer])
                        GUI.show_layer(job_ep, step_net, layer)

            #         Layers.delete_feature(job_ep, step_net, [layer])
            # # 获取sst、ssb层所有
            # layers = ['sst', 'ssb']
            # for layer in layers:
            #     if layer == 'sst':
            #         sstList = [3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757,
            #                    3758, 3759, 3760, 3761, 3762, 3763, 3766, 3765, 3764]
            #         Selection.select_feature_by_id(job_ep, step_net, layer, sstList)
            #         Layers.delete_feature(job_ep, step_net, [layer])
            #     elif layer == 'ssb':
            #         ssbList = [4870, 4871, 4872, 4873, 4874, 4875, 4876, 4877, 4878, 4879, 4880, 4881, 4882, 4883, 4884,
            #                    4885, 4886, 4887, 4888, 4889]
            #         Selection.select_feature_by_id(job_ep, step_net, layer, ssbList)
            #         Layers.delete_feature(job_ep, step_net, [layer])
            # for layer in layers:
            #     points = []
            #     points.append([68 * 1000000, -15 * 1000000])
            #     points.append([68 * 1000000, -11 * 1000000])
            #     points.append([85 * 1000000, -11 * 1000000])
            #     points.append([85 * 1000000, -15 * 1000000])
            #     Selection.select_feature_by_polygon(job_ep, step_net, layer, points)
            # Layers.delete_feature(job_ep, step_net, layers)
            # # GUI.show_layer(job_ep, step_net, layer)
            #
            # """"----------将线路层正、负片合并----------"""
            # layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'bot']
            # # 设置筛选器物件类型，选中所有负极性物件
            # Selection.set_featuretype_filter(0, 1, 1, 1, 1, 1, 1)
            # Selection.select_features_by_filter(job_ep, step_net, layers)
            # # 设置筛选器物件类型，选中所有征集性surface
            # Selection.set_featuretype_filter(1, 0, 0, 1, 0, 0, 0)
            # Selection.select_features_by_filter(job_ep, step_net, layers)
            # # 执行congtourize，将正、负片合并
            # Layers.contourize(job_ep, step_net, layers, 6350, True, 7620, 0)
            # # 重置筛选器
            # Selection.reset_select_filter()
            #
            # """----------孔层定属性----------"""
            # # 自动定义孔层属性
            # layers = ['drl1-10']
            # drill_plated = 'drill-plated'
            # drill_via = 'drill-via'
            # Matrix.create_layer(job_ep, drill_plated, -1)
            # Matrix.create_layer(job_ep, drill_via, -1)
            #
            # BASE.auto_classify_attribute(job_ep, step_net, layers)
            # # 按物件属性copy，验证
            # Selection.set_attribute_filter(0, [{'.drill': 'plated'}])
            # Selection.select_features_by_filter(job_ep, step_net, layers)
            # Layers.copy2other_layer(job_ep, step_net, 'drl1-10', drill_plated, False, 0, 0, 0, 0, 0, 0, 0)
            # Selection.reset_select_filter()
            # Selection.set_attribute_filter(0, [{'.drill': 'via'}])
            # Selection.select_features_by_filter(job_ep, step_net, layers)
            # Layers.copy2other_layer(job_ep, step_net, 'drl1-10', drill_via, False, 0, 0, 0, 0, 0, 0, 0)
            # Selection.reset_select_filter()
            # # GUI.show_layer(job_ep, step_net, drill_plated)
            #
            # # GUI.show_layer(job_ep, step_net, 'top')
            #
            # """将防焊层非pad物件转成pad"""
            # # 设置筛选器物件类型，选中smt和smb层的非pad物件
            # layers = ['smt', 'smb']
            # Selection.set_featuretype_filter(1, 1, 1, 1, 1, 1, 0)
            # Selection.select_features_by_filter(job_ep, step_net, layers)
            # # 执行contour2pad，将surface转成pad
            # Layers.contour2pad(job_ep, step_net, layers, 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
            # # 重置筛选器
            # Selection.reset_select_filter()
            # # GUI.show_layer(job_ep,step_net,'smt')
            #
            # """检查外层SMD PAD"""
            # layers = ['top', 'bot']
            # Selection.select_feature_by_id(job_ep, step_net, layers[0], [2403])
            # Selection.select_feature_by_id(job_ep, step_net, layers[1], [1305])
            # Layers.arc2lines(job_ep, step_net, layers, 1, True)
            # points = []
            # points.append([58.25 * 1000000, 19.60 * 1000000])
            # points.append([57.57 * 1000000, 20.14 * 1000000])
            # points.append([57.97 * 1000000, 20.87 * 1000000])
            # points.append([58.77 * 1000000, 20.66 * 1000000])
            # points.append([58.81 * 1000000, 20.01 * 1000000])
            # Selection.select_feature_by_polygon(job_ep, step_net, layers[0], points)
            # Selection.select_feature_by_polygon(job_ep, step_net, layers[1], points)
            # Layers.contourize(job_ep, step_net, layers, 6350, True, 7620, 1)
            # Selection.select_feature_by_id(job_ep, step_net, layers[0], [2403])
            # Selection.select_feature_by_id(job_ep, step_net, layers[1], [1305])
            # Layers.contour2pad(job_ep, step_net, layers, 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
            # # GUI.show_layer(job_ep,step_net,'top')
            #
            # """----------复制net到pre----------"""
            # step_pre = 'pre'
            # Matrix.copy_step(job_ep, step_net)
            # Matrix.change_matrix_column(job_ep, 'net+1', step_pre)
            # BASE.save_job(job_ep)
            # # Matrix.create_layer(job_ep, 'outline', -1)
            # # GUI.show_matrix(job_ep)
            #
            # """---------线路层自动定属性----------"""
            # # 自动定义线路层属性
            # layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'bot']
            # BASE.auto_classify_attribute(job_ep, step_pre, layers)
            #
            # # 检查线路层属性
            # Selection.select_feature_by_id(job_ep, step_pre, layers[0], [668, 671, 669, 670, 667])
            # bool = Information.has_selected_features(job_ep, step_pre, layers[0])
            # if bool == True:
            #     BASE.modify_attributes(job_ep, step_pre, [layers[0]], 1, [{'.fiducial_name': 'cle'}, {'.smd': ''}])
            #
            # Selection.select_feature_by_id(job_ep, step_pre, layers[9], [104, 105, 106, 107, 154, 183, 204, 205])
            # bool = Information.has_selected_features(job_ep, step_pre, layers[9])
            # if bool == True:
            #     BASE.modify_attributes(job_ep, step_pre, [layers[9]], 1, [{'.via': 'pad'}])
            #
            # # GUI.show_layer(job_ep, step_pre, layers[0])
            #
            # """----------孔层补偿----------"""
            # layers = ['drl1-10']
            # # via孔补偿2条,npt孔补偿2条，pt孔补偿4条，补完取刀径值（看刀径表）
            # Selection.reset_select_filter()
            # # Selection.set_featuretype_filter(1, 0, 0, 0, 0, 0, 1)
            # Selection.set_include_symbol_filter(['r7.87'])
            # Selection.select_features_by_filter(job_ep, step_pre, layers)
            # Layers.resize_global(job_ep, step_pre, layers, 0, 1.973 * 25400)
            # Selection.reset_select_filter()
            # # Selection.set_featuretype_filter(1, 0, 0, 0, 0, 0, 1)
            # Selection.set_include_symbol_filter(['r19.681', 'r102.358'])
            # Selection.select_features_by_filter(job_ep, step_pre, layers)
            # Layers.resize_global(job_ep, step_pre, layers, 0, 3.941 * 25400)
            # Selection.reset_select_filter()
            # Selection.set_include_symbol_filter(['r19.685'])
            # Selection.select_features_by_filter(job_ep, step_pre, layers)
            # Layers.resize_global(job_ep, step_pre, layers, 0, 3.937 * 25400)
            # Selection.reset_select_filter()
            # # GUI.show_layer(job_ep, step_pre, 'drl1-10')
            #
            #
            # BASE.show_matrix(job_ep)


        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        all_layers_list_job_ep = Information.get_layers(job_ep)#比图前重新获取ep做完前处理后的所有层别
        # print("all_layers_list_job_ep:", all_layers_list_job_ep)
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_yg)
        job_ep_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_yg, step1=step_pre, all_layers_list_job1=all_layers_list_job_yg, job2=job_ep,
                                step2=step_pre, all_layers_list_job2=all_layers_list_job_ep)
        data["all_result_g"] = r['all_result_g']
        data["all_result"] = r['all_result']
        data['g_vs_total_result_flag'] = r['g_vs_total_result_flag']
        assert len(all_layers_list_job_yg) == len(r['all_result_g'])

        # ----------------------------------------开始验证结果--------------------------------------------------------
        Print.print_with_delimiter('比对结果信息展示--开始')
        if data['g_vs_total_result_flag'] == True:
            print("恭喜您！料号导入比对通过！")
        if data['g_vs_total_result_flag'] == False:
            print("Sorry！料号导入比对未通过，请人工检查！")
        Print.print_with_delimiter('分割线', sign='-')
        print('G转图的层：', data["all_result_g"])
        Print.print_with_delimiter('分割线', sign='-')
        print('所有层：', data["all_result"])
        Print.print_with_delimiter('分割线', sign='-')
        # print('G1转图的层：', data["all_result_g1"])
        # Print.print_with_delimiter('分割线', sign='-')

        Print.print_with_delimiter("断言--开始")
        assert data['g_vs_total_result_flag'] == True
        for key in data['all_result_g']:
            assert data['all_result_g'][key] == "正常"



