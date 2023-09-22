import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from config_g.g_cc_method import G
from epkernel.Edition import Matrix


class TestGraphicClipAreaUseReference:
    # @pytest.mark.Clip_area_use_reference
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Clip_area_use_reference'))
    def testClip_area_use_reference(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试指定参考层的物件删除工作层--Clip_area_use_reference,ID:34662
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l2']  # 定义需要比对的层
        # layers = ['l1','l2','l4','l3','l5','l6','l7','l8','l9','l10','l1++','l3++','l2++','l4++']
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
        GUI.show_layer(job_ep, step, 'l1')

        # 2.验证Clip area_use_reference功能,指定参考层的物件删除工作层，切割范围外扩5mil，其余默认，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l2'], 'drl1-10', 127000,
                                       False, True, True, True, True, True)
        GUI.show_layer(job_ep, step, 'l2')

        # 3.验证Clip area_use_reference功能,指定参考层的物件删除工作层，切割范围内缩-1mil，其余默认,有问题
        Layers.clip_area_use_reference(job_ep, step, ['l4'], 'drl1-10', -25400,
                                       False, True, True, True, True, True)
        GUI.show_layer(job_ep, step, 'l4')

        # 4.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化（True），其余默认
        Layers.clip_area_use_reference(job_ep, step, ['l3'], 'drl1-10', 0,
                                       True, True, True, True, True, True)
        GUI.show_layer(job_ep, step, 'l3')
        #
        # 5.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化，切割范围外扩3mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l5'], 'drl1-10', 76200,
                                       True, True, True, True, True, True)
        GUI.show_layer(job_ep, step, 'l5')

        # 6.验证Clip area_use_reference功能,指定参考层的物件删除工作层，物件轮廓化，切割范围内缩-1.5mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l6'], 'drl1-10', -38100,
                                       True, True, True, True, True, True)
        GUI.show_layer(job_ep, step, 'l6')

        # 7.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，其余默认
        Layers.clip_area_use_reference(job_ep, step, ['l7'], 'drl1-10', 0,
                                       False, False, False, False, False, True)
        GUI.show_layer(job_ep, step, 'l7')

        # 8.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化
        Layers.clip_area_use_reference(job_ep, step, ['l8'], 'drl1-10', 0,
                                       True, False, False, False, False, True)
        GUI.show_layer(job_ep, step, 'l8')

        # 9.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化，切割范围外扩2mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l9'], 'drl1-10', 50800,
                                       True, False, False, False, False, True)
        GUI.show_layer(job_ep, step, 'l9')

        # 10.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除pad，物件轮廓化，切割范围内缩-2mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l10'], 'drl1-10', -50800,
                                       True, False, False, False, False, True)
        GUI.show_layer(job_ep, step, 'l10')

        # 11.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除line
        Layers.clip_area_use_reference(job_ep, step, ['l1++'], 'smt', 0,
                                       False, False, False, False, True, False)
        GUI.show_layer(job_ep, step, 'l1++')

        # 12.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除line,物件轮廓化，切割范围外扩4mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l3++'], 'smt', 101600,
                                       True, False, False, False, True, False)
        GUI.show_layer(job_ep, step, 'l3++')

        # 13.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除surface
        Layers.clip_area_use_reference(job_ep, step, ['l2++'], 'smt', 0,
                                       False, False, True, False, False, False)
        GUI.show_layer(job_ep, step, 'l2++')
        #
        # 14.验证Clip area_use_reference功能,指定参考层的物件删除工作层，只删除surface，物件轮廓化，切割范围外扩4mil，有问题
        Layers.clip_area_use_reference(job_ep, step, ['l4++'], 'smt', 101600,
                                       True, False, True, False, False, False)
        GUI.show_layer(job_ep, step, 'l4++')

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
