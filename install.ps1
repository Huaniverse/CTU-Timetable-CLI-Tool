# ============================================================
# HUANIVERSE TIMETABLE TOOL - INSTALLER (FLAT STRUCTURE)
# ============================================================

# 1. CAU HINH THONG TIN 
# ------------------------------------------------------------
$RepoUser = "Huaniverse"  
$RepoName = "CTU-Timetable-CLI-Tool"        
# ------------------------------------------------------------

# Cau hinh duong dan
$InstallDir = "$env:USERPROFILE\Downloads\CTU-Timetable-CLI-Tool"
# File version nam ngay trong thu muc chinh
$VersionFile = "$InstallDir\.version" 
$ZipUrl = "https://github.com/$RepoUser/$RepoName/archive/refs/heads/main.zip"
$ZipPath = "$env:TEMP\HuaniverseTimetable.zip"
$ApiUrl = "https://api.github.com/repos/$RepoUser/$RepoName/commits/main"

Write-Host "`=== HUANIVERSE AUTO INSTALLER ===" -ForegroundColor Cyan

# 2. KIEM TRA PHIEN BAN (Update Check)
Write-Host "1. Dang kiem tra phien ban..." -ForegroundColor Yellow

$NeedUpdate = $true
$LatestHash = ""

try {
    # Lay thong tin commit moi nhat tu GitHub API
    $Response = Invoke-RestMethod -Uri $ApiUrl -Headers @{"User-Agent" = "PowerShell"} -ErrorAction Stop
    $LatestHash = $Response.sha

    # Kiem tra neu thu muc va file version da ton tai
    if ((Test-Path $InstallDir) -and (Test-Path $VersionFile)) {
        $CurrentHash = Get-Content -Path $VersionFile -ErrorAction SilentlyContinue
        
        if ($CurrentHash -eq $LatestHash) {
            Write-Host "-> Phien ban hien tai da la moi nhat ($LatestHash)." -ForegroundColor Green
            $NeedUpdate = $false
        } else {
            Write-Host "-> Phat hien phien ban moi. Dang cap nhat..." -ForegroundColor Magenta
        }
    }
}
catch {
    Write-Warning "Khong the kiem tra phien ban online. Se tien hanh cai dat lai de dam bao an toan."
    $NeedUpdate = $true
}

# 3. TAI VA GIAI NEN (Chi chay khi can update)
if ($NeedUpdate) {
    Write-Host "2. Dang tai source code moi nhat..."

    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -ErrorAction Stop
    }
    catch {
        Write-Error "LOI: Khong the tai xuong. Vui long kiem tra ket noi mang."
        exit
    }

    Write-Host "3. Dang cai dat du lieu..."
    
    # 3.1. Xoa thu muc cu neu ton tai de dam bao sach se
    if (Test-Path $InstallDir) { Remove-Item -Path $InstallDir -Recurse -Force }
    
    # 3.2. Tao thu muc cai dat moi
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

    # 3.3. Giai nen vao thu muc TAM (Temp) truoc
    $TempExtractPath = "$env:TEMP\Huaniverse_Extract_Temp"
    if (Test-Path $TempExtractPath) { Remove-Item $TempExtractPath -Recurse -Force }
    
    Expand-Archive -Path $ZipPath -DestinationPath $TempExtractPath -Force
    
    # 3.4. Tim thu muc con ben trong (GitHub luon tao 1 folder boc ngoai, v.d. CTU-Timetable-main)
    $InnerFolder = Get-ChildItem -Path $TempExtractPath | Select-Object -First 1
    
    # 3.5. Di chuyen TOAN BO file tu thu muc con ra thu muc chinh ($InstallDir)
    if ($InnerFolder) {
        Get-ChildItem -Path $InnerFolder.FullName | Move-Item -Destination $InstallDir -Force
    }

    # 3.6. Don dep rac (File zip va thu muc temp)
    Remove-Item -Path $ZipPath -Force
    Remove-Item -Path $TempExtractPath -Recurse -Force

    # 3.7. Tao file version nam NGAY TRONG thu muc tool
    if ($LatestHash) {
        Set-Content -Path $VersionFile -Value $LatestHash
    }
    
    Write-Host "-> Da cap nhat cau truc thu muc gon gang." -ForegroundColor Cyan

} else {
    Write-Host "-> Bo qua buoc tai xuong." -ForegroundColor Gray
}

# 4. TIM VA CHAY FILE CAI DAT
Write-Host "4. Dang khoi dong chuong trinh..." -ForegroundColor Yellow

# Vi da lam phang cau truc, file auto_run.bat se nam ngay trong $InstallDir
$BatFile = "$InstallDir\auto_run.bat"

if (Test-Path $BatFile) {
    Write-Host "-> Da tim thay file. Dang chay..." -ForegroundColor Green
    
    # Chay file bat
    Start-Process -FilePath $BatFile -Wait
} else {
    # Fallback: Tim de quy neu co su co
    $FoundBat = Get-ChildItem -Path $InstallDir -Filter "auto_run.bat" -Recurse | Select-Object -First 1
    if ($FoundBat) {
        Start-Process -FilePath $FoundBat.FullName -Wait
    } else {
        Write-Error "LOI: Khong tim thay file 'auto_run.bat'."
        Write-Host "Vui long kiem tra thu muc: $InstallDir"
    }
}

Write-Host "Hoan tat!" -ForegroundColor Green