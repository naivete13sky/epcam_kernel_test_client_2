import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job


class TestGraphicClipAreaUseManual:
    # @pytest.mark.Clip_area_use_manual
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Clip_area_use_manual'))
    def testClip_area_use_manual(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试删除指定框选区域的feature--Clip_area_use_manual,ID:31201
        本测试用例共测20个测试场景
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
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


        #1.验证Clip area功能，手动框选部分区域以内全部去除，参数默认
        add_left_x1 = 2019300
        add_left_y1 = 22811740
        add_left_x2 = 27795220
        add_left_y2 = -840740
        Layers.clip_area_use_manual(job_ep, step, ['l1'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, True, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l1')


        # 2.验证Clip area功能，手动矩形框选区域以内删除，部分物件轮廓化（切割一半保留的物件转换为surface）
        add_left_x1 = 29.155 * 1000000
        add_left_y1 = 24.784 * 1000000
        add_left_x2 = 58.204 * 1000000
        add_left_y2 = -2.170 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l2'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, True, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l2')


        # 3.验证Clip area功能,多边形框选区域以外全部删除，参数默认
        add_left_x1 = 18.571 * 1000000
        add_left_y1 = 24.894 * 1000000
        add_left_x2 = 10.248 * 1000000
        add_left_y2 = 8.027 * 1000000
        add_left_x3 = 30.864 * 1000000
        add_left_y3 = 2.239 * 1000000
        add_left_x4 = 46.298 * 1000000
        add_left_y4 = 22.469 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l3'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y2},
                                     {'ix': add_left_x3, 'iy': add_left_y3}, {'ix': add_left_x4, 'iy': add_left_y4},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l3')

        # 4.验证Clip area功能,矩形框选区域以外删除，部分物件轮廓化（切割一半保留的物件转换为surface）
        add_left_x1 = 16.036 * 1000000
        add_left_y1 = 24.288 * 1000000
        add_left_x2 = 44.258 * 1000000
        add_left_y2 = -3.382 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l4'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, False, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l4')

        # 5.验证Clip area功能,矩形框选以外的删除正负line，其余物件不删。
        add_left_x1 = 25.351 * 1000000
        add_left_y1 = 25.280 * 1000000
        add_left_x2 = 48.778 * 1000000
        add_left_y2 = -2.555 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l5'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, False, False, False, True,
                                    False)
        # GUI.show_layer(job_ep, step, 'l5')

        # 6.验证Clip area功能,矩形框选以外的删除正负pad，其余物件不删。
        add_left_x1 = 31.856 * 1000000
        add_left_y1 = 26.493 * 1000000
        add_left_x2 = 53.078 * 1000000
        add_left_y2 = -2.335 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l6'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, False, False, False, False,
                                    True)
        # GUI.show_layer(job_ep, step, 'l6')

        # 7.验证Clip area功能,矩形框选以外的删除正负surface，其余物件不删。
        add_left_x1 = 24.469 * 1000000
        add_left_y1 = 25.005 * 1000000
        add_left_x2 = 50.763 * 1000000
        add_left_y2 = -3.272 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l7'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, False, True, False, False,
                                    False)
        # GUI.show_layer(job_ep, step, 'l7')

        # 8.验证Clip area功能,矩形框选以外的删除正负arc，其余物件不删。
        add_left_x1 = 15.898 * 1000000
        add_left_y1 = 27.017 * 1000000
        add_left_x2 = 44.892 * 1000000
        add_left_y2 = -4.237 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['sst'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, False, False, True, False,
                                    False)
        # GUI.show_layer(job_ep, step, 'sst')

        # 9.验证Clip area功能,矩形框选以外的删除正负text，其余物件不删。
        add_left_x1 = 7.244 * 1000000
        add_left_y1 = 26.631 * 1000000
        add_left_x2 = 55.641 * 1000000
        add_left_y2 = -3.685 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['ssb'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, False, False, True, False, False, False,
                                    False)
        # GUI.show_layer(job_ep, step, 'ssb')

        # 10.验证Clip area功能,矩形框选以内删除正负text，部分text轮廓化（切割一半保留的物件转换为surface）。
        add_left_x1 = 9.697 * 1000000
        add_left_y1 = 26.245 * 1000000
        add_left_x2 = 49.715 * 1000000
        add_left_y2 = -5.449 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['ssb_in'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, True, True, False, False, False,
                                    False)
        # GUI.show_layer(job_ep, step, 'ssb_in')

        # 11.验证Clip area功能,矩形框选以内删除正负arc，部分arc轮廓化（切割一半保留的物件转换为surface）。
        add_left_x1 = 13.860 * 1000000
        add_left_y1 = 27.122 * 1000000
        add_left_x2 = 50.584 * 1000000
        add_left_y2 = -5.632 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['sst_in'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, True, False, False, True, False,
                                    False)
        # GUI.show_layer(job_ep, step, 'sst_in')

        # 12.验证Clip area功能,矩形框选以内删除正负pad，部分pad轮廓化（切割一半保留的物件转换为surface）。
        add_left_x1 = 9.891 * 1000000
        add_left_y1 = 25.535 * 1000000
        add_left_x2 = 38.149 * 1000000
        add_left_y2 = 0.240 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l8'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, True, False, False, False, False,
                                    True)
        # GUI.show_layer(job_ep, step, 'l8')

        # 13.验证Clip area功能,矩形框选以内删除正负line，部分line轮廓化（切割一半保留的物件转换为surface）。
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l9'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 0, True, True, False, False, False, True,
                                    False)
        # GUI.show_layer(job_ep, step, 'l9')

        # 14.验证Clip area功能,矩形框选以外外扩10mil删除所有物件，不轮廓化/////,UI上没有margin参数
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 254000, False, False, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10')

        # 15.验证Clip area功能,矩形框选以外外扩10mil删除所有物件,物件轮廓化/////,UI上没有margin参数
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10+1'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 254000, True, False, True, True, True,
                                    True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10+1')

        # 16.验证Clip area功能,矩形框选以外内缩-10mil删除所有物件，并轮廓化/////,UI上没有margin参数
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10-2'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], -254000, True, False, True, True, True,
                                    True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10-2')

        # 17.验证Clip area功能,矩形框选以外内缩-10mil删除所有物件，不轮廓化/////,UI上没有margin参数
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10-3'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], -254000, False, False, True, True, True,True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10-3')

        # 18.验证Clip area功能,矩形框选以内内缩-10mil删除物件，部分物件轮廓化（切割一半保留的物件转换为surface）。
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10-4'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], -254000, True, True, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10-4')

        # 19.验证Clip area功能,矩形框选以内内缩-10mil删除所有物件，不轮廓化
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10-5'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], -254000, False, True, True, True, True, True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10-5')

        # 20.验证Clip area功能,矩形框选以内外扩15mil删除所有物件，轮廓化
        add_left_x1 = 13.225 * 1000000
        add_left_y1 = 26.117 * 1000000
        add_left_x2 = 45.980 * 1000000
        add_left_y2 = 1.669 * 1000000
        Layers.clip_area_use_manual(job_ep, step, ['l10-6'],
                                    [{'ix': add_left_x1, 'iy': add_left_y1}, {'ix': add_left_x2, 'iy': add_left_y1},
                                     {'ix': add_left_x2, 'iy': add_left_y2}, {'ix': add_left_x1, 'iy': add_left_y2},
                                     {'ix': add_left_x1, 'iy': add_left_y1}], 381000, True, True, True, True, True,
                                    True,
                                    True)
        # GUI.show_layer(job_ep, step, 'l10-6')


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




class TestGraphicClipAreaUseReference:
    # @pytest.mark.Clip_area_use_reference
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Clip_area_use_reference'))
    def testClip_area_use_reference(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试指定参考层的物件删除工作层--Clip_area_use_reference,ID:34662
        本用例共测14个测试场景
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l2']  # 定义需要比对的层
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

        # 1.验证Clip area_use_reference功能,指定参考层的物件删除工作层，参数默认
        Layers.clip_area_use_reference(job_ep, step, ['l1'], 'drl1-10', 0,
                                       False, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 2.验证Clip area_use_reference功能,指定参考层的物件删除工作层，切割范围外扩5mil，其余默认，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l2'], 'drl1-10', 127000,
                                       False, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l2')

        # 3.验证Clip area_use_reference功能,指定参考层的物件删除工作层，切割范围内缩-1mil，其余默认,有问题
        Layers.clip_area_use_reference(job_ep, step, ['l4'], 'drl1-10', -25400,
                                       False, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l4')

        # 4.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化（True），其余默认
        Layers.clip_area_use_reference(job_ep, step, ['l3'], 'drl1-10', 0,
                                       True, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l3')
        #
        # 5.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化，切割范围外扩3mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l5'], 'drl1-10', 76200,
                                       True, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l5')

        # 6.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化，切割范围内缩-1.5mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l6'], 'drl1-10', -38100,
                                       True, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l6')

        # 7.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，其余默认
        Layers.clip_area_use_reference(job_ep, step, ['l7'], 'drl1-10', 0,
                                       False, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l7')

        # 8.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化
        Layers.clip_area_use_reference(job_ep, step, ['l8'], 'drl1-10', 0,
                                       True, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l8')

        # 9.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化，切割范围外扩2mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l9'], 'drl1-10', 50800,
                                       True, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l9')

        # 10.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化，切割范围内缩-2mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l10'], 'drl1-10', -50800,
                                       True, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l10')

        # 11.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除line
        Layers.clip_area_use_reference(job_ep, step, ['l1++'], 'smt', 0,
                                       False, False, False, False, True, False)
        # GUI.show_layer(job_ep, step, 'l1++')

        # 12.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除line,物件轮廓化，切割范围外扩4mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l3++'], 'smt', 101600,
                                       True, False, False, False, True, False)
        # GUI.show_layer(job_ep, step, 'l3++')

        # 13.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除surface
        Layers.clip_area_use_reference(job_ep, step, ['l2++'], 'smt', 0,
                                       False, False, True, False, False, False)
        # GUI.show_layer(job_ep, step, 'l2++')
        #
        # 14.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除surface，物件轮廓化，切割范围外扩4mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l4++'], 'smt', 101600,
                                       True, False, True, False, False, False)
        # GUI.show_layer(job_ep, step, 'l4++')

        # # 15.验证单选物件作为参考物删除工作层功能
        # Layers.clip_area_use_reference(job_ep, step, ['l5++'], 'smt', 101.6 * 1000000,
        #                                True, False, True, False, False, False)
        # GUI.show_layer(job_ep, step, 'l5++')




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




class TestGraphicClipAreaUseProfile:
    # @pytest.mark.Clip_area_use_reference
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Clip_area_use_profile'))
    def testClip_area_use_profile(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试根据Profile线删除工作层--Clip_area_use_profile,ID:40756
        本用例共测22个测试场景
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'net'  # 定义需要执行比对的step名
        # layers = ['l2']  # 定义需要比对的层
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

        # 1.验证去除profile版外杂物，不轮廓化，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l1'], False, False,
                                     0, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 2.验证去除profile版外杂物，轮廓化，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l2'], False, True,
                                     0, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 3.验证去除profile版外杂物，轮廓化，切割范围外扩12mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l3'], False, True,
                                     304800, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 4.验证去除profile版外杂物，轮廓化，切割范围内缩-1mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['spb'], False, True,
                                     -25400, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 5.验证去除profile版外杂物，不轮廓化，切割范围外扩14mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l4'], False, True,
                                     355600, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 6.验证去除profile版外杂物，不轮廓化，切割范围内缩-2mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['spt'], False, True,
                                     -50800, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 7.验证去除profile版外杂物，轮廓化，切割范围外扩6mil，只删除line（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l5'], False, True,
                                     152400, False, False, False, True, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 8.验证去除profile版外杂物，轮廓化，切割范围内缩-3mil，只删除pad（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l6'], False, True,
                                     -76200, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 9.验证去除profile版外杂物，轮廓化，切割范围外扩7mil，只删除surface（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l7'], False, True,
                                     177800, False, True, False, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 10.验证去除profile版外杂物，轮廓化，切割范围内缩-4mil，只删除arc（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l8'], False, True,
                                     -101600, False, False, True, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 11.验证去除profile版外杂物，轮廓化，切割范围外扩6mil，只删除text（正负）
        Layers.clip_area_use_profile(job_ep, step, ['sst'], False, True,
                                     152400, True, False, False, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 12.验证去除profile板内，不轮廓化，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l9'], True, False,
                                     0, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 13.验证去除profile板内，轮廓化，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l10'], True,True,
                                     0, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 14.验证去除profile板内，轮廓化，切割范围外扩16mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['smt'], True, True,
                                     406400, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 15.验证去除profile板内，轮廓化，切割范围内缩-5mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['smb'], True, True,
                                     -127000, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 16.验证去除profile板内，不轮廓化，切割范围内缩-20mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l10++'], True, True,
                                     -508000, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 17.验证去除profile板内，不轮廓化，切割范围外扩9mil，参数默认。
        Layers.clip_area_use_profile(job_ep, step, ['l9++'], True, True,
                                     228600, True, True, True, True, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 18.验证去除profile板内，轮廓化，切割范围内缩-6mil，只删除text（正负）
        Layers.clip_area_use_profile(job_ep, step, ['ssb'], True, True,
                                     152400, True, False, False, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 19.验证去除profile板内，轮廓化，切割范围外扩5mil，只删除arc（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l1++'], True, True,
                                     127000, False, False, True, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 20.验证去除profile板内，轮廓化，切割范围内缩-14mil，只删除surface（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l2++'], True, True,
                                     -355600, False, True, False, False, False)
        # GUI.show_layer(job_ep, step, 'l1')

        # 21.验证去除profile板内，轮廓化，切割范围外扩4mil，只删除pad（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l3++'], True, True,
                                     101600, False, False, False, False, True)
        # GUI.show_layer(job_ep, step, 'l1')

        # 22.验证去除profile板内，轮廓化，切割范围内缩-6mil，只删除line（正负）
        Layers.clip_area_use_profile(job_ep, step, ['l4++'], True, True,
                                     -152400, False, False, False, True, False)
        # GUI.show_layer(job_ep, step, 'l1')










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
