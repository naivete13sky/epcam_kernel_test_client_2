import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers, Job
from epkernel.Output import save_job
from config_g.g_cc_method import G

class TestGraphicEditBreak_features:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Break1'))
    def testBreak_features (self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Break_features删除物件功能（ID：17486）
        '''
        g = RunConfig.driver_g  # 拿到G软件

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'orig'
        layers = ['smt', 'l1','l2','l3','l4','l5']

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
        Layers.add_pad(job_ep, step, ['l5'], "s100", 25400000, 25400000, True,
                       9, [{'.drill': 'via'}, {'.drill_first_last': 'first'}], 0)#添加普通焊盘
        attributes = [{'.comment': '3pin'}, {'.aoi': ''}]
        Layers.add_arc(job_ep, step, ['l5'], 'r7.874', 40 * 1000000, 25 * 1000000,
               40 * 1000000, 31 * 1000000, 40 * 1000000, 28 * 1000000, True, True, attributes)#添加弧
        Layers.break_features(job_ep, step, ['l5'], 1)#打散整层物件
        Selection.select_feature_by_id(job_ep, step, 'l5', [1897, 1898,1899,1900])#选中添加的线、面、pad、弧
        Layers.delete_feature(job_ep, step, ['l5'])  # 全部被删除证明没有被打散
        #GUI.show_layer(job_ep, step, 'l5')

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
