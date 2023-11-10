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
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_pad'))
    def testFeatureIndex(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add_pad功能（ID:39608）
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



        #增加pad
        '''
        测试用例名称:添加不同形状大小的正、负极性Pad
        预期结果: 均可正确添加
        执行测试用例数: 66个
        '''
        points_location = []
        points_location.append([1 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 36 * 1000000])
        points_location.append([208 * 1000000, 36 * 1000000])
        points_location.append([208 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 29 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 先添加一块正极性大同皮，后面在铜皮上添加负极性pad
        symbols = ['r50', 's50', 'rect50x50', 'rect50x50xr25x2', 'rect50x50xr25x12', 'rect50x50xr25x123', 'rect50x50xr25',  'rect50x50','rect50x50xc25x2',
                   'rect50x50xc25x12', 'rect50x50xc25x123', 'rect50x50xc25', 'oval50x50', 'di50x50', 'oct50x50x10', 'donut_r50x30', 'donut_s50x30',
                   'hex_l50x50x10', 'hex_s50x30x10', 'bfr50', 'bfs50', 'tri50x30', 'oval_h50x30', 'thr60x30x1x3x10', 'ths60x30x1x3x10', 'sr_ths60x30x1x3x10',
                   'rc_ths60x30x1x3x10x10', 'el50x20', 'moire60x30x1x30x10x10', 'hole20xvx1x1', 'hole50xnx2x2', 'hole80xpx2x2', 'null50000']  #设置pad形状大小(共33种类型)}
        #s_tho60x30x1x3x10", 'rc_tho60x30x1x3x10x6这两种Pad，G软件不识别，会报错（已提交bug）
        polaritys = [True, False]  # 设置pad极性
        num_x1 = 1  # x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义pad属性
        for symbol in symbols:
            num_y1 = 25  # y轴坐标
            for polarity in polaritys:
                Layers.add_pad(job_ep, step, ['l2'], symbol, num_x1*1000000, num_y1*1000000, polarity,
                               9,attributes, 0)
                num_x1 = num_x1 + 3
                num_y1 = num_y1 + 8



        '''
        测试用例名称:添加不同镜像和角度的正负极性Pad
        预期结果: 均正确添加
        执行测试用例数: 20个
        '''
        points_location = []
        points_location.append([1 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 48 * 1000000])
        points_location.append([72 * 1000000, 48 * 1000000])
        points_location.append([72 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 42 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 先添加一块正极性大同皮，方便后面在铜皮上添加正负极性的不同镜像和角度的Pad

        orients=[0 ,1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9]
        polaritys = [True, False]  # 设置pad极性
        num_x2 = 1# x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义pad属性
        for orient in orients:
            num_y2 = 40  # y轴坐标
            for polarity in polaritys:
                Layers.add_pad(job_ep, step, ['l2'],"rect50x100xr25x2", num_x2 * 1000000, num_y2 * 1000000, polarity,
                       orient, attributes, 66)
                num_x2 = num_x2 + 3
                num_y2 = num_y2 + 6
        #GUI.show_layer(job_ep, step, 'l2')

        '''
        测试用例名称:添加不同大小的正负极性Pad
        预期结果: r-1和s-1的正负极性pad由于超出边界值不能添加，其他均可正确添加
        执行测试用例数: 12个
        '''
        points_location = []
        points_location.append([1 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 36 * 1000000])
        points_location.append([72 * 1000000, 36 * 1000000])
        points_location.append([72 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 29 * 1000000])
        Layers.add_surface(job_ep, step, ['l3'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}],
                           points_location)  # 先添加一块正极性大同皮，方便后面在铜皮上添加正负极性的不同镜像和角度的Pad

        symbols = ['r0', 'r-1', 'r50', 's0', 's-1', 's50']#根据边界值法设置不同类型pad的大小
        polaritys = [True, False]  # 设置pad极性
        num_x3 = 1  # x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义pad属性
        for symbol in symbols:
            num_y3 = 25  # y轴坐标
            for polarity in polaritys:
                Layers.add_pad(job_ep, step, ['l3'], symbol, num_x3 * 1000000, num_y3 * 1000000, polarity,
                               orient, attributes, 66)
                num_x3 = num_x3 + 3
                num_y3 = num_y3 + 6
        GUI.show_layer(job_ep, step, 'l3')


        '''
        测试用例名称:添加不同角度的正负极性Pad
        预期结果: pad无法旋转-1度和361度，其他角度均可正确旋转
        执行测试用例数: 10个
        '''
        points_location = []
        points_location.append([1 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 48 * 1000000])
        points_location.append([72 * 1000000, 48 * 1000000])
        points_location.append([72 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 42 * 1000000])
        Layers.add_surface(job_ep, step, ['l3'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}],
                           points_location)  # 先添加一块正极性大同皮，方便后面在铜皮上添加正负极性的不同镜像和角度的Pad


        special_angles = [-1,0,180,360,361]#根据边界值法设置不同的旋转角度
        polaritys = [True, False]  # 设置pad正负极性
        num_x4 = 1  # x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义pad属性
        orients = [8, 9]
        for special_angle in special_angles:
            num_y4 = 40  # y轴坐标
            for polarity in polaritys:
                for orient in orients:
                    Layers.add_pad(job_ep, step, ['l3'], "rect50x100xr25x2", num_x4 * 1000000, num_y4 * 1000000, polarity,
                               orient, attributes, special_angle)
                    num_x4 = num_x4 + 3
                    num_y4 = num_y4 + 6
        GUI.show_layer(job_ep, step, 'l3')




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
        for each in ['l2',]:
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