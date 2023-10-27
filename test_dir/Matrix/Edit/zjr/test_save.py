import pytest,os, time
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from config_ep.epcam_cc_method import Pretreatment
from epkernel import Input,GUI,BASE
from epkernel.Action import Information
from epkernel.Edition import Matrix
import shutil

class Test_MatrixSave:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Save'))
    def test_matrix_save(self, job_id):
        '''
        本用例测试cam对料号执行增、删层别保存后，验证ui上的层别和layers文件夹下的层别是否一致，bugid:4665
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
            Pretreatment(job=job_ep, job_id=job_id).input_folder(temp_gerber_path, temp_ep_path)
            dir_path = temp_ep_path
        elif file_format =='.tgz':
            job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')
            Input.open_job(job_ep, temp_compressed_path)  # 用悦谱CAM打开料号
            dir_path = temp_compressed_path
        all_layers_list_job_ep = Information.get_layers(job_ep)
        step_name = Information.get_steps(job_ep)[0]

        # ----------第一次对料号进行编辑（删除、新增层别），验证save后layers文件夹中多出一个netlist层、以及ui上删除层别还存在-------------
        # 删除料号的第一个层别
        Matrix.delete_layer(job_ep, all_layers_list_job_ep[0])
        # GUI.show_matrix(job_ep)
        # 创建一个新的层别
        add_layer_name = 'test_add_layer_save'
        Matrix.create_layer(job_ep, add_layer_name, -1)
        # 保存料号,必须调用BASE中的save_job
        BASE.save_job(job_ep)
        # 重新获取ui上的层别
        all_layers_list_job_ep_1 = Information.get_layers(job_ep)

        # ----------第二次对料号进行编辑（删除层别），验证ui上删除层别后，然后rename_job，再save_job，ui上删除的层别，在layers文件夹中依然存在-------------
        job_ep_new = job_ep + '_new'
        BASE.save_job_as(job_ep,temp_path)
        BASE.close_job(job_ep)
        Input.open_job(job_ep,temp_path)
        # GUI.show_matrix(job_ep)
        # 删除料号的第一个层别
        Matrix.delete_layer(job_ep, all_layers_list_job_ep[1])
        BASE.job_rename(job_ep,job_ep_new)
        BASE.save_job(job_ep_new)
        all_layers_list_job_ep_2 = Information.get_layers(job_ep_new)

        # 获取layers文件夹下的层别数量
        ep_dir_path_1 = dir_path + '\\' + job_ep + '\\steps\\' + step_name + '\\layers'
        ep_folder_names_1 = [] #存放ep层别名称
        for item in os.listdir(ep_dir_path_1):
            item_path = os.path.join(ep_dir_path_1, item)
            if os.path.isdir(item_path):
                ep_folder_names_1.append(item)

        ep_dir_path_2 = temp_path + '\\' + job_ep_new + '\\steps\\' + step_name + '\\layers'
        ep_folder_names_2 = []  # 存放ep层别名称
        for item in os.listdir(ep_dir_path_2):
            item_path = os.path.join(ep_dir_path_2, item)
            if os.path.isdir(item_path):
                ep_folder_names_2.append(item)

        print("原始layers:",all_layers_list_job_ep)
        print("第一次ep文件夹layers名:", ep_folder_names_1)
        print("第一次ui最新layers名：", all_layers_list_job_ep_1)
        # 重新获取ui上的层别
        print("第二次ep文件夹layers名:", ep_folder_names_2)
        print("第二次ui最新layers名：", all_layers_list_job_ep_2)
        # GUI.show_matrix(job_ep)

        # ----------------------------------------开始验证结果：G与EP---------------------------------------------------------
        Print.print_with_delimiter('断言--开始')
        for ep_layer_name_1 in ep_folder_names_1:
            assert ep_layer_name_1 in all_layers_list_job_ep_1
        for ep_layer_name_2 in ep_folder_names_2:
            assert ep_layer_name_2 in all_layers_list_job_ep_2
        Print.print_with_delimiter("断言--结束")

