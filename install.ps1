# ============================================================
# HUANIVERSE TIMETABLE TOOL - INSTALLER
# ============================================================

# 1. CAU HINH THONG TIN 
# ------------------------------------------------------------
$RepoUser = "Huaniverse"  
$RepoName = "CTU-Timetable-CLI-Tool"        
# ------------------------------------------------------------

# Cau hinh duong dan va URL
$ZipUrl = "https://github.com/$RepoUser/$RepoName/archive/refs/heads/main.zip"
$InstallDir = "$env:USERPROFILE\Downloads\HuaniverseTimetable"
$ZipPath = "$env:TEMP\HuaniverseTimetable.zip"

Write-Host "`n=== HUANIVERSE AUTO INSTALLER ===" -ForegroundColor Cyan

# 2. TAI SOURCE CODE
Write-Host "1. Dang ket noi den GitHub..." -ForegroundColor Yellow

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipPath -ErrorAction Stop
}
catch {
    Write-Error "LOI: Khong the tai xuong. Vui long kiem tra ket noi mang."
    exit
}

# 3. GIAI NEN
Write-Host "2. Dang giai nen du lieu..."

# Xoa thu muc cu neu da ton tai de tranh loi
if (Test-Path $InstallDir) { Remove-Item -Path $InstallDir -Recurse -Force }
Expand-Archive -Path $ZipPath -DestinationPath $InstallDir -Force

# Xoa file zip rac
Remove-Item -Path $ZipPath -Force

# 4. TIM VA CHAY FILE CAI DAT
Write-Host "3. Dang khoi dong trinh cai dat..." -ForegroundColor Yellow

# Tim file auto_install.bat trong thu muc vua giai nen 
$BatFile = Get-ChildItem -Path $InstallDir -Filter "auto_install.bat" -Recurse | Select-Object -First 1

if ($BatFile -and (Test-Path $BatFile.FullName)) {
    Write-Host "-> Da tim thay file cai dat. Dang chay..." -ForegroundColor Green
    Write-Host "Vui long doi cua so tiep theo hien len..." -ForegroundColor Cyan
    
    # Chay file bat trong cua so CMD rieng biet
    Start-Process -FilePath $BatFile.FullName -Wait
} else {
    Write-Error "LOI: Khong tim thay file 'auto_install.bat'."
}

Write-Host "`nHoan tat!" -ForegroundColor Green