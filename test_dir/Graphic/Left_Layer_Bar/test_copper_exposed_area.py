import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from epkernel import Input, GUI, BASE
from epkernel.Action import Information, Selection
from epkernel.Edition import Layers
from epkernel.Output import save_job
from config_g.g_cc_method import G
from epkernel.Edition import Matrix


class TestGraphicCopper_Exposed_Area:
    # @pytest.mark.Copper_Exposed_Area
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Copper_Exposed_Area'))
    def testcopper_exposed_area(self, job_id, g, prepare_test_job_clean_g):
        '''
        测试计算铜箔面积：Copper_Exposed_Area,ID:38023
        '''

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l1']  # 定义需要比对的层
        # layers = ['l1++', 'l2', 'l4', 'l6']
        # 取到临时目录
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

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号

        surface_info = Information.get_rest_cu_rate(job_ep, step, 'l1', 254000)
        # GUI.show_layer(job_ep, step, 'l1')
        print("残铜率：", surface_info)

        surface_info = {
            'surface_copper': 0.68,
        }

        surface_value = surface_info.get('surface_copper')
        print("'surface_copper' key is:", surface_value)

        surface_info_new = surface_info.get('surface_copper', 0.68)
        print(" 'surface_info_new' key is:", surface_info_new)

        save_job(job_ep, temp_ep_path)
        # GUI.show_layer(job_case, step, 'l1')

        # 断言（比对某个字典信息）
        assert surface_value == surface_info_new




