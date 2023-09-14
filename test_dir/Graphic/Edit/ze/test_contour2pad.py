import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditFeatureIndex:
    # @pytest.mark.Feature index
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Contour2pad'))
    def testFeatureIndex(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Contour2pad铜皮转pad功能（ID: 17870）
        '''
        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'orig'  # 定义需要执行比对的step名
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

        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep,temp_compressed_path)  # 用悦谱CAM打开料号


        #1.选取多个铜皮转换成pad,然后删除所有pad(验证多个surface可正确转换为pad)
        points_location = []
        points_location.append([2 * 1000000, 25 * 1000000])
        points_location.append([2 * 1000000, 30 * 1000000])
        points_location.append([5 * 1000000, 30 * 1000000])
        points_location.append([5 * 1000000, 25 * 1000000])      # 添加一个方形铜皮
        Layers.add_surface(job_ep, step, ['l1'], True, [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)
        Selection.select_feature_by_id(job_ep, step, 'l1', [0, 5, 22, 25, 2526])
        Layers.contour2pad(job_ep, step, ['l1'], 1*25400, 0.01*25400, 99999*25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l1'])
        Layers.delete_feature(job_ep, step, ['l1'])#删除所有pad
        Selection.reset_selection()     # 重置筛选
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l1')

        #2.添加特殊surface，全部转为pad之后将其删除（验证不规则surface可正确转换为pad）
        Layers.add_round_surface(job_ep, step, ['l2'], True,
                                 [{'.out_flag': '233'}, {'.pattern_fill': ''}], 200*25400, 200*25400, 300 * 25400)#添加圆surface
        points_location = []
        points_location.append([15 * 1000000, 30 * 1000000])
        points_location.append([37 * 1000000, 26 * 1000000])
        points_location.append([55 * 1000000, 20 * 1000000])
        points_location.append([61 * 1000000, 15 * 1000000])
        points_location.append([39 * 1000000, 16 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#添加多边形
        Layers.contour2pad(job_ep, step, ['l2'], 1 * 25400, 0.01 * 25400, 99999 * 25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Layers.delete_feature(job_ep, step, ['l2'])#删除L2层所有pad
        Selection.reset_selection()     # 重置筛选
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l2')

        #3.不选中物件，整层一起执行，转换pad成功(可正确将单层surface全部转换为pad)
        Layers.contour2pad(job_ep, step, ['l3'], 1 * 25400, 0.01 * 25400, 99999 * 25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Layers.delete_feature(job_ep, step, ['l3'])  # 删除该层所有pad
        Selection.reset_selection()  # 重置筛选
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l3')

        #4.不选中物件，将多层打上影响层一起执行，转换pad成功(可正确将多层surface全部转换为pad)
        Layers.contour2pad(job_ep, step, ['l4','l5'], 1 * 25400, 0.01 * 25400, 99999 * 25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l4','l5'])
        Layers.delete_feature(job_ep, step, ['l4','l5'])  # 删除该层所有pad
        Selection.reset_selection()  # 重置筛选
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l5')

        #5.验证suffix栏功能正确
        Layers.contour2pad(job_ep, step, ['l6'], 1 * 25400, 0.01 * 25400, 99999 * 25400, 'bf')
        Layers.add_pad(job_ep, step, ['l6bf'], "s100", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)#在新创建的层添加一个pad，证明suffix栏功能正确
        #GUI.show_layer(job_ep, step, 'l6bf')


        #6.验证tolerance栏、min size栏和max size栏的正确性
        points_location = []
        points_location.append([10 * 25400, 1000 * 25400])
        points_location.append([10 * 25400, 1500 * 25400])
        points_location.append([510 * 25400, 1500 * 25400])
        points_location.append([510 * 25400, 1000 * 25400])  # 添加一个边长500mil的方形大铜皮
        Layers.add_surface(job_ep, step, ['l7'], True, [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)
        points_location = []
        points_location.append([900 * 25400, 1000 * 25400])
        points_location.append([900 * 25400, 1008 * 25400])
        points_location.append([908 * 25400, 1008 * 25400])
        points_location.append([908 * 25400, 1000 * 25400])  # 添加一个边长8mil的小铜皮
        Layers.add_surface(job_ep, step, ['l7'], True, [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)
        Layers.contour2pad(job_ep, step, ['l7'], 0.5 * 25400, 8.51 * 25400, 499.4 * 25400, '+++')#设置公差值为0.5，最小尺寸为8mil,最大尺寸为499mil
        #GUI.show_layer(job_ep, step, 'l7')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l7'])
        Layers.delete_feature(job_ep, step, ['l7'])  # 删除所有pad,若添加的两个Surface都被保留了下来，则证明tolerance栏、min size栏和max size栏的功能正确
        Selection.reset_selection()  # 重置筛选
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l7')


        '''
        验证使用Contour to Pad功能转换附件指定物件，转换后的图形与原图形保持一致
        bug编号：4814
        功能用例ID：3590
        影响版本号：1.1.8.2
        '''
        Selection.select_feature_by_id(job_ep, step, 'xqy_top', [9164, 9165, 9166, 9167])  # 选中目标物件,（X=2.852,y=5.089Inch）处的surface
        Layers.contour2pad(job_ep, step, ['xqy_top'], 1*25400, 0.01*25400, 99999*25400, '+++')#转换pad后的图形与原图形保持一致
        # BASE.undo(job_ep,step)
        # GUI.show_layer(job_ep, step, 'xqy_top')

        '''
        验证按照要求在smb层执行Contour to Pad操作，软件正确执行不卡死
        bug编号：4809
        功能用例ID：3600
        影响版本号：1.1.8.2
        '''
        Layers.contour2pad(job_ep, step, ['p1_pre_smb'], 1*25400, 0.01*25400, 99999*25400, '+++')#执行Contour to Pad操作，软件正确执行不卡死
        #GUI.show_layer(job_ep, step, 'p1_pre_smb')



        '''
        验证gts+++层正确执行surface转pad操作，且图形不变形
        bug编号：3660
        对应功能用例ID：3612、3616、3617、3618共四条用例
        '''
        Layers.contour2pad(job_ep, step, ['3660_h3_orig_gts','3616_pre_l6',], 1*25400, 0.01*25400, 99999*25400, '+++')#执行Contour to Pad操作，软件正确执行不变形
        #GUI.show_layer(job_ep, step, 'p1_pre_smb')



        save_job(job_ep, temp_ep_path)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = os.path.join(RunConfig.temp_path_g,'g',job_yg)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, 'ep', job_ep)
        print("job_testep_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        layerInfo = []
        for each in ['l1', 'l2', 'l3', 'l4', 'l5', 'l6','l6bf', 'l7']:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = ''
            layerInfo.append(each_dict)

        print("layerInfo:", layerInfo)
        job1, job2 = job_yg, job_ep
        step1, step2 = 'orig', 'orig'
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
        data["all_result_g1"] = compareResult['all_result_g']
        data['g1_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']

        # ----------------------------------------开始验证结果--------------------------------------------------------
        Print.print_with_delimiter('比对结果信息展示--开始')
        if data['g1_vs_total_result_flag'] == True:
            print("恭喜您！料号导入比对通过！")
        if data['g1_vs_total_result_flag'] == False:
            print("Sorry！料号导入比对未通过，请人工检查！")
        Print.print_with_delimiter('分割线', sign='-')
        print('G1转图的层：', data["all_result_g1"])
        Print.print_with_delimiter('分割线', sign='-')
        # print('悦谱比图结果：', all_result_ep_vs_g_g2)
        Print.print_with_delimiter('比对结果信息展示--结束')
        assert data['g1_vs_total_result_flag'] == True
        for key in data['all_result_g1']:
            assert data['all_result_g1'][key] == "正常"
        Print.print_with_delimiter("断言--结束")