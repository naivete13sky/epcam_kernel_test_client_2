import pytest,os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from config_ep.epcam_cc_method import MyInput
from epkernel import Input,GUI,BASE
from epkernel.Action import Information
from epkernel.Edition import Matrix
from epkernel.Output import save_job
from datetime import datetime
import shutil

class TestSaveJob:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Save'))
    def test_save(self, job_id):
        '''
        本用例测试cam对料号执行增、删层别保存后，验证ui上的层别和layers文件夹下的层别是否一致
        '''
        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息
        vs_time_g = str(int(time.time()))  # 比对时间
        data["vs_time_g"] = vs_time_g  # 比对时间存入字典
        data["job_id"] = job_id

        # 取到临时目录
        temp_path = RunConfig.temp_path_base + "_" + str(job_id) + "_" + vs_time_g
        temp_gerber_path = os.path.join(temp_path, 'compressed')
        temp_compressed_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')


        # ----------悦谱转图。先下载并解压原始gerber文件,拿到解压后的文件夹名称，此名称加上_ep就是我们要的名称。然后转图。-------------
        result = DMS().get_job_fields_from_dms_db_pandas(job_id)
        file_format = os.path.splitext(result['file'])[1]
        if file_format == '.rar':
            job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='rar')
            MyInput(folder_path=os.path.join(temp_gerber_path, os.listdir(temp_gerber_path)[0].lower()),
                    job=job_ep, step=r'orig', job_id=job_id, save_path=temp_ep_path)
            dir_path = temp_ep_path
        elif file_format =='.tgz':
            job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
            Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号
            dir_path = temp_compressed_path
        all_layers_list_job_ep = Information.get_layers(job_ep)
        step_name = Information.get_steps(job_ep)[0]

        # GUI.show_matrix(job_ep)
        # 删除料号的第一个层别
        Matrix.delete_layer(job_ep, all_layers_list_job_ep[0])
        # 创建一个新的层别
        add_layer_name = 'test_add_layer_save'
        Matrix.create_layer(job_ep, add_layer_name, -1)
        # GUI.show_matrix(job_ep)

        # job若存在则删除
        # shutil.rmtree(os.path.join(dir_path, job_ep)) if os.path.exists(os.path.join(dir_path, job_ep)) else True
        # 保存料号
        BASE.save_job(job_ep)

        # 获取layers文件夹下的层别数量
        ep_dir_path = dir_path + '\\' + job_ep + '\\steps\\' + step_name + '\\layers'

        ep_folder_names = [] #存放ep层别名称
        for item in os.listdir(ep_dir_path):
            item_path = os.path.join(ep_dir_path, item)
            if os.path.isdir(item_path):
                ep_folder_names.append(item)
        print("ep文件夹所有layer名:", ep_folder_names)

        # 重新获取ui上的层别
        all_layers_list_job_ep_new = Information.get_layers(job_ep)
        print("ui所有layer名：",all_layers_list_job_ep_new)
        # GUI.show_matrix(job_ep)

        # ----------------------------------------断言--------------------------------------------------------
        Print.print_with_delimiter("断言--开始")
        for ep_layer_name in ep_folder_names:
            assert ep_layer_name in all_layers_list_job_ep_new

