import pytest, os, time, json, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job

# @pytest.mark.ChangeText
class TestGraphicEditChangeText:
    # @pytest.mark.ChangeText
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Change_Text'))
    def testChangeText(self, job_id, g, prepare_test_job_clean_g):
        '''
        id:18585,本用例测试改变文字(Change_Text)
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['spt','sst','smt','l1','l2','l3','l4','l5','l6','l7','l8','l9','l10','smb','drl']  # 定义需要比对的层
        # layers = ['drl']

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

        # 1.整层修改文字内容，线款和XY大小，选择Negative反转，其他与原字体参数一致,禅道ID2554
        Layers.change_text(job_ep, step, ['spt'], '89', 'suntak_date', 2540000,
                           2540000, 304800, False, 0, 0)
        Layers.change_polarity(job_ep,step,['spt'],2,1)
        # GUI.show_layer(job_case, step, 'spt')

        # 2.单选某个文字，修改为动态文本，其余参数不变,禅道ID2553
        Selection.select_feature_by_id(job_ep, step, 'sst', [24])
        Layers.change_text(job_ep,step,['sst'],'$$DD','suntak_date',5080000,
                           5080000,762000,True,0,0)
        # GUI.show_layer(job_case, step, 'sst')

        # 3.选中某个文字，角度旋转15°修改成功，其余参数不变，禅道ID2548
        Selection.select_feature_by_id(job_ep,step,'smt',[3])
        Layers.change_text(job_ep,step,['smt'],'$$STEP','standard',5080000,
                           5080000,304800,True,0,15)
        # GUI.show_layer(job_case,step,'smt')

        # 4.选中某个文字，镜像修改成功，其余参数不变，禅道ID2545
        Selection.select_feature_by_id(job_ep, step, 'l1', [24])
        Layers.change_text(job_ep,step,['l1'],'$$YY/WK','suntak_date',5080000,
                           5080000,762000,True,1,0)
        # GUI.show_layer(job_case,step,'l1')

        # 5.选中多个文字，修改文字字体线宽，其余参数不变，禅道ID2544
        Selection.select_feature_by_id(job_ep,step,'l2',[14,1,55,22])
        Layers.change_text(job_ep,step,['l2'],'','',5080000,5080000,254000,True,0,0)
        # GUI.show_layer(job_case, step, 'l2')

        # 6.选中某个文字，修改文字的宽度与高度，其余参数不变，禅道ID2543
        Selection.select_feature_by_id(job_ep,step,'l3',[28])
        Layers.change_text(job_ep,step,['l3'],'$$YYYY','standard',2540000,
                           2540000,762000,True,0,45)
        # GUI.show_layer(job_case, step, 'l3')

        # 7.选中多个负极性的文字，修改其极性，其余参数不变，禅道ID2542
        Selection.select_feature_by_id(job_ep,step,'l4',[37,43,38,40])
        Layers.change_text(job_ep,step,['l4'],'','',5080000,
                           5080000,609600,True,0,0)
        # GUI.show_layer(job_case, step, 'l4')

        # 8.选中某个正极性的文字，修改文字内容，其余参数不变，禅道2538
        Selection.select_feature_by_id(job_ep,step,'l5',[22])
        Layers.change_text(job_ep,step,['l5'],'Turday','canned_67',5080000,
                           5080000,762000,True,0,0)
        # GUI.show_layer(job_case, step, 'l5')

        # 9.整层修改文字信息,字体类型为seven_seg，旋转角度60,禅道ID2555
        Layers.change_text(job_ep, step, ['l6'], '$$YY', 'seven_seg', 5080000,
                           5080000, 762000, True, 0, 60)
        # GUI.show_layer(job_case, step, 'l6')

        # 10.整层修改文字为负极性,字体类型为simple，角度选择90度并镜像，禅道ID3540
        Layers.change_text(job_ep, step, ['l7'], '', 'simple', 5080000,
                           5080000, 762000, False, 1, 90)
        Layers.change_polarity(job_ep,step,['l7'],2,1)
        # GUI.show_layer(job_case, step, 'l7')


        # 11.单选文字修改信息,字体类型为standard，镜像并角度旋转45度，禅道ID2539
        Selection.select_feature_by_id(job_ep, step, 'l8', [53])
        Layers.change_text(job_ep, step, ['l8'], '$$WEEK-DAY', 'standard', 2540000,
                           2540000, 406400, True, 1, 45)
        # GUI.show_layer(job_case, step, 'l8')

        # 12.选中多个文字修改信息转为负极性,字体类型为canned_67,镜像并旋转角度,禅道ID2541
        Selection.select_feature_by_id(job_ep, step, 'l9', [52, 23, 40, 25])
        Layers.change_text(job_ep, step, ['l9'], '$$LAYER', 'canned_67', 5080000,
                           5080000, 762000, False, 1, 45)
        # GUI.show_layer(job_case, step, 'l9')

        # 13.多选负极性文字转换为正，字体类型为 “standard”，禅道ID2540
        Selection.select_feature_by_id(job_ep, step, 'l10', [0,49,51,55,52])
        Layers.change_text(job_ep, step, ['l10'], 'test', 'standard', 2540000,
                           2540000, 304800, True, 0, 0)
        # GUI.show_layer(job_case, step, 'l10')

        # 14.验证多层整层改变字体，极性为正，镜像并角度旋转15°,禅道ID3546
        Layers.change_text(job_ep, step, ['smb','smb+1'], 'ceshi', 'canned_57', 5080000,
                           5080000, 635000, True, 1, 15)
        # GUI.show_layer(job_case, step, 'smb')

        # # 15.验证多层选中负极性文字改变字体，极性为正，镜像并角度旋转15°
        # Selection.select_feature_by_id(job_ep, step, ['ssb','ssb+1'], [49])
        # Layers.change_text(job_ep, step, ['ssb', 'ssb+1'], '$$WEEK-DAY', 'suntak_date', 5080000,
        #                    5080000, 635000, True, 1, 15)
        # GUI.show_layer(job_ep, step, 'ssb')
        #
        # # 16.验证多层选中负极性文字改变字体，极性为正，镜像并角度旋转20°
        # Selection.select_feature_by_id(job_ep, step, ['spb','spb+1'], [13,16,23,29])
        # Layers.change_text(job_ep, step, ['spb', 'spb+1'], '', '', 5080000,
        #                    5080000, 381000, False, 1, 20)
        # GUI.show_layer(job_ep, step, 'spb')

        # 17.验证整层文字极性为负，镜像并角度旋转20°，禅道ID3547
        Layers.change_text(job_ep, step, ['drl', 'drl+1'], '', '', 2540000,
                           2540000, 304800, False, 1, 20)
        Layers.change_polarity(job_ep,step,['drl', 'drl+1'],2,1)
        # GUI.show_layer(job_case, step, 'drl')



        # GUI.show_layer(job_case, step, 'l4')
        save_job(job_ep, temp_ep_path)


        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_g_remote_path = os.path.join(RunConfig.temp_path_g,'g',job_g)
        print("job_yg_remote_path:", job_g_remote_path)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g,'ep',job_ep)
        print("job_testcase_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)

        layerInfo = []
        # Input.open_job(job_g, temp_g_path)  # 用悦谱CAM打开料号
        # all_layers_list_job_g = Information.get_layers(job_g)
        for each in ['spt','sst','smt','l1','l2','l3','l4','l5','l6','l7','l8','l9','l10','smb','drl']:
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
        # assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])

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



# @pytest.mark.TranChange_Text
class TestTranChange_Text:
    # @pytest.mark.TranChange_text
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('TranChange_text'))
    def testTranChange_Text(self, job_id):
        '''
        本用例测试change_text提取器功能
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        # vs_time_g = str(int(time.time()))  # 比对时间
        # data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        # data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        layers = ['f']# 定义需要比对的层

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

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号

        '''
                验证文字transform旋转后change_text功能的吸取器可以正常获取文字的Line Width大小
                预期：获取文字的Line Width大小
                bug:1247
                功能测试用例：3613
                影响版本号：2.28.054_s4_u5_
                执行测试场景：1个
                '''
        # 使用提取器获取原始文字的信息大小
        points_location = []
        points_location.append({'ix': 44348400, 'iy': 194437000})
        points_location.append({'ix': 66344800, 'iy': 194437000})
        points_location.append({'ix': 66344800, 'iy': 179324000})
        points_location.append({'ix': 44348400, 'iy': 179324000})
        points_location.append({'ix': 44348400, 'iy': 194437000})
        GUI.show_layer(job_ep, step, 'f')
        ret = BASE.get_text_name(job_ep, step, 'f', points_location)
        print("rect1:",type(ret))
        info = json.loads(ret)['paras']
        print("infoo1:",type(info))
        print('information:', info)

        # 方法1：获取原始文字的linewidth的值并打印
        # linewidth_value = info.get('linewidth', 'unknown')
        # print(" 'linewidth' key is:", linewidth_value)

        # 方法2：获取原始文字的linewidth的值，给出linewidth的值
        info_new = {
            'linewidth': 609600,
        }

        linewidth_value = info_new.get('linewidth')
        print("'linewidth' key is:", linewidth_value)


        # 旋转文字90°
        Selection.select_feature_by_id(job_ep, step, 'f', [5])
        Layers.transform_features(job_ep, step, 'f', 0,
                                  True, False, False, False, False, {'ix': 56036112, 'iy': 185131029}, 90, 0, 0, 0, 0)

        # GUI.show_layer(job_case, step, 'f')

        # 文字旋转后利用提取器获取文字的大小信息
        points_location = []
        points_location.append({'ix': 44348400, 'iy': 194437000})
        points_location.append({'ix': 66344800, 'iy': 194437000})
        points_location.append({'ix': 66344800, 'iy': 179324000})
        points_location.append({'ix': 44348400, 'iy': 179324000})
        points_location.append({'ix': 44348400, 'iy': 194437000})
        ret_new = BASE.get_text_name(job_ep, step, 'f', points_location)
        info_new = json.loads(ret_new)['paras']
        print('information_new:', info_new)

        # 获取旋转后文字的linewidth的值并打印
        linewidth_new = info_new.get('linewidth', 'unknown')
        print(" 'linewidth_new' key is:", linewidth_new)

        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_case, step, 'l1')

        #断言（比对某个字典信息）
        assert linewidth_value == linewidth_new
