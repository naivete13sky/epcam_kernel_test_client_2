import shutil
import tarfile

import pytest, os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from collections import namedtuple
from epkernel import Input, GUI, BASE, Output, Application
from epkernel.Action import Information
from epkernel.Edition import Layers, Matrix, Job


@pytest.mark.cc
class Test_Export_tgz():
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Rename_save'))
    def test_output_gerber274x(self, job_id):
        '''
        本用例测试 Rename、Save功能。料号ID：21648
        导入tgz删除step、删除layer，更改step、job名之后save
        '''
        print('分割线'.center(192, "-"))

        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_compressed_path = os.path.join(temp_path, 'compressed')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job, temp_compressed_path)  # 用悦谱CAM打开料号
        all_layers_list_job = Information.get_layers(job)
        all_step_list_job = Information.get_steps(job)

        # 删除以及保留的layer、step
        delete_layers = [x for x in all_layers_list_job if len(str(x)) > 3]
        delete_step = all_step_list_job[1:]

        # 删除step、layer
        for layer in delete_layers:
            Matrix.delete_layer('2625262a', layer)
        for step in delete_step:
            Matrix.delete_step('2625262a', step)

        # 更名、保存
        Job.rename_job('2625262a', '2625262a-orig')
        BASE.save_job('2625262a-orig')
        # GUI.show_matrix('2625262a-orig')
        # GUI.show_layer('8037049a', 'net', 'l1')

        # 获取save之后的文件层别信息
        steps_list = os.listdir(os.path.join(temp_compressed_path, '2625262a-orig\\steps'))
        layers_list = os.listdir(os.path.join(temp_compressed_path, '2625262a-orig\\steps\\orig\\layers'))

        # 获取EP—CAM层别信息
        steps = Information.get_layers('2625262a-orig')
        layers = Information.get_steps('2625262a-orig')

        # if sorted(steps_list) == sorted(steps):
        #     print('测试通过')
        # else:
        #     print('测试失败')
        #     print(steps_list)
        #     print(steps)
        #
        # if sorted(layers_list) == sorted(layers):
        #     print('测试通过')
        # else:
        #     print('测试失败')
        #     print(sorted(layers_list))
        #     print(sorted(layers))

        assert sorted(steps_list) == sorted(steps)
        assert sorted(layers_list) == sorted(layers)
