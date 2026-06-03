# 雷石 K 歌智能助手 - 快速启动脚本
# PowerShell 5 脚本

Write-Host "🎤 雷石 K 歌智能助手" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# 检查 Python
Write-Host "`n1. 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ 发现 $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ 未找到 Python，请先安装 Python 3.8+" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查 .env 文件
Write-Host "`n2. 检查配置文件..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "   未找到 .env 文件，正在从 .env.example 创建..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "   ✓ 已创建 .env 文件" -ForegroundColor Green
    Write-Host "   ⚠ 请编辑 .env 文件，填写您的 ZHIPUAI_API_KEY" -ForegroundColor Magenta
    Write-Host "   获取 API Key: https://open.bigmodel.cn/" -ForegroundColor Cyan
    $choice = Read-Host "`n是否继续？(Y/N)"
    if ($choice -ne "Y" -and $choice -ne "y") {
        exit 0
    }
} else {
    Write-Host "   ✓ 找到 .env 文件" -ForegroundColor Green
}

# 检查依赖
Write-Host "`n3. 检查依赖..." -ForegroundColor Yellow
try {
    python -c "import streamlit, pymilvus, sentence_transformers" 2>&1 | Out-Null
    Write-Host "   ✓ 依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "   正在安装依赖..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ 依赖安装成功" -ForegroundColor Green
    } else {
        Write-Host "   ✗ 依赖安装失败，请手动运行: pip install -r requirements.txt" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
}

# 检查向量数据库
Write-Host "`n4. 检查向量数据库..." -ForegroundColor Yellow
$dbPath = "milvus_db\milvus_demo.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "   向量数据库不存在，正在构建..." -ForegroundColor Yellow
    Write-Host "   (首次运行需要下载 BGE 模型，可能需要几分钟)" -ForegroundColor Cyan
    python milvus_db\milvus_lite.py --build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ 向量数据库构建成功" -ForegroundColor Green
    } else {
        Write-Host "   ✗ 向量数据库构建失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
} else {
    Write-Host "   ✓ 向量数据库已存在" -ForegroundColor Green
}

# 启动 Streamlit
Write-Host "`n5. 启动应用..." -ForegroundColor Yellow
Write-Host "`n🎉 应用即将启动！" -ForegroundColor Green
Write-Host "浏览器将自动打开 http://localhost:8501" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "`n==========================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 2
streamlit run web\app.py
