
#define MyAppName "HOTS Hosts"
#define MyAppVersion "2.2"
#define MyAppPublisher "Darsono"
#define MyAppExeName "HOTS Hosts.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ""
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt
#expr EmitLanguagesSection

[Setup]
AppId={{4340573B-8723-4313-8A37-F61536544D32}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}.0.0
VersionInfoTextVersion={#MyAppVersion}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductName={#MyAppName}
VersionInfoDescription={#MyAppName} Setup
DefaultDirName={autopf}\{#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=Output
OutputBaseFilename=HOTS_Hosts_setup
SetupIconFile=icon.ico
SolidCompression=yes
WizardStyle=modern dynamic

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\hosts_editor_launcher.dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\hosts_editor_launcher.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "hots_uninstall_cleanup.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{app}\hots_uninstall_cleanup.cmd"; Flags: runhidden waituntilterminated

[Code]

function VerifyUninstallPassword(const Password: String): Boolean;
var
  TempFile: String;
  ResultCode: Integer;
  ExePath: String;
begin
  Result := False;
  TempFile := ExpandConstant('{tmp}\hots_uninst_pw.tmp');
  SaveStringToFile(TempFile, Password, False);
  ExePath := ExpandConstant('{app}\{#MyAppExeName}');

  if Exec(ExePath, '--verify-uninstall-password "' + TempFile + '"', '',
          SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;

  if FileExists(TempFile) then
    DeleteFile(TempFile);
end;

function AskUninstallPassword(): Boolean;
var
  Form: TSetupForm;
  EditPwd: TEdit;
  LabelInfo: TNewStaticText;
  BtnOK, BtnCancel: TNewButton;
  Attempts: Integer;
  ModalRes: Integer;
begin
  Result := False;
  Attempts := 0;

  while Attempts < 3 do
  begin
    Form := CreateCustomForm(ScaleX(360), ScaleY(140), False, False);
    Form.Caption := '{#MyAppName}';
    Form.Position := poScreenCenter;

    LabelInfo := TNewStaticText.Create(Form);
    LabelInfo.Parent := Form;
    LabelInfo.Left := ScaleX(16);
    LabelInfo.Top := ScaleY(16);
    LabelInfo.Width := Form.ClientWidth - ScaleX(32);
    LabelInfo.AutoSize := False;
    LabelInfo.WordWrap := True;
    LabelInfo.Caption := 'This program is password-protected. Enter the password to continue uninstalling:';

    EditPwd := TEdit.Create(Form);
    EditPwd.Parent := Form;
    EditPwd.Left := ScaleX(16);
    EditPwd.Top := ScaleY(56);
    EditPwd.Width := Form.ClientWidth - ScaleX(32);
    EditPwd.PasswordChar := '*';

    BtnOK := TNewButton.Create(Form);
    BtnOK.Parent := Form;
    BtnOK.Caption := 'OK';
    BtnOK.Left := Form.ClientWidth - ScaleX(170);
    BtnOK.Top := ScaleY(96);
    BtnOK.Width := ScaleX(75);
    BtnOK.ModalResult := mrOk;
    BtnOK.Default := True;

    BtnCancel := TNewButton.Create(Form);
    BtnCancel.Parent := Form;
    BtnCancel.Caption := 'Cancel';
    BtnCancel.Left := Form.ClientWidth - ScaleX(85);
    BtnCancel.Top := ScaleY(96);
    BtnCancel.Width := ScaleX(75);
    BtnCancel.ModalResult := mrCancel;
    BtnCancel.Cancel := True;

    Form.ActiveControl := EditPwd;
    ModalRes := Form.ShowModal();

    if ModalRes = mrOk then
    begin
      if VerifyUninstallPassword(EditPwd.Text) then
      begin
        Form.Free();
        Result := True;
        Exit;
      end;
      Attempts := Attempts + 1;
      Form.Free();
      if Attempts < 3 then
        MsgBox('Incorrect password. Attempts remaining: ' + IntToStr(3 - Attempts), mbError, MB_OK)
      else
        MsgBox('Too many failed attempts. Uninstall has been cancelled.', mbError, MB_OK);
    end
    else
    begin
      Form.Free();
      Exit;
    end;
  end;
end;

function InitializeUninstall(): Boolean;
var
  Hash: String;
begin
  Result := True;

  if not RegQueryStringValue(HKLM, 'Software\HOTS Hosts', 'AppPasswordHash', Hash) then
    Exit;
  if Hash = '' then
    Exit;

  if UninstallSilent then
  begin
    Result := False;
    Exit;
  end;

  Result := AskUninstallPassword();
end;
