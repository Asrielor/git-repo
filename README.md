# openlab-2026

OpenLab 2026 秋季笔试提交仓库。内容对应三部分：

- 第 2 题：本仓库的 Git 使用方式（目录结构、.gitignore、分支、提交信息）
- 第 4 题：`tools/todo-cli/` 命令行待办清单
- 第 7 题：`src/` 下的 Brainfuck 程序与解释器

## 目录

```
openlab-2026/
├── src/
│   ├── hello.py              Python 环境自检
│   ├── bf-interpreter.ps1    Brainfuck 解释器（PowerShell）
│   └── bf-programs.txt       第 7 题三段程序
├── tools/
│   └── todo-cli/
│       └── todo.py           第 4 题命令行工具
├── docs/
├── res/
├── README.md
└── .gitignore
```

## 第 2 题：Git 实践

- 代码放 `src/` 和 `tools/`，文档放 `docs/`，资源放 `res/`，不混在一起
- `.gitignore` 排除编译产物、编辑器配置、模型权重（`*.gguf`）、运行时数据（`todos.json`）
- 两个功能各开一个分支，用 `--no-ff` 合并回 `main`，保留分叉结构
- 提交信息统一前缀：`chore`（初始化）、`feat`（新功能）、`fix`（修 bug）
- 仓库体积控制在 10MB 以内，不放二进制文件

## 第 4 题：todo-cli

单文件 Python 命令行待办清单，无第三方依赖，在 DeepSeek 会话中生成后整理提交。

```
cd tools/todo-cli
python todo.py add "写作业"
python todo.py list
python todo.py done 1
python todo.py rm 1
```

数据存在脚本同目录的 `todos.json`（已在 .gitignore 中排除）。三个关键点：

1. **原子写入**：先写 `todos.json.tmp`，再 `os.replace()` 覆盖。直接覆盖的话，写一半断电会留下半截 JSON。
2. **路径锚定**：数据路径用 `__file__` 拼绝对路径，从任何目录运行都读同一份数据。
3. **退出码**：`done` / `rm` 遇到不存在的 id 返回 1，这样 `todo.py done 99 && echo ok` 不会执行 `ok`。

文件读坏时打印错误并按空清单继续，不会抛 traceback。

## 第 7 题：Brainfuck

题面给的注释是错的。程序 `,[ >+ <-] >-.` 的循环是把第一格的值搬到第二格，
循环结束时第二格等于输入字符的 ASCII 码，然后 `-` 减一才输出。

所以实际输出是输入字符的 ASCII 码减 1：

| 输入 | ASCII | 输出 | ASCII |
|---|---|---|---|
| A | 65 | @ | 64 |
| Z | 90 | Y | 89 |
| b | 98 | a | 97 |

第二段 `++++++++++ [ >++++++++ >++++++++ <<-] >-. >.` 输出 `OP`，两个格子都是 8×10=80。

我的解答 `,>,<[->+<]>.`：读两个字符，把第一格的值搬到第二格，输出和。

运行解释器：

```powershell
$src = Get-Content -Raw -Encoding UTF8 .\src\bf-interpreter.ps1
Invoke-Expression $src
```

直接 `& .\src\bf-interpreter.ps1` 会被 Windows 执行策略拦住，所以用 Invoke-Expression 读进内存跑。

## 分支

- `main`：主分支
- `feature/bf-interpreter`：第 7 题解释器
- `feature/todo-cli`：第 4 题工具
