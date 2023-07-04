# -*- coding:utf-8 -*-
import os
import sys

base_path = os.path.dirname(__file__)


def get_insert_lines(data: dict, key: str, level: int):
    result = []

    if key in data:
        target = data[key]

        if isinstance(target, list):
            for d in target:
                space_count = level
                if d:
                    # print("add line = %s" % d)
                    while space_count > 0:
                        result.append("    ")
                        space_count = space_count - 1
                    result.append(d)
                    result.append("\n")
        else:
            # print("add line = %s" % target)
            while level > 0:
                result.append("    ")
                level = level - 1
            result.append(target)
            result.append("\n")

    return result


def insert(path: str, data):
    """
    自动打包时为引入本地 gradle 插件，需要更改 gradle 相关配置，暂时通过该脚本直接修改文件。
    注意:
        调用时不会做内容检测，多次调用会重复插入。
        "{" 与 "}" 在同一行时不会进行插入

    :param path: .gradle 文件路径
    :param data: 匹配规则与要插入的数据，会在末尾插入。
    :return: None
    """
    if not path or not data:
        print("invalid param: path or data is null")
        return

    if not path.strip().endswith("gradle"):
        print("invalid param: path is not a build.gradle file")
        return

    if not os.path.exists(path):
        print("invalid param: path is not exists. path = %s " % path)
        return

    lines = []
    with open(path, mode="r", encoding="utf-8") as f:
        line = f.readline()
        max_space_line = 10
        space_line = 1 if not line else 0

        g_path_stack = []

        while line.strip() or space_line < max_space_line:

            if not line.strip():
                space_line = space_line + 1
                lines.append(line)
                line = f.readline()

                if space_line + 1 == max_space_line:
                    # 外层配置
                    tmp = get_insert_lines(data, "null", 0)
                    if len(tmp) > 0:
                        lines.append("\n")
                        lines.extend(tmp)

                continue
            else:
                if space_line > 0:
                    # 非连续空行这里重置为0
                    space_line = 0

            # { } 在同一行不处理
            if "{" in line and "}" in line:
                lines.append(line)
            elif "{" not in line and "}" not in line:
                lines.append(line)
            else:
                if "{" in line:
                    g_path_stack.append(line.replace("{", "").strip())
                    lines.append(line)
                elif "}" in line:
                    full_b_path = ".".join(g_path_stack)
                    lines.extend(get_insert_lines(data, full_b_path, len(g_path_stack)))
                    g_path_stack.pop()
                    lines.append(line)

            line = f.readline()

    # print("new lines = %s" % lines)

    with open(path, mode="w", encoding="utf-8") as f:
        f.writelines(lines)

