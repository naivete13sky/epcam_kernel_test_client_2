import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel import Application
from epkernel.Action import Information, Selection

class TestGraphicAdd_text:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_text'))
    def testAdd_text(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add_text功能（ID:39614）
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
        测试用例名称:添加不同镜像和角度的正负极性的text
        预期结果: 均正确添加
        执行测试用例数: 20个
        '''
        points_location = []
        points_location.append([1 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 50 * 1000000])
        points_location.append([72 * 1000000, 50 * 1000000])
        points_location.append([72 * 1000000, 42 * 1000000])
        points_location.append([1 * 1000000, 42 * 1000000])
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
                num_y7 = num_y7 + 6
        GUI.show_layer(job_ep, step, 'l1')


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
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./ ', 20 * 25400, 20 * 25400, 3 * 25400,
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