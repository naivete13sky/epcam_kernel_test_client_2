import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job
from epkernel.Output import save_job

class TestMatrixMove:
    '''
    id:36900
    '''
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Matrix_Move'))
    def test_matrix_move (self, job_id):
        '''
        本用例测试Matrix窗口的Move，共执行1个测试用例，实现3个方法，覆盖3个测试场景
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

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_gerber_path)
        '''
        用例名称：一次move单个layer到指定位置
        预期1：move成功
        执行场景数：1个
        '''
        row = 5
        Matrix.move_layer(job_ep,row,1)
        test_cases = test_cases + 1

        '''
        用例名称：一次move多个layer到指定位置
        预期1：move成功
        执行场景数：1个
        '''
        row_list = [7,8]
        for row in row_list:
            Matrix.move_layer(job_ep,row,4)
        test_cases = test_cases + 1
        '''
        用例名称：将目标层move超出
        预期1：move失败
        执行场景数：1个
        '''
        row = 9
        tar_row = len(Information.get_layer_information(job_ep)) + 1
        Matrix.move_layer(job_ep,row,tar_row)
        test_cases = test_cases + 1

        # GUI.show_matrix(job_ep)
        save_job(job_ep, temp_ep_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        informatitons_ep = Information.get_layer_information(job_ep)
        informatitons_g = Information.get_layer_information(job_g)

        Job.close_job(job_ep)
        print("test_cases：", test_cases)


        # ----------------------------------------开始验证结果--------------------------------------------------------
        dict_layer_row_ep = {}
        for layer_ep in all_layers_list_job_ep:
            for information in informatitons_ep:
                if information['name'] == layer_ep:
                    row = information['row']
                    dict_layer_row_ep[layer_ep] = row

        dict_layer_row_g = {}
        for layer_g in all_layers_list_job_g:
            for information in informatitons_g:
                if information['name'] == layer_g:
                    row = information['row']
                    dict_layer_row_g[layer_g] = row
        assert dict_layer_row_ep == dict_layer_row_g
        Print.print_with_delimiter("断言--结束")
