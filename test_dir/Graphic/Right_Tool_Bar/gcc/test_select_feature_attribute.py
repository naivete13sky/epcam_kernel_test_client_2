import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection, Information
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job


class TestGraphicSelectFeatureAttribute:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Select_attribute'))
    def test_select_features_attribute(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试select_features_attribute功能，用例数：
        ID:
        BUG:
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        step = 'orig'
        layers = ['top', 'l2']

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

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称--------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        # 1、筛选包含单个属性的物件
        Selection.set_attribute_filter(0, [{'.bga': ' '}])
        Selection.select_features_by_filter(job_ep, step, ['top'])
        Layers.delete_feature(job_ep, step, ['top'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 2、筛选包含多个属性的物件
        Selection.set_attribute_filter(0, [{'.bga': ' '}, {'.aoi: '}])
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Layers.delete_feature(job_ep, step, ['l2'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 3、筛选包含A或者B属性的物件
        Selection.set_attribute_filter(1, [{'.bga': ' '}, {'.aoi: '}])
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Layers.delete_feature(job_ep, step, ['l3'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 4、筛选不包含单个属性的物件（第一种方法）
        Selection.set_attribute_filter(2, [{'.bga': ' '}])
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Layers.delete_feature(job_ep, step, ['l4'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 5、筛选不包含单个属性的物件（第二种方法）
        Selection.set_exclude_attr_filter([{'tool': '0'}])
        Selection.select_features_by_filter(job_ep, step, ['l6'])
        Layers.delete_feature(job_ep, step, ['l6'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 6、筛选不包含多个属性的物件（第一种方法）
        Selection.set_attribute_filter(2, [{'.bga': ' '}, {'.aoi: '}])
        Selection.select_features_by_filter(job_ep, step, ['l5'])
        Layers.delete_feature(job_ep, step, ['l5'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 7、筛选不包含多个属性的物件（第二种方法）
        Selection.set_exclude_attr_filter([{'tool': '0'}, {'.drill_flag': '10'}])
        Selection.select_features_by_filter(job_ep, step, ['l7'])
        Layers.delete_feature(job_ep, step, ['l7'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 8、筛选包含A属性，不包含B属性的物件
        Selection.set_attribute_filter(0, [{'.bga': ' '}])
        Selection.set_exclude_attr_filter([{'tool': '0'}])
        Selection.select_features_by_filter(job_ep, step, ['l8'])
        Layers.delete_feature(job_ep, step, ['l8'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 9、筛选单个属性范围内的物件
        Selection.set_attr_range_filter(0, [{'attr_name': 'tool', 'min_value': 0, 'max_value': 10}])
        Selection.select_features_by_filter(job_ep, step, ['5'])
        Layers.delete_feature(job_ep, step, ['5'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 10、筛选多个属性范围内的物件
        Selection.set_attr_range_filter(0, [{'attr_name': 'tool', 'min_value': 0, 'max_value': 10},
                                            {'attr_name': '.drill_flag', 'min_value': 1, 'max_value': 5}])
        Selection.select_features_by_filter(job_ep, step, ['bot'])
        Layers.delete_feature(job_ep, step, ['bot'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 11、筛选A或者B属性范围内的物件
        Selection.set_attr_range_filter(1, [{'attr_name': 'tool', 'min_value': 0, 'max_value': 10},
                                            {'attr_name': '.drill_flag', 'min_value': 1, 'max_value': 5}])
        Selection.select_features_by_filter(job_ep, step, ['1'])
        Layers.delete_feature(job_ep, step, ['1'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 12、筛选单个属性范围之外的物件
        Selection.set_exclude_attr_range_filter([{'attr_name': 'tool', 'min_value': 0, 'max_value': 10},
                                                 {'attr_name': '.drill_flag', 'min_value': 1, 'max_value': 5}])
        Selection.select_features_by_filter(job_ep, step, ['2'])
        Layers.delete_feature(job_ep, step, ['2'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 13、筛选多个属性范围之外的物件
        Selection.set_exclude_attr_range_filter([{'attr_name': 'tool', 'min_value': 0, 'max_value': 10},
                                                 {'attr_name': '.drill_flag', 'min_value': 1, 'max_value': 5}])
        Selection.select_features_by_filter(job_ep, step, ['bot'])
        Layers.delete_feature(job_ep, step, ['bot'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        GUI.show_layer(job_ep, step, 'top')
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
        assert len(layers) == len(data["all_result_g1"])

        # --------------------------------------------开始验证结果--------------------------------------------------------
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
