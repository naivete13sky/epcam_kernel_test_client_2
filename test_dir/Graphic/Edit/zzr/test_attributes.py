import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from config_g.g_cc_method import G
from epkernel.Edition import Matrix

# @pytest.mark.Attributes
class TestGraphicEditChangeAttributes:
    # @pytest.mark.Attributes
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Modify_attributes'))
    def testChangeAttributes(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试改变物件属性--Modify_attributes,ID:12226
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        layers = ['drl1-10+1', 'l4+1', 'l5+1','l1+1','l6+1', 'l7+1', 'l7-neg', 'l2+1']  # 定义需要比对的层
        # layers = ['drl1-10+1']
        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_case = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        job_yg = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job_case, temp_compressed_path)  # 用悦谱CAM打开料号

        #1.整层物件替换属性,筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层）,1为替换，pass
        # Layers.modify_attributes(job_case, step, ['drl1-10'], 1, [{".smd":""}])
        BASE.modify_attributes(job_case,step,['drl1-10'],1,[{".smd":""}])
        Selection.set_attribute_filter(0, [{".smd":""}])          #设置筛选器属性
        Selection.select_features_by_filter(job_case, step, ['drl1-10'])      #选中满足以上条件的物件
        Matrix.create_layer(job_case, 'drl1-10+1')
        Layers.copy2other_layer(job_case, step, 'drl1-10', 'drl1-10+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'drl1-10+1')


        #2.单选有属性物件替换属性，筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层），1为替换，pass
        Selection.select_feature_by_id(job_case, step, 'l4', [623])
        # Layers.modify_attributes(job_case, step, ['l4'], 1, [{".fiducial_name": "trace"}])
        BASE.modify_attributes(job_case, step, ['l4'], 1, [{".fiducial_name": "trace"}])
        Selection.set_attribute_filter(0, [{".fiducial_name": "trace"}])
        Selection.select_features_by_filter(job_case, step, ['l4'])
        Matrix.create_layer(job_case, 'l4+1')
        Layers.copy2other_layer(job_case, step, 'l4', 'l4+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l4+1')


        # 3.多选物件替换属性，筛选器选中该属性的物件，copy复制到目标层（matrix创建一个空层），1为替换，pass   ---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l5', [1351,1805,65,611])
        # Layers.modify_attributes(job_case, step, ['l5'], 1, [{".AOI_ALIGN": ""}])
        BASE.modify_attributes(job_case, step, ['l5'], 1, [{".AOI_ALIGN": ""}])
        Selection.set_attribute_filter(0, [{".AOI_ALIGN": ""}])
        Selection.select_features_by_filter(job_case, step, ['l5'])
        Matrix.create_layer(job_case, 'l5+1')
        Layers.copy2other_layer(job_case, step, 'l5', 'l5+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l5+1')


        # 4.单选物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass
        Selection.select_feature_by_id(job_case, step, 'l1', [2418])
        Layers.modify_attributes(job_case, step, ['l1'], 0, [{".2nd_drill":""}])
        Selection.set_attribute_filter(0,[{".2nd_drill":""},{'.pattern_fill':''}])
        Selection.select_features_by_filter(job_case, step, ['l1'])
        Matrix.create_layer(job_case, 'l1+1')
        Layers.copy2other_layer(job_case, step, 'l1', 'l1+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l1+1')


        # 5.多选物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass    ---待补充用例
        Selection.select_feature_by_id(job_case, step, 'l6', [624,622,288,333,366])
        Layers.modify_attributes(job_case, step, ['l6'], 0, [{".copper_weight": "1"}])
        Selection.set_attribute_filter(0, [{".copper_weight": "1"}])
        Selection.select_features_by_filter(job_case, step, ['l6'])
        Matrix.create_layer(job_case, 'l6+1')
        Layers.copy2other_layer(job_case, step, 'l6', 'l6+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l6+1')

        # 6.整层物件添加属性，筛选器选中该属性的物件，copy复制到目标层,0为添加,pass
        Layers.modify_attributes(job_case, step, ['l7'], 0, [{".generated_net_point": "gasket"}])
        Selection.set_attribute_filter(0, [{".generated_net_point": "gasket"}])
        Selection.select_features_by_filter(job_case, step, ['l7'])
        Matrix.create_layer(job_case, 'l7+1')
        Layers.copy2other_layer(job_case, step, 'l7', 'l7+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l7+1')

        # 7.整层负极性物件添加属性，筛选器选中该属性的物件，反转极性为正,0为添加,pass
        Layers.modify_attributes(job_case, step, ['l7'], 0, [{".burry_drill": ""}])
        Selection.set_attribute_filter(0, [{".burry_drill": ""}])
        Selection.select_features_by_filter(job_case, step, ['l7-neg'])
        Layers.change_polarity(job_case, step, ['l7-neg'], 0, 1)
        Selection.reset_select_filter()
        Selection.reset_selection()
        # GUI.show_layer(job_case, step, 'l7-neg')

        # 8.删除指定属性，筛选器选中该物件，copy复制到目标层,pass
        Layers.modify_attributes(job_case, step, ['l2'], 2, [{".pattern_fill": ""}])
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)
        Selection.select_features_by_filter(job_case, step, ['l2'])
        Matrix.create_layer(job_case, 'l2+1')
        Layers.copy2other_layer(job_case, step, 'l2', 'l2+1', False, 0, 0, 0, 0, 0, 0, 0)
        Selection.reset_selection()  # 重置选中模式为默认状态

        # 9.删除所有属性，筛选器选中该物件，copy复制到目标层(暂且搁置，场景未想好)
        # Layers.modify_attributes(job_case, step, ['l3'], 3, [{".pattern_fill": ""}, {".pth_pad": ""}, {".via_pad": ""},
        #                                                      {".fiducial_name": "trace"}])
        # Selection.set_featuretype_filter(True, True, True, True, True, True, True)
        # Selection.select_features_by_filter(job_case, step, ['l3'])
        # Matrix.create_layer(job_case, 'l3+1')
        # Layers.copy2other_layer(job_case, step, 'l3', 'l3+1', False, 0, 0, 0, 0, 0, 0, 0)
        # GUI.show_layer(job_case, step, 'l3+1')

        save_job(job_case, temp_ep_path)
        # GUI.show_layer(job_case,step,'drl1-10')

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190, '-'))
        job_yg_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_yg)
        print("job_yg_remote_path:", job_yg_remote_path)
        job_case_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
            'temp' + "_" + str(job_id) + "_" + vs_time_g, job_case)
        print("job_testcase_remote_path:", job_case_remote_path)
        # # 导入要比图的资料
        g.import_odb_folder(job_yg_remote_path)
        g.import_odb_folder(job_case_remote_path)

        r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
                                job1=job_yg, step1=step, all_layers_list_job1=layers, job2=job_case, step2=step,
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
