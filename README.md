# openlab-2026

OpenLab 2026 秋季笔试提交仓库。

本仓库包含第 7 题（Brainfuck「魔术书」）的作答程序与验证解释器，
以及第 2 题要求的 Git 规范实践（目录结构、.gitignore、分支合并、语义化提交信息）。

## 目录结构

```
openlab-2026/
├── src/                    # 源代码
│   ├── hello.py            # Python 环境自检
│   ├── bf-interpreter.ps1  # Brainfuck 解释器（Windows PowerShell）
│   └── bf-programs.txt     # 第 7 题三段程序与预期输出
├── docs/                   # 文档
├── res/                    # 资源文件
├── README.md
└── .gitignore
```

## 怎么跑

### 1. Python 自检

```bash
python src/hello.py
```

### 2. Brainfuck 解释器（第 7 题）

Windows PowerShell 中执行：

```powershell
$src = Get-Content -Raw -Encoding UTF8 .\src\bf-interpreter.ps1
Invoke-Expression $src
```

会依次跑三组用例，打印每一步的磁带状态和输出字符。

> 说明：不能直接 `& .\src\bf-interpreter.ps1`，Windows 默认执行策略会拦截脚本文件，
> 用 `Invoke-Expression` 读进内存执行可以绕开这个限制。

## 关于第 7 题

题面给出的注释「读入一个字符，若这个字符不为 0 则输出该字符」**与实际行为不符**：

程序 `,[ >+ <-] >-.` 的循环在做「把 cell0 的值搬到 cell1」，
循环结束时 cell1 等于输入字符的 ASCII 码，随后 `-` 减一，`.` 输出。

所以实际输出是**输入字符的 ASCII 码减 1**：

| 输入 | ASCII | 输出 | ASCII |
|------|-------|------|-------|
| A    | 65    | @    | 64    |
| Z    | 90    | Y    | 89    |
| b    | 98    | a    | 97    |

## 分支说明

- `main`：主分支
- `feature/bf-interpreter`：第 7 题解释器开发分支，已合并回 main

## 许可

仅用于本次笔试提交。
