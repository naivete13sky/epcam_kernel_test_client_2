import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job
from epkernel.Output import save_job

class TestMatrixDelete:
    '''
    id:30872,共执行1个测试用例，实现4个方法，覆盖6个测试场景
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Matrix_Delete'))
    def test_matrix_delete(self, job_id):
        '''
        本用例测试Matrix窗口的Delete
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
        all_layers_list_job_g = Information.get_layers(job_g)
        all_steps_list_job_g = Information.get_steps(job_g)

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_gerber_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        '''
        用例名称：删除存在的layer和不存在的layer
        预期1：存在的layer删除成功
        预期2：不存在的layer不执行删除
        执行场景数：2个
        '''
        layer_list = []
        layer_list.append(all_layers_list_job_ep[0])# 存在的layer
        layer_list.append("abc")# 不存在的layer
        for layer in layer_list:
            Matrix.delete_layer(job_ep, layer)
            test_cases = test_cases + 1

        '''
        用例名称：删除存在的step和不存在的step
        预期1：存在的step删除成功
        预期2：不存在的step不执行删除
        执行场景数：2个
        '''
        step_list = []
        step_list.append(all_steps_list_job_ep[1])
        step_list.append("abc")
        for step in step_list:
            Matrix.delete_step(job_ep, step)
            test_cases = test_cases + 1

        '''
        用例名称：删除多个step
        预期：删除成功
        执行场景数：1个
        '''
        all_steps_list_job_ep = Information.get_steps(job_ep)
        for step in all_steps_list_job_ep:
            if "+1" in step:
                Matrix.delete_step(job_ep,step)
        test_cases = test_cases + 1

        '''
        用例名称：删除多个layer
        预期：删除成功
        执行场景数：1个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        for layer in all_layers_list_job_ep:
            if "+1" in layer:
                Matrix.delete_layer(job_ep,layer)
        test_cases = test_cases + 1

        save_job(job_ep, temp_ep_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)  # 获取新的ep所有layer信息
        all_steps_list_job_ep = Information.get_steps(job_ep)  # 获取新的ep所有step信息

        print("test_cases：", test_cases) #统计覆盖场景数
        # ----------------------------------------开始验证结果：G与EP---------------------------------------------------------
        Print.print_with_delimiter('断言--开始')
        for layer_ep in all_layers_list_job_ep:
            assert layer_ep in all_layers_list_job_g
        for layer_g in all_layers_list_job_g:
            assert layer_g in all_layers_list_job_ep
        for step_ep in all_steps_list_job_ep:
            assert step_ep in all_steps_list_job_g
        for step_g in all_steps_list_job_g:
            assert step_g in all_steps_list_job_ep
        Print.print_with_delimiter("断言--结束")
        Job.close_job(job_ep)
        Job.close_job(job_g)
