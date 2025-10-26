from __future__ import annotations
from typing import Iterable
import os


def must_input() -> str:
    """
    要求用户必须输入一个合法的字符串（去除首尾空白后非空）。
    不捕获 Ctrl+C（KeyboardInterrupt），由调用环境自然退出。
    """
    while True:
        s = input()
        s = s.strip()
        if s:
            return s
        else:
            print("输入不能为空，请重新输入：")
            continue


def must_input_list(options: Iterable[str]) -> str:
    """
    要求用户必须输入一个在 options 中的字符串（比较基于去除首尾空白后的值）。
    不捕获 Ctrl+C（KeyboardInterrupt）。
    """
    opts = {str(o) for o in options}
    while True:
        s = input()
        s = s.strip()
        if s and s in opts:
            return s
        else:
            print(f"输入不合法，请输入以下选项之一：{', '.join(opts)}")
            continue


def must_input_absolute_path(*, must_exist: bool = False, must_non_exst: bool = False) -> str:
    """
    要求用户必须输入一个路径：
    - must_exist=True 时，该路径必须存在；
    - must_non_exst=True 时，该路径必须不存在。
    两者不能同时为 True，且至少一个应为 True。
    输入不合法时会继续要求输入；不捕获 Ctrl+C。
    返回展开了 ~ 与环境变量的路径字符串。
    """
    if must_exist and must_non_exst:
        raise ValueError("must_exist and must_non_exst cannot both be True")
    if not must_exist and not must_non_exst:
        raise ValueError("one of must_exist or must_non_exst must be True")

    while True:
        p = input()
        p = p.strip()
        if not p:
            print("输入不能为空，请重新输入：")
            continue
        expanded = os.path.expandvars(os.path.expanduser(p))
        if not os.path.isabs(expanded):
            print("路径必须是绝对路径，请重新输入：")
            continue
        exists = os.path.exists(expanded)
        if must_exist and exists:
            return expanded
        elif must_non_exst and not exists:
            return expanded
        elif must_exist and not exists:
            print("路径不存在，请重新输入：")
        elif must_non_exst and exists:
            print("路径已存在，请重新输入：")
