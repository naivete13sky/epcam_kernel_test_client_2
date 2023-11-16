import pytest, os, shutil
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print
from epkernel import Input, GUI
from epkernel.Action import Information
from epkernel.Edition import Matrix, Job
from epkernel.Output import save_job

class TestChangeMatrix:
    """
    共执行2条测试用例，覆盖70个测试场景
    """
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Change_Matrix_Column'))
    def test_change_matrix_column(self, job_id):
        """
        id:39596,本用例测试Matrix窗口的chang_matrix_column功能,共执行1个测试用例，覆盖30个测试场景
        """
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
        all_steps_list_job_g = Information.get_steps(job_g)

        # 用悦谱CAM打开料号
        Input.open_job(job_ep, temp_gerber_path)
        all_steps_list_job_ep = Information.get_steps(job_ep)

        '''
        用例名称：对step名修改新的名字
        预期1：修改成功
        执行场景数：1个
        '''
        for step in all_steps_list_job_ep:
            if step == 'orig+1':
                old_step_name = step
                new_step_name = 'neworig'
        Matrix.change_matrix_column(job_ep,old_step_name,new_step_name)

        '''
        用例名称：对step名修改已存在的名字
        预期1：无法修改
        执行场景数：1个
        '''
        for step in all_steps_list_job_ep:
            if step == 'net':
                new_step_name = step
            if step == 'net+1':
                old_step_name = step
        Matrix.change_matrix_column(job_ep,old_step_name,new_step_name)
        # GUI.show_matrix(job_ep)
        '''
        用例名称：修改step名为有效特殊字符
        预期1：修改成功
        执行场景数：3个
        '''
        num = 1
        index = 0
        valid_list = ['_','+','-']
        all_steps_list_job_ep = Information.get_steps(job_ep)
        for step in all_steps_list_job_ep:
            if num > len(valid_list):
                break
            old_step_name = step
            new_step_name = step + valid_list[index]
            num = num +1
            index = index + 1
            Matrix.change_matrix_column(job_ep,old_step_name,new_step_name)

        '''
        用例名称：修改最后一列step名有大写字母
        预期1：修改成功，大写转换为小写
        执行场景数：1个
        '''
        all_steps_list_job_ep = Information.get_steps(job_ep)
        item = len(all_steps_list_job_ep)
        step_name_capital_letter = 'A'
        Matrix.change_matrix_column(job_ep, all_steps_list_job_ep[item - 1],
                                    all_steps_list_job_ep[item - 1] + step_name_capital_letter)

        '''
        用例名称：修改step名为无效特殊字符
        预期1：大修改失败
        执行场景数：24个
        '''
        all_steps_list_job_ep = Information.get_steps(job_ep)
        illegal_list = ['你好', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '{', '[', '}', ']','\\', '|',
                        ';', ':', '"', '/', '?']
        for illegal in illegal_list:
            item = len(all_steps_list_job_ep)
            Matrix.change_matrix_column(job_ep, all_steps_list_job_ep[item - 1],
                                        all_steps_list_job_ep[item - 1] + illegal)
        # GUI.show_matrix(job_ep)

        save_job(job_ep, temp_ep_path)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        # print("test_cases：", test_cases)

        # ----------------------------------------开始验证结果--------------------------------------------------------
        column_ep = 1
        dict_step_column_ep = {}
        for step_ep in all_steps_list_job_ep:
            dict_step_column_ep[step_ep] = column_ep
            column_ep = column_ep + 1

        column_g = 1
        dict_step_column_g = {}
        for step_g in all_steps_list_job_g:
            dict_step_column_g[step_g] = column_g
            column_g = column_g + 1
        print("dict_step_column_ep",dict_step_column_ep)
        print("dict_step_column_g",dict_step_column_g)
        assert dict_step_column_ep == dict_step_column_g
        Print.print_with_delimiter("断言--结束")

        Job.close_job(job_ep)
        Job.close_job(job_g)

    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Change_Matrix_Row'))
    def test_change_matrix_row(self, job_id):
        """
        id:40665,本用例测试Matrix窗口的chang_matrix_row功能,共执行1个测试用例，覆盖40个测试场景
        """
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
        all_layers_list_job_ep = Information.get_layers(job_ep)
        '''
        用例名称：对layer名修改新的名字
        预期1：修改成功
        执行场景数：1个
        '''
        for layer in all_layers_list_job_ep:
            if layer == 'top.art':
                old_layer_name = layer
                new_layer_name = 'newtop'
        Matrix.change_matrix_row(job_ep, old_layer_name, 'misc', 'signal', new_layer_name, True)

        '''
        用例名称：对layer名修改已存在的名字
        预期1：修改失败
        执行场景数：1个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        for layer in all_layers_list_job_ep:
            if layer == 'newtop':
                new_layer_name = layer
            if layer == 'layer2.art':
                old_layer_name = layer
        Matrix.change_matrix_row(job_ep, old_layer_name, 'misc', 'signal', new_layer_name, True)

        '''
        用例名称：修改layer名为有效特殊字符
        预期1：修改成功
        执行场景数：3个
        '''
        num = 1
        index = 0
        valid_list = ['_','+','-']
        all_layer_list_job_ep = Information.get_layers(job_ep)
        for layer in all_layer_list_job_ep:
            if num > len(valid_list):
                break
            old_layer_name = layer
            new_layer_name = layer.split('.')[0] + valid_list[index]
            num = num +1
            index = index + 1
            Matrix.change_matrix_row(job_ep, old_layer_name, 'misc', 'signal', new_layer_name, True)


        '''
        用例名称：修改最后一列step名有大写字母
        预期1：修改成功，大写转换为小写
        执行场景数：1个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        item = len(all_layers_list_job_ep)
        old_layer_name = all_layers_list_job_ep[item - 1]
        new_layer_name = old_layer_name.split('.')[0] + 'A'
        Matrix.change_matrix_row(job_ep, old_layer_name, 'misc', 'signal', new_layer_name, True)

        '''
        用例名称：修改layer名为无效特殊字符
        预期1：修改失败
        执行场景数：24个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        illegal_list = ['你好', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '{', '[', '}', ']', '\\', '|',
                        ';', ':', '"', '/', '?']
        for illegal in illegal_list:
            item = len(all_layers_list_job_ep)
            old_layer_name = all_layers_list_job_ep[item - 1]
            new_layer_name = old_layer_name + illegal
            Matrix.change_matrix_row(job_ep, old_layer_name, 'misc', 'signal', new_layer_name, True)

        '''
        用例名称：修改layer属性
        预期1：修改成功
        执行场景数：1个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        layer_context = 'board'
        index = 0
        layer_name = all_layers_list_job_ep[index]
        Matrix.change_matrix_row(job_ep, layer_name, layer_context, 'signal', layer_name, True)
        # GUI.show_matrix(job_ep)
        '''
        用例名称：修改layer类型
        预期1：修改成功
        执行场景数：8个
        '''
        all_layers_list_job_ep = Information.get_layers(job_ep)
        layer_type_list = ['power_ground', 'mixed', 'solder_mask', 'silk_screen', 'solder_paste', 'drill', 'rout',
                           'document']
        for type in layer_type_list:
            index = index + 1
            if index > len(layer_type_list):
                break
            old_layer_name = all_layers_list_job_ep[index]
            new_layer_name = old_layer_name.split('.')[0]
            Matrix.change_matrix_row(job_ep, old_layer_name, layer_context, type, new_layer_name, True)

        '''
        用例名称：修改layer极性
        预期1：修改成功
        执行场景数：1个
        '''
        index = index + 1
        old_layer_name = all_layers_list_job_ep[index]
        new_layer_name = old_layer_name.split('.')[0]
        Matrix.change_matrix_row(job_ep, old_layer_name, layer_context, 'signal', new_layer_name, False)

        save_job(job_ep, temp_ep_path)

        # ----------------------------------------开始验证结果--------------------------------------------------------
        all_layers_list_job_ep = Information.get_layers(job_ep)
        all_steps_list_job_ep = Information.get_steps(job_ep)
        layer_informations_ep = Information.get_layer_information(job_ep)
        layer_informations_g = Information.get_layer_information(job_g)

        dict_layer_row_ep = {}
        for layer_ep in all_layers_list_job_ep:
            if Information.get_layer_feature_count(job_ep,all_steps_list_job_ep[0],layer_ep) > 0:
                for information in layer_informations_ep:
                    if information['name'] == layer_ep:
                        context = information['context']
                        type = information['type']
                        polarity = information['polarity']
                        dict_layer_row_ep[layer_ep] = context, type, polarity

        dict_layer_row_g = {}
        for layer_g in all_layers_list_job_g:
            for information in layer_informations_g:
                if information['name'] == layer_g:
                    context = information['context']
                    type = information['type']
                    polarity = information['polarity']
                    dict_layer_row_g[layer_g] = context, type, polarity
        assert dict_layer_row_ep == dict_layer_row_g
        Print.print_with_delimiter("断言--结束")

        Job.close_job(job_ep)
        Job.close_job(job_g)