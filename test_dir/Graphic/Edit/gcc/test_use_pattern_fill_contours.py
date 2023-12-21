import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditUsepatternfillcontours:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Fill_pattern'))
    def test_use_pattern_fill_contours(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Use_pattern_fill_contours填充功能，用例数：6
        ID: 17873
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'bot', '1511']

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

        # 1、指定符号填充铜皮（拆分删除框外元素，且奇数行偏移）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'top', [27])
        Layers.use_pattern_fill_contours(job_ep, step, 'top', 'bfr8', 10*25400, 10*25400,
                                         True, False, False, False, 1*25400, False, 5*25400, 0*25400)

        # 2、指定符号填充铜皮（切除位于边框上的基本元素，创建轮廓化的铜面，且偶数行偏移）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l2', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'bfr8', 10*25400, 10*25400,
                                         False, True, False, False, 1*25400, False, 0*25400, 5*25400)

        # 3、指定符号填充铜皮（将原点设置为基准点）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l3', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l3', 'bfr8', 10*25400, 10*25400,
                                         False, False, True, False, 1*25400, False, 0*25400, 0*25400)

        # 4、指定符号填充铜皮（铜皮轮廓化）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l4', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l4', 'di10x10', 10*25400, 10*25400,
                                         False, False, False, True, 2*25400, False, 0*25400, 0*25400)

        # 5、指定符号填充铜皮（铜皮轮廓化并转换轮廓线极性）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l5', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l5', 'di10x10', 10*25400, 10*25400,
                                         False, False, False, True, 2*25400, True, 0*25400, 0*25400)
        Selection.set_featuretype_filter(False, True, False, False, False, True, False)
        Selection.select_features_by_filter(job_ep, step, ['l5'])   # 负极性外框线不可见，再次转换极性
        Layers.change_polarity(job_ep, step, ['l5'], 2, 0)
        Selection.reset_select_filter()  # 重置筛选

        # 6、指定符号填充负极性铜皮（切除位于边框上的基本元素，创建轮廓化的铜面）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'bot', [34, 38])
        Layers.use_pattern_fill_contours(job_ep, step, 'bot', 'di10x10', 10*25400, 10*25400,
                                         False, True, False, True, 2*25400, False, 0*25400, 0*25400)

        # 7、验证Fill过程中自动删除不满足dummy pad的小铜块-----BUG号：1511
        Layers.use_pattern_fill_contours(job_ep, step, '1511', 'r40', 50 * 25400, 50 * 25400,
                                         True, False, False, False, 0 * 25400, False, 0 * 25400, 0 * 25400)

        # GUI.show_layer(job_ep, step, 'bot')
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
