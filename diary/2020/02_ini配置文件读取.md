# ini配置文件的读取

实际就是使用了第三方库 configparser ，使用的方法也很简单，下面用例子展开。值得注意的是，如果获取一个不存在的 options 时，会抛出异常而不是返回一个 None 类型。  

所有'[]'包含的内容是 section ，具体配置名称是一个 option .  

```conf
[yuling]
times=400
type=dragon
layer=3
```

代码见：  
[config.ini](../../src/config/config.ini)  
[jupyter_config.py](../../src/config/../conf/jupyter_config.py)  

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# %% 加载基础库
import configparser
import os
import sys

cur_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
#conf_path = os.path.join(cur_dir, 'config.ini')
conf_path = os.path.abspath(r'F:\gitee\knowledge\Python\yys_script\src\conf\config.ini')

# %% 打开config文件，要以utf-8的方式打开，否则中文乱码
config = configparser.RawConfigParser()
config.read(conf_path, encoding='utf-8')


# %% sections options
sections = config.sections()  # [str]
general_options = config.options('general')   # [str]
print(sections, general_options)

# %% 测试获取值
print(config.get('general', 'title'))
print(config.getint('yuhun', 'players'))

# %% 测试设置值
config.set('yuhun', 'players', '3')
print(config.getint('yuhun', 'players'))
```
