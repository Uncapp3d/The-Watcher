[Setup]
AppName=The Watcher
AppVersion=1.0
DefaultDirName={autopf}\TheWatcher
DefaultGroupName=The Watcher
OutputDir=.
OutputBaseFilename=TheWatcher_Installer
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\TheWatcher.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\The Watcher"; Filename: "{app}\TheWatcher.exe"
Name: "{commondesktop}\The Watcher"; Filename: "{app}\TheWatcher.exe"
Name: "{userstartup}\The Watcher"; Filename: "{app}\TheWatcher.exe"

[Run]
Filename: "{app}\TheWatcher.exe"; Description: "Start The Watcher now"; Flags: nowait postinstall skipifsilent