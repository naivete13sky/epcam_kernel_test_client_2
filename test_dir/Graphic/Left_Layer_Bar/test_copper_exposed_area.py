from pathlib import Path
import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS
from epkernel import Input
from epkernel.Action import Information
from epkernel.Edition import Job

class TestGraphicCopper_Exposed_Area:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Copper_Exposed_Area'))
    def testcopper_exposed_area(self, job_id, g, prepare_test_job_clean_g):
        """
        测试计算铜箔面积：Copper_Exposed_Area,任何odb资料都可以测试。
        """
        g = RunConfig.driver_g  # 拿到G软件
        temp_path = RunConfig.temp_path_base # 取到临时目录
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

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        # 测试用例料号
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号
        all_step_list_ep = Information.get_steps(job_ep)  # 得到所有step
        out_layer_list = Information.get_outer_layers(job_ep)  # 得到外层
        remote_temp_g_path = Path(RunConfig.temp_path_g).parent # 得到虚拟机中的share路径
        copper_area_file_name = 'copper_area.txt'  # 存放执行copper_area指令的文本名
        get_result_file_name = 'result_file_name.txt'  # 存放copper_area结果的文本名
        get_result_file_path = os.path.join(temp_path, get_result_file_name)  # copper_area结果文件路径
        if out_layer_list:
            for step in all_step_list_ep:
                if step == 'panel':  # 如果是拼版，则计算外层的残铜率
                    job_g_remote_path = os.path.join(RunConfig.temp_path_g, 'compressed', job_ep)  # 要比图的资料路径
                    g.import_odb_folder(job_g_remote_path)  # g导入要比图的资料
                    g.open_job(job_ep, step)  # 用g打开里料号
                    for layer in out_layer_list:
                        copper_area_ep = Information.get_rest_cu_rate(job_ep, step, layer, 0, 0)  # 得到ep的copper_area
                        g.get_copper_area(layer, temp_path, remote_temp_g_path, copper_area_file_name, get_result_file_name)
                        with open(get_result_file_path, 'r') as file:
                            content = file.readlines()
                        last_line = content[-1]
                        print("last_line", last_line)
                        copper_area_g = float(last_line.split(" ")[1]) / 100
                        # ----------------------------------------开始验证结果------------------------------------------------
                        print("copper_area_ep:",copper_area_ep)
                        print("copper_area_g:", copper_area_g)
                        assert copper_area_ep - copper_area_g < 0.03
        Job.close_job(job_ep)

