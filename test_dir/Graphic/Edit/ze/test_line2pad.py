import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job

class TestGraphicEditLine2pad:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Line2pad'))
    def testLine2pad(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Line2pad线转pad功能(ID：17869)
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


        #1.验证line为起点与终点相同的线段，转换pad成功
        Layers.add_line(job_ep, step, ['l1'], 'r100', 3 * 2540000, 10 * 2540000, 3 * 2540000, 10 * 2540000, True, [])
        Selection.select_feature_by_id(job_ep, step, 'l1', [2526])
        Layers.line2pad(job_ep, step, ['l1'])#Line转pad
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['r100'])
        Selection.select_features_by_filter(job_ep, step, ['l1'])#选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l1'])
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l1')

        #2.验证line为起点与终点不相同的线段，转换pad成功
        Layers.add_line(job_ep, step, ['l2'], 'r100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 10 * 2540000, True, [])
        Selection.select_feature_by_id(job_ep, step, 'l2', [907])
        Layers.line2pad(job_ep, step, ['l2'])  # Line转pad
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['oval600x100'])
        Selection.select_features_by_filter(job_ep, step, ['l2'])  # 选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l2'])
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l2')

        #3.验证场景1:带旋转角度的线段，正确转换pad（转换pad后的角度不发生改变）
           #验证场景2:r开头的线段正确转为oval类型的pad
        Layers.add_line(job_ep, step, ['l3'], 'r100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 15 * 2540000, True, [])
        #添加了一个带角度的物件
        Selection.select_feature_by_id(job_ep, step, 'l3', [2380])
        Layers.line2pad(job_ep, step, ['l3'])  # Line转pad，且被转换的pad为oval类型
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['oval807.107x100'])
        Selection.select_features_by_filter(job_ep, step, ['l3'])  # 选中已转为pad的物件，复制一个出来
        Layers.copy2other_layer(job_ep, step, 'l3', 'l3', False,2540000, 10 * 2540000, 0, 0, 0, 0, 0)
        #复制成功，且被复制的pad角度未发生改变，证明该用例通过
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l3')

        #4.验证s开头的线段正确转为rect类型的pad
        Layers.add_line(job_ep, step, ['l4'], 's100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 15 * 2540000, True, [])
        # 添加了一个带角度的物件
        Selection.select_feature_by_id(job_ep, step, 'l4', [930])
        Layers.line2pad(job_ep, step, ['l4'])  # Line转pad,且被转换的pad为rect类型
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['rect807.107x100'])
        Selection.select_features_by_filter(job_ep, step, ['l4'])  # 选中已转为pad的物件，复制一个出来
        Layers.copy2other_layer(job_ep, step, 'l4', 'l4', False, 2540000, 10 * 2540000, 0, 0, 0, 0, 0)
        # rect类型的pad复制成功，且被复制的pad角度未发生改变
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l4')

        #5.验证单层状态下不选择任何物件，使用Line to Pad功能(只对线有作用)
        Layers.delete_feature(job_ep, step,['l5'])#先删除L5层的整层物件
        Layers.add_line(job_ep, step, ['l5'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        Layers.delete_feature(job_ep, step, ['l5'])  # 先删除L5层的整层物件
        Layers.add_line(job_ep, step, ['l5'], 'r5', 10000000, 50000000, 30000000, 50000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        # 增加两条线
        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l5'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 添加面
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l5'], 'r7.874', 40 * 1000000, 25 * 1000000,
                       40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)  # 添加弧
        Layers.line2pad(job_ep, step, ['l5'])#不选中任何物件，直接使用Line to Pad功能
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l5'])  # 选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l5'])
        #GUI.show_layer(job_ep, step, 'l5')


        # 6.验证多层状态下不选择任何物件，使用Line to Pad功能(只对线有作用)
        Layers.delete_feature(job_ep, step, ['l6','l7'])  # 先删除L6和L7层的整层物件
        Layers.add_line(job_ep, step, ['l6','l7'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        Layers.add_line(job_ep, step, ['l6','l7'], 'r5', 10000000, 50000000, 30000000, 50000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        # 增加两条线

        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l6','l7'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 添加面
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l6','l7'], 'r7.874', 40 * 1000000, 25 * 1000000,
                       40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)  # 添加弧
        Layers.line2pad(job_ep, step, ['l6','l7'])  # 不选中任何物件，直接使用Line to Pad功能，作用于l6层和l7层
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l6','l7'])  # 选中l6层和l7层已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l6','l7'])
        #GUI.show_layer(job_ep, step, 'l7')


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
        for each in ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']:
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