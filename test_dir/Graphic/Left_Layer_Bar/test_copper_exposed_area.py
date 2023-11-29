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
        copper_area_file_name_g = 'copper_area.txt'  # 存放g软件执行copper_area脚本指令的文件名
        get_result_file_name_g = 'result_file_name.txt'  # 存放g软件的残铜率结果文件名
        get_result_file_path_g = os.path.join(temp_path, get_result_file_name_g)  # 存放g软件的残铜率结果文件路径
        step = [step for step in all_step_list_ep if step == 'panel'] #得到panel的step
        if step and out_layer_list: # 如果有panel和外层，则计算外层的残铜率
            job_g_remote_path = os.path.join(RunConfig.temp_path_g, 'compressed', job_ep)  # 要比图的资料路径
            g.import_odb_folder(job_g_remote_path)  # 用g导入要比图的资料
            g.open_job(job_ep, step[0])  # 用g打开料号
            for layer in out_layer_list: #逐个获取ep-cam和g的外层残铜率，并对结果进行断言
                copper_area_ep = Information.get_rest_cu_rate(job_ep, step[0], layer, 0, 0)  # 得到ep的残铜率
                # 获取g的残铜率（通过虚拟机使用cmd操作g软件执行run脚本，将结果数据保存到文件中）
                g.get_copper_area(layer, temp_path, remote_temp_g_path, copper_area_file_name_g, get_result_file_name_g)
                with open(get_result_file_path_g, 'r') as file: #打开文件
                    content = file.readlines() #读取文件中的内容（g的残铜率）
                last_line = content[-1] #获取最后一行内容
                print("last_line", last_line)
                copper_area_g = float(last_line.split(" ")[1]) / 100
                # ----------------------------------------开始验证结果------------------------------------------------
                print("copper_area_ep:",copper_area_ep)
                print("copper_area_g:", copper_area_g)
                assert abs(copper_area_ep - copper_area_g) < 0.03 #断言ep-cam和g的残铜率，差值在0.03以内则通过
        Job.close_job(job_ep)

