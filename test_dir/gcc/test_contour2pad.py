import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditContour2pad:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Contour2pad'))
    def testContour2pad (self, job_id, g, prepare_test_job_clean_g):

        '''本用例测试Contour2pad铜皮转pad功能'''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['top', 'bot', 'gtl', 'top+++', 'bot+++', 'gtl+++']

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

        # 选取多个铜皮转换成pad然后删除所有pad
        points_location = []
        points_location.append([1 * 1000000, -1 * 1000000])
        points_location.append([1 * 1000000, -5 * 1000000])
        points_location.append([5 * 1000000, -5 * 1000000])
        points_location.append([5 * 1000000, -1 * 1000000])      # 添加一个方形铜皮
        Layers.add_surface(job_ep, step, ['top'], True, [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)
        Selection.select_feature_by_id(job_ep, step, 'top', [8, 9, 13, 20, 2526])
        Layers.contour2pad(job_ep, step, ['top'], 1*25400, 5*25400, 99999*25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['top'])
        Layers.delete_feature(job_ep, step, ['top'])
        Selection.reset_selection()     # 重置筛选
        Selection.reset_select_filter()

        # 添加圆surface，全部转为pad之后删除pad
        Layers.add_round_surface(job_ep, step, ['bot'], True,
                                 [{'.out_flag': '233'}, {'.pattern_fill': ''}], 0, 0, 35 * 25400)
        Layers.contour2pad(job_ep, step, ['bot'], 1 * 25400, 5 * 25400, 99999 * 25400, '+++')
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)
        Selection.select_features_by_filter(job_ep, step, ['bot'])
        Layers.delete_feature(job_ep, step, ['bot'])
        Selection.reset_selection()     # 重置筛选
        Selection.reset_select_filter()

        # 铜皮转pad导致物件变形的BUG
        Selection.select_feature_by_id(job_ep, step, 'gtl', [70])
        Layers.contour2pad(job_ep, step, ['gtl'], 1*25400, 5*25400, 99999*25400, '+++')

        # GUI.show_layer(job_ep, step, 'gtl')
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
