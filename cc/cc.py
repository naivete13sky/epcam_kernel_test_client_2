import os

info_path_g = r'C:\cc\share\epcam_kernel\info_layer'
job_name = '6377306a_panel_edit_g2'
step_name = 'edit'

with open(os.path.join(info_path_g, job_name, step_name + '.txt'), 'r') as file:
    content = file.read()
print(content)


text = "set gLAYERS_LIST = ('rout' 'rolb' 'ldi-b' 'ldi' 'l5-1' 'l5' 'l4' 'l3' 'l2-1' 'l2' 'gtl' 'gbs' 'gbl' 'drl5-6' '306-drl2-5' '2-5-ldi' '1.l5' '1.l4' '1.l3' '1.l2' '1.gbs' '1.gbl' '1.56.drl' '1.25.drl')"

# 使用正则表达式提取字符串
import re
pattern = r"'(.*?)'"
matches = re.findall(pattern, text)

# 创建列表
layers_list = list(matches)

# 打印列表
print(layers_list)
