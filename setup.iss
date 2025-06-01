[Setup]
AppName=NESync
AppVersion=1.0
DefaultDirName={pf}\NESync
DefaultGroupName=NESync
OutputBaseFilename=NESyncInstaller
Compression=lzma
SolidCompression=yes

[Files]
; Include everything in your dist folder recursively
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NESync"; Filename: "{app}\run.exe"

[Run]
Filename: "{app}\run.exe"; Description: "Launch NESync"; Flags: nowait postinstall skipifsilent
