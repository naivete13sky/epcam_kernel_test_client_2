import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job


class TestGraphicEditContourize1:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Contourize'))
    def testContourize1(self, job_id, g, prepare_test_job_clean_g):

        '''
        本用例测试Contourize整合铜皮功能（ID：17871）
        '''

        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['l1', 'l2', 'l3', 'l4', 'l5', 'l6', 'l7', 'l8', 'xt','e22_bak_l2',
                  '4809_edit_l3', '19te_net_l1', '10a68_net_l2','8a68782_edit_gts','9397_orig_l1','555_orig_l2',]

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

        #1.默认参数下，验证选中一正一负两块铜皮整合成功
        Selection.select_feature_by_id(job_ep, step, 'l1', [27, 40])#同时选中一块正极性和一块非极性铜皮
        Layers.contourize(job_ep, step, ['l1'], 6350, True, 3*25400, 1)#将其整合到一起，accuracy栏填0.25mil(6350微米)
        Selection.set_featuretype_filter(False, True, False, True, False, False, False)#筛选负极性铜皮进行删除
        Selection.select_features_by_filter(job_ep, step, ['l1'])
        Layers.delete_feature(job_ep, step, ['l1'])#原来ID为40的负极性铜皮没有被删除，证明其已与ID为27的正极性铜皮整合成功
        Selection.reset_selection()     # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l1')

        #2.功能界面默认参数下，验证可以正确整合线铜
        Layers.contourize(job_ep, step, ['xt'], 6350, True, 3 * 25400, 1) # 功能界面默认参数下，整合线铜
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'xt')


        #3.验证存在pad、line、圆surface、ARC、text等五种类型的负极性物件时，均可正确整合（已在L2层创建符合条件的物件）
        Layers.contourize(job_ep, step, ['l2'], 6350, True, 3*25400, 1)# 功能界面默认参数下，整合线铜
        Layers.change_polarity(job_ep, step,['l2'], 2, 1)#整层极性翻转，若整层所有物件变成负极性，则证明铜皮整合正确
        Selection.reset_selection() # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'l2')

        #4.验证整合铜皮时分离孤岛功能选yes，两个符合条件的孤岛没有被整合
        Layers.contourize(job_ep, step, ['l3'], 6350, True, 3*25400, 1)# 是否分离孤岛选YES，整合线铜,
        Selection.select_feature_by_id(job_ep, step, 'l3', [429])#选择其中一个物件删除，证明没有被整合
        Layers.delete_feature(job_ep, step, ['l3'])
        # GUI.show_layer(job_ep, step, 'l3')

        #5.验证整合铜皮时分离孤岛功能选No，两个符合条件的孤岛被整合
        Layers.contourize(job_ep, step, ['l4'], 6350, False, 3 * 25400, 1)  # 是否分离孤岛选No，整合线铜
        Selection.select_feature_by_id(job_ep, step, 'l4', [0])  # 选择其中ID为0的物件删除则整层被删除了，证明整合成功
        Layers.delete_feature(job_ep, step, ['l4'])
        #GUI.show_layer(job_ep, step, 'l4')


        #6.新增负极性长方形pad，X、Y单边清除空洞整合(mode选XorY，验证Maxsize栏和mode栏的正确性)
        Layers.add_pad(job_ep, step, ['l5'], "rect20x10", 2540000, 1 * 2540000, False, 9, [], 0)
        Layers.add_pad(job_ep, step, ['l5'], "rect40x20", 2540000, 3 * 2540000, False, 9, [], 0)
        Layers.add_pad(job_ep, step, ['l5'], "rect50x30", 2540000, 5 * 2540000, False, 9, [], 0)#添加三个负极性长方形pad
        Layers.contourize(job_ep, step, ['l5'], 6350, False, 20 * 25400, 0)#Max size设置为20mil ,mode设置为0：X or Y
                                                                           # （清除X或Y轴任一尺寸小于等于Max Size的洞，预期 "rect20x10","rect40x20"被清除）
        #GUI.show_layer(job_ep, step, 'l5')

        #7.新增负极性长方形pad，X、Y单边清除空洞整合(mode选XandY，验证Maxsize栏和mode栏的正确性)
        Layers.add_pad(job_ep, step, ['l6'], "rect20x10", 2540000, 1 * 2540000, False, 9, [], 0)
        Layers.add_pad(job_ep, step, ['l6'], "rect40x20", 2540000, 3 * 2540000, False, 9, [], 0)
        Layers.add_pad(job_ep, step, ['l6'], "rect50x30", 2540000, 5 * 2540000, False, 9, [], 0)#添加三个负极性长方形pad
        Layers.contourize(job_ep, step, ['l6'], 6350, False, 20 * 25400, 1)#Max size设置为20mil ,mode设置为1：X and Y
                                                                             # （清除X及Y轴两尺寸皆小于等于Max Size的洞，预期"rect20x10"被清除）
        # #GUI.show_layer(job_ep, step, 'l6')

        #8.通过面积清除空洞整合(mode选area，验证Maxsize栏和mode栏的正确性)
        Layers.contourize(job_ep, step, ['l7'], 6350, False, 1000 * 25400, 2)#Max size设置为1000mil ,
                                                                             # mode设置为2：Area（清除X or Y ; X and Y选项检测不到的洞）
        # GUI.show_layer(job_ep, step, 'l7')


        #9.验证accuracy栏的正确性（精度大于等于0.25mil时，那么contour无需靠近原物件的轮廓线，将更快速的处理复杂的输入数据）
        Layers.contourize(job_ep, step, ['l8'], 2*25400, True, 3*25400, 1)#accuracy栏输入2mil时整合铜皮,此时铜皮轮廓会有变化（因为大于0.25mil了）
        #GUI.show_layer(job_ep, step, 'l8')

        '''
        验证按照设置参数正确转铜皮，不丢失空洞
        bug编号：4714
        功能用例ID：3620
        影响版本号：1.1.7.2
        '''
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)  # 筛选正极性铜皮
        Selection.select_features_by_filter(job_ep, step, ['e22_bak_l2'])
        Layers.contourize(job_ep, step, ['e22_bak_l2'], 0*25400, True, 0*25400, 0)
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, 'e22_bak_l2')

        '''
        验证按照设置参数正确转铜皮，不丢失空洞
        bug编号：4683、4388、2223（该用例验证三个不同料号的同一执行场景，已将问题层别拷贝到测试料号）
        功能用例ID：3620
        '''
        Selection.set_featuretype_filter(False, True, True, True, True, True, True)# 筛选所有负极性物件
        Selection.select_features_by_filter(job_ep, step, ['4809_edit_l3', '19te_net_l1', '10a68_net_l2'])
        Selection.set_featuretype_filter(True, False, False, True, False, False, False) #筛选正极性铜皮
        Selection.select_features_by_filter(job_ep, step, ['4809_edit_l3', '19te_net_l1', '10a68_net_l2'])
        Layers.contourize(job_ep, step, ['4809_edit_l3','19te_net_l1','10a68_net_l2'], 1 * 254, True, 3 * 25400, 0)
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, '4809_edit_l3')

        '''
        验证选中选一个bga Pad和组成它的负极性铜皮，按照所填参数铜皮整合后图形不变形
        bug编号：2824
        功能用例ID：3622
        '''
        Selection.select_feature_by_id(job_ep, step, '8a68782_edit_gts', [13492, 2348])#物件坐标（x=2.994,y=3.139）
        Layers.contourize(job_ep, step, ['8a68782_edit_gts'], 0, True, 3 * 25400, 0)
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, '8a68782_edit_gts')

        '''
        验证整合附件线铜后，按照所填参数正确整合，PAD不丢失
        bug编号：1668
        功能用例ID：3624
        '''
        Selection.set_featuretype_filter(False, True, True, True, True, True, True)  # 筛选所有负极性物件
        Selection.select_features_by_filter(job_ep, step, ['9397_orig_l1'])
        Selection.set_featuretype_filter(True, False, False, True, False, False, False)  # 筛选正极性铜皮
        Selection.select_features_by_filter(job_ep, step, ['9397_orig_l1'])
        Layers.contourize(job_ep, step, ['9397_orig_l1'], 25 * 254, True, 3 * 25400, 0)#按照所填参数正确整合，PAD不丢失(其坐标：x=0.920,y=0.333)
        Selection.reset_selection()  # 重置筛选器，不影响后续使用
        Selection.reset_select_filter()
        Selection.reset_select_filter()
        #GUI.show_layer(job_ep, step, '9397_orig_l1')

        '''
        验证线铜物料使用Contourize功能可正确整合铜皮
        bug编号：1053
        功能用例ID：3623
        '''
        Selection.set_featuretype_filter(True, True, False, False, False, True, False)  # 筛选正负极性线
        Selection.select_features_by_filter(job_ep, step, ['555_orig_l2'])
        Selection.set_include_symbol_filter(['r9.843'])
        Layers.contourize(job_ep, step, ['555_orig_l2'], 25 * 254, True, 3 * 25400, 0)
        #GUI.show_layer(job_ep, step, '555_orig_l2')



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
