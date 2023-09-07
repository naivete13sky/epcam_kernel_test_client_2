import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS
from epkernel import Input, GUI
from epkernel.Action import Information
from epkernel.Edition import Matrix

class TestMatrixEditDelete:
    '''
    id:30872
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Matrix_Delete'))
    def test_matrix_delete (self, job_id):
        '''
        本用例测试Matrix窗口的Delete
        '''
        g = RunConfig.driver_g  # 拿到G软件
        test_cases = 0 # 用户统计执行了多少条测试用例
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        print("temp_path:", temp_path)
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')
        # Input.open_job(job_g,temp_g_path)
        # all_layers_list_job_g = Information.get_layers(job_g)

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        '''
        用例名称：删除存在的layer和不存在的layer
        预期1：存在的layer删除成功
        预期2：不存在的layer不执行删除
        执行场景数：2个
        '''
        layer_names = []
        layer_names.append(all_layers_list_job_ep[0])# 存在的layer
        layer_names.append("abc")# 不存在的layer
        for name in layer_names:
            Matrix.delete_layer(job_ep, name)

        '''
        用例名称：删除存在的step和不存在的step
        预期1：存在的step删除成功
        预期2：不存在的step不执行删除
        执行场景数：2个
        '''
        step_names = []
        step_names.append(all_steps_list_job_ep[1])
        step_names.append("abc")
        for name in step_names:
            Matrix.delete_step(job_ep, name)


        GUI.show_matrix(job_ep)



        # save_job(job_ep, temp_ep_path)
        # Job.close_job(job_ep)
        # print("test_cases：", test_cases)

        # # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        # job_g_remote_path = r'\\vmware-host\Shared Folders\share/{}/g/{}'.format(
        #     'temp' + "_" + str(job_id) + "_" + vs_time_g, job_g)
        # print("job_remote_path:", job_g_remote_path)
        # job_ep_remote_path = r'\\vmware-host\Shared Folders\share/{}/ep/{}'.format(
        #     'temp' + "_" + str(job_id) + "_" + vs_time_g, job_ep)
        # print("job_remote_path:", job_ep_remote_path)
        # # 导入要比图的资料
        # g.import_odb_folder(job_g_remote_path)
        # g.import_odb_folder(job_ep_remote_path)
        #
        # r = g.layer_compare_dms(job_id=job_id, vs_time_g=vs_time_g, temp_path=temp_path,
        #                         job1=job_g, step1=step, all_layers_list_job1=all_layers_list_job_g, job2=job_ep,step2=step,
        #                         all_layers_list_job2=all_layers_list_job_ep, adjust_position=True)
        # data["all_result_g1"] = r['all_result_g']
        # data["all_result"] = r['all_result']
        # data['g1_vs_total_result_flag'] = r['g_vs_total_result_flag']
        # Print.print_with_delimiter("断言--看一下G1转图中的层是不是都有比对结果")
        # assert len(all_layers_list_job_g) == len(r['all_result_g'])
        # # ----------------------------------------开始验证结果--------------------------------------------------------
        # Print.print_with_delimiter('比对结果信息展示--开始')
        # if data['g1_vs_total_result_flag'] == True:
        #     print("恭喜您！料号导入比对通过！")
        # if data['g1_vs_total_result_flag'] == False:
        #     print("Sorry！料号导入比对未通过，请人工检查！")
        #
        # Print.print_with_delimiter('分割线', sign='-')
        # print('G1转图的层：', data["all_result_g1"])
        # Print.print_with_delimiter('分割线', sign='-')
        # Print.print_with_delimiter('比对结果信息展示--结束')
        #
        # assert data['g1_vs_total_result_flag'] == True
        # for key in data['all_result_g1']:
        #     assert data['all_result_g1'][key] == "正常"
        # Print.print_with_delimiter("断言--结束")
