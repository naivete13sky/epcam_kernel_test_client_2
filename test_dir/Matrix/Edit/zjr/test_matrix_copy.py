import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job, Layers
from epkernel.Output import save_job

class TestMatrixCopy:
    '''
    id:37292,共执行1个测试用例，实现4个方法，覆盖8个测试场景
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Matrix_Copy'))
    def test_matrix_copy(self, job_id):
        '''
        本用例测试Matrix窗口的Copy
        '''
        g = RunConfig.driver_g  # 拿到G软件
        test_cases = 0  # 用户统计执行了多少条测试用例
        data = {}  # 存放比对结果信息
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
        temp_gerber_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')
        temp_g2_path = os.path.join(temp_path, 'g2')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')
        Input.open_job(job_g,temp_g_path)
        all_steps_list_job_g = Information.get_steps(job_g)
        all_layers_list_job_g = Information.get_layers(job_g)


        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_gerber_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        '''
        用例名称：copy存在的step和不存在的step
        预期1：存在的step copy成功,并自动命名，规则是原来名称+1，或原来名称+2，依次类推。
        预期2：不存在的step不执行
        执行场景数：3个
        '''
        step_list  = []
        step_list.append(all_steps_list_job_ep[1])
        step_list.append("abc")
        for step in step_list:
            Matrix.copy_step(job_ep,step)
        Matrix.copy_step(job_ep,all_steps_list_job_ep[1])
        test_cases = test_cases + 3

        '''
        用例名称：copy存在的layer和不存在的layer
        预期1：存在的layer copy成功,并自动命名，规则是原来名称+1，或原来名称+2，依次类推。
        预期2：不存在的layer不执行
        执行场景数：3个
        '''
        layer_list = []
        layer_list.append(all_layers_list_job_ep[0])
        layer_list.append("abc")
        for layer in layer_list:
            Matrix.copy_layer(job_ep,layer)
        Matrix.copy_layer(job_ep,all_layers_list_job_ep[0])
        test_cases = test_cases + 3

        '''
        用例名称：copy多个step
        预期：copy成功
        执行场景数：1个
        '''
        for i in range(len(all_steps_list_job_ep)):
            if i == 1:
                continue
            Matrix.copy_step(job_ep, all_steps_list_job_ep[i])
        test_cases = test_cases + 1

        '''
        用例名称：copy多个layer
        预期：copy成功
        执行场景数：1个
        '''
        for i in range(len(all_layers_list_job_ep)):
            if i in [2,6,7,8,9,10,11,12,13]:
                Matrix.copy_layer(job_ep,all_layers_list_job_ep[i])
        # GUI.show_matrix(job_ep)
        test_cases = test_cases + 1

        # Layers.delete_feature(job_ep,"orig",[Information.get_layers(job_ep)[0]])
        # GUI.show_matrix(job_ep)

        save_job(job_ep, temp_ep_path)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        all_layers_list_job_ep = Information.get_layers(job_ep)

        print("test_cases：", test_cases)

        # ----------------------------------------开始验证结果--------------------------------------------------------
        dict_has_feature_ep = {}
        for step_ep in all_steps_list_job_ep:
            layer_has_feature_ep = []
            for layer_ep in all_layers_list_job_ep:
                if Information.get_layer_feature_count(job_ep,step_ep,layer_ep) > 0:
                    layer_has_feature_ep.append(layer_ep)
            dict_has_feature_ep[step_ep] = layer_has_feature_ep

        dict_has_feature_g = {}
        for step_g in all_steps_list_job_g:
            layer_has_feature_g = []
            for layer_g in all_layers_list_job_g:
                if Information.get_layer_feature_count(job_g,step_g,layer_g) > 0:
                    layer_has_feature_g.append(layer_g)
            dict_has_feature_g[step_g] = layer_has_feature_g

        assert dict_has_feature_ep == dict_has_feature_g
        Print.print_with_delimiter("断言--结束")
        Job.close_job(job_ep)
        Job.close_job(job_g)