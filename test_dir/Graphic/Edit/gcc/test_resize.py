import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection, Information
from epkernel.Edition import Layers, Job, Matrix
from epkernel.Output import save_job


class TestGraphicEditResize:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Resize'))
    def testResize(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Resize功能，用例数：19
        ID: 11941
        BUG：1262、2135、3934、4097、4701、3515、3809、4110、4175、4393、4464、4465、4466、4753
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        step = 'orig'  # 定义需要执行比对的step名
        layers = ['top', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'l9', 'outline1', 'outline2', 'comp', 'symbol_type',
                  'drlmap', '4753', '4097', '2135']

        # 取到临时目录，如果存在旧目录，则删除
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

        # 取到临时目录
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')

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

        # 7、缩外框线
        feature_id = [y for y in range(1006, 1026)]
        Selection.select_feature_by_id(job_ep, step, 'l9', feature_id)
        Layers.resize_polyline(job_ep, step, ['l9'], -10*25400, True)

        # 8、多层不选中涨大外框线-----BUG号：4701
        Matrix.create_layer(job_ep, 'outline1')
        Matrix.create_layer(job_ep, 'outline2')
        feature_id = [y for y in range(680, 700)]
        Selection.select_feature_by_id(job_ep, step, 'l5', feature_id)
        Layers.copy2other_layer(job_ep, step, 'l5', 'outline1', False, 0, 0, 0, 0, 0, 0, 0)
        Layers.copy2other_layer(job_ep, step, 'outline1', 'outline2', False, 0, 0, 0, 0, 0, 0, 0)
        Layers.resize_polyline(job_ep, step, ['outline1', 'outline2'], 30 * 25400, False)

        # 9、缩小特殊pad(user symbol)导致物件消失-----BUG号:4393
        Selection.set_include_symbol_filter(['i274x.macro138.d138_inc_1.5'])    # 第一个属性物件
        Selection.select_features_by_filter(job_ep, step, ['comp'])
        Layers.resize_global(job_ep, step, ['comp'], 0, -38100)
        Selection.set_include_symbol_filter(['construct_inc_1.5'])    # 第二个属性物件
        Selection.select_features_by_filter(job_ep, step, ['comp'])
        Layers.resize_global(job_ep, step, ['comp'], 0, -38100)
        Selection.reset_select_filter()  # 重置筛选

        # 10、涨大多种symbol
        feature_id = [y for y in range(1, 24)]
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', feature_id)
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 10 * 25400)

        # 11、涨大symbol不能变形-----BUG号：4466
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [24])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 4 * 25400)

        # 12、涨大symbol圆弧角度跟着涨大-----BUG号：3809
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [25])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 2 * 25400)

        # 13、涨大超过symbol允许的极限值物件消失-----BUG号：4464、4465
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [26])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 1 * 25400)
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [27])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 4 * 25400)

        # 14、多边形PAD涨大变形-----BUG号4175
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [28, 29, 30, 31])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 4 * 25400)

        # 15、多边形PAD涨大有偏差-----BUG号：4110
        Selection.select_feature_by_id(job_ep, step, 'symbol_type', [32])
        Layers.resize_global(job_ep, step, ['symbol_type'], 0, 4 * 25400)

        # 16、涨大缩小任意相同值-----BUG号：3515
        Layers.resize_global(job_ep, step, ['drlmap'], 0, 10 * 25400)
        Layers.resize_global(job_ep, step, ['drlmap'], 0, -10 * 25400)

        # 17、铜皮涨大形状优化-----BUG号：4753
        Layers.resize_global(job_ep, step, ['4753'], 1, 1 * 25400)

        # 18、验证外框线有断线能正常外扩以及涨缩精度-----BUG号：4097、3934、1262
        Layers.resize_polyline(job_ep, step, ['4097'], 20 * 25400, False)

        # 19、验证方形、圆形同时涨缩-----BUG号：2135
        Layers.resize_polyline(job_ep, step, ['2135'], 30 * 25400, False)
        Layers.resize_polyline(job_ep, step, ['2135'], -10 * 25400, False)

        # GUI.show_layer(job_ep, step, '4097')
        save_job(job_ep, temp_ep_path)
        Job.close_job(job_ep)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_g_remote_path = os.path.join(RunConfig.temp_path_g, 'g', job_g)
        print("job_yg_remote_path:", job_g_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, 'ep', job_ep)
        print("job_testcase_remote_path:", job_ep_remote_path)

        # 导入要比图的资料
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)

        layerInfo = []
        for each in layers:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = ''
            layerInfo.append(each_dict)
        print("layerInfo:", layerInfo)

        g.layer_compare_g_open_2_job(job1=job_g, step1=step, job2=job_ep, step2=step)

        compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                        job1=job_g, step1=step,
                                        job2=job_ep, step2=step,
                                        layerInfo=layerInfo,
                                        adjust_position=True, jsonPath=r'my_config.json')
        print('compareResult_input_vs:', compareResult)
        data["all_result_g1"] = compareResult['all_result_g']
        data['g1_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']
        assert len(layers) == len(data["all_result_g1"])

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


class TestGraphicEditResize1:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Resize1'))
    def testResize1(self, job_id):

        '''
        本用例测试Resize功能，用例数：1
        ID: 11941
        BUG：3287
        '''

        step = 'orig'
        layer = '3287'

        # 取到临时目录，如果存在旧目录，则删除
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

        # 取到临时目录
        temp_compressed_path = os.path.join(temp_path, 'compressed')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job, temp_compressed_path)

        # 涨大指定物件
        Selection.select_feature_by_id(job, step, layer, [12902])
        Layers.resize_global(job, step, [layer], 0, 6*25400)

        # 获取指定物件信息，拿到symbolname
        Selection.select_feature_by_id(job, step, layer, [12902])
        feature_info = Information.get_selected_features_infos(job, step, layer)
        symbolname = feature_info[0].get('symbolname')
        print('-'*10, symbolname, '-'*10)
        symbol_name = 'i274x.a56m1_inc_6'

        # 断言
        assert symbolname == symbol_name
