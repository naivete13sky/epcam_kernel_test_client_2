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
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add'))
    def testFeatureIndex(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add功能（ID:12812）
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




        #1.增加正极性文字，字体为suntak_date(动态文字，为了不让其变化频率过高，该用例使用动态年份)
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'suntak_date', '$$YYYY', 20 * 25400, 20 * 25400,
                        2 * 25400,
                        5 * 1000000, 29 * 1000000, True, 0, attributes, 0)#添加动态年份（'$$YYYY'）

        #2.验证X size栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 40*25400, 20*25400, 2 * 25400,
                        5*1000000, 30*1000000, True, 0, attributes, 0)
        #3.验证Y size栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 40 * 25400, 2 * 25400,
                        5 * 1000000, 32 * 1000000, True, 0, attributes, 0)
        #4.验证Line Width栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 34 * 1000000, True, 0, attributes, 0)
        #5.，验证旋转角度功能正确性（不镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 35 * 1000000, True, 2, attributes, 0)#文字旋转180度，不镜像
        #6.验证镜像功能的正确性（文字旋转180度，同时镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 35 * 1000000, True, 6, attributes, 0)  # 文字旋转180度，同时镜像
        #7.验证不镜像情况下自定义旋转角度（文字自定义旋转30度，不镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        60 * 1000000, 26 * 1000000, True, 8, attributes, 30)  # 文字自定义旋转30度，不镜像
        #8.验证镜像情况下自定义旋转角度（文字自定义旋转66度，镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        60 * 1000000, 36 * 1000000, True, 9, attributes, 66)  # 文文字自定义旋转66度，镜像
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
        #GUI.show_layer(job_ep, step, 'l3')



        '''
        测试用例名称: 单层添加不同形状大小的正、负极性线段
        预期结果: 正确添加
        执行测试用例数: 8个
        '''

        symbols = ['r5', 's5','r10', 's10']#线段形状大小
        polaritys = [True ,False]  # 线段极性
        num_x1 = 43  # x轴坐标
        attributes = [{'.fiducial_name': '0'}, {'.area': ''}]  # 定义线段属性
        for symbol in symbols:
            num_y1 = 23  # y轴坐标
            num_y2 = 30
            for polarity in polaritys:
                Layers.add_line(job_ep, step, ['l2'], symbol, num_x1 * 1000000, num_y1 * 1000000,
                                num_x1 * 1000000,
                                num_y2 * 1000000, polarity, attributes)  # 多层增加线条
                num_x1 = num_x1 - 1
                num_y1 = num_y1 - 10
                num_y2 = num_y2 - 10

        # GUI.show_layer(job_ep, step, 'l2')

        '''
        测试用例名称: 多层添加不同形状大小的正、负极性线段
        预期结果: 正确添加
        执行测试用例数: 8个
        '''

        symbols = ['r5', 's5','r10', 's10']  # 线段形状大小
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
                num_x2 = num_x2 - 1
                num_y3 = num_y3 - 10
                num_y4 = num_y4 - 10

        # GUI.show_layer(job_ep, step, 'l6')

         #3.增加正极性surface
        points_location = []
        points_location.append([66 * 1000000, 1* 1000000])
        points_location.append([66 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 1 * 1000000])
        points_location.append([66 * 1000000, 1* 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)

        # 3.增加负极性surface
        points_location = []
        points_location.append([68 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 3 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], False,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)


        #添加正极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], True, {'.bga': '', '.cm': ''},68 * 1000000, 8 * 1000000, 50 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')
        #添加负极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], False, {'.bga': '', '.cm': ''}, 67 * 1000000,
                                            5 * 1000000, 30 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')


        # 选中一个铜物件，使用线填充铜物件,不足的地方不使用弧线填充
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

        #选中一个圆形铜物件，使用线填充铜物件,不足的地方使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [925])#选中一个圆形铜皮
        Layers.use_solid_fill_contours(job_ep, step, ['l2'], 5 * 254000, True)  #使用线填充，线的最小间距为5Mil,弧度不足的地方使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [927])  #选中其中一个弧线线将其删除，以证明铜面打散时不足的地方用弧线补充了
        Layers.delete_feature(job_ep, step, ['l2'])
        GUI.show_layer(job_ep, step, 'l2')









        # Layers.use_solid_fill_contours(job_ep, step, ['l2'], 2*1000000, False)  # 使用线填充铜物件，不使用弧物件（Arc）填充
        #
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, False, False, False, 0, False, 0,
        #                                  40 * 25400)  # 为指定层填充铜物件，拆分基本元素构成的符号，并删除板框外的基本元素
        #
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, False, False, False, False, 0, False, 0,
        #                                  40 * 25400)  # 只要符号中的某个元素位于边框上或边框外，即删除整个符号
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, True, False, False, 0, False, 0,
        #                                  40 * 25400)  # 为指定层填充铜物件，切除位于边框上的基本元素，创建轮廓化的铜面
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, False, False, False, 0, False, 0,
        #                                  40 * 25400)  # 为指定层填充铜物件，当边框要切除基本元素时，删除符号
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, False, True, False, 0, False, 0,
        #                                  40 * 25400)  # 为指定层填充铜物件，将原点设置为基准点
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, False, False, False, 0, False, 0,
        #                                  40 * 25400)  # 为指定层填充铜物件，将原点设置为step边缘的(0.0)
        #
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  82 * 25400, 42 * 25400, True, False, False, False, 0, True, 0,
        #                                  40 * 25400)  #为指定层填充铜物件，铜面以指定的距离间隔的符号的填充,轮廓线转换极性
        #
        # Layers.use_pattern_fill_contours(job_ep, step, 'l2', 'r39.37',
        #                                  85 * 25400, 45 * 25400, True, False, False, False, 0, False, 0,
        #                                  40 * 25400)  #为指定层填充铜物件，铜面以指定的距离间隔的符号的填充,轮廓线不转换极性


        #4增加pad
        '''
        测试用例名称:添加不同形状大小的正、负极性Pad
        预期结果: 正确添加
        执行测试用例数: 70个
        '''
        points_location = []
        points_location.append([1 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 36 * 1000000])
        points_location.append([208 * 1000000, 36 * 1000000])
        points_location.append([208 * 1000000, 29 * 1000000])
        points_location.append([1 * 1000000, 29 * 1000000])
        Layers.add_surface(job_ep, step, ['l5'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 先添加一块正极性大同皮，后面在铜皮上添加负极性pad
        Layers.add_pad(job_ep, step, ['l2'], "s100", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)
        symbols = ['r50', 's50', 'rect50x50', 'rect50x50xr25x2', 'rect50x50xr25x12', 'rect50x50xr25x123', 'rect50x50xr25',  'rect50x50','rect50x50xc25x2',
                   'rect50x50xc25x12', 'rect50x50xc25x123', 'rect50x50xc25', 'oval50x50', 'di50x50', 'oct50x50x10', 'donut_r50x30', 'donut_s50x30',
                   'hex_l50x50x10', 'hex_s50x30x10', 'bfr50', 'bfs50', 'tri50x30', 'oval_h50x30', 'thr60x30x1x3x10', 'ths60x30x1x3x10', 'sr_ths60x30x1x3x10',
                   'rc_ths60x30x1x3x10x10', 'el50x20', 'moire60x30x1x30x10x10', 'hole20xvx1x1', 'hole50xnx2x2', 'hole80xpx2x2', 'null50000']  #设置pad形状大小(共35种类型)}
        #s_tho60x30x1x3x10", 'rc_tho60x30x1x3x10x6这两种Pad，G软件不识别，会报错（已提交bug）
        polaritys = [True, False]  # 设置pad极性
        num_x3 = 1  # x轴坐标
        attributes = [{'.drill': 'via'}, {'.drill_first_last': 'first'}]  # 定义线段属性
        for symbol in symbols:
            num_y5 = 25  # y轴坐标
            for polarity in polaritys:
                Layers.add_pad(job_ep, step, ['l5'], symbol, num_x3*1000000, num_y5*1000000, polarity,
                               9,attributes, 0)
                num_x3 = num_x3 + 3
                num_y5 = num_y5 + 8

        #顺时针填加一个正极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 1*1000000, 26*1000000,
        9*1000000, 34*1000000, 5*1000000, 30*1000000, True, True, attributes)

        #顺时针填加一个负极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 1 * 1000000, 7 * 1000000,
                       5 * 1000000, 11 * 1000000, 3 * 1000000, 9 * 1000000, True, False, attributes)

        #逆时针填加一个正极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 39 * 1000000, 26 * 1000000,
                       25 * 1000000, 34 * 1000000, 32 * 1000000, 30 * 1000000, False, True, attributes)
        #逆时针填加一个负极性弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l7'], 'r10', 20 * 1000000, 9 * 1000000,
                       16 * 1000000, 11 * 1000000, 18 * 1000000, 10 * 1000000, False, False, attributes)
        GUI.show_layer(job_ep, step, 'l7')


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
        for each in ['l1','l2','l3','l4','l5','l6','l7']:
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