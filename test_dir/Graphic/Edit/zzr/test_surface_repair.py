import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job

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
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        layers = ['l1', 'l1-c', 'l2', 'l2-c', 'l4', 'l4-c', 'l10', 'l10-c', 'l3', 'l3-c', 'l5', 'l5-c',
                  'l6', 'l6-c', 'l7', 'l7-c']  # 定义需要比对的层
        # layers = ['l7-c']
        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_case = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_case, temp_compressed_path)  # 用悦谱CAM打开料号

        # 1.整层surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为False，pass
        Layers.surface_repair(job_case, step, ['l1'], 1, 127000, 0, False)

        # 2.整层surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为True,pass   ---待补充用例
        Layers.surface_repair(job_case, step, ['l1-c'], 1, 50800, 0, True)

        # 3.整层surface去尖角，模式：1-remove tip,圆角化为False，pass
        Layers.surface_repair(job_case, step, ['l2'], 1, 152400, 1, False)

        # 4.整层surface去尖角，模式：1-remove tip,圆角化为True,pass
        Layers.surface_repair(job_case, step, ['l2-c'], 1, 177800, 1, True)

        # 5.整层surface去尖角，模式：2-bridge,圆角化为False,pass
        Layers.surface_repair(job_case, step, ['l4'], 1, 127000, 2, False)

        # 6.整层surface去尖角，模式：2-bridge,圆角化为True,pass    ---待补充用例
        Layers.surface_repair(job_case, step, ['l4-c'], 1, 127000, 2, True)

        # 7.整层surface去尖角，模式：3-fix sliver,圆角化为False,pass
        Layers.surface_repair(job_case, step, ['l10'], 1, 152400, 3, False)

        # 8.整层surface去尖角，模式：3-fix sliver,圆角化为False,pass    ---待补充用例
        Layers.surface_repair(job_case, step, ['l10-c'], 1, 152400, 3, True)

        # 9.单选surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为False,pass
        Selection.select_feature_by_id(job_case, step, 'l3', [2293])
        Layers.surface_repair(job_case, step, ['l3'], 0, 101600, 0, False)

        # 10.单选surface去尖角，模式：0-Simplify(简易栅格化)，圆角化为True,pass，---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l3-c', [2279, 2288, 2262, 2278])
        Layers.surface_repair(job_case, step, ['l3-c'], 0, 152400, 0, True)

        # 11.单选surface去尖角，模式：1-remove tip,圆角化为False,pass
        Selection.select_feature_by_id(job_case, step, 'l5', [1810, 1809, 1796, 1808])
        Layers.surface_repair(job_case, step, ['l5'], 0, 152400, 1, False)

        # 12.单选surface去尖角，模式：1-remove tip,圆角化为True,pass   ---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l5-c', [1810, 1809, 1796, 1807])
        Layers.surface_repair(job_case, step, ['l5-c'], 0, 152400, 1, True)

        # 13.单选surface去尖角，模式：2-bridge,圆角化为False,pass
        Selection.select_feature_by_id(job_case, step, 'l6', [16])
        Layers.surface_repair(job_case, step, ['l6'], 0, 127000, 2, False)

        # 14.单选surface去尖角，模式：2-bridge,圆角化为True,pass   ---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l6-c', [15, 14])
        Layers.surface_repair(job_case, step, ['l6-c'], 0, 127000, 2, True)

        # 15.单选surface去尖角，模式：3-fix sliver,圆角化为False,pass
        Selection.select_feature_by_id(job_case, step, 'l7', [2139, 2137])
        Layers.surface_repair(job_case, step, ['l7'], 0, 101600, 3, False)

        # 16.单选surface去尖角，模式：3-fix sliver,圆角化为True,pass  ---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l7-c', [2140, 2116, 2137])
        Layers.surface_repair(job_case, step, ['l7-c'], 0, 101600, 3, True)

        # GUI.show_layer(job_case, step, 'l7-c')
        save_job(job_case, temp_ep_path)
        # GUI.show_layer(job_case,step,'l1')

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_yg)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_case_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_case)
        print("job_testcase_remote_path:", job_case_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_case_remote_path)

        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_yg, step1=step, all_layers_list_job1=layers, job2=job_case, step2=step,
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
