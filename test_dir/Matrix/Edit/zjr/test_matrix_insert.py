import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI, BASE
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job, Layers
from epkernel.Output import save_job

class TestMatrixInsert:
    '''
    id:，39595,共执行1个测试用例，实现2个方法，覆盖2个测试场景
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Matrix_Insert'))
    def test_matrix_insert(self, job_id):
        '''
        本用例测试Matrix窗口的Insert
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
        '''
        用例名称：insert一个step
        预期1：insert成功
        执行场景数：1个
        '''
        steps = Information.get_steps(job_ep)
        print("steps1", steps)
        Matrix.create_step(job_ep,'test_insert',2)
        steps = Information.get_steps(job_ep)
        print("steps2",steps)
        test_cases = test_cases + 1

        # BASE.insert_layer(job_ep,7)
        '''
        用例名称：insert一个layer
        预期1：insert成功
        执行场景数：1个
        '''
        Matrix.create_layer(job_ep,'test_insert',7)
        test_cases = test_cases + 1

        # GUI.show_matrix(job_ep)

        save_job(job_ep, temp_ep_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        layer_informations_ep = Information.get_layer_information(job_ep)
        layer_informations_g = Information.get_layer_information(job_g)

        print("test_cases：", test_cases)

        # ----------------------------------------开始验证结果--------------------------------------------------------
        dict_layer_row_ep = {}
        for layer_ep in all_layers_list_job_ep:
            for information in layer_informations_ep:
                if information['name'] == layer_ep:
                    row = information['row']
                    dict_layer_row_ep[layer_ep] = row

        dict_layer_row_g = {}
        for layer_g in all_layers_list_job_g:
            for information in layer_informations_g:
                if information['name'] == layer_g:
                    row = information['row']
                    dict_layer_row_g[layer_g] = row
        assert dict_layer_row_ep == dict_layer_row_g

        column_ep = 1
        dict_step_column_ep = {}
        for step_ep in all_steps_list_job_ep:
            dict_step_column_ep[step_ep] = column_ep
            column_ep = column_ep + 1

        column_g = 1
        dict_step_column_g = {}
        for step_g in all_steps_list_job_g:
            dict_step_column_g[step_g] = column_g
            column_g = column_g + 1
        assert dict_step_column_ep == dict_step_column_g
        Print.print_with_delimiter("断言--结束")
        Job.close_job(job_ep)
        Job.close_job(job_g)