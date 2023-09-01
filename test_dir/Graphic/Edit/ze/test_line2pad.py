import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditLine2pad:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Line2pad'))
    def testLine2pad (self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Line2pad线转pad功能(ID：17869)
        '''
        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']#定义参与比对的层

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        print("temp_path:", temp_path)
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        #1.验证line为起点与终点相同的线段，转换pad成功
        Layers.add_line(job_ep, step, ['l1'], 'r100', 3 * 2540000, 10 * 2540000, 3 * 2540000, 10 * 2540000, True, [])
        Selection.select_feature_by_id(job_ep, step, 'l1', [2526])
        Layers.line2pad(job_ep, step, ['l1'])#Line转pad
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['r100'])
        Selection.select_features_by_filter(job_ep, step, ['l1'])#选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l1'])
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l1')

        #2.验证line为起点与终点不相同的线段，转换pad成功
        Layers.add_line(job_ep, step, ['l2'], 'r100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 10 * 2540000, True, [])
        Selection.select_feature_by_id(job_ep, step, 'l2', [907])
        Layers.line2pad(job_ep, step, ['l2'])  # Line转pad
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['oval600x100'])
        Selection.select_features_by_filter(job_ep, step, ['l2'])  # 选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l2'])
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l2')

        #3.验证场景1:带旋转角度的线段，正确转换pad（转换pad后的角度不发生改变）
           #验证场景2:r开头的线段正确转为oval类型的pad
        Layers.add_line(job_ep, step, ['l3'], 'r100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 15 * 2540000, True, [])
        #添加了一个带角度的物件
        Selection.select_feature_by_id(job_ep, step, 'l3', [2380])
        Layers.line2pad(job_ep, step, ['l3'])  # Line转pad，且被转换的pad为oval类型
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['oval807.107x100'])
        Selection.select_features_by_filter(job_ep, step, ['l3'])  # 选中已转为pad的物件，复制一个出来
        Layers.copy2other_layer(job_ep, step, 'l3', 'l3', False,2540000, 10 * 2540000, 0, 0, 0, 0, 0)
        #复制成功，且被复制的pad角度未发生改变，证明该用例通过
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l3')

        #4.验证s开头的线段正确转为rect类型的pad
        Layers.add_line(job_ep, step, ['l4'], 's100', 3 * 2540000, 10 * 2540000, 8 * 2540000, 15 * 2540000, True, [])
        # 添加了一个带角度的物件
        Selection.select_feature_by_id(job_ep, step, 'l4', [930])
        Layers.line2pad(job_ep, step, ['l4'])  # Line转pad,且被转换的pad为rect类型
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.set_include_symbol_filter(['rect807.107x100'])
        Selection.select_features_by_filter(job_ep, step, ['l4'])  # 选中已转为pad的物件，复制一个出来
        Layers.copy2other_layer(job_ep, step, 'l4', 'l4', False, 2540000, 10 * 2540000, 0, 0, 0, 0, 0)
        # rect类型的pad复制成功，且被复制的pad角度未发生改变
        Selection.reset_selection()  # 重置选中模式，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l4')

        #5.验证单层状态下不选择任何物件，使用Line to Pad功能(只对线有作用)
        Layers.delete_feature(job_ep, step,['l5'])#先删除L5层的整层物件
        Layers.add_line(job_ep, step, ['l5'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        Layers.delete_feature(job_ep, step, ['l5'])  # 先删除L5层的整层物件
        Layers.add_line(job_ep, step, ['l5'], 'r5', 10000000, 50000000, 30000000, 50000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        # 增加两条线
        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l5'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 添加面
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l5'], 'r7.874', 40 * 1000000, 25 * 1000000,
                       40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)  # 添加弧
        Layers.line2pad(job_ep, step, ['l5'])#不选中任何物件，直接使用Line to Pad功能
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l5'])  # 选中已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l5'])
        #GUI.show_layer(job_ep, step, 'l5')


        # 6.验证多层状态下不选择任何物件，使用Line to Pad功能(只对线有作用)
        Layers.delete_feature(job_ep, step, ['l6','l7'])  # 先删除L6和L7层的整层物件
        Layers.add_line(job_ep, step, ['l6','l7'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        Layers.add_line(job_ep, step, ['l6','l7'], 'r5', 10000000, 50000000, 30000000, 50000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])
        # 增加两条线

        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l6','l7'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)  # 添加面
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l6','l7'], 'r7.874', 40 * 1000000, 25 * 1000000,
                       40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)  # 添加弧
        Layers.line2pad(job_ep, step, ['l6','l7'])  # 不选中任何物件，直接使用Line to Pad功能，作用于l6层和l7层
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['l6','l7'])  # 选中l6层和l7层已转为pad的物件，并删除
        Layers.delete_feature(job_ep, step, ['l6','l7'])
        #GUI.show_layer(job_ep, step, 'l7')

        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_g)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_case_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        print("job_testcase_remote_path:", job_case_remote_path)

        # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_case_remote_path)

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