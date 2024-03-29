import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS
from epkernel import Input, GUI, BASE
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job


@pytest.mark.cc
class TestSavejob():
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Rename_save'))
    def test_Savejob(self, job_id):
        '''
        本用例测试 Rename、Save功能。料号ID：21648
        导入tgz删除step、删除layer，更改step、job名之后save
        '''

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
        temp_compressed_path = os.path.join(temp_path, 'compressed')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job, temp_compressed_path)  # 用悦谱CAM打开料号
        all_layers_list_job = Information.get_layers(job)
        all_step_list_job = Information.get_steps(job)

        # 删除以及保留的layer、step
        delete_layers = [x for x in all_layers_list_job if len(str(x)) > 3]
        delete_steps = all_step_list_job[1:]

        # 删除step、layer
        for layer in delete_layers:
            Matrix.delete_layer(job, layer)
        for step in delete_steps:
            Matrix.delete_step(job, step)

        # 更名、保存
        job_rename = '2625262a-orig'
        Job.rename_job(job, job_rename)
        BASE.save_job(job_rename)
        # GUI.show_matrix('2625262a-orig')
        # GUI.show_layer('8037049a', 'net', 'l1')

        # 获取save之后的文件层别信息
        steps_list = os.listdir(os.path.join(temp_compressed_path, '2625262a-orig\\steps'))
        layers_list = os.listdir(os.path.join(temp_compressed_path, '2625262a-orig\\steps\\orig\\layers'))

        # 获取EP—CAM层别信息
        steps = Information.get_steps(job_rename)
        layers = Information.get_layers(job_rename)

        if sorted(steps_list) == sorted(steps):
            print('steps测试通过')
        else:
            print('steps测试失败')
            print(steps_list)
            print(steps)

        if sorted(layers_list) == sorted(layers):
            print('layers测试通过')
        else:
            print('layers测试失败')
            print(sorted(layers_list))
            print(sorted(layers))

        assert sorted(steps_list) == sorted(steps)
        assert sorted(layers_list) == sorted(layers)
