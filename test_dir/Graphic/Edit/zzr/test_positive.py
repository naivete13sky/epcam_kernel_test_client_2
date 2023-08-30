import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from config_g.g_cc_method import G

# @pytest.mark.Polarity
class TestGraphicEditPositivePolarity:
    # @pytest.mark.PositivePolarity
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Polarity'))
    def testPolarity(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试极性反转功能--Polarity,ID:11940
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'net'  # 定义需要执行比对的step名
        layers = ['l1', 'l6', 'l7', 'l8', 'l7+1', 'l8+1', 'l2', 'l3','l4','l4+1','l5','l1+1','l6+1','l2+1']  # 定义需要比对的层

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_case = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_case, temp_compressed_path)  # 用悦谱CAM打开料号

        #1.整层正负资料极性反向转换为负（Invert）
        Layers.change_polarity(job_case, step, ['l1'], 2, 1)

        #2整层负资料极性反向转换为正（Invert）
        Layers.change_polarity(job_case, step, ['l6'], 2, 1)

        #3单选正物件极性反转为负（Invert）
        Selection.select_feature_by_id(job_case, step, 'l7', [2])
        Layers.change_polarity(job_case, step, ['l7'], 2, 0)

        # 4单选负物件极性反转为正（Invert）
        Selection.select_feature_by_id(job_case, step, 'l8', [20])
        Layers.change_polarity(job_case, step, ['l8'], 2, 0)

        #5多选负物件极性反转为正（Invert）
        Selection.select_feature_by_id(job_case, step, 'l7+1', [42,44,38])
        Layers.change_polarity(job_case, step, ['l7+1'], 2, 0)

        #6多选正物件极性反转为正（Invert）
        Selection.select_feature_by_id(job_case, step, 'l8+1', [289,563,621,840,0])
        Layers.change_polarity(job_case, step, ['l8+1'], 2, 0)

        #7.整层资料正极性反转负极性,转正极性(Negative,Positive)
        Layers.change_polarity(job_case, step, ['l2'], 1, 1)
        Layers.change_polarity(job_case, step, ['l2'], 0, 1)

        #8多选物件正极性反转
        Selection.select_feature_by_id(job_case, step, 'l3', [603,430])
        Layers.change_polarity(job_case, step, ['l3'], 2, 0)

        #9单选物件正极性反转负极性
        Selection.select_feature_by_id(job_case, step, 'l4', [866])
        Layers.change_polarity(job_case, step, ['l4'], 1, 0)

        #10单选物件负极性反转负极性
        Selection.select_feature_by_id(job_case, step, 'l4+1', [39])
        Layers.change_polarity(job_case, step, ['l4+1'], 1, 0)

        #11.单选物件负极性反转正极性（Positive）
        Selection.select_feature_by_id(job_case, step, 'l5', [39])
        Layers.change_polarity(job_case, step, ['l5'], 0, 0)

        #12多选物件负极性反转正极性（Positive）
        Selection.select_feature_by_id(job_case, step, 'l1+1', [39,40,42,45])
        Layers.change_polarity(job_case, step, ['l1+1'], 0, 0)

        #13整层负极性反转正极性（Positive）
        Selection.select_feature_by_id(job_case, step, 'l6+1', [39, 40, 42, 45])
        Layers.change_polarity(job_case, step, ['l6+1'], 0, 1)

        #14多选正极性反转正极性（Positive）
        Selection.select_feature_by_id(job_case, step, 'l2+1', [496, 530, 838])
        Layers.change_polarity(job_case, step, ['l2+1'], 0, 0)



        save_job(job_case, temp_ep_path)
        # GUI.show_layer(job_case,step,'l5')

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_yg)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_case_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_case)
        print("job_testcase_remote_path:", job_case_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_case_remote_path)

        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_yg, step1=step, all_layers_list_job1=layers, job2=job_case, step2=step,
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
        # Print.print_with_delimiter('分割线', sign='-')
        # print('G转图的层：', data["all_result_g"])
        # Print.print_with_delimiter('分割线', sign='-')
        # print('所有层：', data["all_result"])
        Print.print_with_delimiter('分割线', sign='-')
        print('G1转图的层：', data["all_result_g1"])
        Print.print_with_delimiter('分割线', sign='-')
        # print('悦谱比图结果：', all_result_ep_vs_g_g2)
        Print.print_with_delimiter('比对结果信息展示--结束')

        # Print.print_with_delimiter("断言--开始")
        # assert data['g_vs_total_result_flag'] == True
        # for key in data['all_result_g']:
        #     assert data['all_result_g'][key] == "正常"

        assert data['g1_vs_total_result_flag'] == True
        for key in data['all_result_g1']:
            assert data['all_result_g1'][key] == "正常"

        # for key in all_result_ep_vs_g_g2:
        #     assert all_result_ep_vs_g_g2[key] == "正常"

        Print.print_with_delimiter("断言--结束")
