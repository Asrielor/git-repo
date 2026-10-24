# 第7题用的 Brainfuck 解释器（Windows PowerShell，无需安装任何东西）
#
# 用法：
#   $src = Get-Content -Raw -Encoding UTF8 .\验证_BF模拟器.ps1
#   Invoke-Expression $src
#
# 说明：直接 & .\xxx.ps1 可能被执行策略拦住，用上面的 Invoke-Expression 方式最省事。

function Invoke-BF {
    param([string]$Code, [string]$InputText = "")

    $tape = New-Object 'int[]' 30000
    $ptr = 0
    $inPos = 0
    $out = New-Object System.Text.StringBuilder

    # 预处理：为每个 [ 找到匹配的 ]，双向建立跳转表（避免运行时逐字符找括号）
    $jump = @{}
    $stack = New-Object System.Collections.Stack
    for ($i = 0; $i -lt $Code.Length; $i++) {
        if ($Code[$i] -eq '[') { $stack.Push($i) }
        elseif ($Code[$i] -eq ']') { $j = $stack.Pop(); $jump[$j] = $i; $jump[$i] = $j }
    }

    $ip = 0; $steps = 0
    while ($ip -lt $Code.Length) {
        $steps++
        if ($steps -gt 50000000) { throw "步数超限（疑似死循环）" }
        switch -CaseSensitive ($Code[$ip]) {
            '>' { $ptr++ }
            '<' { $ptr-- }
            '+' { $tape[$ptr] = ($tape[$ptr] + 1) % 256 }      # 8 位回绕
            '-' { $tape[$ptr] = ($tape[$ptr] + 255) % 256 }    # 0 减 1 得 255
            '.' {
                $v = $tape[$ptr]
                [void]$out.Append([char]$v)
                Write-Host ("    输出: 数值 " + $v + "  ->  字符 [" + [char]$v + "]")
            }
            ',' {
                if ($inPos -lt $InputText.Length) { $tape[$ptr] = [int][char]$InputText[$inPos]; $inPos++ }
                else { $tape[$ptr] = 0 }
            }
            '[' { if ($tape[$ptr] -eq 0) { $ip = $jump[$ip] } }
            ']' { if ($tape[$ptr] -ne 0) { $ip = $jump[$ip] } }
        }
        $ip++
    }
    Write-Host ("    结束磁带: [" + (($tape[0..5]) -join ', ') + "]")
}

Write-Host "=== 题1: ,[ >+ <-] >-.   输入 'A'(65) ==="
Invoke-BF -Code ',[ >+ <-] >-.' -InputText 'A'

Write-Host "=== 题1: 输入 'Z'(90) ==="
Invoke-BF -Code ',[ >+ <-] >-.' -InputText 'Z'

Write-Host "=== 题1: 输入 'b'(98) ==="
Invoke-BF -Code ',[ >+ <-] >-.' -InputText 'b'

Write-Host ""
Write-Host "=== 题1 边界: 输入 0（模拟 EOF）——验证 0-1 下溢为 255 ==="
Invoke-BF -Code ',[ >+ <-] >-.' -InputText ''

Write-Host ""
Write-Host "=== 题2: ++++++++++ [ >++++++++ >++++++++ <<-] >-. >.  (无输入) ==="
Invoke-BF -Code '++++++++++ [ >++++++++ >++++++++ <<-] >-. >.'

Write-Host ""
Write-Host "=== 题3 我的解答: ,>,<[->+<]>.   输入 'A!'(65+33=98) ==="
Invoke-BF -Code ',>,<[->+<]>.' -InputText 'A!'

Write-Host "=== 题3: 输入 '0 '(48+32=80) ==="
Invoke-BF -Code ',>,<[->+<]>.' -InputText '0 '

Write-Host "=== 题3: 输入 'AZ'(65+90=155，不可打印) ==="
Invoke-BF -Code ',>,<[->+<]>.' -InputText 'AZ'

Write-Host "=== 题3: 输入 'ZZ'(90+90=180，不可打印) ==="
Invoke-BF -Code ',>,<[->+<]>.' -InputText 'ZZ'
