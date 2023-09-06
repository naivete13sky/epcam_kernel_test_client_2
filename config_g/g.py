import json
import os,shutil
import subprocess
import time


LAYER_COMPARE_JSON = 'layer_compare.json'


class G():
    def __init__(self,gateway_path,gSetupType='vmware',GENESIS_DIR='C:/genesis',gUserName = '1'):
        self.gateway_path = gateway_path
        self.gUserName = gUserName
        command = '{} {}'.format(self.gateway_path,self.gUserName)#“1”是G软件的登录用户名
        if gSetupType == 'vmware':
            command0 = 'SET GENESIS_DIR=C:/Program Files/shareg'
            self.process = subprocess.Popen(command0 + "&" + command, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, shell=True)
        if gSetupType == 'local':
            command0 = 'SET GENESIS_DIR={}'.format(GENESIS_DIR)
            self.process = subprocess.Popen(command0 + "&" + command, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, shell=True)

    def __del__(self):
        os.system('taskkill /f /im gateway.exe')


    def exec_cmd(self, cmd):
        self.process.stdin.write((cmd + '\n').encode())
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        ret = int(line.decode().strip())
        return ret


    def import_odb_folder(self, jobpath,*args,**kwargs):
        print('import job')
        results=[]
        self.jobpath = jobpath
        if "job_name" in kwargs:
            job_name = kwargs['job_name']
        else:
            job_name = os.path.basename(self.jobpath)
        cmd_list = [
            'COM import_job,db=genesis,path={},name={},analyze_surfaces=no'.format(jobpath, job_name.lower()),
        ]
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            results=results.append(ret)
        return results


    def delete_job(self,job_name):
        pass
        cmd_list = [
            'COM close_job,job={}'.format(job_name),
            'COM close_form,job={}'.format(job_name),
            'COM close_flow,job={}'.format(job_name),
            'COM delete_entity,job=,type=job,name={}'.format(job_name),
            'COM close_form,job={}'.format(job_name),
            'COM close_flow,job={}'.format(job_name)
        ]

        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print(ret)
            if ret != 0:
                print('inner error')
                # return
        return "clean finish!"

    def clean_g_all_pre_get_job_list(self,job_list_path):
        pass
        cmd_list = [
            'COM info,args=-t root -m display -d JOBS_LIST,out_file={},write_mode=replace,units=inch'.format(job_list_path)
        ]

        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print(ret)
            if ret != 0:
                print('inner error')
        return "已生成job_list!"

    def clean_g_all_do_clean(self,job_list_path):
        with open(job_list_path, "r") as f:
            s = f.readlines()
        print(s)

        for each_job in s:

            job_name = each_job.split("=")[1]
            self.delete_job(job_name)

        return "clean finish!"

    def Create_Entity(self, job, step):
        print("*"*100,job,step)
        cmd_list1 = [
            # 'COM abc',
            'COM create_entity,job=,is_fw=no,type=job,name={},db=genesis,fw_type=form'.format(job),
            'COM create_entity,job={},is_fw=no,type=step,name={},db=genesis,fw_type=form'.format(job, step),
            'COM save_job,job={},override=no'.format(job)
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print("*"*100,ret)
            if ret != 0:
                print('inner error')
                return False
        return True

    def save_job(self, job):
        print("save")
        results = []

        cmd_list1 = [
            'COM save_job,job={},override=no'.format(job),
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            if ret != 0:
                print('inner error')
                return results

        time.sleep(1)


    def input_init(self, *, job: str,step='orig',gerberList_path:list,jsonPath:str):
        self.job = job
        self.step = step
        self.gerberList_path = gerberList_path
        self.jsonPath = jsonPath
        self.input_set_para_default(self.jsonPath)
        kw = {}
        self.in_put(self.job,self.step,self.gerberList_path,**kw)

    def input_set_para_default(self,jsonPath):
        # 设置默认导入参数
        # with open(r'settings\epvs.json', 'r') as cfg:
        with open(jsonPath, 'r',encoding='utf-8') as cfg:
            self.para = json.load(cfg)['g']['input']  # (json格式数据)字符串 转化 为字典
            print("self.para::",self.para)

    def input_set_para_customer(self,customer_para:dict):
        pass
        print('customer_para:',customer_para)
        for each in customer_para:
            print(each)
            self.para[each] = customer_para[each]
        print(self.para)
        print("cc")


    def in_put(self,job_name, step, gerberList_path,*args,**kwargs):
        # 先创建job, step
        jobpath = r'C:\genesis\fw\jobs' + '/' + job_name
        results = []
        if os.path.exists(jobpath):
            shutil.rmtree(jobpath)
        self.Create_Entity(job_name, step)
        for each in gerberList_path:
            result = {}
            result['gerberPath'] = each["path"]
            result['result'] = self.gerber_to_odb_one_file(each,*args,**kwargs)
            results.append(result)
        self.save_job(self.job)
        return results

    def gerber_to_odb_one_file(self,eachGerberInfo, *args,**kwargs):
        self.para['job'] = self.job
        self.para['step'] = self.step
        self.para['format'] = 'Gerber274x'
        self.para['separator'] = '*'
        self.para['path'] = eachGerberInfo['path']
        self.para['layer'] = os.path.basename(eachGerberInfo['path']).lower()
        self.para['layer']=self.para['layer'].replace(' ','-').replace('(', '-').replace(')', '-')
        print("iamcc",'kwargs:',kwargs)
        file_type = eachGerberInfo["file_type"]


        if file_type == 'excellon':
            print("I am drill")
            self.para['format'] = 'Excellon2'
            if eachGerberInfo.get('para'):
                self.para['zeroes'] = eachGerberInfo['para']['zeroes']
                self.para['nf1'] = eachGerberInfo['para']['nf1']
                self.para['nf2'] = eachGerberInfo['para']['nf2']
                self.para['units'] = eachGerberInfo['para']['units']
                self.para['tool_units'] = eachGerberInfo['para']['tool_units']
                self.para['separator'] = 'nl'
            else:
                self.para['zeroes'] = 'leading'
                self.para['nf1'] = "2"
                self.para['nf2'] = "4"
                self.para['units'] = 'inch'
                self.para['tool_units'] = 'inch'
                self.para['separator'] = 'nl'



        trans_COM = 'COM input_manual_set,'
        trans_COM += 'path={},job={},step={},format={},data_type={},units={},coordinates={},zeroes={},'.format(
            self.para['path'].replace("\\","/"),
            self.para['job'],
            self.para['step'],
            self.para['format'],
            self.para['data_type'],
            self.para['units'],
            self.para['coordinates'],
            self.para['zeroes'])
        trans_COM += 'nf1={},nf2={},decimal={},separator={},tool_units={},layer={},wheel={},wheel_template={},'.format(
            self.para['nf1'],
            self.para['nf2'],
            self.para['decimal'],
            self.para['separator'],
            self.para['tool_units'],
            self.para['layer'],
            self.para['wheel'],
            self.para['wheel_template'])
        trans_COM += 'nf_comp={},multiplier={},text_line_width={},signed_coords={},break_sr={},drill_only={},'.format(
            self.para['nf_comp'],
            self.para['multiplier'],
            self.para['text_line_width'],
            self.para['signed_coords'],
            self.para['break_sr'],
            self.para['drill_only'])
        # trans_COM += 'merge_by_rule={},threshold={},resolution={},drill_type=unknown'.format(
        trans_COM += 'merge_by_rule={},threshold={},resolution={}'.format(
            self.para['merge_by_rule'],
            self.para['threshold'],
            self.para['resolution'])



        cmd_list1 = [
            'COM input_manual_reset',
            trans_COM,
            ('COM input_manual,script_path={}'.format(''))
        ]


        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            if ret != 0:
                print('inner error')
                return False
        return True

    def g_export(self,job,export_to_path,mode_type='tar_gzip'):
        print("导出--开始")
        print("mode_type:",mode_type)
        if mode_type == 'tar_gzip':
            cmd_list1 = [
                'COM export_job,job={},path={},mode=tar_gzip,submode=full,overwrite=yes,analyze_surfaces=no'.format(job,export_to_path.replace('\\','/')),
            ]
        if mode_type == 'directory':
            cmd_list1 = [
                'COM export_job,job={},path={},mode=directory,submode=full,overwrite=yes'.format(job, export_to_path),
            ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)

            if ret != 0:
                print('inner error')
                return False
        print("导出--结束")
        return True

    def get_info_layer_features_first_coor(self,*args,**kwargs):
        print('get_info_layer_features_first_coor')
        results = []
        temp_path_local_g_info_folder = kwargs['temp_path_local_g_info_folder']
        temp_path_remote_g_info_folder = kwargs['temp_path_remote_g_info_folder']
        job = kwargs['job']
        step = kwargs['step']
        layer = kwargs['layer']

        cmd_list = [
            'COM info, out_file={}/{}.txt,args=  -t layer -e {}/{}/{} -m script -d FEATURES'.format(
                temp_path_remote_g_info_folder,layer,job,step,layer),

        ]
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            results.append(ret)

        with open(os.path.join(temp_path_local_g_info_folder,layer + '.txt'), 'r') as f:
            try:
                features_info_first_all_data = f.readlines()[1]
                coor_x = features_info_first_all_data.split(" ")[1].strip()
                coor_y = features_info_first_all_data.split(" ")[2].strip()
                return (coor_x, coor_y)
            except:
                return (0,0)


    def move_one_layer_by_x_y(self, *args,**kwargs):
        print('move_one_layer_by_x_y')
        results=[]
        layer = kwargs['layer']
        dx = kwargs['dx']
        dy = kwargs['dy']

        cmd_list = [
            'COM display_layer,name={},display=yes,number=1'.format(layer),
            'COM work_layer,name={}'.format(layer),
            'COM sel_move,dx={},dy={}'.format(dx,dy),
        ]
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            results.append(ret)

    def layer_compare_g_open_2_job(self, *args,**kwargs):
        print('comare_open_2_job')
        job1 = kwargs['job1']
        step1 = kwargs['step1']
        step2 = kwargs['step2']
        job2 = kwargs['job2']
        cmd_list = [
            'COM check_inout,mode=out,type=job,job={}'.format(job1),
            'COM clipb_open_job,job={},update_clipboard=view_job'.format(job1),
            'COM open_job,job={}'.format(job1),
            'COM open_entity,job={},type=step,name={},iconic=no'.format(job1, step1),
            'COM units,type=inch',
            'COM open_job,job={}'.format(job2),
        ]
        results = []
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            results.append(ret)

    def layer_compare_one_layer(self, *args,**kwargs):
        print("do_comare")
        results_cmd = []
        result = '未比对'#比对结果
        self.job1 = kwargs['job1']
        self.step1 = kwargs['step1']
        self.layer1 = kwargs['layer1']
        self.job2 = kwargs['job2']
        self.step2 = kwargs['step2']
        self.layer2 = kwargs['layer2']
        self.layer2_ext = kwargs['layer2_ext']
        self.tol = kwargs['tol']
        self.map_layer = kwargs['map_layer']
        self.map_layer_res = kwargs['map_layer_res']
        layer_cp = self.layer2 + self.layer2_ext
        result_path_remote = kwargs['result_path_remote']
        result_path_local = kwargs['result_path_local']
        if "layer_type" in kwargs:
            layer_type=kwargs['layer_type']
        else:
            layer_type=""
        temp_path=kwargs['temp_path']
        temp_path_g = kwargs['temp_path_g']

        cmd_list = [
            'COM compare_layers,layer1={},job2={},step2={},layer2={},layer2_ext={},tol={},area=global,consider_sr=yes,ignore_attr=,map_layer={},map_layer_res={}'.format(
                self.layer1, self.job2, self.step2, self.layer2, self.layer2_ext, self.tol, self.map_layer, self.map_layer_res),
            'COM info, out_file={}/{}.txt,args=  -t layer -e {}/{}/{} -m script -d EXISTS'.format(
                result_path_remote,self.layer1,self.job1,self.step1,self.layer1 + self.layer2_ext
            ),
            # 'COM info, out_file={}/{}_com_features_count.txt,args=  -t layer -e {}/{}/{} -m display -d FEAT_HIST\nsource {}/{}_com_features_count.txt'.format(
            #     result_path_remote,self.layer1,self.job1,self.step1,self.layer1+'-com',result_path_remote,self.layer1
            # ),

        ]
        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print('ret:',ret)
            results_cmd.append(ret)
            # if ret == 44011:
            if ret != 0:
                result = '异常'
                return result


        # time.sleep(1)
        # # 先看一下-com层是不是空的，如果是空的说明比对操作失败。
        # with open(os.path.join(result_path_local,self.layer1 + '_com_features_count.txt'), 'r') as f:
        #     comp_result_count = f.readlines()[0].split(",")[-1].strip()
        # if comp_result_count == 'total=0':
        #     print("比对异常！未能比对！")
        #     result = '错误'
        #     return result

        # 再看一下是否存在_copy层，如果存在说明比对结果有差异。通过info功能。
        with open(os.path.join(result_path_local,self.layer1 + '.txt'), 'r') as f:
            comp_result_text = f.readlines()[0].split(" ")[-1].strip()
        if comp_result_text == 'no':
            result = '正常'
        elif comp_result_text == 'yes':
            result = '错误'
            print("第一次比图未通过")
            if layer_type == 'drill' and kwargs['adjust_position']:
                print("再给一次较正孔位置的机会！")
                #先获取坐标，算出偏移量，然后用G移。
                temp_path_local_g_info1_folder = r'{}\info1'.format(temp_path)
                if not os.path.exists(temp_path_local_g_info1_folder):
                    os.mkdir(temp_path_local_g_info1_folder)
                temp_path_remote_g_info1_folder = os.path.join(temp_path_g,'info1')
                temp_path_local_g_info2_folder = r'{}\info2'.format(temp_path)
                if not os.path.exists(temp_path_local_g_info2_folder):
                    os.mkdir(temp_path_local_g_info2_folder)
                temp_path_remote_g_info2_folder = os.path.join(temp_path_g,'info2')
                coor_1 = self.get_info_layer_features_first_coor(job=self.job1, step=self.step1, layer=self.layer1,
                                                              temp_path_local_g_info_folder=temp_path_local_g_info1_folder,
                                                              temp_path_remote_g_info_folder=temp_path_remote_g_info1_folder)
                coor_2 = self.get_info_layer_features_first_coor(job=self.job2, step=self.step2, layer=self.layer2,
                                                                 temp_path_local_g_info_folder=temp_path_local_g_info2_folder,
                                                                 temp_path_remote_g_info_folder=temp_path_remote_g_info2_folder)
                x1 = float(coor_1[0])
                y1 = float(coor_1[1])
                x2 = float(coor_2[0])
                y2 = float(coor_2[1])
                dx = x2 - x1
                dy = y2 - y1
                # print("dx:", dx, "dy:", dy)
                #开始移
                self.move_one_layer_by_x_y(layer=self.layer1, dx=dx, dy=dy)
                print("已经移了孔位置！")
                #再比一次图
                cmd_list = [
                    'COM compare_layers,layer1={},job2={},step2={},layer2={},layer2_ext={},tol={},area=global,consider_sr=yes,ignore_attr=,map_layer={},map_layer_res={}'.format(
                        self.layer1, self.job2, self.step2, self.layer2, "_copy2", self.tol, self.map_layer,
                        self.map_layer_res),
                    'COM info, out_file={}/{}_2.txt,args=  -t layer -e {}/{}/{} -m script -d EXISTS'.format(
                        result_path_remote, self.layer1, self.job1, self.step1, self.layer1 + "_copy2"
                    ),
                ]
                for cmd in cmd_list:
                    print(cmd)
                    ret = self.exec_cmd(cmd)
                    results_cmd.append(ret)

                with open(os.path.join(result_path_local, self.layer1 + '_2.txt'), 'r') as f:
                    comp_result_text = f.readlines()[0].split(" ")[-1].strip()
                if comp_result_text == 'no':
                    result = '正常'
                elif comp_result_text == 'yes':
                    result = '错误'

                print("第二次比图结束！结果是：",result)

        print("比对结果：",result)
        return result

    def layer_compare_close_job(self, *args,**kwargs):
        results = []
        self.job1 = kwargs['job1']
        self.job2 = kwargs['job2']

        cmd_list1 = [
            'COM editor_page_close',
            'COM check_inout,mode=out,type=job,job={}'.format(self.job1),
            'COM close_job,job={}'.format(self.job1),
            'COM close_form,job={}'.format(self.job1),
            'COM close_flow,job={}'.format(self.job1),

            'COM close_job,job={}'.format(self.job2),
            'COM close_form,job={}'.format(self.job2),
            'COM close_flow,job={}'.format(self.job2)
        ]

        cmd_list2 = [
        ]

        for cmd in cmd_list1:
            print(cmd)
            ret = self.exec_cmd(cmd)
            if ret != 0:
                print('inner error')
                return results
        time.sleep(1)

    def layer_compare(self,*args,temp_path,temp_path_g,job1,step1='orig',job2,step2='orig',layerInfo,
                      adjust_position=False,jsonPath,
                      **kwargs):
        global g_vs_total_result_flag
        adjust_position = adjust_position


        data_g = {}
        g_vs_total_result_flag = True  # True表示最新一次G比对通过
        # 读取配置文件
        with open(jsonPath, encoding='utf-8') as f:
            cfg = json.load(f)
        tol = cfg['g']['vs']['vs_tol_g']
        map_layer_res = cfg['g']['vs']['map_layer_res']


        # G打开要比图的2个料号

        g_compare_result_folder = job1 + '_compare_result'
        temp_g_compare_result_path = os.path.join(temp_path, g_compare_result_folder)
        if not os.path.exists(temp_g_compare_result_path):
            os.mkdir(temp_g_compare_result_path)

        # temp_path_remote_g_compare_result = os.path.join(temp_path_vm_parent,os.path.basename(temp_path),g_compare_result_folder)
        temp_path_remote_g_compare_result = os.path.join(temp_path_g, g_compare_result_folder)

        temp_path_local_g_compare_result = os.path.join(temp_path, g_compare_result_folder)





        all_result_g = {}
        for each in layerInfo:
            layer = each['layer'].lower()
            layer_type = each['layer_type']
            map_layer = layer + '-com'
            result = self.layer_compare_one_layer(job1=job1, step1=step1, layer1=layer, job2=job2,
                                               step2=step2, layer2=layer, layer2_ext='_copy', tol=tol,
                                               map_layer=map_layer, map_layer_res=map_layer_res,
                                               result_path_remote=temp_path_remote_g_compare_result,
                                               result_path_local=temp_path_local_g_compare_result,
                                               layer_type=layer_type,adjust_position=adjust_position,
                                                  temp_path=temp_path,temp_path_g=temp_path_g)
            all_result_g[layer] = result
            if result != "正常":
                g_vs_total_result_flag = False

        data_g['all_result_g'] = all_result_g
        data_g['g_vs_total_result_flag'] = g_vs_total_result_flag
        self.save_job(job1)
        self.save_job(job2)
        self.layer_compare_close_job(job1=job1, job2=job2)

        return data_g

    def input_reset(self,job_name):
        '''没写好，还要研究'''
        cmd_list = [
            # 'COM close_job,job={}'.format(job_name),
            # 'COM close_form,job={}'.format(job_name),
            # 'COM close_flow,job={}'.format(job_name),
            'COM input_manual_reset',
            'COM input_manual,script_path='
        ]

        for cmd in cmd_list:
            print(cmd)
            ret = self.exec_cmd(cmd)
            print(ret)
            if ret != 0:
                print('inner error')
                # return
        return "input reset finish!"


def test():
    g = G(r"C:\cc\python\epwork\epvs\config_g\bin\gateway.exe",gSetupType='vmware')

    #删除所有料号
    g.clean_g_all_pre_get_job_list(r'//vmware-host/Shared Folders/share/job_list.txt')
    g.clean_g_all_do_clean(r'C:\cc\share\job_list.txt')

    g.import_odb_folder(r'C:\temp\biz22351_ep')

    job_name = 'test'
    step = 'orig'
    gerberList_path = [{"path":r"C:\temp\gerber\nca60led\Polaris_600_LED.DRD","file_type":"excellon"},
                       {"path":r"C:\temp\gerber\nca60led\Polaris_600_LED.TOP","file_type":"gerber"}]
    out_path_g = r'Z:\share\g\output'
    g.input_init(job=job_name, step=step, gerberList_path=gerberList_path,jsonPath=r'../settings/epvs.json')
    # 输出tgz到指定目录
    g.g_export(job_name, out_path_g,mode_type='directory')

def test_compare():
    temp_path = r"C:\cc\share\1682591221_test"
    # self.temp_path = os.path.join(r"C:\cc\share", self.vs_time + '_' + self.jobName)
    g1_compare_result_folder = 'g1_compare_result'
    temp_g1_compare_result_path = os.path.join(temp_path, g1_compare_result_folder)
    if not os.path.exists(temp_g1_compare_result_path):
        os.mkdir(temp_g1_compare_result_path)


    g = G(r"C:\cc\python\epwork\epvs\config_g\bin\gateway.exe")

    layerInfo=[{'layer':'polaris_600_led.drd','layer_type':'drill'},{'layer':'polaris_600_led.top','layer_type':''}]

    g.layer_compare_g_open_2_job(job1="test",step1='orig',job2="test",step2='orig')
    res = g.layer_compare(vs_time_g='1682591221',temp_path=temp_path,
                    job1="test",step1='orig',
                    job2="test2",step2='orig',
                    layerInfo=layerInfo)
    print(res)

if __name__ == '__main__':
    pass
    test()
    # test_compare()

