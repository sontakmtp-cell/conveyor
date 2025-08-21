; Script for Inno Setup Compiler - Fixed Version
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Conveyor Calculator AI"
#define MyAppVersion "2.20"
#define MyAppPublisher "Boring Company"
#define MyAppURL "haingocson@gmail.com"
#define MyAppExeName "ConveyorCalculator.exe"
#define MyBuildPath "dist\ConveyorCalculator"
#define MyIconPath "icon.ico"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID in the IDE.)
AppId={{F2A4E6E1-5BBE-4E42-A5A4-3A3A3A3A3A3A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputBaseFilename=ConveyorCalculatorAI-{#MyAppVersion}-setup
SetupIconFile={#MyIconPath}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
UninstallDisplayIcon={app}\{#MyAppExeName}
; Thêm thông tin về yêu cầu hệ thống
MinVersion=6.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "{#MyBuildPath}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Thêm registry entries để đăng ký file associations nếu cần
Root: HKCR; Subkey: ".ccai"; ValueType: string; ValueName: ""; ValueData: "ConveyorCalculatorAI"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ConveyorCalculatorAI"; ValueType: string; ValueName: ""; ValueData: "Conveyor Calculator AI File"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ConveyorCalculatorAI\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCR; Subkey: "ConveyorCalculatorAI\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Code]
; Thêm kiểm tra phiên bản Windows
function InitializeSetup(): Boolean;
begin
  Result := True;
  // Kiểm tra Windows 10 trở lên
  if not IsWindowsVersionOrGreater(10, 0, 0) then
  begin
    MsgBox('This application requires Windows 10 or later.', mbError, MB_OK);
    Result := False;
  end;
end;
