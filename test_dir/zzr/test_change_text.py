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

# @pytest.mark.ChangeText
class TestGraphicEditChangeText:
    # @pytest.mark.ChangeText
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Change_Text'))
    def testChangeText(self, job_id, g, prepare_test_job_clean_g):
        '''
        id:18585,本用例测试改变文字(Change_Text)
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        layers = ['sst','spt','smt','l1','spt-1','sst-1','l2','smt-1','l3','l4','l5','l6','l1-1' ,'l2-1','l3-1']  # 定义需要比对的层
        # layers = ['l2-1','l3-1']

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

        #1.整层修改文字信息且为正极性,字体类型为standard,不镜像不旋转
        Layers.change_text(job_case, step, ['sst'], '8', 'standard', 5080000,
                           5080000, 609600, True, 0, 0)

        #2.整层修改文字信息且为正极性,字体类型为simple，不镜像不旋转
        Layers.change_text(job_case, step, ['spt'], 'g', 'simple', 2540000,
                           2540000, 762000, True, 0, 0)

        # 3.整层修改文字信息且为正极性,字体类型为seven_seg，旋转角度45
        Layers.change_text(job_case, step, ['smt'], 'W', 'seven_seg', 5080000,
                           5080000, 609600, True, 0, 45)

        # 4.整层修改文字信息且为正极性,字体类型为canned_67，角度选择90度并镜像
        Layers.change_text(job_case, step, ['l1'], 'M', 'canned_67', 7620000,
                           7620000, 609600, True, 1, 90)

        # 5.整层修改文字信息且为正极性,字体类型为suntak_date,镜像
        Layers.change_text(job_case, step, ['spt-1'], '$$DD', 'suntak_date', 3810000,
                           2540000, 508000, True, 1, 0)

        # 6.整层默认原始文字信息且为正极性,字体类型为canned_57,角度旋转360
        Layers.change_text(job_case, step, ['sst-1'], '', 'canned_57', 3810000,
                           2540000, 508000, True, 0, 360)
        # GUI.show_layer(job_case, step, 'sst-1')

        # 7.整层修改文字信息且为负极性,字体类型为canned_57,角度旋转45度并镜像，然后整层资料极性反向转换
        Layers.change_text(job_case, step, ['l2'], '$$MM', 'canned_57', 2540000,
                           2540000, 304800, False, 1, 45)
        Layers.change_polarity(job_case, step, ['l2'], 2, 1)

        # 8.整层默认原始文字信息且为负极性,字体类型为simple,极性为正
        Layers.change_text(job_case, step, ['smt-1'], '', 'simple', 5080000,
                           5080000, 762000, True, 0, 0)
        # GUI.show_layer(job_case, step, 'smt-1')

        # 9.整层修改文字信息且为负极性,字体类型为suntak_date并镜像
        Layers.change_text(job_case, step, ['l3'], '$$DD', 'suntak_date', 5080000,
                           5080000, 609600, True, 1, 0)

        # 10.单选文字修改信息且为正极性,字体类型为standard，镜像并角度旋转45度
        Selection.select_feature_by_id(job_case, step, 'l4', [52])
        Layers.change_text(job_case, step, ['l4'], '$$DATE-MMDDYYYY', 'standard', 5080000,
                           5080000, 609600, True, 1, 45)

        # 11.单选文字修改信息转为负极性,字体类型为canned_67,镜像并旋转角度
        Selection.select_feature_by_id(job_case, step, 'l6', [52, 23, 40, 25])
        Layers.change_text(job_case, step, ['l6'], '$$LAYER', 'canned_67', 5080000,
                           5080000, 762000, False, 1, 45)

        # 12.单选文字修改信息转为负极性,字体类型为seven_seg，镜像并旋转角度，然后转极性为正。
        Selection.select_feature_by_id(job_case, step, 'l5', [26])
        Layers.change_text(job_case, step, ['l5'], '$$YY', 'seven_seg', 5080000,
                           5080000, 762000, False, 1, 45)
        Selection.select_feature_by_id(job_case, step, 'l5', [26])
        Layers.change_polarity(job_case, step, ['l5'], 2, 0)

        # 13.验证多选负极性文字转换为正，字体类型为 “standard”
        Selection.select_feature_by_id(job_case, step, 'l1-1', [0, 1, 2, 40,48])
        Layers.change_text(job_case, step, ['l1-1'], 'test', 'standard', 5080000,
                           5080000, 762000, True, 0, 0)

        # 14.验证多层改变字体，极性为正，镜像并角度旋转15°
        Layers.change_text(job_case, step, ['l2-1','l3-1'], '$$MM', 'seven_seg', 5080000,
                           3810000, 635000, True, 1, 15)

        # GUI.show_layer(job_case, step, 'l4')
        save_job(job_case, temp_ep_path)


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
