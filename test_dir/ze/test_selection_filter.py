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

class TestGraphicSelection_filter:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Selection_filter'))
    def testSelection_filter(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Selection_filter功能
        '''
        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['l1','l2','l3','l4']  # 自定义比对的层

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

        #1.用筛选器选中整层物件，然后删除它
        Selection.select_features_by_filter(job_ep, step, ['l1'])#选中整层物件
        Layers.delete_feature(job_ep, step, ['l1'])  # 删除所选物件

        #2.用筛选器选中所有负极性物件，然后删除它
        Selection.set_featuretype_filter(False,True, True, True, True, True, True)#选中所有负极性物件
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Layers.delete_feature(job_ep, step, ['l2'])  # 删除所选物件

        #3.用筛选器选中所有正极性物件，然后删除它
        Selection.set_featuretype_filter(True, False, True, True, True, True, True)  # 选中所有正极性物件
        Selection.select_features_by_filter(job_ep, step, ['l3'])
        Layers.delete_feature(job_ep, step, ['l3'])  # 删除所选物件

      #4.手动添加文字、线、surface、pad、弧线,然后删除surface属性外的物件
        attributes = [{'.text': '2'}]  # 定义文字属性
        Layers.add_text(job_ep, step, ['l4'], 'standard', '66666', 20 * 25400, 20 * 25400, 2 * 25400,
                        3 * 10000000, 4 * 10000000, True, 0, attributes, 45)

        Layers.add_line(job_ep, step, ['l4'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])

        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l4'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#添加surface

        Layers.add_pad(job_ep, step, ['l4'], "s100", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)#添加pad

        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l4'], 'r7.874', 40 * 1000000, 25 * 1000000,
                       40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)#添加ARC
        Selection.set_featuretype_filter(True, True, True, False, True, True, True)  # 用筛选器只留surface
        Selection.select_features_by_filter(job_ep, step, ['l4'])# 用筛选器除了surface其他属性全选
        Layers.delete_feature(job_ep, step, ['l4'])  # 删除所选物件


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