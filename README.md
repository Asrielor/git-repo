# openlab-2026

OpenLab 2026 笔试提交仓库，对应三部分内容：第 2 题的 Git 用法、第 4 题的命令行工具、第 7 题的 Brainfuck 程序。

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

## 第 2 题：Git 用法

- 代码放 `src` 和 `tools`，文档放 `docs`，资源放 `res`
- `.gitignore` 排除编译产物、编辑器配置、模型权重、运行时数据
- 两个功能各开一个分支，用 `--no-ff` 合并回 `main`
- 提交信息用 `chore`、`feat`、`fix` 前缀
- 仓库控制在 10MB 以内，不放二进制文件

## 第 4 题：todo-cli

单文件 Python 命令行待办清单，无第三方依赖，在 DeepSeek 会话里生成。

```bash
cd tools/todo-cli
python todo.py add "写作业"
python todo.py list
python todo.py done 1
python todo.py rm 1
```

数据存在同目录 `todos.json`，已排除在版本库外。三个设计点：

1. 写文件先写 `todos.json.tmp` 再 `os.replace` 覆盖，避免写到一半留下半截文件
2. 数据路径用 `__file__` 拼绝对路径，从任何目录运行都读同一份
3. `done` 和 `rm` 遇到不存在的 id 返回 1，方便脚本串联

文件读坏时打印错误并按空清单继续。

## 第 7 题：Brainfuck

题面注释是错的。`,[ >+ <-] >-.` 的循环是把第一格的值搬到第二格，结束时第二格等于输入字符的 ASCII 码，再减 1 输出。

| 输入 | ASCII | 输出 | ASCII |
|---|---|---|---|
| A | 65 | @ | 64 |
| Z | 90 | Y | 89 |
| b | 98 | a | 97 |

第二段 `++++++++++ [ >++++++++ >++++++++ <<-] >-. >.` 输出 `OP`，两格都是 8×10=80。

我的解答 `,>,<[->+<]>.`：读两个字符，把第一格搬到第二格，输出和。

运行解释器：

```powershell
$src = Get-Content -Raw -Encoding UTF8 .\src\bf-interpreter.ps1
Invoke-Expression $src
```

直接 `& .\src\bf-interpreter.ps1` 会被执行策略拦住，所以用 Invoke-Expression 读进内存跑。

## 分支

- `main`
- `feature/bf-interpreter`
- `feature/todo-cli`
