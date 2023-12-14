import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel import Application
from epkernel.Action import Information, Selection

'''
本用例测试Add_line功能，共覆盖24个场景（ID:12812）
'''
class TestGraphicAdd_line:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_line'))
    def testAdd_line(self, job_id, g, prepare_test_job_clean_g):

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
        预期结果1:大小在取值范围内[0,50000]的正负极性line均可正确添加
        预期结果2:r-1和s-1的正负极性line由于超出边界值不能添加
        覆盖用例场景数: 12个
        '''
        symbols = ['r0', 'r-1', 'r20', 's0', 's-1', 's20']#根据边界值法设置不同类型线段的大小
        #1.在正极性铜皮上添加负极性的r0或s0线段，UI上不显示添加的负极性线段(BugID：5560)
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
        #GUI.show_layer(job_ep, step, 'l2')





        '''
        测试用例名称: 多层添加不同形状大小的正、负极性线段
        预期结果1:大小在取值范围内[0,50000]的正负极性line均可在多层正确添加
        预期结果2:r-1和s-1的正负极性line由于超出边界值不能添加
        执行测试用例数: 12个
        '''
        symbols = ['r0', 'r-1', 'r20','s0', 's-1', 's20']  # 设置线段形状大小
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

        #GUI.show_layer(job_ep, step, 'l6')


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
        for each in ['l2','l4','l6']:
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



'''
本用例测试Add_pad功能，共覆盖108个场景（ID:39608）
'''
class TestGraphicAdd_pad:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_pad'))
    def testAdd_pad(self, job_id, g, prepare_test_job_clean_g):
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
        #“s_tho4x2x1x1x3", 'rc_tho20x6x2x2x4x2这两种Pad，在G里面打不开了
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
        预期结果1: 'r0', 'r50', 's0', 's50的正负极性Pad可正确添加
        预期结果2:  r-1和s-1的正负极性pad由于超出边界值不能添加
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

        symbols = ['s0', 's-1', 's50', 'r0', 'r-1', 'r50']#根据边界值法设置不同类型pad的大小
        polaritys = [True, False]  # 设置pad极性
        num_x3 = 1  # x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义pad属性
        for symbol in symbols:
            num_y3 = 25  # y轴坐标
            for polarity in polaritys:
                Layers.add_pad(job_ep, step, ['l3'], symbol, num_x3 * 1000000, num_y3 * 1000000, polarity,
                               0, attributes, 66)
                num_x3 = num_x3 + 3
                num_y3 = num_y3 + 6
        #GUI.show_layer(job_ep, step, 'l3')


        '''
        测试用例名称:添加不同角度的正负极性Pad
        预期结果1: pad正确添加，但无法旋转-1度和361度，角度取值范围[0,360]
        预期结果2: pad正确添加，可旋转[0,360]取值范围内的任一角度，角度取值范围[0,360]
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
        #GUI.show_layer(job_ep, step, 'l3')


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
        for each in ['l2', 'l3']:
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





'''
本用例测试Add_surface功能，共覆盖7个场景（ID:39611）
'''
class TestGraphicAdd_surface:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_surface'))
    def testAdd_surface(self, job_id, g, prepare_test_job_clean_g):
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


        #1.验证可正确添加正极性surface
        points_location = []
        points_location.append([66 * 1000000, 1* 1000000])
        points_location.append([66 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 1 * 1000000])
        points_location.append([66 * 1000000, 1* 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)

        #2.验证可正确添加负极性surface
        points_location = []
        points_location.append([68 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 3 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], False,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)


        #3.验证可正确添加正极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], True, {'.bga': '', '.cm': ''},68 * 1000000, 8 * 1000000, 50 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')

        #4.验证可正确添加负极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], False, {'.bga': '', '.cm': ''}, 67 * 1000000,
                                            5 * 1000000, 30 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')


        #5. 选中一个铜物件，使用线填充铜物件,不足的地方不使用弧线填充
        points_location = []
        points_location.append([66 * 1000000, 12 * 1000000])
        points_location.append([66 * 1000000, 18 * 1000000])
        points_location.append([71 * 1000000, 18 * 1000000])
        points_location.append([71 * 1000000, 12 * 1000000])
        points_location.append([66 * 1000000, 12 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#先添加一块正极性铜皮
        Selection.select_feature_by_id(job_ep, step, 'l2', [927])#选中刚添加的铜皮
        Layers.use_solid_fill_contours(job_ep, step, ['l2'], 5 * 254000, False)#使用线填充，线的最小间距为5Mil,弧度不足的地方不使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [936])#选中其中一个线将其删除，以证明铜面被打散了
        Layers.delete_feature(job_ep, step, ['l2'])
        #GUI.show_layer(job_ep, step, 'l2')

        #6.选中一个圆形铜物件，使用线填充铜物件,不足的地方使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [925])#选中一个圆形铜皮
        Layers.use_solid_fill_contours(job_ep, step, ['l2'], 5 * 254000, True)  #使用线填充，线的最小间距为5Mil,弧度不足的地方使用弧线正确填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [927])  #选中其中一个弧线线将其删除，以证明铜面打散时不足的地方用弧线补充了
        Layers.delete_feature(job_ep, step, ['l2'])
        #GUI.show_layer(job_ep, step, 'l2')

        #7.验证可多层舔加surface
        points_location = []
        points_location.append([66 * 1000000, 1 * 1000000])
        points_location.append([66 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 1 * 1000000])
        points_location.append([66 * 1000000, 1 * 1000000])
        Layers.add_surface(job_ep, step, ['l3', 'l4'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#多层添加正极性Surface


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
        for each in ['l2', 'l3', 'l4']:
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


'''
本用例测试Add_arc功能,共覆盖5个场景（ID:39612）
'''
class TestGraphicAdd_arc:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_arc'))
    def testAdd_arc(self, job_id, g, prepare_test_job_clean_g):

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

        #1.验证可以在多层正确添加弧线
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l2', 'l3'], 'r10', 1 * 1000000, 26 * 1000000,
                       9 * 1000000, 34 * 1000000, 5 * 1000000, 30 * 1000000, True, True, attributes)
        #2.验证可顺时针填加一个正极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 1*1000000, 26*1000000,
        9*1000000, 34*1000000, 5*1000000, 30*1000000, True, True, attributes)

        #3.验证可顺时针填加一个负极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 1 * 1000000, 7 * 1000000,
                       5 * 1000000, 11 * 1000000, 3 * 1000000, 9 * 1000000, True, False, attributes)

        #4.验证可逆时针填加一个正极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 39 * 1000000, 26 * 1000000,
                       25 * 1000000, 34 * 1000000, 32 * 1000000, 30 * 1000000, False, True, attributes)
        #5.验证可逆时针填加一个负极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 20 * 1000000, 9 * 1000000,
                       16 * 1000000, 11 * 1000000, 18 * 1000000, 10 * 1000000, False, False, attributes)

        #GUI.show_layer(job_ep, step, 'l7')




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
        for each in ['l2', 'l3', 'l7']:
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



'''
本用例测试Add_text功能,,共覆盖55个场景（ID:39614）
'''
class TestGraphicAdd_text:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_text'))
    def testAdd_text(self, job_id, g, prepare_test_job_clean_g):

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
        测试用例名称:添加不同镜像和角度的正负极性的text
        预期结果: 均正确添加
        执行测试用例数: 20个
        '''
        points_location = []
        points_location.append([1 * 1000000, 45 * 1000000])
        points_location.append([1 * 1000000, 53 * 1000000])
        points_location.append([72 * 1000000, 53 * 1000000])
        points_location.append([72 * 1000000, 45 * 1000000])
        points_location.append([1 * 1000000, 45 * 1000000])
        Layers.add_surface(job_ep, step, ['l1'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}],
                           points_location)  # 先添加一块正极性大同皮，方便后面在铜皮上添加正负极性的不同镜像和角度的text

        orients = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        polaritys = [True, False]  # 设置text极性
        num_x5 = 1  # x轴坐标
        attributes=[{'.text':'2'},{'.text_88':''}]  # 定义text属性
        for orient in orients:
            num_y7 = 40  # y轴坐标
            for polarity in polaritys:
                Layers.add_text(job_ep, step, ['l1'], 'standard', 'GBhf689', 20 * 25400, 20 * 25400,
                                2 * 25400,
                                num_x5 * 1000000, num_y7 * 1000000, polarity, orient, attributes, 56)
                num_x5 = num_x5 + 3
                num_y7 = num_y7 + 9
        #GUI.show_layer(job_ep, step, 'l1')



        #1.验证X_size栏的正确性（X_size栏输入40mil）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 40*25400, 20*25400, 2 * 25400,
                        5*1000000, 30*1000000, True, 0, attributes, 0)#X_size栏输入40mil

        #2.验证Y_size栏的正确性（Y_size栏输入40mil）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 40 * 25400, 2 * 25400,
                        5 * 1000000, 32 * 1000000, True, 0, attributes, 0)#Y_size栏输入40mil
        #3.验证Line_Width栏的正确性（Line_Width栏输入3mil）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./ ', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 34 * 1000000, True, 0, attributes, 0)#Line_Width栏输入3mil

        #GUI.show_layer(job_ep, step, 'l2')

        '''
        测试用例名称: 添加不同字体的正、负极性文字
        预期结果: 正确添加
        执行测试用例数: 12个
        '''
        points_location = []
        points_location.append([24 * 1000000, 23 * 1000000])
        points_location.append([24 * 1000000, 30 * 1000000])
        points_location.append([40 * 1000000, 30 * 1000000])
        points_location.append([40 * 1000000, 23 * 1000000])
        points_location.append([24 * 1000000, 23 * 1000000])
        Layers.add_surface(job_ep, step, ['l3'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#先添加一块正极性大同皮，后面在铜皮上添加负极性文字
        fonts = ['standard', 'canned_57', 'canned_67', 'seven_seg', 'simple', 'suntak_date']#文字类型
        polaritys = [True,False]  # 物件极性属性
        num_y = 24  # Y轴坐标
        attributes = [{'.text': '2'}]  # 定义文字属性
        for font in fonts:
            num_X = 5  # X轴坐标
            for polarity in polaritys:
                Layers.add_text(job_ep, step, ['l3'], font,'Gh6-=,./<>!@#$%^&*()_,./',20* 25400,20 * 25400,2 * 25400,
                            num_X*1000000, num_y*1000000, polarity,0, attributes, 0)
                num_X = 26
            num_y=num_y + 1

        '''
        测试用例名称: 多层添加不同类型的正负动态文字
        预期结果: 均可正确添加
        执行测试用例数: 20个
        '''
        points_location = []
        points_location.append([24 * 1000000, 23 * 1000000])
        points_location.append([24 * 1000000, 45 * 1000000])
        points_location.append([33 * 1000000, 45 * 1000000])
        points_location.append([33 * 1000000, 23 * 1000000])
        points_location.append([24 * 1000000, 23 * 1000000])
        Layers.add_surface(job_ep, step, ['l4', 'l5'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#先添加一块正极性大同皮，方便后面在铜皮上添加负极性文字
        texts = ['$$DATE', '$$DATE-MMDDYY', '$$DATE-DDMMYY', '$$DATE-MMDDYYYY', '$$DATE-DDMMYYYY', '$$DD', '$$WEEK-DAY', '$$MM',
                 '$$YY', '$$YYYY', '$$WW', '$$WK/YY', '$$YY/WK', '$$TIME', '$$STEP', '$$LAYER', '$$X', '$$Y', '$$X_MM', '$$Y_MM']#设置不同类型的动态文字，共20种
        polaritys = [True,False]  # 物件极性属性
        num_y = 24  # Y轴坐标
        attributes = [{'.text': '2'}]  # 定义文字属性
        for text in texts:
            num_X = 5  # X轴坐标
            for polarity in polaritys:
                Layers.add_text(job_ep, step, ['l4', 'l5'], 'standard',text,20* 25400,20 * 25400,2 * 25400,
                            num_X*1000000, num_y*1000000, polarity,0, attributes, 0)
                num_X = 26
            num_y=num_y + 1
        #GUI.show_layer(job_ep, step, 'l5')

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
        for each in ['l1', 'l2', 'l3', 'l4', 'l5']:
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










