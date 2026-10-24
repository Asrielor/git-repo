#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hello.py —— 环境自检，顺便验证仓库能正常 clone 下来跑。"""

import platform
import sys


def main():
    print("OpenLab 2026")
    print("-" * 30)
    print(f"Python : {sys.version.split()[0]}")
    print(f"系统   : {platform.system()} {platform.release()}")
    print(f"架构   : {platform.machine()}")


if __name__ == "__main__":
    main()
