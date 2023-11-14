import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job

class TestGraphicEditLine_fill_contours:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Line_fill_contours'))
    def testLine_fill_contours(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Use_line_fill_contours填充功能（ID：18646）
        '''
        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'orig'  # 定义需要执行比对的step名
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

        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_ep,temp_compressed_path)  # 用悦谱CAM打开料号


        #1.选中两块正极性铜皮进行填充,按照设置的参数正确执行
        Selection.select_feature_by_id(job_ep, step, 'l1', [27,0])
        Layers.use_line_fill_contours(job_ep, step, 'l1', 10*25400, 10*25400, 5*25400, 20*25400, 20*25400, 45)#设置网格X方向间距为10mil,Y方向间距为10mil,
        # 网格线宽为5mil,首根网格线X方向偏置20mil,首根网格线Y方向偏置20mil,网格线旋转顺时针角度45度
        #GUI.show_layer(job_ep, step, 'l1')

        #2.整合一层的正负极性铜皮填充,按照设置的参数正确执行
        Selection.set_featuretype_filter(True, True, False, True, False, False, False)#筛选正极性和负极性的铜皮
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Layers.contourize(job_ep, step, ['l2'], 6350, True, 3*25400, 1)#按照界面默认属性进行填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [0])#选中整块铜皮，证明铜皮整合正确
        Layers.use_line_fill_contours(job_ep, step, 'l2', 20*25400, 15*25400, 10*25400, 30*25400, 30*25400, 89)
        # 设置网格X方向间距为20mil,Y方向间距为15mil,
        # 网格线宽为10mil,首根网格线X方向偏置30mil,首根网格线Y方向偏置30mil,网格线旋转顺时针角度89度
        Layers.use_line_fill_contours(job_ep, step, 'l2', 20 * 25400, 15 * 25400, 10 * 25400, 30 * 25400, 30 * 25400,
                                      90)
        Selection.reset_selection()     # 重置筛选器，不影响后续功能使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l2')

        #3.选中1块铜皮进行填充,按照设置的参数正确执行（验证angle取值范围0~89）
        Selection.select_feature_by_id(job_ep, step, 'l3', [0])
        Layers.use_line_fill_contours(job_ep, step, 'l3', 10*25400, 10*25400, 5*25400, 0*25400, 0*25400, 90)
        # 设置网格X方向间距为10mil,Y方向间距为10mil,
        # 网格线宽为5mil,首根网格线X方向偏置0mil,首根网格线Y方向偏置0mil,网格线旋转顺时针角度90度(预期：由于角度超过边界值，所以不执行旋转操作，其他设置正确执行)
        # GUI.show_layer(job_ep, step, 'l3')

        #4.选中负极性铜皮填充,按照设置的参数正确执行
        Selection.set_featuretype_filter(False, True, False, True, False, False, False)  # 筛选所有负极性的铜皮
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        #GUI.show_layer(job_ep, step, 'l4')
        Layers.use_line_fill_contours(job_ep, step, 'l4', 3*25400, 3*25400,2*25400, 0*25400, 0*25400, 45)
        # 设置网格X方向间距为3mil,Y方向间距为3mil,
        # 网格线宽为2mil,首根网格线X方向偏置0mil,首根网格线Y方向偏置0mil,网格线旋转顺时针角度45度
        Selection.reset_selection()  # 重置筛选器，不影响后续功能使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l4')

        #5.中铜皮填充,按照设置的参数正确执行(验证Dx.Dy栏的边界值为(1e-6,100）)
        Selection.select_feature_by_id(job_ep, step, 'l5', [1])
        Layers.use_line_fill_contours(job_ep, step, 'l5', 100*25400, 100*25400, 10*25400, 10*25400, 10*25400, 0)
        # 设置网格X方向间距为100mil,Y方向间距为100mil,
        # 网格线宽为10mil,首根网格线X方向偏置10mil,首根网格线Y方向偏置10mil,网格线旋转顺时针角度0度
        #GUI.show_layer(job_ep, step, 'l5')

        #6.选中铜皮填充,按照设置的参数正确执行(验证x_offset,y_offset栏的边界值为(-100,100）)
        Selection.select_feature_by_id(job_ep, step, 'l6', [0, 1, 2])#所选物件均为负极性
        Layers.use_line_fill_contours(job_ep, step, 'l6', 10*25400, 10*25400, 10*25400, 100*25400, 100*25400, 0)
        # 设置网格X方向间距为10mil,Y方向间距为10mil,
        # 网格线宽为10mil,首根网格线X方向偏置100mil,首根网格线Y方向偏置100mil,网格线旋转顺时针角度0度
        # GUI.show_layer(job_ep, step, 'l6')

        #7.选中铜皮填充,按照设置的参数正确执行(验证x_offset,y_offset栏的边界值为(-100,100）)
        Selection.select_feature_by_id(job_ep, step, 'l7', [0, 1, 2,5])#所选物件均为正极性
        Layers.use_line_fill_contours(job_ep, step, 'l7', 10 * 25400, 10 * 25400, 10 * 25400, -100 * 25400, -100 * 25400,
                                      0)
        # 设置网格X方向间距为10mil,Y方向间距为10mil,
        # 网格线宽为10mil,首根网格线X方向偏置-100mil,首根网格线Y方向偏置-100mil,网格线旋转顺时针角度0度
        #GUI.show_layer(job_ep, step, 'l7')

        save_job(job_ep, temp_ep_path)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = os.path.join(RunConfig.temp_path_g,'g',job_yg)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g, 'ep', job_ep)
        print("job_testep_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        layerInfo = []
        for each in ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7']:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = ''
            layerInfo.append(each_dict)

        print("layerInfo:", layerInfo)
        job1, job2 = job_yg, job_ep
        step1, step2 = 'orig', 'orig'
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

        # ----------------------------------------开始验证结果--------------------------------------------------------
        Print.print_with_delimiter('比对结果信息展示--开始')
        if data['g1_vs_total_result_flag'] == True:
            print("恭喜您！料号导入比对通过！")
        if data['g1_vs_total_result_flag'] == False:
            print("Sorry！料号导入比对未通过，请人工检查！")
        Print.print_with_delimiter('分割线', sign='-')
        print('G1转图的层：', data["all_result_g1"])
        Print.print_with_delimiter('分割线', sign='-')
        # print('悦谱比图结果：', all_result_ep_vs_g_g2)
        Print.print_with_delimiter('比对结果信息展示--结束')
        assert data['g1_vs_total_result_flag'] == True
        for key in data['all_result_g1']:
            assert data['all_result_g1'][key] == "正常"
        Print.print_with_delimiter("断言--结束")
