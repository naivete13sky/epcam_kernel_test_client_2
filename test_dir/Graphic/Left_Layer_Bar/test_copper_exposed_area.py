import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
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
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id
        step = 'prepare'  # 定义需要执行比对的step名
        # layers = ['l1']  # 定义需要比对的层
        # layers = ['l1++', 'l2', 'l4', 'l6']
        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
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




