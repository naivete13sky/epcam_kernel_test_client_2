import pytest, os, time, json, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel.Edition import Matrix

@pytest.mark.change_attributes
class TestGraphicEditChangeAttributes:
    # @pytest.mark.Attributes
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Modify_attributes'))
    def test_change_attributes(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试改变物件属性--Modify_attributes,ID:12226
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息

        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['drl1-10+1', 'l4+1', 'l5+1','l1+1','l6+1', 'l7+1', 'l7-neg', 'l2+1']  # 定义需要比对的层
        # layers = ['drl1-10+1']
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

        #1.整层物件替换属性,筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层）,1为替换，pass
        # Layers.modify_attributes(job_case, step, ['drl1-10'], 1, [{".smd":""}])
        BASE.modify_attributes(job_ep,step,['drl1-10'],1,[{".smd":""}])
        Selection.set_attribute_filter(0, [{".smd":""}])          #设置筛选器属性
        Selection.select_features_by_filter(job_ep, step, ['drl1-10'])      #选中满足以上条件的物件
        Matrix.create_layer(job_ep, 'drl1-10+1')
        Layers.copy2other_layer(job_ep, step, 'drl1-10', 'drl1-10+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'drl1-10+1')


        #2.单选有属性物件替换属性，筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层），1为替换，pass
        Selection.select_feature_by_id(job_ep, step, 'l4', [623])
        # Layers.modify_attributes(job_case, step, ['l4'], 1, [{".fiducial_name": "trace"}])
        BASE.modify_attributes(job_ep, step, ['l4'], 1, [{".fiducial_name": "trace"}])
        Selection.set_attribute_filter(0, [{".fiducial_name": "trace"}])
        Selection.select_features_by_filter(job_ep, step, ['l4'])
        Matrix.create_layer(job_ep, 'l4+1')
        Layers.copy2other_layer(job_ep, step, 'l4', 'l4+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l4+1')


        # 3.多选物件替换属性，筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层），1为替换，pass   ---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l5', [1351,1805,65,611])
        # Layers.modify_attributes(job_case, step, ['l5'], 1, [{".AOI_ALIGN": ""}])
        BASE.modify_attributes(job_ep, step, ['l5'], 1, [{".AOI_ALIGN": ""}])
        Selection.set_attribute_filter(0, [{".AOI_ALIGN": ""}])
        Selection.select_features_by_filter(job_ep, step, ['l5'])
        Matrix.create_layer(job_ep, 'l5+1')
        Layers.copy2other_layer(job_ep, step, 'l5', 'l5+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l5+1')


        # 4.单选物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass
        Selection.select_feature_by_id(job_ep, step, 'l1', [2418])
        Layers.modify_attributes(job_ep, step, ['l1'], 0, [{".2nd_drill":""}])
        Selection.set_attribute_filter(0,[{".2nd_drill":""},{'.pattern_fill':''}])
        Selection.select_features_by_filter(job_ep, step, ['l1'])
        Matrix.create_layer(job_ep, 'l1+1')
        Layers.copy2other_layer(job_ep, step, 'l1', 'l1+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l1+1')


        # 5.多选物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass    ---待补充用例
        Selection.select_feature_by_id(job_ep, step, 'l6', [624,622,288,333,366])
        Layers.modify_attributes(job_ep, step, ['l6'], 0, [{".copper_weight": "1"}])
        Selection.set_attribute_filter(0, [{".copper_weight": "1"}])
        Selection.select_features_by_filter(job_ep, step, ['l6'])
        Matrix.create_layer(job_ep, 'l6+1')
        Layers.copy2other_layer(job_ep, step, 'l6', 'l6+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l6+1')

        # 6.整层物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass
        Layers.modify_attributes(job_ep, step, ['l7'], 0, [{".generated_net_point": "gasket"}])
        Selection.set_attribute_filter(0, [{".generated_net_point": "gasket"}])
        Selection.select_features_by_filter(job_ep, step, ['l7'])
        Matrix.create_layer(job_ep, 'l7+1')
        Layers.copy2other_layer(job_ep, step, 'l7', 'l7+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l7+1')

        # 7.整层负极性物件添加属性，筛选器选中该属性的物件，反转极性为正,0为添加,pass
        Layers.modify_attributes(job_ep, step, ['l7'], 0, [{".burry_drill": ""}])
        Selection.set_attribute_filter(0, [{".burry_drill": ""}])
        Selection.select_features_by_filter(job_ep, step, ['l7-neg'])
        Layers.change_polarity(job_ep, step, ['l7-neg'], 0, 1)
        Selection.reset_select_filter()
        Selection.reset_selection()
        # GUI.show_layer(job_case, step, 'l7-neg')

        # 8.删除指定属性，筛选器选中该物件，copy复制到目标层,pass
        Layers.modify_attributes(job_ep, step, ['l2'], 2, [{".pattern_fill": ""}])
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)
        Selection.select_features_by_filter(job_ep, step, ['l2'])
        Matrix.create_layer(job_ep, 'l2+1')
        Layers.copy2other_layer(job_ep, step, 'l2', 'l2+1', False, 0, 0, 0, 0, 0, 0, 0)
        Selection.reset_selection()  # 重置选中模式为默认状态

        # 9.删除所有属性，筛选器选中该物件，copy复制到目标层(暂且搁置，场景未想好)
        # Layers.modify_attributes(job_case, step, ['l3'], 3, [{".pattern_fill": ""}, {".pth_pad": ""}, {".via_pad": ""},
        #                                                      {".fiducial_name": "trace"}])
        # Selection.set_featuretype_filter(True, True, True, True, True, True, True)
        # Selection.select_features_by_filter(job_case, step, ['l3'])
        # Matrix.create_layer(job_case, 'l3+1')
        # Layers.copy2other_layer(job_case, step, 'l3', 'l3+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l3+1')

        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_case,step,'drl1-10')

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
        Input.open_job(job_g, temp_g_path)  # 用悦谱CAM打开料号
        all_layers_list_job_g = Information.get_layers(job_g)
        for each in all_layers_list_job_g:
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
        assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])

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
