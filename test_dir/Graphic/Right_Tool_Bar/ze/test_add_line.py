import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel import Application
from epkernel.Action import Information, Selection

class TestGraphicEditFeatureIndex:
    # @pytest.mark.Feature index
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_line'))
    def testFeatureIndex(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add_line功能（ID:12812）
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



        '''
        测试用例名称: 单层添加不同形状、大小的正、负极性线段
        预期结果: 正确添加
        执行测试用例数: 20个
        '''
        symbols = ['r0', 'r-1', 'r50','s0', 's-1', 's10','rect50x50', 'rect50x50xr25x2', 'rect50x50xr25x12', 'rect50x50xr25x123', 'rect50x50xr25',  'rect50x50','rect50x50xc25x2',
                   'rect50x50xc25x12', 'rect50x50xc25x123', 'rect50x50xc25', 'oval50x50', 'di50x50', 'oct50x50x10', 'donut_r50x30', 'donut_s50x30',
                   'hex_l50x50x10', 'hex_s50x30x10', 'bfr50', 'bfs50', 'tri50x30', 'oval_h50x30', 'thr60x30x1x3x10', 'ths60x30x1x3x10', 'sr_ths60x30x1x3x10',
                   'rc_ths60x30x1x3x10x10', 'el50x20', 'moire60x30x1x30x10x10', 'hole20xvx1x1', 'hole50xnx2x2', 'hole80xpx2x2', 'null50000']#根据边界值法设置不同类型线段的大小
        polaritys = [True ,False]  # 设置线段的两种极性
        num_x1 = 43  # x轴坐标
        attributes = [{'.fiducial_name': '0'}, {'.area': ''}]  # 定义线段属性
        for symbol in symbols:
            num_y1 = 23  # y轴坐标
            num_y2 = 30
            for polarity in polaritys:
                Layers.add_line(job_ep, step, ['l2'], symbol, num_x1 * 1000000, num_y1 * 1000000,
                                num_x1 * 1000000,
                                num_y2 * 1000000, polarity, attributes)  #单层增加所设置线条
                num_x1 = num_x1 + 1
                num_y1 = num_y1 - 10
                num_y2 = num_y2 - 10
        GUI.show_layer(job_ep, step, 'l2')

        Layers.add_line(job_ep, step, ['l3'], 'r50000',0, 0, 25400000, 25400000,
        True, [{'.fiducial_name': '0'},{'.area':''}])   # 单层增加r50000的正极性线条

        Layers.add_line(job_ep, step, ['l3'], 'r50000', 0, 0, 25400000, 25400000,
                        False, [{'.fiducial_name': '0'}, {'.area': ''}])  # 单层增加r50000的负极性线条
        GUI.show_layer(job_ep, step, 'l3')

        Layers.add_line(job_ep, step, ['l5'], 'r50000', 0, 0, 25400000, 25400000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])  # 单层增加s50000线条


        '''
        测试用例名称: 多层添加不同形状大小的正、负极性线段
        预期结果: 正确添加
        执行测试用例数: 8个
        '''
        symbols = ['r8', 's8','r20', 's20']  # 设置线段形状大小
        polaritys = [True, False]  # 线段极性
        num_x2 = 43  # x轴坐标
        attributes = [{'.fiducial_name': '0'}, {'.area': ''}]  # 定义线段属性
        for symbol in symbols:
            num_y3 = 23  # y轴坐标
            num_y4 = 30
            for polarity in polaritys:
                Layers.add_line(job_ep, step, ['l4','l6'], symbol, num_x2 * 1000000, num_y3 * 1000000,
                                num_x2 * 1000000,
                                num_y4 * 1000000, polarity, attributes)  # 多层增加线条
                num_x2 = num_x2 + 1
                num_y3 = num_y3 - 10
                num_y4 = num_y4 - 10

        GUI.show_layer(job_ep, step, 'l6')



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
        for each in ['l2','l3','l4']:
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