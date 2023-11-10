import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job


# @pytest.mark.Fill_Profile_left_panel
class TestGraphicFillProfilePanel:
    # @pytest.mark.Fill_Profile_left_panel
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Fill_Profile_left_panel'))
    def testfill_profile_panel(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试根据外形轮廓填充实体--fill profile,ID:
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'panel'  # 定义需要执行比对的step名
        # layers = ['drl1-10+1', 'l4+1', 'l5+1','l1+1','l6+1', 'l7+1', 'l7-neg', 'l2+1']  # 定义需要比对的层
        # layers = ['l1','l2','l3','l4','l5','l6','l7','l8']
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

        # 1.验证填充方式为实铜，依据父profile线x方向涨缩值，margin外扩为负数
        Layers.fill_profile(job_ep, step, ['gtl'], 0, False, [],
                            -50800000, -50800000, 0, 0, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gtl')

        # 2.验证填充方式为实铜，依据父profile线x方向涨缩值，margin内缩为正数
        Layers.fill_profile(job_ep, step, ['l2'], 0, False, [],
                            5080000, 12700000, 0, 0, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l2')

        # 3.验证填充方式为实铜，铺的铜从父Margin线边缘算起Max Distancee的x、y方向最大的铺铜距离
        Layers.fill_profile(job_ep, step, ['l3'], 0, False, [],
                            0, 0, 203200000, 127000000, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l3')

        # 4.验证填充方式为实铜，依据子profile线x、y方向涨缩值，S&R的Margin内缩为负数
        Layers.fill_profile(job_ep, step, ['gbl'], 0, False, [],
                            0, 0, 0, 0, -25400000, -50800000, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gbl')

        # 5.验证填充方式为实铜，依据子profile线x、y方向涨缩值，S&R的Margin外扩为正数
        Layers.fill_profile(job_ep, step, ['gts'], 0, False, [],
                            0, 0, 0, 0, 10160000, 5080000, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gts')

        # 6.验证填充方式为实铜，铺的铜从子Margin线边缘算起SR_max_distance的x、y方向最大的铺铜距离
        Layers.fill_profile(job_ep, step, ['gbs'], 0, False, [],
                            0, 0, 0, 0, 0, 0, 12700000, 25400000, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gbs')

        # 7.验证填充方式为实铜，依据父profile线x方向涨缩值，margin内缩并计算最大的铺铜距离
        Layers.fill_profile(job_ep, step, ['gbo'], 0, False, [],
                            12700000, 20320000, 76200000, 127000000, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gbo')

        # 8.验证填充方式为实铜，依据父profile线x方向涨缩值，margin外扩并计算最大的铺铜距离
        Layers.fill_profile(job_ep, step, ['gto'], 0, False, [],
                            -15240000, -12700000, 101600000, 127000000, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gto')

        # 9.验证填充方式为实铜，依据子profile线x、y方向涨缩值，S&R的Margin外扩为正数并计算子Margin线边缘
        Layers.fill_profile(job_ep, step, ['gtl+1'], 0, False, [],
                            0, 0, 0, 0, 5080000, 15240000, 101600000, 76200000, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gtl+1')

        # 10.验证填充方式为实铜，依据子profile线x、y方向涨缩值，S&R的Margin内缩为负数并计算子Margin线边缘
        Layers.fill_profile(job_ep, step, ['l2+1'], 0, False, [],
                            0, 0, 0, 0, -12700000, -20320000, 25400000, 5080000, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l2+1')

        # 11.验证填充方式为实铜，需避的子step列表
        Layers.fill_profile(job_ep, step, ['l3+1'], 0, True, ['set46'],
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l3+1')

        # 12.验证填充方式为实铜，需避的子step列表并避孔外扩0.3inch
        Layers.fill_profile(job_ep, step, ['gbl+1'], 0, True, ['set033'],
                            0, 0, 0, 0, 0, 0, 0, 0, 7620000, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'gbl+1')

        # 13.验证填充方式为实铜，需避的子step列表并避rout层时外扩值0.08inch
        Layers.fill_profile(job_ep, step, ['rout'], 0, True, ['set033'],
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 2032000, 0, True)
        # GUI.show_layer(job_ep, step, 'rout')

        # 14.验证填充方式为实铜,避同层物件外扩值
        Layers.fill_profile(job_ep, step, ['gtl+2'], 0, True, ['set46'],
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7620000, True)
        GUI.show_layer(job_ep, step, 'gtl+2')




        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_case,step,'drl1-10')

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
        step1, step2 = 'panel', 'panel'
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
