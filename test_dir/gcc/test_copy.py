import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job


class TestGraphicEditCopy:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Copy'))
    def testCopy(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Copy功能，用例数：5
        ID: 11839
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['top', 'l2', 'l3', 'l4', 'l5_1']

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)

        # 1、同层别原地复制极性反转
        Selection.select_feature_by_id(job_ep, step, 'top', [2525])
        Layers.copy2other_layer(job_ep, step, 'top', 'top', True, 0, 0, 0, 0, 0, 0, 0)

        # 2、同层复制坐标偏移
        Selection.select_feature_by_id(job_ep, step, 'l2', [840])
        Layers.copy2other_layer(job_ep, step, 'l2', 'l2', False, 6000000, 2000000, 0, 0, 0, 0, 0)

        # 3、同层水平镜像复制
        Selection.select_feature_by_id(job_ep, step, 'l3', [0])
        Layers.copy2other_layer(job_ep, step, 'l3', 'l3', False, 0, 0, 1, 0, 0, 0, 0)

        # 4、同层垂直镜像
        Selection.select_feature_by_id(job_ep, step, 'l4', [0])
        Layers.copy2other_layer(job_ep, step, 'l4', 'l4', False, 0, 0, 2, 0, 0, 0, 0)

        # 5、旋转90度复制到新建层别
        Matrix.create_layer(job_ep, 'l5_1')
        Selection.select_feature_by_id(job_ep, step, 'l5', [0])
        Layers.copy2other_layer(job_ep, step, 'l5', 'l5_1', False, 0, 0, 0, 0, 90, 0, 0)

        # GUI.show_layer(job_ep, step, 'l5_1')
        save_job(job_ep,temp_ep_path)
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
