# install.ps1 — 安装 cli-novel-writer 到 Claude Skills 目录。
# 用法: powershell -ExecutionPolicy Bypass -File install.ps1 [-Target <目标目录>]
param(
    [string]$Target = (Join-Path $HOME '.claude\skills\cli-novel-writer')
)
$src = Split-Path -Parent $MyInvocation.MyCommand.Path
$files = @('SKILL.md', 'README.md', 'LICENSE', 'scripts\count_cjk.py')
$copied = 0
$skipped = 0
foreach ($rel in $files) {
    $s = Join-Path $src $rel
    $d = Join-Path $Target $rel
    if (-not (Test-Path $s)) {
        Write-Host "仓库中缺失文件: $rel"
        continue
    }
    New-Item -ItemType Directory -Force (Split-Path -Parent $d) | Out-Null
    if (Test-Path $d) {
        Write-Host "已存在，跳过: $rel"
        $skipped++
    } else {
        Copy-Item $s $d
        $copied++
    }
}
Write-Host "安装完成: $copied 个文件复制, $skipped 个跳过。目标: $Target"
