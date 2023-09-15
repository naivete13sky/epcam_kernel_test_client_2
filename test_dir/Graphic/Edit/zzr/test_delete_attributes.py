import pytest, os, time, json, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS
from epkernel import Input
from epkernel.Action import Information
from epkernel.Edition import Layers


class TestDeleteAttributes():
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Delete_attributes'))
    def test_deleteattributes(self, job_id):
        '''
        本用例测试delete attributes功能。料号ID：27329
        测试删除所有属性是否成功
        禅道bug:434
        测试用例ID：3601
        '''
        print('分割线'.center(192, "-"))

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息


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

                # 取到临时目录
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')

        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # --------------------------------下载yg转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        # 原稿料号
        # job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job, temp_compressed_path)  # 用悦谱CAM打开料号
        # all_layers_list_job = Information.get_layers(job)


        # 获取原始物件属性存入字典
        layer_infos = Information.get_all_features_info(job, 'prepare', 'drl110')

        before_attributes_info = {}
        for i in layer_infos:
            for key, value in i.items():
                if 'attributes' in i:
                    if key == 'attributes':
                        print(key, ':', value)
                        before_attributes_info[key] = value
                        print(before_attributes_info)

        # 删除物件属性
        Layers.modify_attributes(job, 'prepare', ['drl110'], 3, [])
        # Layers.modify_attributes(job, 'prepare', ['drl110'], 2, [{'.orig_size_mm': '199998'}])

        # 获取删除之后的物件属性存入字典
        layer_infos = Information.get_all_features_info(job, 'prepare', 'drl110')

        now_attributes_info = {}
        for i in layer_infos:
            for key, value in i.items():
                if 'attributes' in i:
                    if key == 'attributes':
                        print(key, ':', value)
                        now_attributes_info[key] = value
                        print(now_attributes_info)

        # 断言
        assert before_attributes_info  != now_attributes_info
