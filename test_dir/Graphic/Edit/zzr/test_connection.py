import pytest, os, time, json, shutil
from config import RunConfig
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Output import save_job

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

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l1', 'l2', 'l3', 'l4', 'l6', 'l7', 'l8', 'l9', 'c', 'nc', 'l10', 'smb', 'ssb', 'spt', 'sst',
        #           'smt', 'spb', 'spb+1']  # 定义需要比对的层
        # layers = ['l6','l9']

        # 取到临时目录
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
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号

        # 1.选择两根未连接线导圆角,角度为0.1inch
        Selection.select_feature_by_id(job_ep, step, 'l1', [0, 1])
        BASE.connections(job_ep, step, ['l1'], 1, 2540000, 0)
        # GUI.show_layer(job_ep, step, 'l1')

        # 2.选择连接的两根直角线导圆角,角度为0.4inch
        Selection.reverse_select(job_ep, step, 'l2')
        # Layers.rounding_line_corner(job_case, step, ['l2'], 10160000)
        BASE.connections(job_ep, step, ['l2'], 1, 10160000, 0)
        # GUI.show_layer(job_ep, step, 'l2')

        # 3.选择连接的两根锐角线段导圆角,角度为0.25inch
        Selection.reverse_select(job_ep, step, 'l3')
        # Layers.rounding_line_corner(job_case, step, ['l3'], 6350000)
        BASE.connections(job_ep, step, ['l3'], 1, 6350000, 0)
        # GUI.show_layer(job_ep, step, 'l3')

        # 4.选择连接的两根钝角线段导圆角,角度为0.6inch
        Selection.reverse_select(job_ep, step, 'l4')
        # Layers.rounding_line_corner(job_case, step, ['l4'], 15240000)
        BASE.connections(job_ep, step, ['l4'], 1, 15240000, 0)
        # GUI.show_layer(job_ep, step, 'l4')

        # 5.选择两根部分相交线导圆角,角度为1inch
        Selection.reverse_select(job_ep, step, 'l6')
        # Layers.rounding_line_corner(job_case, step, ['l6'], 25400000)
        BASE.connections(job_ep, step, ['l6'], 1, 25400000, 0)
        # GUI.show_layer(job_ep, step, 'l6')

        # 6.选择两根相触碰线段导圆角,角度为0.2inch
        Selection.reverse_select(job_ep, step, 'l7')
        BASE.connections(job_ep, step, ['l7'], 1, 5080000, 0)
        # GUI.show_layer(job_ep, step, 'l7')

        # 7.选择两根未连接钝角线段导圆角,角度为0.4inch
        Selection.reverse_select(job_ep, step, 'l8')
        BASE.connections(job_ep, step, ['l8'], 1, 10160000, 0)
        # GUI.show_layer(job_ep, step, 'l8')

        # 8.选择两根相交线导圆角,角度为0.08inch
        Selection.reverse_select(job_ep, step, 'l9')
        BASE.connections(job_ep, step, ['l9'], 1, 2032000, 0)
        # GUI.show_layer(job_ep, step, 'l9')

        # 9.选择两根未相交的线和弧导圆角,角度为0.03inch
        Selection.reverse_select(job_ep, step, 'c')
        BASE.connections(job_ep, step, ['c'], 1, 762000, 0)
        # GUI.show_layer(job_ep, step, 'c')

        # 10.选择两根相交的线和弧导圆角,角度为0.3inch
        Selection.reverse_select(job_ep, step, 'nc')
        BASE.connections(job_ep, step, ['nc'], 1, 7620000, 0)
        # GUI.show_layer(job_ep, step, 'nc')

        # 11.选择两根未连接线段进行连接，形成钝角
        Selection.select_feature_by_id(job_ep, step, 'l10', [0, 1])
        BASE.connections(job_ep, step, ['l10'], 0, 0, 0)
        # GUI.show_layer(job_ep, step, 'l10')

        # 12.选择两根触碰线段进行连接，形成锐角
        Selection.select_feature_by_id(job_ep, step, 'smb', [0, 1])
        BASE.connections(job_ep, step, ['smb'], 0, 0, 0)

        # 13.选择两根未连接线段进行连接，形成锐角
        Selection.select_feature_by_id(job_ep, step, 'ssb', [0, 1])
        BASE.connections(job_ep, step, ['ssb'], 0, 0, 0)

        # 14.选择两根未连接线段进行连接，形成直角
        Selection.select_feature_by_id(job_ep, step, 'spt', [0, 1])
        BASE.connections(job_ep, step, ['spt'], 0, 0, 0)

        # 15.选择两根未连接的”T“字形线段，形成夹角
        Selection.select_feature_by_id(job_ep, step, 'sst', [0, 1])
        BASE.connections(job_ep, step, ['sst'], 0, 0, 0)

        # 16.选择两根相交的线段进行连接
        Selection.select_feature_by_id(job_ep, step, 'smt', [0, 1])
        BASE.connections(job_ep, step, ['smt'], 0, 0, 0)

        # 17.选择线和弧未相交进行连接
        Selection.select_feature_by_id(job_ep, step, 'spb', [0, 1])
        BASE.connections(job_ep, step, ['spb'], 0, 0, 0)

        # 18.选择线和弧相交进行连接
        Selection.select_feature_by_id(job_ep, step, 'spb+1', [0, 2])
        BASE.connections(job_ep, step, ['spb+1'], 0, 0, 0)

        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_case, step, 'l6')

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_g_remote_path = os.path.join(RunConfig.temp_path_g, 'g', job_g)
        print("job_yg_remote_path:", job_g_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, 'ep', job_ep)
        print("job_testcase_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)

        layerInfo = []
        Input.open_job(job_g, temp_g_path)  # 用悦谱CAM打开料号
        all_layers_list_job_g = Information.get_layers(job_g)
        for each in all_layers_list_job_g:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = ''
            layerInfo.append(each_dict)

        print("layerInfo:", layerInfo)
        job1, job2 = job_g, job_ep
        step1, step2 = 'prepare', 'prepare'
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
        assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])

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
