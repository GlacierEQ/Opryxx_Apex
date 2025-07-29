
; NEXUS AI System Installer
!define APPNAME "NEXUS AI System"
!define VERSION "2.0"
!define PUBLISHER "OPRYXX Systems"

Name "${APPNAME}"
OutFile "NEXUS_AI_Installer.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"

Page directory
Page instfiles

Section "Install"
    SetOutPath $INSTDIR
    
    ; Copy main files
    File "dist\NEXUS_AI_Ultimate.exe"
    File "dist\MEGA_OPRYXX.exe" 
    File "dist\AI_Workbench.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\NEXUS AI Ultimate.lnk" "$INSTDIR\NEXUS_AI_Ultimate.exe"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\MEGA OPRYXX.lnk" "$INSTDIR\MEGA_OPRYXX.exe"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\AI Workbench.lnk" "$INSTDIR\AI_Workbench.exe"
    
    ; Desktop shortcuts
    CreateShortCut "$DESKTOP\NEXUS AI.lnk" "$INSTDIR\NEXUS_AI_Ultimate.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\*.exe"
    RMDir "$INSTDIR"
    Delete "$SMPROGRAMS\${APPNAME}\*.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    Delete "$DESKTOP\NEXUS AI.lnk"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd
