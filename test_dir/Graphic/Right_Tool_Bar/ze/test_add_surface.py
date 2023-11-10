import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Edition import Layers
from epkernel.Output import save_job
from epkernel import Application
from epkernel.Action import Information, Selection

class TestGraphicEditFeatureIndex:
    # @pytest.mark.Feature index
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Add_surface'))
    def testFeatureIndex(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Add_surface功能（ID:39611）
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


        #3.增加正极性surface
        points_location = []
        points_location.append([66 * 1000000, 1* 1000000])
        points_location.append([66 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 6 * 1000000])
        points_location.append([71 * 1000000, 1 * 1000000])
        points_location.append([66 * 1000000, 1* 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)

        # 3.增加负极性surface
        points_location = []
        points_location.append([68 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 4 * 1000000])
        points_location.append([69 * 1000000, 3 * 1000000])
        points_location.append([68 * 1000000, 3 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], False,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)


        #4.添加正极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], True, {'.bga': '', '.cm': ''},68 * 1000000, 8 * 1000000, 50 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')
        #5.添加负极性圆形surface
        Application.add_round_surface_jwApp(job_ep, step, ['l2'], False, {'.bga': '', '.cm': ''}, 67 * 1000000,
                                            5 * 1000000, 30 * 25400)
        #GUI.show_layer(job_ep, step, 'l2')


        #5. 选中一个铜物件，使用线填充铜物件,不足的地方不使用弧线填充
        points_location = []
        points_location.append([66 * 1000000, 12 * 1000000])
        points_location.append([66 * 1000000, 18 * 1000000])
        points_location.append([71 * 1000000, 18 * 1000000])
        points_location.append([71 * 1000000, 12 * 1000000])
        points_location.append([66 * 1000000, 12 * 1000000])
        Layers.add_surface(job_ep, step, ['l2'], True,
                           [{'.out_flag': '233'}, {'.pattern_fill': ''}], points_location)#先添加一块正极性铜皮
        Selection.select_feature_by_id(job_ep, step, 'l2', [927])#选中刚添加的铜皮
        Layers.use_solid_fill_contours(job_ep, step, ['l2'], 5 * 254000, False)#使用线填充，线的最小间距为5Mil,弧度不足的地方不使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [936])#选中其中一个线将其删除，以证明铜面被打散了
        Layers.delete_feature(job_ep, step, ['l2'])
        #GUI.show_layer(job_ep, step, 'l2')

        #6.选中一个圆形铜物件，使用线填充铜物件,不足的地方使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [925])#选中一个圆形铜皮
        Layers.use_solid_fill_contours(job_ep, step, ['l2'], 5 * 254000, True)  #使用线填充，线的最小间距为5Mil,弧度不足的地方使用弧线填充
        Selection.select_feature_by_id(job_ep, step, 'l2', [927])  #选中其中一个弧线线将其删除，以证明铜面打散时不足的地方用弧线补充了
        Layers.delete_feature(job_ep, step, ['l2'])
        #GUI.show_layer(job_ep, step, 'l2')






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
        for each in ['l1','l2','l3','l4','l5','l6','l7']:
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