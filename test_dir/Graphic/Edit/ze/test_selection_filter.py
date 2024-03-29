import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print

from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job

class TestGraphicSelection_filter:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Selection_filter'))
    def testSelection_filter(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Selection_filter功能（ID:13912）
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
        for each in ['l1','l2','l3','l4']:
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