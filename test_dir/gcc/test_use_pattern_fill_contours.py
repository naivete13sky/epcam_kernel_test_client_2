import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job
from config_g.g_cc_method import G

class TestGraphicEditUse_pattern_fill_contours:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Fill_pattern'))
    def testUse_pattern_fill_contours (self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Use_pattern_fill_contours填充功能
        '''
        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6']

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        print("temp_path:", temp_path)
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        # 指定符号填充铜皮（拆分删除框外元素，且奇数行偏移）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'top', [27])
        Layers.use_pattern_fill_contours(job_ep, step, 'top', 'bfr6', 10*25400, 10*25400,
                                         True, False, False, False, 0*25400, False, 5*25400, 0*25400)

        # 指定符号填充铜皮（切除位于边框上的基本元素，创建轮廓化的铜面，且偶数行偏移）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l2', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'bfr6', 10*25400, 10*25400,
                                         False, True, False, False, 0*25400, False, 0*25400, 5*25400)

        # 指定符号填充铜皮（将原点设置为基准点）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l3', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l3', 'bfr6', 10*25400, 10*25400,
                                         False, False, True, False, 0, False, 0*25400, 0*25400)

        # 指定符号填充铜皮（铜皮轮廓化）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l4', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l4', 'bfr6', 10*25400, 10*25400,
                                         False, False, False, True, 2*25400, False, 0*25400, 0*25400)

        # 指定符号填充铜皮（铜皮轮廓化并转换轮廓线极性）❤❤❤
        Selection.select_feature_by_id(job_ep, step, 'l5', [0])
        Layers.use_pattern_fill_contours(job_ep, step, 'l5', 'bfr6', 10*25400, 10*25400,
                                         False, False, False, True, 2*25400, True, 0*25400, 0*25400)


        GUI.show_layer(job_ep, step, 'l2')
        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_g)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_case_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        print("job_testcase_remote_path:", job_case_remote_path)
        # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_case_remote_path)

        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_g, step1=step, all_layers_list_job1=layers, job2=job_ep, step2=step,
                                all_layers_list_job2=layers, adjust_position=True)
        data["all_result_g1"] = r['all_result_g']
        data["all_result"] = r['all_result']
        data['g1_vs_total_result_flag'] = r['g_vs_total_result_flag']
        Print.print_with_delimiter("断言--看一下G1转图中的层是不是都有比对结果")
        assert len(layers) == len(r['all_result_g'])

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
