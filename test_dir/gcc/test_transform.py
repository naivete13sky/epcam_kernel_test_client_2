import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditTransform:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Transform'))
    def testTransform (self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Transform功能，用例数：9
        ID: 12015
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'spb']

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

        # 1、选中物件以原点旋转缩小
        Selection.select_feature_by_id(job_ep, step, 'top', [2525])
        Layers.transform_features(job_ep, step, 'top', 0, True, True, False, False, False, {'ix': 0, 'iy': 0},
                                  180, 0.8, 0.8, 0, 0)

        # 2、整层物件以指定锚点旋转X轴镜像
        Layers.transform_features(job_ep, step, 'l2', 0, True, False, True, False, False,
                                  {'ix': 100*25400, 'iy': 10*25400}, 90, 0, 0, 0, 0)

        # 3、整层物件以Y轴镜像并向下偏移
        Layers.transform_features(job_ep, step, 'l3', 0, False, False, False, True, False, {'ix': 0, 'iy': 0},
                                  0, 0, 0, 0, -100*25400)

        # 4、整层物件以X轴偏移放大复制
        Layers.transform_features(job_ep, step, 'l4', 0, False, True, True, False, True, {'ix': 0, 'iy': 0},
                                  0, 2, 2, 200*25400, 0)

        # 5、选中单物件以其中心点旋转并放大
        Selection.select_feature_by_id(job_ep, step, 'l5', [1])
        Layers.transform_features(job_ep, step, 'l5', 1, True, True, False, False, False, {'ix': 0, 'iy': 0},
                                  45, 1.2, 1.2, 0, 0)

        # 6、选中多物件以各自中心点X轴镜像并缩小
        Selection.select_feature_by_id(job_ep, step, 'l6', [0, 1, 2])
        Layers.transform_features(job_ep, step, 'l6', 1, False, True, True, False, False, {'ix': 0, 'iy': 0},
                                  0, 0.8, 0.8, 0, 0)

        # 7、选中多个物件以各自中心点Y轴镜像并向上偏移
        Selection.select_feature_by_id(job_ep, step, 'l7', [0, 1, 5, 722])
        Layers.transform_features(job_ep, step, 'l7', 1, False, False, False, True, False, {'ix': 0, 'iy': 0},
                                  0, 0, 0, 0, 100*25400)

        # 8、整层物件以各自中心点X轴偏移放大复制
        Layers.transform_features(job_ep, step, 'l8', 0, False, True, True, False, True, {'ix': 0, 'iy': 0},
                                  0, 2, 2, 200 * 25400, 0)

        # 9、涨大带有弧线的外框线-----BUG号：1785
        Selection.set_featuretype_filter(True, False, False, False, True, True, False)
        Selection.select_features_by_filter(job_ep, step, ['spb'])
        Layers.transform_features(job_ep, step, 'spb', 0, False, True, False, False, False, {'ix': 0, 'iy': 0}, 0, 1.2,
                                  1.2, 0, 0)
        Selection.reset_select_filter()

        # GUI.show_layer(job_ep, step, 'spb')
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
                                job1=job_g, step1=step, all_layers_list_job1=layers, job2=job_ep,step2=step,
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
