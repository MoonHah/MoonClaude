"""打印版本号
"""


import moon_claude


# 打印当前 moon_claude 包的版本号
def cmd_version() -> None:
    print(moon_claude.__version__)
