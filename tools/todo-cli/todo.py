#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单文件、零第三方依赖的命令行待办清单。

用法:
    python todo.py add 买牛奶 买鸡蛋
    python todo.py list
    python todo.py done 1
    python todo.py rm 1

数据保存在本脚本同目录的 todos.json 中。
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime

# 固定放在脚本所在目录，避免受当前工作目录影响
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")
TMP_PREFIX = ".todos-"
TMP_SUFFIX = ".tmp"


# --------------------------------------------------------------------------- #
# 读取
# --------------------------------------------------------------------------- #
def _warn(msg):
    print(msg, file=sys.stderr)


def _backup_corrupt_file():
    """把读不动的数据文件改名备份，返回备份路径（失败返回 None）。"""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = "{}.corrupt-{}".format(DATA_FILE, stamp)
    path, n = base, 1
    while os.path.exists(path):
        n += 1
        path = "{}-{}".format(base, n)
    try:
        os.replace(DATA_FILE, path)
        return path
    except OSError:
        return None


def _load_failed(reason, can_backup):
    _warn("警告：读取 {} 失败（{}）。".format(DATA_FILE, reason))
    if can_backup:
        backup = _backup_corrupt_file()
        if backup:
            _warn("      原文件已备份为 {}，本次按空清单处理。".format(backup))
        else:
            _warn("      无法备份原文件，本次按空清单处理。")
    else:
        _warn("      本次按空清单处理。")


def _normalize(item):
    if not isinstance(item, dict):
        raise ValueError("条目不是 JSON 对象：{!r}".format(item))
    if "id" not in item or "text" not in item:
        raise ValueError("条目缺少 id 或 text 字段：{!r}".format(item))
    return {
        "id": int(item["id"]),
        "text": str(item["text"]),
        "done": bool(item.get("done", False)),
    }


def load_todos():
    """读取待办列表；文件不存在或损坏时返回空列表，绝不抛异常。"""
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        _load_failed("JSON 解析错误：{}".format(exc), can_backup=True)
        return []
    except (OSError, UnicodeDecodeError) as exc:
        _load_failed("{}: {}".format(type(exc).__name__, exc), can_backup=False)
        return []

    if not isinstance(raw, list):
        _load_failed(
            "顶层应为数组，实际是 {}".format(type(raw).__name__), can_backup=True
        )
        return []

    todos = []
    for index, item in enumerate(raw):
        try:
            todos.append(_normalize(item))
        except (TypeError, ValueError) as exc:
            _load_failed(
                "第 {} 条数据无效（{}）".format(index + 1, exc), can_backup=True
            )
            return []
    return todos


# --------------------------------------------------------------------------- #
# 写入（原子替换）
# --------------------------------------------------------------------------- #
def _fsync_dir(directory):
    """尽量把目录项也刷盘；不支持的平台直接忽略。"""
    try:
        dir_fd = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(dir_fd)
    except OSError:
        pass
    finally:
        os.close(dir_fd)


def save_todos(todos):
    """先写同目录临时文件 → fsync → os.replace 原子替换。"""
    directory = os.path.dirname(DATA_FILE) or "."
    fd, tmp_path = tempfile.mkstemp(
        dir=directory, prefix=TMP_PREFIX, suffix=TMP_SUFFIX
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(todos, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, DATA_FILE)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    _fsync_dir(directory)


def _save_or_report(todos):
    try:
        save_todos(todos)
        return True
    except OSError as exc:
        _warn("错误：写入 {} 失败：{}".format(DATA_FILE, exc))
        return False


# --------------------------------------------------------------------------- #
# 子命令
# --------------------------------------------------------------------------- #
def _find(todos, todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            return todo
    return None


def cmd_add(args):
    text = " ".join(args.text).strip()
    if not text:
        _warn("错误：待办内容不能为空。")
        return 2
    todos = load_todos()
    new_id = max((t["id"] for t in todos), default=0) + 1
    todos.append({"id": new_id, "text": text, "done": False})
    if not _save_or_report(todos):
        return 1
    print("已添加 #{}：{}".format(new_id, text))
    return 0


def cmd_list(args):
    todos = load_todos()
    if not todos:
        print("（暂无待办）")
        return 0

    id_width = max(len(str(t["id"])) for t in todos)
    for todo in todos:
        box = "x" if todo["done"] else " "
        print("[{}] #{:>{}}  {}".format(box, todo["id"], id_width, todo["text"]))

    total = len(todos)
    done = sum(1 for t in todos if t["done"])
    print("\n共 {} 条，已完成 {} 条，未完成 {} 条。".format(total, done, total - done))
    return 0


def cmd_done(args):
    todos = load_todos()
    todo = _find(todos, args.id)
    if todo is None:
        _warn("错误：找不到 id 为 {} 的待办。".format(args.id))
        return 1
    if todo["done"]:
        print("#{} 已经是完成状态。".format(args.id))
        return 0
    todo["done"] = True
    if not _save_or_report(todos):
        return 1
    print("已完成 #{}：{}".format(args.id, todo["text"]))
    return 0


def cmd_rm(args):
    todos = load_todos()
    todo = _find(todos, args.id)
    if todo is None:
        _warn("错误：找不到 id 为 {} 的待办。".format(args.id))
        return 1
    todos.remove(todo)
    if not _save_or_report(todos):
        return 1
    print("已删除 #{}：{}".format(args.id, todo["text"]))
    return 0


# --------------------------------------------------------------------------- #
# 入口
# --------------------------------------------------------------------------- #
def build_parser():
    parser = argparse.ArgumentParser(
        prog="todo",
        description="单文件命令行待办清单（数据存于脚本同目录的 todos.json）",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    p_add = sub.add_parser("add", help="添加一条待办")
    p_add.add_argument(
        "text",
        nargs="+",
        metavar="内容",
        help="待办内容；内容以 - 开头时用 -- 分隔，如：add -- -5度",
    )
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="列出全部待办")
    p_list.set_defaults(func=cmd_list)

    p_done = sub.add_parser("done", help="把某条待办标记为完成")
    p_done.add_argument("id", type=int, metavar="ID")
    p_done.set_defaults(func=cmd_done)

    p_rm = sub.add_parser("rm", help="删除某条待办")
    p_rm.add_argument("id", type=int, metavar="ID")
    p_rm.set_defaults(func=cmd_rm)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help(sys.stderr)
        return 2
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())