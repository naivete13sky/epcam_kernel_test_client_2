import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job


class TestGraphicEditResize:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Resize'))
    def testResize(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Resize功能，用例数：11
        ID: 11941
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'  # 定义需要执行比对的step名
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'outline', 'comp', 'symbol_type', 'drlmap']

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        Input.open_job(job_ep, temp_compressed_path)

        # 1、选中pad、line、surface物件涨大
        Selection.select_feature_by_id(job_ep, step, 'top', [9, 36, 58, 1457, 2525])
        Layers.resize_global(job_ep, step, ['top'], 0, 10*25400)

        # 2、整层物件缩小
        Layers.resize_global(job_ep, step, ['l2'], 1, -5 * 25400)

        # 3、多层物件涨大
        Layers.resize_global(job_ep, step, ['l3', 'l4'], 1, 5*25400)

        # 4、涨大0mil
        Layers.resize_global(job_ep, step, ['l5'], 1, 0)

        # 5、涨大缩小极限值8000
        Layers.resize_global(job_ep, step, ['l6'], 1, 8000*25400)
        Layers.resize_global(job_ep, step, ['l7'], 1, -8000*25400)

        # 6、涨弧
        Selection.select_feature_by_id(job_ep, step, 'l8', [899, 903, 911, 915])
        Layers.resize_polyline(job_ep, step, ['l8'], 14*25400, True)

        # 7、涨外框线
        Selection.select_feature_by_id(job_ep, step, 'l9', [1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015,
                                                            1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025])
        Layers.resize_polyline(job_ep, step, ['l9'], 30*25400, True)

        # 8、不选中缩小外框线
        Selection.select_feature_by_id(job_ep, step, 'l5', [680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691,
                                                            692, 693, 694, 695, 696, 697, 698, 699])
        Matrix.create_layer(job_ep, 'outline')
        Layers.copy2other_layer(job_ep, step, 'l5', 'outline', False, 0, 0, 0, 0, 0, 0, 0)
        Layers.resize_polyline(job_ep, step, ['outline'], -5 * 25400, False)

        # 9、缩小特殊pad(user symbol)导致物件消失-----BUG号:4393
        Selection.set_include_symbol_filter(['i274x.macro138.d138_inc_1.5'])    # 第一个属性物件
        Selection.select_features_by_filter(job_ep, step, ['comp'])
        Layers.resize_global(job_ep, step, ['comp'], 0, -38100)
        Selection.set_include_symbol_filter(['construct_inc_1.5'])    # 第二个属性物件
        Selection.select_features_by_filter(job_ep, step, ['comp'])
        Layers.resize_global(job_ep, step, ['comp'], 0, -38100)
        Selection.reset_select_filter()  # 重置筛选

        # 10、涨大多种symbol-----BUG号：3809
        Layers.resize_global(job_ep, step, ['symbol_type'], 1, 20 * 25400)

        # 11、涨大缩小任意相同值-----BUG号：3515
        Layers.resize_global(job_ep, step, ['drlmap'], 0, 10 * 25400)
        Layers.resize_global(job_ep, step, ['drlmap'], 0, -10 * 25400)

        # BUG号：387 暂未解决，解决了再更新场景、测试料号

        GUI.show_layer(job_ep, step, 'l8')
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

        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path, job1=job_g, step1=step,
                                all_layers_list_job1=layers, job2=job_ep, step2=step,
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
