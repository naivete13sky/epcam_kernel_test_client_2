import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job
from config_g.g_cc_method import G

class TestGraphicAdd:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add'))
    def testAdd(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add功能（ID：12812）
        '''
        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['l2']  # 自定义比对的层

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        # 1.增加正极性文字，字体为standard
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20*25400, 20*25400, 2 * 25400,
                        5*1000000, 24*1000000, True, 0, attributes, 0)
        # 2.增加正极性文字，字体为canned_57
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'canned_57', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 2 * 25400,
                        5 * 1000000, 25 * 1000000, True, 0, attributes, 0)
        # 3.增加正极性文字，字体为canned_67
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'canned_67', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400,
                        2 * 25400,
                        5 * 1000000, 26 * 1000000, True, 0, attributes, 0)
        # 4.增加正极性文字，字体为seven_seg
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'seven_seg', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400,
                        2 * 25400,
                        5 * 1000000, 27 * 1000000, True, 0, attributes, 0)
        # 5.增加正极性文字，字体为simple
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'simple', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400,
                        2 * 25400,
                        5 * 1000000, 28 * 1000000, True, 0, attributes, 0)
        # 6.增加正极性文字，字体为suntak_date(动态文字，为了不让其变化频率过高，该用例使用动态年份)
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'suntak_date', '$$YYYY', 20 * 25400, 20 * 25400,
                        2 * 25400,
                        5 * 1000000, 29 * 1000000, True, 0, attributes, 0)#添加动态年份（'$$YYYY'）
        #7.增加负极性文字
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20*25400, 20*25400, 2 * 25400,
                        26*1000000, 35*100000, False, 0, attributes, 0)
        #8.增加正极性文字，验证X size栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 40*25400, 20*25400, 2 * 25400,
                        5*1000000, 30*1000000, True, 0, attributes, 0)
        #9.增加正极性文字，验证Y size栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 40 * 25400, 2 * 25400,
                        5 * 1000000, 32 * 1000000, True, 0, attributes, 0)
        #10.增加正极性文字，验证Line Width栏的正确性
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 34 * 1000000, True, 0, attributes, 0)
        #11.增加正极性文字，验证旋转角度功能正确性（不镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 35 * 1000000, True, 2, attributes, 0)#文字旋转180度，不镜像
        #12.增加正极性文字，验证镜像功能的正确性（文字旋转180度，同时镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        5 * 1000000, 35 * 1000000, True, 6, attributes, 0)  # 文字旋转180度，同时镜像
        #13.增加正极性文字，验证不镜像情况下自定义旋转角度（文字自定义旋转30度，不镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        60 * 1000000, 26 * 1000000, True, 8, attributes, 30)  # 文字自定义旋转30度，不镜像
        # 13.增加正极性文字，验证镜像情况下自定义旋转角度（文字自定义旋转66度，镜像）
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l2'], 'standard', 'Gh6-=,./<>!@#$%^&*()_,./', 20 * 25400, 20 * 25400, 3 * 25400,
                        60 * 1000000, 36 * 1000000, True, 9, attributes, 66)  # 文文字自定义旋转66度，镜像



        GUI.show_layer(job_ep, step, 'l2')
        # 2.增加线条
        Layers.add_line(job_ep, step, ['l2'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        #3.增加surface
        points_location = []
        points_location.append([50 * 1000000,25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000,25 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)
        #4增加pad
        Layers.add_pad(job_ep, step, ['l2'], "s100", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)
        #5增加弧
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l2'],'r7.874', 40*1000000, 25*1000000,
        40*1000000, 31*1000000, 40*1000000, 28*1000000, True, True, attributes)


        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_g_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_g)
        print("job_yg_remote_path:", job_g_remote_path)
        job_ep_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        print("job_testcase_remote_path:", job_ep_remote_path)

        # 导入要比图的资料
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)

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