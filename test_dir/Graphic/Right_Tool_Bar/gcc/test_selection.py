import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicSelection:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Selection'))
    def test_selection(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Selection多条件筛选功能，用例数：15
        ID:36899
        BUG:
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l3+1', 'l3+2', 'l3+3', 'l3+4', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'bot', 'smb']

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

        # 取到临时目录
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        # 1、筛选物件类型，再取消筛选symbol
        Selection.set_featuretype_filter(True, False, True, True, True, True, True)
        Selection.select_features_by_filter(job_ep, step, ['smt'])
        Selection.reset_select_filter()
        Selection.set_symbol_filter(True, ['r13.78'])
        Selection.unselect_features(job_ep, step, 'smt')
        Layers.delete_feature(job_ep, step, ['smt'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 2、筛选symbol，再取消筛选单一物件属性
        Selection.set_symbol_filter(True, ['r4', 'r5', 'r10', 'r12', 'r14'])
        Selection.select_features_by_filter(job_ep, step, ['top'])
        Selection.set_attribute_filter(0, [{'.fy':''}])
        Selection.unselect_features(job_ep, step, 'top')
        Layers.delete_feature(job_ep, step, ['top'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 3、筛选物件属性，再取消筛选单一物件类型
        Selection.set_attribute_filter(1, [{'.pth_pad': ''}, {'.ball_pad': ''}, {'.npth_pad': ''}, {'.area': ''}])
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.unselect_features(job_ep, step, 'l2')
        Layers.delete_feature(job_ep, step, ['l2'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 4、根据线的长度范围筛选
        Selection.set_featuretype_filter(True, False, False, False, False, True, False)
        Selection.set_slot_range_filter(True, False, True, False, 1*254000, 5*25400000, 0, 90)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Layers.delete_feature(job_ep, step, ['l3'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 5、根据线的角度范围筛选
        Selection.set_featuretype_filter(True, False, False, False, False, True, False)
        Selection.set_slot_range_filter(True, False, False, True, 1*254000, 5*25400000, 0, 45)
        Selection.select_features_by_filter(job_ep, step, ['l3+1'])
        Layers.delete_feature(job_ep, step, ['l3+1'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 6、根据槽孔的长度范围筛选
        Selection.set_include_symbol_filter(['oval100x50', 'oval50x20', 'oval50x200'])
        Selection.set_slot_range_filter(False, True, True, False, 1*254000, 1*2540000, 0, 90)
        Selection.select_features_by_filter(job_ep, step, ['l3+2'])
        Layers.delete_feature(job_ep, step, ['l3+2'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 7、根据槽孔的角度范围筛选
        Selection.set_include_symbol_filter(['oval100x50', 'oval50x20', 'oval50x200'])
        Selection.set_slot_range_filter(False, True, False, True, 1*254000, 5*25400000, 0, 45)
        Selection.select_features_by_filter(job_ep, step, ['l3+3'])
        Layers.delete_feature(job_ep, step, ['l3+3'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 8、根据槽孔的长度角度范围筛选
        Selection.set_include_symbol_filter(['oval100x50', 'oval50x20', 'oval50x200'])
        Selection.set_slot_range_filter(False, True, True, True, 1*254000, 1*2540000, 0, 45)
        Selection.select_features_by_filter(job_ep, step, ['l3+4'])
        Layers.delete_feature(job_ep, step, ['l3+4'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 9、根据线的长度和角度范围筛选
        Selection.set_featuretype_filter(True, False, False, False, False, True, False)
        Selection.set_slot_range_filter(True, False, True, True, 1*254000, 5*25400000, 0, 45)
        Selection.select_features_by_filter(job_ep, step, ['l3+4'])
        Layers.delete_feature(job_ep, step, ['l3+4'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 10、筛选profile线内正、负极性pad、正极性arc
        Selection.set_featuretype_filter(True, True, False, False, False, False, True)
        Selection.set_inprofile_filter(1)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Selection.set_featuretype_filter(True, False, False, False, True, False, False)
        Selection.set_inprofile_filter(1)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Layers.delete_feature(job_ep, step, ['l4'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 11、筛选profile外正极性line、铜皮
        Selection.set_featuretype_filter(True, False, False, False, False, True, False)
        Selection.set_inprofile_filter(2)
        Selection.select_features_by_filter(job_ep, step, ['l5'])
        Layers.delete_feature(job_ep, step, ['l5'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 12、筛选profile线内的多个symbol以外的物件
        Selection.set_exclude_symbol_filter(['r15.748', 'r31.496'])
        Selection.set_inprofile_filter(1)
        Selection.select_features_by_filter(job_ep, step, ['l6'])
        Layers.delete_feature(job_ep, step, ['l6'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 13、筛选profile线外单个symbol
        Selection.set_include_symbol_filter(['r8'])
        Selection.set_inprofile_filter(2)
        Selection.select_features_by_filter(job_ep, step, ['l7'])
        Layers.delete_feature(job_ep, step, ['l7'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 14、筛选profile线内包含A属性的物件
        Selection.set_attribute_filter(0, [{'.cu_surface': ''}])
        Selection.set_inprofile_filter(1)
        Selection.select_features_by_filter(job_ep, step, ['l8'])
        Layers.delete_feature(job_ep, step, ['l8'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 15、筛选profile线外不包含B属性的物件
        Selection.set_exclude_attr_filter([{'.imp_line': ''}])
        Selection.set_inprofile_filter(2)
        Selection.select_features_by_filter(job_ep, step, ['l9'])
        Layers.delete_feature(job_ep, step, ['l9'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 16、筛选包含单属性的symbol
        Selection.set_include_symbol_filter(['r15.748'])
        Selection.set_attribute_filter(0, [{'.bga': ''}])
        Selection.select_features_by_filter(job_ep, step, ['bot'])
        Layers.delete_feature(job_ep, step, ['bot'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 17、筛选不包含bga属性的pad
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_exclude_attr_filter([{'.bga': ''}])
        Selection.select_features_by_filter(job_ep, step, ['smb'])
        Layers.delete_feature(job_ep, step, ['smb'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # GUI.show_layer(job_ep, step, 'l3+4')
        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_g_remote_path = os.path.join(RunConfig.temp_path_g, 'g', job_g)
        print("job_yg_remote_path:", job_g_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, 'ep', job_ep)
        print("job_testcase_remote_path:", job_ep_remote_path)

        # 导入要比图的资料
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)

        layerInfo = []
        for each in layers:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = ''
            layerInfo.append(each_dict)
        print("layerInfo:", layerInfo)

        g.layer_compare_g_open_2_job(job1=job_g, step1=step, job2=job_ep, step2=step)

        compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                        job1=job_g, step1=step,
                                        job2=job_ep, step2=step,
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
        Print.print_with_delimiter('比对结果信息展示--结束')

        assert data['g1_vs_total_result_flag'] == True
        for key in data['all_result_g1']:
            assert data['all_result_g1'][key] == "正常"

        Print.print_with_delimiter("断言--结束")
