import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection, Information
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job


class TestGraphicSelectFeatureType:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Select_type'))
    def test_select_features_type(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试select_features_type功能，用例数：14
        ID:36182
        BUG:
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8']

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

        # 1、验证选中所有正极性物件
        Selection.set_featuretype_filter(True, False, True, True, True, True, True)
        Selection.select_features_by_filter(job_ep, step, ['top'])
        Layers.delete_feature(job_ep, step, ['top'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 2、验证选中所有负极性物件
        Selection.set_featuretype_filter(False, True, True, True, True, True, True)
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Layers.delete_feature(job_ep, step, ['l2'])    # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 3-7、验证选中单类型正极性物件
        Selection.set_featuretype_filter(True, False, True, False, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Selection.set_featuretype_filter(True, False, False, False, True, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Selection.set_featuretype_filter(True, False, False, False, False, True, False)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Layers.delete_feature(job_ep, step, ['l3'])    # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 8-12、验证选中单类型负极性物件
        Selection.set_featuretype_filter(False, True, True, False, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Selection.set_featuretype_filter(False, True, False, True, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Selection.set_featuretype_filter(False, True, False, False, True, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Selection.set_featuretype_filter(False, True, False, False, False, True, False)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Selection.set_featuretype_filter(False, True, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Layers.delete_feature(job_ep, step, ['l4'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 13、筛选多层多类型正极性物件
        Selection.set_featuretype_filter(True, False, False, False, True, True, True)
        Selection.select_features_by_filter(job_ep, step, ['l5', 'l6'])
        Layers.delete_feature(job_ep, step, ['l5', 'l6'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # 14、筛选多层多类型负极性物件
        Selection.set_featuretype_filter(False, True, True, True, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l7', 'l8'])
        Layers.delete_feature(job_ep, step, ['l7', 'l8'])  # 通过删除来验证是否选中
        Selection.reset_select_filter()

        # GUI.show_layer(job_ep, step, 'top')
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
