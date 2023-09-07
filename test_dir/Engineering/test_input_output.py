import pytest, os, time, json, shutil, sys
from config import RunConfig
from cc.cc_method import GetTestData, DMS, Print, getFlist, CompressTool
from config_ep.epcam_cc_method import MyInput, MyOutput
from config_g.g_cc_method import GInput
from epkernel import Input, GUI, BASE
from epkernel.Action import Information
from epkernel.Edition import Layers
from datetime import datetime


@pytest.mark.input_output
class TestInputOutputBasicGerber274X:
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Input_Output'))
    def test_input_output_gerber274x(self, job_id, g, prepare_test_job_clean_g):
        '''
        本用例测试Gerber274X（包括Excellon2）的导入与导出功能.
        '''

        g = RunConfig.driver_g#拿到G软件
        data = {}#存放比对结果信息

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



        temp_gerber_path = os.path.join(temp_path, 'compressed')
        temp_ep_path = os.path.join(temp_path, 'ep')
        temp_g_path = os.path.join(temp_path, 'g')
        temp_g2_path = os.path.join(temp_path, 'g2')

        # ----------悦谱转图。先下载并解压原始gerber文件,拿到解压后的文件夹名称，此名称加上_ep就是我们要的名称。然后转图。-------------
        job_ep = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='rar')
        # print('job_ep:',job_ep)
        MyInput(folder_path = os.path.join(temp_gerber_path, os.listdir(temp_gerber_path)[0].lower()),
                job = job_ep, step = r'orig', job_id = job_id, save_path = temp_ep_path)
        all_layers_list_job_ep = Information.get_layers(job_ep)
        # print('all_layers_list_job_ep:',all_layers_list_job_ep)

        # GUI.show_layer(job_ep, 'orig', all_layers_list_job_ep[0])
        # time.sleep(1000)

        # --------------------------------下载G转图tgz，并解压好，获取到文件夹名称，作为g料号名称-------------------------------
        job_g = DMS().get_file_from_dms_db(temp_path, job_id, field='file_odb_g', decompress='tgz')
        Input.open_job(job_g, temp_g_path)#用悦谱CAM打开料号
        all_layers_list_job_g = Information.get_layers(job_g)

        # ----------------------------------------开始比图：G与EP---------------------------------------------------------
        print('比图--G转图VS悦谱转图'.center(190,'-'))
        all_layer_from_org = [each for each in DMS().get_job_layer_fields_from_dms_db_pandas(job_id, field='layer_org')]
        drill_layers = [each.lower() for each in DMS().get_job_layer_drill_from_dms_db_pandas_one_job(job_id)['layer']]

        layerInfo = []
        for each in all_layers_list_job_g:
            each_dict = {}
            each_dict["layer"] = each.lower()
            each_dict['layer_type'] = 'drill' if each in drill_layers else ''
            layerInfo.append(each_dict)

        print("layerInfo:",layerInfo)

        job1, job2 = job_g, job_ep
        step1, step2 = 'orig', 'orig'
        # 导入要比图的资料,并打开
        job_g_remote_path = os.path.join(RunConfig.temp_path_g,r'g',job_g)
        job_ep_remote_path = os.path.join(RunConfig.temp_path_g,r'ep',job_ep)
        g.import_odb_folder(job_g_remote_path)
        g.import_odb_folder(job_ep_remote_path)
        g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)



        # 校正孔用
        temp_path_local_info1 = os.path.join(temp_path, 'info1')
        if not os.path.exists(temp_path_local_info1):
            os.mkdir(temp_path_local_info1)
        temp_path_local_info2 = os.path.join(temp_path, 'info2')
        if not os.path.exists(temp_path_local_info2):
            os.mkdir(temp_path_local_info2)


        compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                             job1=job1, step1=step1,
                                             job2=job2, step2=step2,
                                             layerInfo=layerInfo,
                                             adjust_position=True, jsonPath=r'my_config.json')
        print('compareResult_input_vs:',compareResult)
        data["all_result_g"] = compareResult['all_result_g']
        data['g_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']
        assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])



        # ----------------------------------------开始测试输出gerber功能---------------------------------------------------
        customer_para = {}
        customer_para['numberFormatR'] = 6
        MyOutput(temp_path = temp_path, job = job_ep, job_id = job_id,layer_info_from_obj='dms',customer_para = customer_para)

        # ----------------------------------------开始用G软件input--------------------------------------------------------
        ep_out_put_gerber_folder = os.path.join(temp_path, r'output_gerber', job_ep, r'orig')
        job_g2 = os.listdir(temp_gerber_path)[0].lower() + '_g2'  # epcam输出gerber，再用g软件input。
        step = 'orig'
        file_path = os.path.join(temp_path, ep_out_put_gerber_folder)
        gerberList = getFlist(file_path)
        print(gerberList)
        g_temp_path = RunConfig.temp_path_g
        # gerberList_path = []
        # for each in gerberList:
        #     gerberList_path.append(os.path.join(g_temp_path, r'output_gerber', job_ep, r'orig', each))
        # print(gerberList_path)

        temp_out_put_gerber_g_input_path = os.path.join(temp_path, 'g2')
        if os.path.exists(temp_out_put_gerber_g_input_path):
            shutil.rmtree(temp_out_put_gerber_g_input_path)
        os.mkdir(temp_out_put_gerber_g_input_path)
        out_path = temp_out_put_gerber_g_input_path

        # g.gerber_to_odb_batch(job_g2, step, gerberList_path, out_path, job_id, drill_para='epcam_default')
        gerberList_path = []

        for each in gerberList:
            each_dict = {}
            each_dict['path'] = os.path.join(g_temp_path, r'output_gerber', job_ep, r'orig', each)
            layer_e2 = DMS().get_job_layer_fields_from_dms_db_pandas_one_layer(job_id,filter=each.replace(' ', '-').replace('(', '-').replace(')', '-'))
            if layer_e2.status.values[0] == 'published' and layer_e2.layer_file_type.values[0]=='excellon2':
                each_dict['file_type'] = 'excellon'
                each_dict_para = {}
                print('layer_e2cc:',layer_e2)
                # each_dict_para['zeroes'] = layer_e2.zeroes_omitted.values[0].lower()
                # each_dict_para['nf1'] = int(layer_e2.number_format_A.values[0])
                # each_dict_para['nf2'] = int(layer_e2.number_format_B.values[0])
                # each_dict_para['units'] = layer_e2.units.values[0].lower()
                # # g软件的tool_units没有mils选项
                # if layer_e2.tool_units_g.values[0].lower() == 'mils':
                #     each_dict_para['tool_units'] = 'inch'
                # else:
                #     each_dict_para['tool_units'] = layer_e2.tool_units_g.values[0].lower()

                each_dict_para['units'] = 'inch'
                each_dict_para['zeroes'] = 'none'
                each_dict_para['nf1'] = "2"
                each_dict_para['nf2'] = "6"
                each_dict_para['tool_units'] = 'mm'

                each_dict['para'] = each_dict_para
                gerberList_path.append(each_dict)
            else:#不是孔就当作是gerber处理
                each_dict['file_type'] = 'gerber'
                gerberList_path.append(each_dict)
        g.input_init(job=job_g2, step=step, gerberList_path=gerberList_path,jsonPath=r'D:\cc\python\epwork\epcam_kernel_test_client_2\my_config.json')
        # 输出tgz到指定目录
        g.g_export(job_g2, os.path.join(g_temp_path, r'g2'))

        # ----------------------------------------开始用G软件比图，g1和g2--------------------------------------------------------
        # 再导入一个标准G转图，加个后缀1。
        job_g1 = job_g + "1"
        g.import_odb_folder(job_g_remote_path, job_name=job_g1)
        g1_compare_result_folder = 'g1_compare_result'
        temp_g1_compare_result_path = os.path.join(temp_path, g1_compare_result_folder)
        if not os.path.exists(temp_g1_compare_result_path):
            os.mkdir(temp_g1_compare_result_path)







        #校正孔用
        temp_path_local_info1 = os.path.join(temp_path, 'info1')
        if not os.path.exists(temp_path_local_info1):
            os.mkdir(temp_path_local_info1)
        temp_path_local_info2 = os.path.join(temp_path, 'info2')
        if not os.path.exists(temp_path_local_info2):
            os.mkdir(temp_path_local_info2)

        # 以G1转图为主来比对
        # G打开要比图的2个料号g1和g2。g1就是原始的G转图，g2是悦谱输出的gerber又input得到的
        job1,job2 = job_g1,job_g2
        step1, step2 = 'orig', 'orig'
        g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)# 打开要比图的料号
        compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                        job1=job1, step1=step1,
                                        job2=job2, step2=step2,
                                        layerInfo=layerInfo,
                                        adjust_position=True, jsonPath=r'my_config.json')
        print('compareResult_output_vs:', compareResult)
        data["all_result_g1"] = compareResult['all_result_g']
        data['g1_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']
        assert len(all_layers_list_job_g) == len(compareResult['all_result_g'])

        # 获取原始层文件信息，最全的

        all_result = {}  # all_result存放原始文件中所有层的比对信息
        for layer_org in all_layer_from_org:
            layer_org_find_flag = False
            layer_org_vs_value = ''
            for each_layer_g_result in compareResult['all_result_g']:
                if each_layer_g_result == str(layer_org).lower().replace(" ", "-").replace("(", "-").replace(")", "-"):
                    layer_org_find_flag = True
                    layer_org_vs_value = compareResult['all_result_g'][each_layer_g_result]
            if layer_org_find_flag == True:
                all_result[layer_org] = layer_org_vs_value
            else:
                all_result[layer_org] = 'G转图中无此层'




        # ----------------------------------------开始用EP软件比图，g和g2--------------------------------------------------
        # all_result_ep_vs_g_g2 = {}
        # # 打开job_g
        # # 前面打开过的。直接show下看看
        # # GUI.show_layer(job_g, 'orig', 'top')
        #
        # # 打开 job_g2
        # #先解压tgz
        # CompressTool.untgz(os.path.join(temp_g2_path, os.listdir(temp_g2_path)[0]),temp_g2_path)
        # Input.open_job(job_g2, temp_g2_path)
        # # GUI.show_layer(job_g2, 'orig', 'top')
        #
        # # 开始用kernel比对
        # for each_layer_g in all_layers_list_job_g:
        #     print('EP VS'.center(192,'-'))
        #     print('层名称：',each_layer_g)
        #     ep_layer_compare_result = BASE.layer_compare_point(job_g, 'orig', each_layer_g, job_g2, 'orig', each_layer_g, 22860,True, True, 5080000)
        #     ep_layer_compare_result = json.loads(ep_layer_compare_result)
        #     print(ep_layer_compare_result)
        #     print(len(ep_layer_compare_result['result']))
        #     if len(ep_layer_compare_result['result']) > 0:
        #         all_result_ep_vs_g_g2[each_layer_g] = '错误'
        #         print('错误！')
        #         # Layers.layer_compare(job_g, 'orig', each_layer_g, job_g2, 'orig', each_layer_g, 22860,True, True, each_layer_g + '-com', 5080000)
        #         # GUI.show_layer(job_g, 'orig', each_layer_g)
        #     if len(ep_layer_compare_result['result']) == 0:
        #         all_result_ep_vs_g_g2[each_layer_g] = '正常'
        #         print('正常！')
        #
        # assert len(all_result_ep_vs_g_g2) == len(all_layers_list_job_g)





        # ----------------------------------------开始验证结果--------------------------------------------------------

        print('比对结果信息展示--开始'.center(198,'*'))
        if data['g_vs_total_result_flag'] == True:
            print("恭喜您！料号导入比对通过！")
        if data['g_vs_total_result_flag'] == False:
            print("Sorry！料号导入比对未通过，请人工检查！")
        print('分割线'.center(198,'-'))
        print('G转图的层：', data["all_result_g"])
        print('分割线'.center(198,'-'))
        print('所有层：', all_result)
        print('分割线'.center(198,'-'))
        print('G1转图的层：', data["all_result_g1"])
        print('分割线'.center(198,'-'))
        # print('悦谱比图结果：', all_result_ep_vs_g_g2)
        # Print.print_with_delimiter('比对结果信息展示--结束')

        Print.print_with_delimiter("断言--开始")
        assert data['g_vs_total_result_flag'] == True
        for key in data['all_result_g']:
            assert data['all_result_g'][key] == "正常"

        assert data['g1_vs_total_result_flag'] == True
        for key in data['all_result_g1']:
            assert data['all_result_g1'][key] == "正常"

        # for key in all_result_ep_vs_g_g2:
        #     assert all_result_ep_vs_g_g2[key] == "正常"

        Print.print_with_delimiter("断言--结束")




# 输出参数组合太多啦，这里是通过参数化设置导出参数。这里使用python内置的namedtuple方法来存放参数
from collections import namedtuple
GerberOutputPara = namedtuple('GerberOutputPara',
                              ['resize', 'angle', 'scalingX', 'scalingY', 'mirror', 'rotate', 'scale', 'cw',
                               'mirrorpointX', 'mirrorpointY', 'rotatepointX', 'rotatepointY',
                               'scalepointX', 'scalepointY', 'mirrorX', 'mirrorY', 'numberFormatL', 'numberFormatR',
                               'zeros', 'unit'])
# 设置默认参数
GerberOutputPara.__new__.__defaults__ = (0, 0, 1, 1, False, False, False, False,
                                         0, 0, 0, 0,
                                         0, 0, False, False, 2, 6,
                                         2, 0)
gerber_output_paras_to_test = (
    GerberOutputPara(),#默认参数
    # GerberOutputPara(numberFormatR=5),#自定义参数
    # GerberOutputPara(numberFormatL=3),#自定义参数
)

def id_func(fixture_value):
    """A function for generating ids."""
    p = fixture_value
    return '''GerberOutputPara({},{},{},{},{},{},{},{},
        {},{},{},{},
        {},{},{},{},{},{},
        {},{})'''.format(p.resize, p.angle, p.scalingX, p.scalingY, p.mirror, p.rotate, p.scale, p.cw,
                         p.mirrorpointX, p.mirrorpointY, p.rotatepointX, p.rotatepointY,
                         p.scalepointX, p.scalepointY, p.mirrorX, p.mirrorY, p.numberFormatL, p.numberFormatR,
                         p.zeros, p.unit)

@pytest.fixture(params=gerber_output_paras_to_test, ids=id_func)
def para_gerber_output(request):
    """Using a function (id_func) to generate ids."""
    return request.param

@pytest.mark.cc
class TestOutputGerber274XParas():
    # @pytest.mark.parametrize('step_name',['orig','panel'])
    @pytest.mark.parametrize("job_id", GetTestData().get_job_id('Output'))
    def test_output_gerber274x(self, job_id, g, prepare_test_job_clean_g, para_gerber_output):
        '''本用例测试Gerber274X（包括Excellon2）的导入与导出功能'''
        print('分割线'.center(192, "-"))
        print(para_gerber_output)

        g = RunConfig.driver_g  # 拿到G软件
        data = {}  # 存放比对结果信息



        # 取到临时目录，如果存在旧目录，则删除
        temp_path = RunConfig.temp_path_base
        temp_compressed_path = os.path.join(temp_path, 'compressed')
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



        # --------------------------------下载测试资料--tgz文件，并解压完，文件夹名称作为料号名称-------------------------------
        job = DMS().get_file_from_dms_db(temp_path, job_id, field='file_compressed', decompress='tgz')

        # 用悦谱CAM打开料号
        Input.open_job(job, temp_compressed_path)  # 用悦谱CAM打开料号
        all_layers_list_job = Information.get_layers(job)
        all_step_list_job = Information.get_steps(job)
        step_name_list = ['orig', 'panel']
        for step_name in step_name_list:
            if step_name in all_step_list_job:
                print('测试Step：', step_name)
                print('all_layer_list_job:', all_layers_list_job)
                # 区分层别类型
                drill_layers = list(map(lambda x: x['name'], Information.get_layer_info(job, context='board', type=['drill'])))
                rout_layers = list(map(lambda x: x['name'], Information.get_layer_info(job, context='board', type=['rout'])))


                print('drill_layers:', drill_layers)
                print('rout_layers:', rout_layers)
                common_layers = []
                for each in all_layers_list_job:
                    if each not in drill_layers:
                        common_layers.append(each)
                print('common_layers:', common_layers)

                # 导出
                customer_para = {}
                customer_para['numberFormatL'] = para_gerber_output.numberFormatL
                customer_para['numberFormatR'] = para_gerber_output.numberFormatR

                MyOutput(temp_path=temp_path, job=job, job_id=job_id, step = step_name, layer_info_from_obj='job_tgz_file',
                         customer_para=customer_para)

                # ----------------------------------------开始用G软件input--------------------------------------------------------
                ep_out_put_gerber_folder = os.path.join(temp_path, r'output_gerber', job, step_name)
                job_g2 = os.listdir(temp_compressed_path)[0].lower() + '_g2'  # epcam输出gerber，再用g软件input。
                # step = 'orig'
                step = step_name
                file_path = os.path.join(temp_path, ep_out_put_gerber_folder)
                gerberList = getFlist(file_path)
                print(gerberList)
                # g_temp_path = r'//vmware-host/Shared Folders/share/temp_{}_{}'.format(job_id, vs_time_g)
                g_temp_path = RunConfig.temp_path_g
                gerberList_path = []
                for each in gerberList:
                    gerberList_path.append(os.path.join(g_temp_path, r'output_gerber', job, step_name, each))
                print(gerberList_path)

                temp_out_put_gerber_g_input_path = os.path.join(temp_path, 'g2')
                if os.path.exists(temp_out_put_gerber_g_input_path):
                    shutil.rmtree(temp_out_put_gerber_g_input_path)
                os.mkdir(temp_out_put_gerber_g_input_path)
                out_path = temp_out_put_gerber_g_input_path

                GInput(job=job_g2, step=step, gerberList_path=gerberList_path, out_path=out_path, job_id=job_id,
                       drill_para='epcam_default', layer_info_from_obj='job_tgz_file',
                       layer_list=all_layers_list_job, gerber_layer_list=common_layers, drill_layer_list=drill_layers,
                       rout_layer_list=rout_layers)
                # 输出tgz到指定目录
                g.g_export(job_g2, os.path.join(g_temp_path, r'g2'))

                # ----------------------------------------开始用G软件比图，g与g2---------------------------------------------------
                # 先导入
                # job_g_remote_path = r'\\vmware-host\Shared Folders\share/{}/compressed/{}'.format(
                #     'temp' + "_" + str(job_id) + "_" + vs_time_g, job)
                job_g_remote_path = os.path.join(RunConfig.temp_path_g,'compressed',job)
                # 导入要比图的资料
                g.import_odb_folder(job_g_remote_path)

                layerInfo = []
                for each in all_layers_list_job:
                    each_dict = {}
                    each_dict["layer"] = each.lower()
                    each_dict['layer_type'] = 'drill' if each in drill_layers else ''
                    layerInfo.append(each_dict)

                print("layerInfo:", layerInfo)

                job1, job2 = job, job_g2
                step1, step2 = step_name, step_name
                # 打开要比图的资料
                g.layer_compare_g_open_2_job(job1=job1, step1=step1, job2=job2, step2=step2)

                # 校正孔用
                temp_path_local_info1 = os.path.join(temp_path, 'info1')
                if not os.path.exists(temp_path_local_info1):
                    os.mkdir(temp_path_local_info1)
                temp_path_local_info2 = os.path.join(temp_path, 'info2')
                if not os.path.exists(temp_path_local_info2):
                    os.mkdir(temp_path_local_info2)

                # 以G转图为主来比对
                # G打开要比图的2个料号g和g2。g就是原始，g2是悦谱输出的gerber又input得到的
                compareResult = g.layer_compare(temp_path=temp_path, temp_path_g=RunConfig.temp_path_g,
                                                job1=job1, step1=step1,
                                                job2=job2, step2=step2,
                                                layerInfo=layerInfo,
                                                adjust_position=True, jsonPath=r'my_config.json')
                print('compareResult_input_vs:', compareResult)
                data["all_result_g"] = compareResult['all_result_g']
                data['g_vs_total_result_flag'] = compareResult['g_vs_total_result_flag']
                assert len(all_layers_list_job) == len(compareResult['all_result_g'])



                # ----------------------------------------开始验证结果--------------------------------------------------------
                print('比对结果信息展示--开始'.center(192,'*'))
                if data['g_vs_total_result_flag'] == True:
                    print("恭喜您！料号导入比对通过！")
                if data['g_vs_total_result_flag'] == False:
                    print("Sorry！料号导入比对未通过，请人工检查！")
                print('分割线'.center(192,'-'))
                print('G转图的层：', data["all_result_g"])

                print('比对结果信息展示--结束'.center(192,'*'))

                print("断言--开始".center(192,'*'))
                assert data['g_vs_total_result_flag'] == True
                for key in data['all_result_g']:
                    assert data['all_result_g'][key] == "正常"

                print("断言--结束".center(192,'*'))
            else:
                print('无此step!')


