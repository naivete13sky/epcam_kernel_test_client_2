import pytest,os, time,json,shutil,sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput,MyOutput
from config_ep.epcam_jerry_method import Pretreatment
from config_g.g_cc_method import GInput
from epkernel import Input, GUI,BASE,Guide,Analysis,Configuration
from epkernel.Action import Information,Selection
from epkernel.Edition import Layers,Matrix
from epkernel.Output import save_job
import re
from datetime import datetime

class TestPretreatment:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Pretreatment'))
    def test_pretreatment(self, job_id, g, prepare_test_job_clean_g):
        '''
        id:11633,15892本用例测试Gerber274X自动化模拟人工做料，到前处理
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
        step_net = 'net'
        step_pre = 'pre'

        pretreatment = Pretreatment(job = job_ep, job_id = job_id)
        if (job_id == 11633):
            """-----------修改层别名称，定义层别属性，重新排序-----------"""
            #定义新的层别名称，属性，层别顺序
            new_layer_attribute = {
                '0114-1240-1-10.drl': ['board', 'drill', 'drl1-10', 18],
                'bottom.art': ['board', 'signal', 'bot', 17],
                'bot_mask.art': ['board', 'solder_mask', 'smb', 17],
                'bot_past.art': ['board', 'solder_paste', 'spb', 17],
                'bot_silk.art': ['board', 'silk_screen', 'ssb', 16],
                'drill.art': ['misc', 'signal', 'map', 18],
                'top.art': ['board', 'signal', 'top', 1],
                'top_mask.art': ['board', 'solder_mask', 'smt', 1],
                'top_past.art': ['board', 'solder_paste', 'spt', 1],
                'top_silk.art': ['board', 'silk_screen', 'sst', 2],
                'layer2.art': ['board', 'signal', 'l2', 5],
                'layer3.art': ['board', 'signal', 'l3', 6],
                'layer4.art': ['board', 'signal', 'l4', 7],
                'layer5.art': ['board', 'signal', 'l5', 8],
                'layer6.art': ['board', 'signal', 'l6', 9],
                'layer7.art': ['board', 'signal', 'l7', 10],
                'layer8.art': ['board', 'signal', 'l8', 11],
                'layer9.art': ['board', 'signal', 'l9', 12]
            }
            # 修改层别名称，属性，排序
            pretreatment.change_layer_attribute(new_layer_attribute)
            # GUI.show_matrix(job_ep)

            """"----------定原点（没有专门的函数，可以试用move2same_layer代替）----------"""

            """----------复制orig到net，并创建一个ouline层----------"""
            outline = 'outline'
            pretreatment.copy2step(step_orig, step_net, outline)
            # GUI.show_matrix(job_ep)

            """----------获取外框线，复制到outline层，创建profile线----------"""
            layer = 'top'
            feature_indexs = [1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955,
                         1956, 1957, 1958, 1959]
            # 根据index选中外框线
            pretreatment.select_feature_type(step_net, layer, ['ids'], [], feature_indexs, [])
            # GUI.show_layer(job_ep,step_net,layer)
            # 将选中的外框线复制到outline层
            Layers.copy2other_layer(job_ep, step_net, layer, outline, False, 0, 0, 0, 0, 0, 0, 0)
            # 选中outline层的外框线
            Selection.set_featuretype_filter(1, 1, 1, 1, 1, 1, 1)
            Selection.select_features_by_filter(job_ep, step_net, [outline])
            # 创建profile线
            Layers.create_profile(job_ep, step_net, outline)
            # GUI.show_layer(job_ep,step_net,outline)

            """--------去除板外杂物----------"""
            layers = []
            # 获取所有board属性层别
            board_layers = Information.get_board_layers(job_ep)
            # 获取所有drill类型层别
            drl_layers = Information.get_drill_layers(job_ep)
            # 获取所有silk_screen类型的层别
            silk_layers = Information.get_silkscreen_layers(job_ep)
            # 遍历所有board属性层别
            for layer in board_layers:
                # 如果层别不在drill类型和silk screen类型中就添加到layers中
                if layer not in drl_layers and layer not in silk_layers:
                    layers.append(layer)
            # 执行clip_area功能删除板外的杂物
            Layers.clip_area_use_profile(job_ep, step_net, layers, 0, 0, 0, 1, 1, 1, 1, 0)
            # GUI.show_layer(job_ep, step_net, layers[0])

            # 定义物件坐标数组手动删除板外剩余杂物
            locations = [4 * 1000000, 21.5 * 1000000], [2 * 1000000, 20.9 * 1000000], [2 * 1000000, 17.7 * 1000000], [2 * 1000000, 16.5 * 1000000], \
                  [2 * 1000000, 6 * 1000000], [2 * 1000000, 4.8 * 1000000], [2 * 1000000, 1.1 * 1000000], [4 * 1000000,0.25 * 1000000], [3.67 * 1000000, 1 * 1000000]
            # 定义sst层物件index数组
            sstIndexs = [3744, 3745, 3746, 3747, 3748, 3749, 3750, 3751, 3752, 3753, 3754, 3755, 3756, 3757,
                      3758, 3759, 3760, 3761, 3762, 3763, 3766, 3765, 3764]
            # 定义ssb层物件index数组
            ssbIndexs = [4870, 4871, 4872, 4873, 4874, 4875, 4876, 4877, 4878, 4879, 4880, 4881, 4882, 4883, 4884,
                      4885, 4886, 4887, 4888, 4889]
            # 定义框选范围
            points = []
            points.append([68 * 1000000, -15 * 1000000])
            points.append([68 * 1000000, -11 * 1000000])
            points.append([85 * 1000000, -11 * 1000000])
            points.append([85 * 1000000, -15 * 1000000])

            # 设置连续选中物件
            Selection.set_selection(False, True, True, True, True, True)
            # 根据物件坐标选中线路层、防焊层、锡膏层物件
            for layer in layers:
                pretreatment.select_feature_type(step_net, layer, ['locations'], locations, [], [])
            # GUI.show_layer(job_ep, step_net, layer)

            # 根据物件index和框选范围选中sst层和ssb层物件
            ids = []
            for layer in silk_layers:
                if layer == 'sst':
                    ids = sstIndexs
                elif layer == 'ssb':
                    ids = ssbIndexs
                pretreatment.select_feature_type(step_net, layer, ['ids','points'], [], ids, points)
                layers.append(layer)
            # GUI.show_layer(job_ep, step_net, layer)

            # 判断如有物件选中，则执行删除
            if Information.has_selected_features(job_ep,step_net,layer):
                Layers.delete_feature(job_ep, step_net, layers)
            else:
                print("没有选中物件！")
            # 重置连续选中
            Selection.reset_selection()
            # GUI.show_layer(job_ep, step_net, layer)

            """"----------将线路层正、负片合并----------"""
            # 获取所有线路层
            signal_layers = Information.get_signal_layers(job_ep)
            # 将线路层正、负片合并
            pretreatment.signal_layers_contourize(step_net, signal_layers)

            """----------孔层定属性----------"""
            # 定义孔层属性(如果有错误属性需要手动修改)
            BASE.auto_classify_attribute(job_ep,step_net,drl_layers)
            # GUI.show_layer(job_ep, step_net, drill_plated)

            """将防焊层非pad物件转成pad"""
            # 获取所有防焊层
            solder_mask_layers = Information.get_soldermask_layers(job_ep)
            # 将防焊层非pad物件转成pad
            pretreatment.solder_mask_layers2pad(step_net, solder_mask_layers)
            # GUI.show_layer(job_ep,step_net,'smt')

            """检查外层SMD PAD"""
            # 获取所有外层
            out_layers = Information.get_outer_layers(job_ep)
            # 定义物件index字典
            ids = {'top':2403, 'bot':1305}
            # 定义框选范围
            points = []
            points.append([58.25 * 1000000, 19.60 * 1000000])
            points.append([57.57 * 1000000, 20.14 * 1000000])
            points.append([57.97 * 1000000, 20.87 * 1000000])
            points.append([58.77 * 1000000, 20.66 * 1000000])
            points.append([58.81 * 1000000, 20.01 * 1000000])

            for layer in out_layers:
                # 将指定的arc转成line
                pretreatment.change_symbol(step_net, layer, ['arc'], ['ids'], [], [ids[layer]], [])
                # 将指定的line转成surface
                pretreatment.change_symbol(step_net, layer, ['line'], ['points'], [], [], points)
                # 将指定的surface转成pad
                pretreatment.change_symbol(step_net, layer, ['surface'], ['ids'], [], [ids[layer]], [])
            # GUI.show_layer(job_ep, step_net, layer)

            """----------复制net到pre----------"""
            outline = ''
            pretreatment.copy2step(step_net, step_pre, outline)
            # GUI.show_matrix(job_ep)


            """---------线路层自动定属性,手动修改错误属性----------"""
            # 自动定义线路层属性
            BASE.auto_classify_attribute(job_ep, step_pre, signal_layers)
            #修改错误属性
            attributes = []
            ids = []
            for layer in signal_layers:
                if layer == 'top':
                    ids = [668, 671, 669, 670, 667]
                    attributes = [{'.fiducial_name': 'cle'}, {'.smd': ''}]
                elif layer == 'bot':
                    ids = [104, 105, 106, 107, 154, 183, 204, 205]
                    attributes = [{'.via': 'pad'}]
                else:
                    ids = []
                # 修改top和bot层错误属性
                pretreatment.change_attribute(step_pre, layer, attributes, ['ids'], [], ids, [])

            """----------孔层补偿----------"""
            #via孔补偿2条,npt孔补偿2条，pt孔补偿4条，补完取刀径值（看刀径表）
            Selection.reset_select_filter()
            # Selection.set_featuretype_filter(1, 0, 0, 0, 0, 0, 1)
            feature_items = ['r7.87', 'r19.681', 'r102.358', 'r19.685']
            resize = 0
            for item in feature_items:
                if item in ['r7.87']:
                    Selection.set_include_symbol_filter([item])
                    resize = 1.973 * 25400
                elif item in ['r19.681','r102.358']:
                    Selection.set_include_symbol_filter([item])
                    resize = 3.941 * 25400
                elif item in ['r19.685']:
                    Selection.set_include_symbol_filter([item])
                    resize = 3.937 * 25400
                Selection.select_features_by_filter(job_ep, step_pre, drl_layers)
                Layers.resize_global(job_ep, step_pre, drl_layers, 0, resize)
            Selection.reset_select_filter()
            # GUI.show_layer(job_ep, step_pre, 'drl1-10')

            # 将线路层和孔层按照属性分层，验证自动定属性是否正确
            for layer in board_layers:
                if layer not in signal_layers or layer not in solder_mask_layers:
                    BASE.split_layer_with_attribute(job_ep, step_pre, layer)
            GUI.show_layer(job_ep, step_pre, 'top')



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

        elif (job_id == 15892):# 未写好
            """-----------修改层别名称，定义层别属性，重新排序-----------"""
            # 定义新的层名和属性字典
            new_layer_attribute = {
                'bottom.art': ['board', 'signal', 'bot', 15],
                'drill-1-6.art': ['misc', 'signal', 'map', 15],
                'dual720pdisp_p0-1-6.drl': ['board', 'drill', 'drl1-6', 14],
                'l2_gnd1.art': ['board', 'signal', 'l2', 1],
                'l3_sig.art': ['board', 'signal', 'l3', 2],
                'l4_pwr2.art': ['board', 'signal', 'l4', 3],
                'l5_gnd2.art': ['board', 'signal', 'l5', 4],
                'outline.art': ['misc', 'signal', 'outline', 15],
                'paste_bot.art': ['board', 'solder_paste', 'spb', 12],
                'paste_top.art': ['board', 'solder_paste', 'spt', 1],
                'silk_bot.art': ['board', 'silk_screen', 'ssb', 11],
                'silk_top.art': ['board', 'silk_screen', 'sst', 2],
                'solder_bot.art': ['board', 'solder_mask', 'smb', 10],
                'solder_top.art': ['board', 'solder_mask', 'smt', 3],
                'top.art': ['board', 'signal', 'top', 4]
            }
            # 修改层别名称和属性
            pretreatment.change_layer_attribute(new_layer_attribute)
            # GUI.show_matrix(job_ep)


            """"----------定原点（没有专门的函数，可以试用move2same_layer代替）----------"""
            # 获取新的层名
            layers = Information.get_layers(job_ep)
            # 将所有层选中
            Selection.select_features_by_filter(job_ep, step_orig, layers)
            Layers.move2same_layer(job_ep, step_orig, layers, 0, -5000000)
            # GUI.show_layer(job_ep, step_orig, 'outline')

            """----------复制orig到step----------"""
            outline = 'outline+1'
            pretreatment.copy2step(step_orig, step_net, outline)
            # GUI.show_matrix(job_ep)

            """----------获取外框线，复制到outline层，创建profile线----------"""
            layer = 'outline'
            feature_indexs = [6, 7, 8, 9, 10, 11, 12, 13]
            # 根据index选中外框线
            pretreatment.select_feature_type(step_net, layer, ['ids'], [], feature_indexs, [])
            # GUI.show_layer(job_ep,step_net,layer)
            # 将选中的外框线复制到outline层
            Layers.copy2other_layer(job_ep, step_net, layer, outline, False, 0, 0, 0, 0, 0, 0, 0)
            # 选中outline层的外框线
            Selection.set_featuretype_filter(1, 1, 1, 1, 1, 1, 1)
            Selection.select_features_by_filter(job_ep, step_net, [outline])
            # 创建profile线
            Layers.create_profile(job_ep, step_net, outline)
            # GUI.show_layer(job_ep,step_net,outline)

            """--------去除版外杂物----------"""
            # 获取所有board属性层别
            board_layers = Information.get_board_layers(job_ep)
            Layers.clip_area_use_profile(job_ep, step_net, board_layers, 0, 0, 0, 1, 1, 1, 1, 0)
            # GUI.show_layer(job_ep, step_net, board_layers[0])

            """"----------将线路层正、负片合并----------"""
            signal_layers = Information.get_signal_layers(job_ep)
            pretreatment.signal_layers_contourize(step_net, signal_layers)
            # GUI.show_layer(job_ep, step_net, signal_layers[0])

            """----------检查孔层，补孔----------"""
            map = 'map'
            drl_layers = Information.get_drill_layers(job_ep)
            map_feature_indexs = [0, 1, 7796, 7797]
            pretreatment.select_feature_type(step_net, map, ['ids'], [], map_feature_indexs, [])
            Layers.copy2other_layer(job_ep, step_net, map, drl_layers[0], False, 0, 0, 0, 0, 0, 0, 0)


            change_symbols = {
                (1904,1905) : 'rect118.11x51.1811',
                (1906,1907) : 'rect23.6221x110.236'
            }
            drl_feature_index = [1904, 1905, 1906, 1907]
            for index in drl_feature_index:
                for index_range,symbol in change_symbols.items():
                    if index in index_range:
                        pretreatment.select_feature_type(step_net, drl_layers[0], ['ids'], [], [index], [])
                        Layers.change_feature_symbols(job_ep, step_net, drl_layers, symbol, False)
            # GUI.show_layer(job_ep, step_net, drl_layers[0])

            """----------孔层定属性----------"""
            BASE.auto_classify_attribute(job_ep, step_net, drl_layers)
            GUI.show_layer(job_ep, step_net, drl_layers[0])
            Configuration.read_auto_matrix_rule()

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
        print("job_ep_remote_path",job_ep_remote_path)
        # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        vs_star_time = datetime.now()
        print("比对开始时间", vs_star_time)
        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_yg, step1=step_pre, all_layers_list_job1=all_layers_list_job_yg, job2=job_ep,
                                step2=step_pre, all_layers_list_job2=all_layers_list_job_ep)
        vs_end_time = datetime.now()
        print("比对开始时间", vs_end_time)
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



