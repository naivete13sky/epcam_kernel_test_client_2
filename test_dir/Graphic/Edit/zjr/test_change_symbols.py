import pytest, os, json, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS
from epkernel import Input, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditChangesymbols:
    '''
    id:17804，共执行1个测试用例，实现10个方法，覆盖50个测试场景
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Change_Symbol'))
    def testChange_symbols (self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Change_symbols功能
        '''
        g = RunConfig.driver_g  # 拿到G软件
        test_cases = 0 # 用户统计执行了多少条测试用例
        data = {}  # 存放比对结果信息
        # 取到临时目录，如果存在旧目录，则删除
        temp_path = RunConfig.temp_path_base
        if os.path.exists(temp_path):
            if RunConfig.gSetupType == 'local':
                # os.remove(self.tempGerberPath)#此方法容易因权限问题报错
                shutil.rmtree(temp_path)
            if RunConfig.gSetupType == 'vmware':
                # 使用PsExec通过命令删除远程机器的文件
                from cc.cc_method import RemoteCMD
                myRemoteCMD = RemoteCMD(psexec_path='cc', computer='192.168.1.3',
                                        username='administrator',
                                        password='cc')
                command_operator = 'rd /s /q'
                command_folder_path = os.path.join(RunConfig.temp_path_g)
                command = r'cmd /c {} "{}"'.format(command_operator, command_folder_path)
                myRemoteCMD.run_cmd(command)
                print("remote delete finish")

        # vs_time_g = str(int(time.time()))  # 比对时间
        # data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        # data["job_id"] = job_id

        # 取到临时目录
        # temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        # print("temp_path:", temp_path)
        # temp_compressed_path = os.path.join(temp_path, 'compressed')
        # temp_ep_path = os.path.join(temp_path, 'ep')
        # temp_g_path = os.path.join(temp_path, 'g')

        temp_gerber_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')
        temp_g2_path = os.path.join(temp_path, 'g2')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')
        Input.open_job(job_g,temp_g_path)
        all_layers_list_job_g = Information.get_layers(job_g)

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_gerber_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        # GUI.show_matrix(job_ep)
        # BASE.show_layer(job_id, 'orig', 'top')
        step = 'orig'

        '''
        用例名称：对正极性的line, pad, surface, arc, text不同物件类型分别执行change_symbol操作
        预期：line,pad,arc图形发生变更；surface和text图形未发生变更，和执行前一样
        执行场景数：5个
        '''
        layer = 'top'
        features_id = [1954, 2525, 34, 1956, 2526]#id依序分别为line, pad, surface, arc, text
        for id in features_id:
            print("=id=:",id)
            Selection.select_feature_by_id(job_ep, step, layer, [id])
            # GUI.show_layer(job_ep, step, layer)
            Layers.change_feature_symbols(job_ep, step, [layer],'r220',False)
            Selection.unselect_features(job_ep, step, layer)
        test_cases = test_cases + len(features_id)
        # GUI.show_layer(job_ep, step, layer)

        '''
        用例名称：对负极性的line, pad, surface, arc, text不同物件类型分别执行change_symbol操作
        预期：line,pad,arc图形发生变更；surface和text图形未发生变更，和执行前一样
        执行场景数：5个
        '''
        layer = 'top'
        features_id = [1954, 2525, 34, 1956, 2526]  # id依序分别为line, pad, surface, arc, text
        for id in features_id:
            print("=id=:", id)
            Selection.select_feature_by_id(job_ep, step, layer, [id])
            # GUI.show_layer(job_ep, step, layer)
            Layers.change_feature_symbols(job_ep, step, [layer], 'r220', False)
            Selection.unselect_features(job_ep, step, layer)
        test_cases = test_cases + len(features_id)
        '''
        用例名称：执行层未选中物件进行change_symbol操作
        场景1：执行层中存在line（或pad、或arc）和surface（或text）
        预期：图形未发生变更，和执行前一样
        场景2：执行层中只有line、pad、arc三种物件
        预期：图形发生变更
        场景3：执行层中只有surface,text两种物件
        预期：图形未发生变更，和执行前一样
        执行场景数：3个
        '''
        layers = ['top_all','top_line_pad_arc','top_surface_text']#top_all层中五种物件都存在，top_line_pad_arc层中存在
        # line、pad、arc三种物件，top_surface_text层中存在surface、text两种物件
        for layer in layers:
            print("=layer=:",layer)
            Layers.change_feature_symbols(job_ep, step, [layer],'r220',False)
        # GUI.show_layer(job_ep, step, layer)
        test_cases = test_cases + len(layers)
        '''
        测试用例：使用无效值对pad执行change_symbol
        场景1：值为文字
        预期：图形未发生变更，和执行前一样
        场景2：值为数字
        预期：图形未发生变更，和执行前一样
        场景3：值为特殊字符
        预期：图形未发生变更，和执行前一样
        执行测试场景：3个
        '''
        # layer = 'top'
        feature_id = 2515
        symbols = ['abc',123,'!']
        for symbol in symbols:
            print("=symbol=:",symbol)
            Selection.select_feature_by_id(job_ep, step, layer, [feature_id])
            # GUI.show_layer(job_ep, step, layer)
            Layers.change_feature_symbols(job_ep, step, [layer], symbol, False)
            Selection.unselect_features(job_ep, step, layer)
            # GUI.show_layer(job_ep, step, layer)
        test_cases = test_cases + len(symbols)
        '''
        测试用例名称：Reset pad angle参数设置为yes对有旋转角度的pad进行复位
        预期：已旋转的角度复位
        执行测试场景：1个
        '''
        layer = 'top'
        feature_id = 2528
        Selection.select_feature_by_id(job_ep, step, layer, [feature_id])
        # GUI.show_layer(job_ep, step, layer)
        Layers.change_feature_symbols(job_ep, step, [layer], 'rect50x100', True)
        # GUI.show_layer(job_ep, step, layer)
        test_cases = test_cases + 1
        '''
        测试用例名称：对圆pad执行symbol中29种类型操作:Round、
        预期：图形发生变更
        执行测试场景：29个
        '''
        layer = 'symbol_type'
        symbols = ['r300', 's200', 'rect200x300', 'rect200x300xr50', 'rect200x300xc50', 'oval200x300', 'di200x300',
                   'oct200x300x30', 'donut_r200x100', 'donut_s200x100', 'hex_l200x300x20', 'hex_s200x300x30', 'bfr200',
                   'bfs200', 'tri200x300', 'oval_h200x100', 'thr200x100x20x5x5', 'ths200x100x20x5x5',
                   's_ths200x100x10x5x5', 's_tho200x100x45x4x5', 'sr_ths200x100x10x5x5', 'rc_ths200x100x90x3x20x20',
                   'rc_tho200x100x90x4x20x20', 'el200x300', 'moire20x10x5x10x20x20', 'hole250xvx10x20', 'hole260xnx10x20',
                   'hole270xpx10x20', 'null1000']
        Selection.reverse_select(job_ep, step, layer)
        result = Information.get_selected_features_infos(job_ep, step, layer)
        index = 0
        #获取执行层中所有物件id,逐个执行change_symbol
        if len(symbols) == len(result):
            for item in result:
                pass
                print("=index=",index)
                feature_index = item['feature_index']
                Selection.unselect_features(job_ep, step, layer)
                Selection.select_feature_by_id(job_ep, step, layer, [feature_index])
                Layers.change_feature_symbols(job_ep, step, [layer], symbols[index], False)
                index += 1
                # GUI.show_layer(job_ep, step, layer)
        else:
            print("请检查物件数量是否一致！")
        test_cases = test_cases + len(symbols)

        '''
        验证Round/Round Thermal类型Num Spokes值为0时，软件不会卡死
        预期：软件不会卡死
        bug：4572
        功能测试用例：3553
        影响版本号：1.1.7.0
        执行测试场景：1个
        '''
        layer = 'symbol_type'
        feature_index = 27
        symbol = 'thr200x150x90x0x10' #Round/Round Thermal类型
        Selection.select_feature_by_id(job_ep, step, layer, [feature_index])
        try:
            Layers.change_feature_symbols(job_ep, step, [layer], symbol, False)
        except Exception as e:
            print(e)
        test_cases = test_cases + 1

        '''
        验证change_symbol功能的吸取器可以正常获取物件属性
        预期：可以获取物件属性，软件不闪退
        bug：3276
        功能测试用例：3569
        影响版本号：1.1.0.0
        执行测试场景：1个
        '''
        layer = 'top'
        points = []
        points.append({'ix': 28 * 1000000, 'iy': 24 * 1000000})
        points.append({'ix': 28 * 1000000, 'iy': 26 * 1000000})
        points.append({'ix': 31 * 1000000, 'iy': 26 * 1000000})
        points.append({'ix': 31 * 1000000, 'iy': 24 * 1000000})
        points.append({'ix': 28 * 1000000, 'iy': 24 * 1000000})
        ret = BASE.get_symbol_name(job_ep, step, layer, points)
        symbol = json.loads(ret)['paras']['symbol_name']
        print('symbols1:', symbol)
        # GUI.show_layer(job_ep, step, layer)
        test_cases = test_cases + 1

        '''
        验证使用吸附器读取特殊pad的形状和大小，可以对其他pad执行改变，
        预期：可以获取物件属性，软件不闪退
        bug：3991
        功能测试用例：3578
        影响版本号：1.1.3.18
        执行测试场景：1个
        '''
        layer = 'gts'
        points = []
        points.append({'ix': 104 * 1000000, 'iy': 19 * 1000000})
        points.append({'ix': 104 * 1000000, 'iy': 24 * 1000000})
        points.append({'ix': 106 * 1000000, 'iy': 24 * 1000000})
        points.append({'ix': 106 * 1000000, 'iy': 19 * 1000000})
        points.append({'ix': 104 * 1000000, 'iy': 19 * 1000000})
        ret = BASE.get_symbol_name(job_ep, step, layer, points)
        symbol = json.loads(ret)['paras']['symbol_name']
        Selection.select_feature_by_id(job_ep, step, layer, [372])
        print('symbols2:', symbol)
        Layers.change_feature_symbols(job_ep, step, [layer], symbol[0], False)
        # GUI.show_layer(job_ep, step, layer)
        test_cases = test_cases + 1

        '''
        验证对带有.rout_chain属性的物件执行change_symbol
        预期：无法改变，软件不闪退
        bug：4828
        功能测试用例：3579
        影响版本号：1.1.8.2
        执行测试场景：1个
        '''
        layer = 'gts'
        symbol = 'r200'
        Selection.set_attribute_filter(0,[{'.rout_chain':'1'}])
        Selection.select_features_by_filter(job_ep, step, [layer])
        Layers.change_feature_symbols(job_ep, step, [layer], symbol, False)
        Selection.reset_select_filter()
        test_cases = test_cases + 1

        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)
        print("test_cases：", test_cases)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        # all_layer_from_org = [each for each in DMS().get_job_layer_fields_from_dms_db_pandas(job_id, field='layer_org')]
        drill_layers = [each.lower() for each in DMS().get_job_layer_drill_from_dms_db_pandas_one_job(job_id)['layer']]

        layerInfo = []
        for each in all_layers_list_job_g:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = 'drill' if each in drill_layers else ''
            layerInfo.append(each_dict)

        print("layerInfo:", layerInfo)

        job1, job2 = job_g, job_ep
        step1, step2 = 'orig', 'orig'
        # 导入要比图的资料,并打开

        job_g_remote_path = os.path.join(RunConfig.temp_path_g, r'g', job_g)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, r'ep', job_ep)
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)

        # 校正孔用
        temp_path_local_info1 = os.path.join(temp_path, 'info1')
        if not os.path.exists(temp_path_local_info1):
            os.mkdir(temp_path_local_info1)
        temp_path_local_info2 = os.path.join(temp_path, 'info2')
        if not os.path.exists(temp_path_local_info2):
            os.mkdir(temp_path_local_info2)

        compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                        job1=job1, step1=step1,
                                        job2=job2, step2=step2,
                                        layerInfo=layerInfo,
                                        adjust_position=True, jsonPath=r'my_config.json')
        print('compareResult_input_vs:', compareResult)
        data["all_result_g"] = compareResult['all_result_g']
        data['g_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']
        assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])

        # ----------------------------------------开始验证结果--------------------------------------------------------
        print('比对结果信息展示--开始'.center(192, '*'))
        if data['g_vs_total_result_flag'] == True:
            print("恭喜您！料号导入比对通过！")
        if data['g_vs_total_result_flag'] == False:
            print("Sorry！料号导入比对未通过，请人工检查！")
        print('分割线'.center(192, '-'))
        print('G转图的层：', data["all_result_g"])

        print('比对结果信息展示--结束'.center(192, '*'))

        print("断言--开始".center(192, '*'))
        assert data['g_vs_total_result_flag'] == True
        for key in data['all_result_g']:
            assert data['all_result_g'][key] == "正常"
        print("断言--结束".center(192, '*'))

        # # 获取原始层文件信息，最全的
        #
        # all_result = {}  # all_result存放原始文件中所有层的比对信息
        # for layer_org in all_layer_from_org:
        #     layer_org_find_flag = False
        #     layer_org_vs_value = ''
        #     for each_layer_g_result in compareResult['all_result_g']:
        #         if each_layer_g_result == str(layer_org).lower().replace(" ", "-").replace("(", "-").replace(")", "-"):
        #             layer_org_find_flag = True
        #             layer_org_vs_value = compareResult['all_result_g'][each_layer_g_result]
        #     if layer_org_find_flag == True:
        #         all_result[layer_org] = layer_org_vs_value
        #     else:
        #         all_result[layer_org] = 'G转图中无此层'


        # job_g_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
        #     'temp' + "_" + str(job_id) + "_" + vs_time_g, job_g)
        # print("job_remote_path:", job_g_remote_path)
        # job_ep_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
        #     'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        # print("job_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        # g.import_odb_folder(job_g_remote_path)
        # g.import_odb_folder(job_ep_remote_path)
        #
        # r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
        #                         job1=job_g, step1=step, all_layers_list_job1=all_layers_list_job_g, job2=job_ep,step2=step,
        #                         all_layers_list_job2=all_layers_list_job_ep, adjust_position=True)
        # data["all_result_g1"] = r['all_result_g']
        # data["all_result"] = r['all_result']
        # data['g1_vs_total_result_flag'] = r['g_vs_total_result_flag']
        # Print.print_with_delimiter("断言--看一下G1转图中的层是不是都有比对结果")
        # assert len(all_layers_list_job_g) == len(r['all_result_g'])
        # # ----------------------------------------开始验证结果--------------------------------------------------------
        # Print.print_with_delimiter('比对结果信息展示--开始')
        # if data['g1_vs_total_result_flag'] == True:
        #     print("恭喜您！料号导入比对通过！")
        # if data['g1_vs_total_result_flag'] == False:
        #     print("Sorry！料号导入比对未通过，请人工检查！")
        #
        # Print.print_with_delimiter('分割线', sign='-')
        # print('G1转图的层：', data["all_result_g1"])
        # Print.print_with_delimiter('分割线', sign='-')
        # Print.print_with_delimiter('比对结果信息展示--结束')
        #
        # assert data['g1_vs_total_result_flag'] == True
        # for key in data['all_result_g1']:
        #     assert data['all_result_g1'][key] == "正常"
        # Print.print_with_delimiter("断言--结束")
