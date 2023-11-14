import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditBreak_feature:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Break_feature'))
    def testBreak_feature(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Break_features删除物件功能（ID：17486）
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



        # 1.先添加多个文字，然后选择其中一个打散
        attributes = [{'.text_88': ''}]
        Layers.add_text(job_ep, step, ['l1'], 'standard', '666', 200*25400, 200*25400, 20 * 25400,
                        1 * 25400000, 2 * 25400000, True, 0, attributes, 45)
        Layers.add_text(job_ep, step, ['l1'], 'standard', '999', 200*25400, 200*25400, 20 * 25400,
                        1 * 25400000, -1 * 25400000, True, 0, attributes, 0)
        Selection.select_feature_by_id(job_ep, step, 'l1', [2526])
        Layers.break_features(job_ep, step, ['l1'], 0)#打散文字666
        Selection.select_feature_by_id(job_ep, step, 'l1', [2539,2553])#选中已打散的物件和未打散的物件
        Layers.delete_feature(job_ep, step, ['l1'])   # 已打散的文字只删除部分，未打散的文字被整个删除


        #2.整层打散
        attributes = [{'.text_88': ''}]
        Layers.add_text(job_ep, step, ['l2'], 'standard', '123', 200*25400, 200*25400, 20 * 25400,
                        1 * 25400000, 2 * 25400000, True, 0, attributes, 45)
        Layers.add_text(job_ep, step, ['l2'], 'standard', '456', 200*25400, 200*25400, 20 * 25400,
                        1 * 25400000, -1 * 25400000, True, 0, attributes, 0)
        Layers.break_features(job_ep, step, ['l2'], 1)
        Selection.select_feature_by_id(job_ep, step, 'l2', [908,927])
        Layers.delete_feature(job_ep, step, ['l2'])   # 删除打散之后的某个物件（用以证明物件被打散）

        #3.多层打散
        attributes = [{'.text_88': ''}]
        Layers.add_text(job_ep, step, ['l3'], 'standard', '333', 200 * 25400, 200 * 25400, 20 * 25400,
                        1 * 25400000, 2 * 25400000, True, 0, attributes, 45)
        Layers.add_text(job_ep, step, ['l4'], 'standard', '234', 200 * 25400, 200 * 25400, 20 * 25400,
                        1 * 25400000, -1 * 25400000, True, 0, attributes, 0)
        Layers.break_features(job_ep, step, ['l3','l4'], 1)
        Selection.select_feature_by_id(job_ep, step, 'l3', [2380])
        Selection.select_feature_by_id(job_ep, step, 'l4', [937])
        Layers.delete_feature(job_ep, step, ['l3','l4'])  # 删除多层中打散之后的某个物件（用以证明物件被打散）

        #4.打散特殊焊盘
        Layers.add_pad(job_ep, step, ['smt'], "macro11", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}],90)#添加一个特殊焊盘（macro11），镜像并翻转90度
        Selection.select_feature_by_id(job_ep, step, 'smt', [801])
        Layers.break_features(job_ep, step, ['smt'], 0)  # 选中并打散该垫盘
        Selection.select_feature_by_id(job_ep, step, 'smt', [814]) #选中已打散焊盘的部分物件
        Layers.delete_feature(job_ep, step, ['smt'])  #打散后的焊盘的部分物件被删除


        #5.验证不能打散的物件类型（反用例）
        Layers.add_line(job_ep, step, ['l5'], 'r5', 10000000, 30000000, 30000000, 30000000,
                        True, [{'.fiducial_name': '0'}, {'.area': ''}])#增加线
        points_location = []
        points_location.append([50 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 25 * 1000000])
        points_location.append([55 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 36 * 1000000])
        points_location.append([50 * 1000000, 25 * 1000000])
        Layers.add_surface(job_ep, step, ['l5'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#添加面
        Layers.add_pad(job_ep, step, ['l5'], "s150", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)#添加S开头的焊盘
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l5'], 'r7.874', 40 * 1000000, 25 * 1000000,
               40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)#添加弧
        Layers.break_features(job_ep, step, ['l5'], 1)#打散整层物件
        Selection.select_feature_by_id(job_ep, step, 'l5', [1897, 1898,1899,1900])#选中添加的线、面、pad、弧
        Layers.delete_feature(job_ep, step, ['l5'])  # 全部被删除证明没有被打散
        #GUI.show_layer(job_ep, step, 'l5')

        '''
        验证S开头方形Pad打散后还是Pad的属性
        bug编号：4474
        功能用例ID：3586
        影响版本号：1.1.6.8
        '''
        Layers.add_pad(job_ep, step, ['l6'], "s150", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)  # 添加S开头的焊盘
        #GUI.show_layer(job_ep, step, 'l6')
        Selection.select_feature_by_id(job_ep, step, 'l6', [933],)#选中它
        Layers.break_features(job_ep, step, ['l6'], 0)  # 打散选中物件
        Selection.set_featuretype_filter(True, False, False, False, False, False, True)  # 用筛选器筛选中正极性Pad
        Selection.select_features_by_filter(job_ep, step, ['l6'])
        Layers.delete_feature(job_ep, step, ['l6'])  # 删除所选pad，如被删除证明改pad属性没有改变
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l6')

        '''
        验证所选物件不属于可被打散物件时，执行Break操作后取消被选中状态
        bug编号：4428
        功能用例ID：3588
        影响版本号：1.1.6.8
        '''
        Selection.select_feature_by_id(job_ep, step, 'l7', [721,244,251],)#选中几个正极性普通pad
        Layers.break_features(job_ep, step, ['l7'], 0)  # 打散选中物件
        Layers.delete_feature(job_ep, step, ['l7'])#如果整层物件被删除，则说明执行Break操作后取消被选中状态了
        #GUI.show_layer(job_ep, step, 'l7')

        '''
        验证 使用Break功能可正确打散附件指定物件（可将指定pad打散为surface）
        bug编号：4281
        功能用例ID：3589
        影响版本号：1.1.5.1
        '''
        Selection.select_feature_by_id(job_ep, step, '4281_panel_dc-s', [22], )  # 选中一个箭头
        #GUI.show_layer(job_ep, step, '4281_panel_dc-s')
        Layers.break_features(job_ep, step, ['4281_panel_dc-s'], 0)  # 打散选中物件为Surface属性
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)  # 用筛选器筛选正极性Surface
        Selection.select_features_by_filter(job_ep, step, ['4281_panel_dc-s'])
        Layers.delete_feature(job_ep, step, ['4281_panel_dc-s'])#如果最初选中的箭头件被删除则证明符合预期
        #GUI.show_layer(job_ep, step, '4281_panel_dc-s')



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
        for each in ['smt', 'l1','l2','l3','l4','l5','l6','l7','4281_panel_dc-s']:
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