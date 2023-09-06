import json
import os.path


class RunConfig:
    """
    运行测试配置
    """

    #配置EPCAM路径，只要换了版本就要更改
    with open(os.path.join(os.path.dirname(__file__),r'my_config.json'), encoding='utf-8') as f:
        cfg = json.load(f)

    ep_cam_path = cfg['epcam']['path']
    dms_ip = cfg['dms']['ip']






    # 运行测试用例的目录或文件
    cases_path = "./test_dir/"

    # 配置浏览器驱动类型(chrome/firefox/chrome-headless/firefox-headless)。
    # driver_type = "chrome"

    # EPCAM驱动类型
    driver_type = "epcam"

    #悦谱python接口目录
    epcam_python_interface_path = r'config_ep/epcam'


    # 配置运行的 URL
    url = "http://www.epsemicon.com/"

    # 失败重跑次数
    rerun = "0"

    # 当达到最大失败数，停止执行
    max_fail = "300"

    # 浏览器驱动（不需要修改）
    driver = None

    # epcam驱动（不需要修改）
    driver_epcam = None

    # g驱动类型
    driver_type_g = "g"

    # g驱动（不需要修改）
    driver_g = None

    # 报告路径（不需要修改）
    NEW_REPORT = None

    # 当前执行电脑的临时目录
    temp_path_base = r'C:\cc\share\temp'

    # 悦谱出gerber的配置默认參數
    config_ep_output = r'config_ep\outcfg.json'

    # 调用G的管道
    gateway_path = r'config_g\bin\gateway.exe'

    # g软件导入默认参数
    config_g_input = r'config_g\config.json'


    # test_item = ['1','2','3','4','5','6','7']
    test_item = ['1', '2', '3']


