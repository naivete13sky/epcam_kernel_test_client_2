import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job

class TestGraphicEditMove:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Move'))
    def testMove(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试 Move功能, 用例数：9
        ID: 11631
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['top', 'l2', 'l2+1', 'l3', 'l3+1', 'l4', 'l4+1', 'l5', 'l5+1', 'l6', 'l6+1', 'l7', 'l7+1', 'bot']

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

        # 1、移动选中物件
        Selection.select_feature_by_id(job_ep, step, 'top', [2525])
        Layers.move2same_layer(job_ep, step, ['top'], 2*2540000, 0)

        # 2、移动整层物件
        Layers.move2same_layer(job_ep, step, ['bot'], 2*2540000, 0)

        # 3、选中负属性物件移动到其他层并反转极性
        Selection.select_feature_by_id(job_ep, step, 'l2', [20])
        Matrix.create_layer(job_ep, 'l2+1')
        Layers.move2other_layer(job_ep, step, ['l2'], job_ep, step, 'l2+1', True, 0, 0, 0, 0, 0, 0, 0)

        # 4、选中物件移动至其他层并横纵向偏移
        Selection.select_feature_by_id(job_ep, step, 'l3', [0])
        Matrix.create_layer(job_ep, 'l3+1')
        Layers.move2other_layer(job_ep, step, ['l3'], job_ep, step, 'l3+1', False, 200*25400, -200*25400, 0, 0, 0, 0, 0)

        # 5、选中物件移动至其他层并水平镜像
        Selection.select_feature_by_id(job_ep, step, 'l4', [0])
        Matrix.create_layer(job_ep, 'l4+1')
        Layers.move2other_layer(job_ep, step, ['l4'], job_ep, step, 'l4+1', False, 0, 0, 1, 0, 0, 0, 0)

        # 6、选中物件移动至其他层并竖直镜像
        Selection.select_feature_by_id(job_ep, step, 'l5', [0])
        Matrix.create_layer(job_ep, 'l5+1')
        Layers.move2other_layer(job_ep, step, ['l5'], job_ep, step, 'l5+1', False, 0, 0, 2, 0, 0, 0, 0)

        # 7、选中物件移动至其他层并涨大4mil
        Selection.select_feature_by_id(job_ep, step, 'l6', [866])
        Matrix.create_layer(job_ep, 'l6+1')
        Layers.move2other_layer(job_ep, step, ['l6'], job_ep, step, 'l6+1', False, 0, 0, 0, 4*25400, 0, 0, 0)

        # 8、选中物件移动至其他层并以锚点旋转45°
        Selection.select_feature_by_id(job_ep, step, 'l7', [0])
        Matrix.create_layer(job_ep, 'l7+1')
        Layers.move2other_layer(job_ep, step, ['l7'], job_ep, step, 'l7+1', False, 0, 0, 0, 0, 45, 0, 0)

        # 9、多个层别移动到同一层
        Matrix.create_layer(job_ep, 'l8+1')
        Layers.move2other_layer(job_ep, step, ['l8', 'l9', 'drl1-10'], job_ep, step, 'l8+1', False, 0, 0, 0, 0, 0, 0, 0)

        # GUI.show_layer(job_ep, step, 'l8+1')
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
