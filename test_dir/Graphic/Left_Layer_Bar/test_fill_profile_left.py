import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from config_g.g_cc_method import G
from epkernel.Edition import Matrix

# @pytest.mark.Attributes
class TestGraphicFillProfile:
    # @pytest.mark.Attributes
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Fill_Profile_left'))
    def testfill_profile(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试根据外形轮廓填充实体--fill profile,ID:34663
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
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

        # 1.验证填充方式为实铜，其余参数默认
        Layers.fill_profile(job_ep, step, ['l1'], 0, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 2.验证填充方式为网格铜，其余参数默认
        # Layers.delete_feature(job_ep, step, ['l2'])
        Layers.set_fill_grid_param(0, 2540000, 2540000, 254000, 0, 0)
        Layers.fill_profile(job_ep, step, ['l2'], 2, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l2')

        # 2.1.验证填充方式为网格铜，角度旋转45
        Layers.delete_feature(job_ep, step, ['l10'])
        Layers.set_fill_grid_param(45, 15240000, 10160000, 508000, 0, 0)
        Layers.fill_profile(job_ep, step, ['l10'], 2, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        GUI.show_layer(job_ep, step, 'l10')

        # 2.2.验证填充方式为网格铜，x_offset偏移1inch
        Layers.delete_feature(job_ep, step, ['smb'])
        Layers.set_fill_grid_param(0, 15240000, 10160000, 508000, 25400000, 0)
        Layers.fill_profile(job_ep, step, ['smb'], 2, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        GUI.show_layer(job_ep, step, 'smb')

        # 2.3.验证填充方式为网格铜，y_offset偏移3inch
        Layers.delete_feature(job_ep, step, ['smt'])
        Layers.set_fill_grid_param(0, 10160000, 10160000, 508000, 0, 76200000 )
        Layers.fill_profile(job_ep, step, ['smt'], 2, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        GUI.show_layer(job_ep, step, 'smt')

        # 3.验证填充方式为line填充。不使用arc，其余参数默认
        Layers.delete_feature(job_ep, step, ['l3'])
        Layers.set_fill_solid_param(False, 12700, False)
        Layers.fill_profile(job_ep, step, ['l3'], 1, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l3')

        # 4.验证填充方式为line，使用arc，其余参数默认
        Layers.delete_feature(job_ep, step, ['l4'])
        Layers.set_fill_solid_param(False, 12700, True)
        Layers.fill_profile(job_ep, step, ['l4'], 1, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l4')

        # 5.验证填充方式为指定symbol，其余参数默认
        Layers.delete_feature(job_ep, step, ['l5'])
        Layers.set_fill_pattern_param('s36', True, False, 2540000,
                                      2540000, True, False, False, 0, 0, 0, 0)
        Layers.fill_profile(job_ep, step, ['l5'], 3, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l5')

        # 5.1.验证填充方式为指定symbol，odd_offset奇数行偏移0.3inch
        Layers.delete_feature(job_ep, step, ['l6'])
        Layers.set_fill_pattern_param('donut_r50x25', True, False, 7620000,
                                      7620000, True, False, False, 0, 0, 12700000, 0)
        Layers.fill_profile(job_ep, step, ['l6'], 3, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l6')

        # 5.2.验证填充方式为指定symbol，even_offset偶数行偏移0.2inch
        Layers.delete_feature(job_ep, step, ['l7'])
        Layers.set_fill_pattern_param('hex_l100x60x15', True, False, 5080000,
                                      5080000, True, False, False, 0, 5080000, 0, 0)
        Layers.fill_profile(job_ep, step, ['l7'], 3, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l7')

        # 5.3.验证填充方式为指定symbol，角度旋转45
        Layers.delete_feature(job_ep, step, ['l8'])
        Layers.set_fill_pattern_param('tri20x40', True, False, 2540000,
                                      2540000, True, False, False, 0, 0, 0, 45)
        Layers.fill_profile(job_ep, step, ['l8'], 3, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        # GUI.show_layer(job_ep, step, 'l8')

        # 5.4.验证填充方式为指定symbol，break_partial为false
        Layers.delete_feature(job_ep, step, ['l9'])
        Layers.set_fill_pattern_param('el100x60', False, False, 15240000,
                                      10160000, True, False, False, 0, 0, 0, 0)
        Layers.fill_profile(job_ep, step, ['l9'], 3, False, [], 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, True)
        GUI.show_layer(job_ep, step, 'l9')




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
