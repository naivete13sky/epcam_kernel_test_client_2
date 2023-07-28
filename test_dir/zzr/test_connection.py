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

# @pytest.mark.Connection
class TestGraphicRoutConnection:
    # @pytest.mark.Connection
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('rounding_line_corner'))
    def testConnection(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试line导圆角功能--rounding_line_corner,ID:12150
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        layers = ['l1', 'l2', 'l3','l4','l6','l7','l8','l9','l10','smb','ssb','spb','spt','sst','smt']  # 定义需要比对的层
        # layers = ['l1']

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

        # 1.选择两根未连接线导圆角,角度为0.1inch,pass
        Selection.select_feature_by_id(job_case, step, 'l1', [0, 1])
        BASE.connections(job_case, step, ['l1'], 1, 2540000, 0)
        # GUI.show_layer(job_case, step, 'l1')

        # 2.选择两根线导圆角,角度为0.4inch,pass
        Selection.reverse_select(job_case, step, 'l2')
        # Layers.rounding_line_corner(job_case, step, ['l2'], 10160000)
        BASE.connections(job_case, step, ['l2'], 1, 10160000, 0)
        # GUI.show_layer(job_case, step, 'l2')

        # 3.选择两根线导圆角,角度为0.25inch,pass
        Selection.reverse_select(job_case, step, 'l3')
        # Layers.rounding_line_corner(job_case, step, ['l3'], 6350000)
        BASE.connections(job_case, step, ['l3'], 1, 6350000, 0)
        # GUI.show_layer(job_case, step, 'l3')

        # 4.选择两根线导圆角,角度为0.6inch,pass
        Selection.reverse_select(job_case, step, 'l4')
        # Layers.rounding_line_corner(job_case, step, ['l4'], 15240000)
        BASE.connections(job_case, step, ['l4'], 1, 15240000, 0)
        # GUI.show_layer(job_case, step, 'l4')

        # 5.选择两根线导圆角,角度为1inch,pass
        Selection.reverse_select(job_case, step, 'l6')
        # Layers.rounding_line_corner(job_case, step, ['l6'], 25400000)
        BASE.connections(job_case, step, ['l6'], 1, 25400000, 0)
        # GUI.show_layer(job_case, step, 'l6')

        # 6.选择两根线导圆角,角度为0.2inch,pass
        Selection.reverse_select(job_case, step, 'l7')
        BASE.connections(job_case, step, ['l7'], 1, 5080000, 0)
        # GUI.show_layer(job_case, step, 'l7')

        # 7.选择两根线导圆角,角度为0.4inch,pass
        Selection.reverse_select(job_case, step, 'l8')
        BASE.connections(job_case, step, ['l8'], 1, 10160000, 0)
        # GUI.show_layer(job_case, step, 'l8')

        # 8.选择两根线导圆角,角度为1inch,pass
        Selection.reverse_select(job_case, step, 'l9')
        BASE.connections(job_case, step, ['l9'], 1, 2032000, 0)
        # GUI.show_layer(job_case, step, 'l9')

        # 9.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'l10', [0, 1])
        BASE.connections(job_case, step, ['l10'], 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l10')

        # 10.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'smb', [0, 1])
        BASE.connections(job_case, step, ['smb'], 0, 0, 0)

        # 11.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'ssb', [0, 1])
        BASE.connections(job_case, step, ['ssb'], 0, 0, 0)

        # 12.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'spb', [0, 1])
        BASE.connections(job_case, step, ['spb'], 0, 0, 0)

        # 13.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'spt', [0, 1])
        BASE.connections(job_case, step, ['spt'], 0, 0, 0)

        # 14.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'sst', [0, 1])
        BASE.connections(job_case, step, ['sst'], 0, 0, 0)

        # 15.单选两根线段进行连接，功能为：corner
        Selection.select_feature_by_id(job_case, step, 'smt', [0, 1])
        BASE.connections(job_case, step, ['smt'], 0, 0, 0)

        save_job(job_case, temp_ep_path)
        # GUI.show_layer(job_case, step, 'l6')

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
