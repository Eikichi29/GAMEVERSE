#define MyAppName "GAMESVERSE"
#define MyAppVersion "0.5.0"
#define MyAppPublisher "GAMESVERSE contributors"
#define MyAppExeName "GAMESVERSE.exe"

[Setup]
AppId={{B8A51E76-9C2B-4D1C-9C17-6A5C8E9F0433}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\GAMESVERSE
DefaultGroupName=GAMESVERSE
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer-output
OutputBaseFilename=GAMESVERSE-Setup-0.5.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked

[Files]
Source: "dist\GAMESVERSE.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\GAMESVERSE"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\GAMESVERSE"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch GAMESVERSE"; Flags: postinstall nowait skipifsilent
