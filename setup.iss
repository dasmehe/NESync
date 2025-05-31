; NESync Installer Script
; For GitHub project: https://github.com/dasmehe/NESync

#define MyAppName "NESync"
#define MyAppVersion "1.0"
#define MyAppPublisher "dasmehe"
#define MyAppURL "https://github.com/dasmehe/NESync"
#define MyAppExeName "NESync.exe"
#define MyAppOutputDir ".\dist"
#define MyAppOutputName "NESync_Setup"

[Setup]
AppId={{E3F1D3A4-1234-5678-9012-345678901234}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#MyAppOutputDir}
OutputBaseFilename={#MyAppOutputName}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=.\src-tauri\icons\icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "pythoninstall"; Description: "Install Python 3.10+ (required for backend)"; GroupDescription: "Dependencies"; Flags: checkedonce

[Files]
; Main application files (Tauri output)
Source: "{#MyAppOutputDir}\*.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppOutputDir}\*.dll"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppOutputDir}\*.bin"; DestDir: "{app}"; Flags: ignoreversion

; Python backend files
Source: ".\backend\*"; DestDir: "{app}\backend"; Flags: ignoreversion recursesubdirs createallsubdirs

; Web assets
Source: ".\public\*"; DestDir: "{app}\public"; Flags: ignoreversion recursesubdirs createallsubdirs

; Application resources
Source: ".\src-tauri\icons\*"; DestDir: "{app}\icons"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  PythonVersion: String;
begin
  // Check for Python installation
  if not RegQueryStringValue(HKLM, 'Software\Python\PythonCore\3.10\InstallPath', '', PythonVersion) then
  begin
    if not RegQueryStringValue(HKLM, 'Software\Python\PythonCore\3.11\InstallPath', '', PythonVersion) then
    begin
      if MsgBox('Python 3.10 or later is required for the backend functionality. Do you want to install it now?', 
          mbConfirmation, MB_YESNO) = IDYES then
      begin
        // This would launch the Python installer - you'd need to provide the path
        // ShellExec('open', 'https://www.python.org/downloads/', '', '', SW_SHOW, ewNoWait, ErrorCode);
        Result := True;
      end
      else
      begin
        MsgBox('NESync will be installed, but backend functionality will not work without Python.', mbInformation, MB_OK);
        Result := True;
      end;
    end
    else
      Result := True;
  end
  else
    Result := True;
end;