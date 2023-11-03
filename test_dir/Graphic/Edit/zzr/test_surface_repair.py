import pytest, os, time, json, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel.Edition import Matrix

# @pytest.mark.Remove Copper Wire
class TestGraphicEditRemove_Copper_Wire:
    # @pytest.mark.Feature index
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Surface_repair'))
    def testRemove_Copper_Wire(self, job_id, g,prepare_test_job_clean_g):
        '''
        Id:15168,Surface_repair--本用例测试改变物件叠放顺序（编号）
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l1', 'l1-c', 'l2', 'l2-c', 'l4', 'l4-c', 'l10', 'l10-c', 'l3', 'l3-c', 'l5', 'l5-c',
        #           # 'l6', 'l6-c', 'l7', 'l7-c']  # 定义需要比对的层
        # layers = ['l3', 'l3-c']
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

        # 1.整层surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为False，pass
        Layers.surface_repair(job_ep, step, ['l1'], 1, 127000, 0, False)

        # 2.整层surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为True,pass   ---待补充用例
        Layers.surface_repair(job_ep, step, ['l1-c'], 1, 50800, 0, True)

        # 3.整层surface去尖角，模式：1-remove tip,圆角化为False，pass
        Layers.surface_repair(job_ep, step, ['l2'], 1, 152400, 1, False)

        # 4.整层surface去尖角，模式：1-remove tip,圆角化为True,pass
        Layers.surface_repair(job_ep, step, ['l2-c'], 1, 177800, 1, True)

        # # 5.整层surface去尖角，模式：2-bridge,圆角化为False,pass
        Layers.surface_repair(job_ep, step, ['l4'], 1, 127000, 2, False)
        #
        # # 6.整层surface去尖角，模式：2-bridge,圆角化为True,pass    ---待补充用例
        Layers.surface_repair(job_ep, step, ['l4-c'], 1, 127000, 2, True)

        # 7.整层surface去尖角，模式：3-fix sliver,圆角化为False,pass
        Layers.surface_repair(job_ep, step, ['l10'], 1, 406400, 3, False)

        # 8.整层surface去尖角，模式：3-fix sliver,圆角化为True,pass    ---待补充用例
        Layers.surface_repair(job_ep, step, ['l10-c'], 1, 406400, 3, True)

        # 9.单选surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为False,pass
        Selection.select_feature_by_id(job_ep, step, 'l3', [2279])
        Layers.surface_repair(job_ep, step, ['l3'], 0, 101600, 0, False)
        # Matrix.delete_layer(job_ep, 'l3_remove_sharp_angle')
        # GUI.show_layer(job_ep, step, 'l3')

        # 10.单选surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为True,pass，---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l3-c', [2288, 2262, 2278, 2263])
        Layers.surface_repair(job_ep, step, ['l3-c'], 0, 152400, 0, True)

        # 11.单选surface去尖角，模式：1-remove tip,圆角化为False,pass
        Selection.select_feature_by_id(job_ep, step, 'l5', [1796, 1807, 1809, 1808])
        Layers.surface_repair(job_ep, step, ['l5'], 0, 152400, 1, False)

        # 12.单选surface去尖角，模式：1-remove tip,圆角化为True,pass   ---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l5-c', [1810, 1809, 1796, 1807])
        Layers.surface_repair(job_ep, step, ['l5-c'], 0, 152400, 1, True)

        # 13.单选surface去尖角，模式：2-bridge,圆角化为False,pass
        Selection.select_feature_by_id(job_ep, step, 'l6', [16])
        Layers.surface_repair(job_ep, step, ['l6'], 0, 127000, 2, False)

        # 14.单选surface去尖角，模式：2-bridge,圆角化为True,pass   ---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l6-c', [15, 14])
        Layers.surface_repair(job_ep, step, ['l6-c'], 0, 127000, 2, True)

        # 15.单选surface去尖角，模式：3-fix sliver,圆角化为False,pass
        Selection.select_feature_by_id(job_ep, step, 'l7', [2139, 2137])
        Layers.surface_repair(job_ep, step, ['l7'], 0, 457200, 3, False)

        # 16.单选surface去尖角，模式：3-fix sliver,圆角化为True,pass  ---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l7-c', [2140, 2139, 2137])
        Layers.surface_repair(job_ep, step, ['l7-c'], 0, 406400, 3, True)

        # GUI.show_layer(job_ep, step, 'l7-c')
        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_ep,step,'l1')

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
        # for each in ['l3', 'l3-c']:
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
