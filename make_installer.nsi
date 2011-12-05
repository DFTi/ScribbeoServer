; This script shows how to make your applicaton uninstallable

;--------------------------------

; The name of the installer
Name "Scribbeo Server v1.0"

; The file to write
OutFile "ScribbeoServerSetup.exe"

; The default installation directory
InstallDir $PROGRAMFILES\ScribbeoServer\

; The text to prompt the user to enter a directory
DirText "This will install Scribbeo Server v1.0 on your computer."

;--------------------------------

; ---------------------------------------------------------
; INSTALL SECTION
; ---------------------------------------------------------
; The stuff to install
Section "" ; No components page, name is not important

; This is important to have $APPDATA variable
; point to ProgramData folder
; instead of current user's Roaming folder
SetShellVarContext all


; Set output path to the installation directory.
SetOutPath $INSTDIR

; Put a file there
File dist\icon.bmp
File dist\icon.ico
File dist\library.zip
File dist\ScribbeoServer.exe
File dist\ScribbeoServerEULA.txt
File dist\ScribbeoServerGUI.exe
File dist\w9xpopen.exe
File dist\ScribbeoServer.exe
File vcredist_x86.exe

; Install the VisualC++ Redist package
ExecWait '"$INSTDIR\vcredist_x86.exe" /q:a /c:"VCREDI~1.EXE /q:a /c:""msiexec /i vcredist.msi /qb!"" "'

; Tell the compiler to write an uninstaller and to look for a "Uninstall" section 
WriteUninstaller $INSTDIR\Uninstall.exe

CreateDirectory "$SMPROGRAMS\Scribbeo Server"
CreateShortCut "$SMPROGRAMS\Scribbeo Server\Scribbeo Server.lnk" "$INSTDIR\ScribbeoServerGUI.exe"
CreateShortCut "$SMPROGRAMS\Scribbeo Server\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
CreateShortCut "$DESKTOP\Scribbeo Server.lnk" "$INSTDIR\ScribbeoServerGUI.exe"

WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Scribbeo Server" "DisplayName"\
"Scribbeo Server (remove only)"

WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Scribbeo Server" "UninstallString" \
"$INSTDIR\Uninstall.exe"

; //////////////////////// END CREATING REGISTRY KEYS ////////////////////////////

; This sets us permissions
AccessControl::GrantOnFile "$APPDATA\ScribbeoServer" "(S-1-5-32-545)" "FullAccess"
AccessControl::GrantOnFile "$APPDATA\ScribbeoServer\*" "(S-1-5-32-545)" "FullAccess"
AccessControl::GrantOnFile "$INSTDIR\ScribbeoServer" "(S-1-5-32-545)" "FullAccess"
AccessControl::GrantOnFile "$INSTDIR\ScribbeoServer\*" "(S-1-5-32-545)" "FullAccess"

; Now we can delete the vcredist package too.
Delete $INSTDIR\vcredist_x86.exe

MessageBox MB_OK "Installation was successful."
SectionEnd ; end the section

; ---------------------------------------------------------
; UNINSTALL SECTION
; ---------------------------------------------------------

; The uninstall section
Section "Uninstall"

Delete $INSTDIR\Uninstall.exe
Delete $INSTDIR\icon.bmp
Delete $INSTDIR\icon.ico
Delete $INSTDIR\library.zip
Delete $INSTDIR\ScribbeoServer.exe
Delete $INSTDIR\ScribbeoServerEULA.txt
Delete $INSTDIR\ScribbeoServerGUI.exe
Delete $INSTDIR\w9xpopen.exe

RMDir $INSTDIR

Delete $APPDATA\ScribbeoServer\settings.json
RMDir $APPDATA\ScribbeoServer

; Now remove shortcuts too
Delete "$SMPROGRAMS\Scribbeo Server\Scribbeo Server.lnk"
Delete "$SMPROGRAMS\Scribbeo Server\Uninstall.lnk"
RMDIR "$SMPROGRAMS\Scribbeo Server"

Delete "$DESKTOP\Scribbeo Server.lnk"

DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Scribbeo Server"
DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Scribbeo Server"

SectionEnd