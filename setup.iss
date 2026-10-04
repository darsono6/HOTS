
#define MyAppName "HOTS Hosts"
#define MyAppVersion "2.3"
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
; Same mutex that hosts_editor_launcher.pyw holds while the app runs; lets Inno
; detect a running instance and ask to close it before touching files in {app}.
AppMutex=Global\HOTS_HostsEditor_SingleInstance_Mutex

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

[UninstallDelete]
; hots_uninstall_cleanup.cmd removes ProgramData/AppData user data and runs
; BEFORE this step. {app} holds only program files (no user data), so the
; whole folder can be deleted, including files not listed in [Files].
Type: filesandordirs; Name: "{app}"

[Code]

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // {app} holds no user data (password/settings/block lists live in
    // ProgramData and AppData), so wipe it before copying new files; otherwise
    // files removed or renamed in newer builds (e.g. old Nuitka DLLs) would linger.
    DelTree(ExpandConstant('{app}'), True, True, True);
  end;
end;

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

function GetAppLanguage(): String;
var
  SettingsPath: String;
  Lines: TArrayOfString;
  I, P1, P2: Integer;
  Line, Lang: String;
begin
  Result := 'en';
  SettingsPath := ExpandConstant('{userappdata}') + '\HOTS Hosts\settings.json';
  if not FileExists(SettingsPath) then
    Exit;
  if not LoadStringsFromFile(SettingsPath, Lines) then
    Exit;

  for I := 0 to GetArrayLength(Lines) - 1 do
  begin
    Line := Lines[I];
    if Pos('"language"', Line) > 0 then
    begin
      P1 := Pos(':', Line);
      if P1 = 0 then
        Continue;
      Line := Copy(Line, P1 + 1, Length(Line) - P1);
      P1 := Pos('"', Line);
      if P1 = 0 then
        Continue;
      Line := Copy(Line, P1 + 1, Length(Line) - P1);
      P2 := Pos('"', Line);
      if P2 = 0 then
        Continue;
      Lang := Copy(Line, 1, P2 - 1);

      if (Lang = 'pl') or (Lang = 'fr') or (Lang = 'de') or (Lang = 'es')
         or (Lang = 'ru') or (Lang = 'pt') or (Lang = 'en') then
        Result := Lang;
      Exit;
    end;
  end;
end;

procedure GetPasswordDialogTexts(out PromptText, IncorrectPrefix, TooManyText,
  OkText, CancelText: String);
var
  Lang: String;
begin
  Lang := GetAppLanguage();

  if Lang = 'pl' then
  begin
    PromptText := 'Ten program jest chroniony hasłem. Wprowadź hasło, aby kontynuować deinstalację:';
    IncorrectPrefix := 'Nieprawidłowe hasło. Pozostałe próby: ';
    TooManyText := 'Zbyt wiele nieudanych prób. Deinstalacja została anulowana.';
    OkText := 'OK';
    CancelText := 'Anuluj';
  end
  else if Lang = 'fr' then
  begin
    PromptText := 'Ce programme est protégé par un mot de passe. Entrez le mot de passe pour continuer la désinstallation :';
    IncorrectPrefix := 'Mot de passe incorrect. Tentatives restantes : ';
    TooManyText := 'Trop de tentatives échouées. La désinstallation a été annulée.';
    OkText := 'OK';
    CancelText := 'Annuler';
  end
  else if Lang = 'de' then
  begin
    PromptText := 'Dieses Programm ist passwortgeschützt. Geben Sie das Passwort ein, um die Deinstallation fortzusetzen:';
    IncorrectPrefix := 'Falsches Passwort. Verbleibende Versuche: ';
    TooManyText := 'Zu viele fehlgeschlagene Versuche. Die Deinstallation wurde abgebrochen.';
    OkText := 'OK';
    CancelText := 'Abbrechen';
  end
  else if Lang = 'es' then
  begin
    PromptText := 'Este programa está protegido con contraseña. Introduce la contraseña para continuar con la desinstalación:';
    IncorrectPrefix := 'Contraseña incorrecta. Intentos restantes: ';
    TooManyText := 'Demasiados intentos fallidos. Se ha cancelado la desinstalación.';
    OkText := 'OK';
    CancelText := 'Cancelar';
  end
  else if Lang = 'ru' then
  begin
    PromptText := 'Эта программа защищена паролем. Введите пароль, чтобы продолжить удаление:';
    IncorrectPrefix := 'Неверный пароль. Осталось попыток: ';
    TooManyText := 'Слишком много неудачных попыток. Удаление отменено.';
    OkText := 'ОК';
    CancelText := 'Отмена';
  end
  else if Lang = 'pt' then
  begin
    PromptText := 'Este programa está protegido por palavra-passe. Introduza a palavra-passe para continuar a desinstalação:';
    IncorrectPrefix := 'Palavra-passe incorreta. Tentativas restantes: ';
    TooManyText := 'Demasiadas tentativas falhadas. A desinstalação foi cancelada.';
    OkText := 'OK';
    CancelText := 'Cancelar';
  end
  else
  begin
    PromptText := 'This program is password-protected. Enter the password to continue uninstalling:';
    IncorrectPrefix := 'Incorrect password. Attempts remaining: ';
    TooManyText := 'Too many failed attempts. Uninstall has been cancelled.';
    OkText := 'OK';
    CancelText := 'Cancel';
  end;
end;

function AskUninstallPassword(): Boolean;
var
  Form: TSetupForm;
  EditPwd: TEdit;
  LabelInfo: TNewStaticText;
  BtnOK, BtnCancel: TNewButton;
  Attempts: Integer;
  ModalRes: Integer;
  PromptText, IncorrectPrefix, TooManyText, OkText, CancelText: String;
begin
  Result := False;
  Attempts := 0;
  GetPasswordDialogTexts(PromptText, IncorrectPrefix, TooManyText, OkText, CancelText);

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
    LabelInfo.Caption := PromptText;

    EditPwd := TEdit.Create(Form);
    EditPwd.Parent := Form;
    EditPwd.Left := ScaleX(16);
    EditPwd.Top := ScaleY(56);
    EditPwd.Width := Form.ClientWidth - ScaleX(32);
    EditPwd.PasswordChar := '*';

    BtnOK := TNewButton.Create(Form);
    BtnOK.Parent := Form;
    BtnOK.Caption := OkText;
    BtnOK.Left := Form.ClientWidth - ScaleX(170);
    BtnOK.Top := ScaleY(96);
    BtnOK.Width := ScaleX(75);
    BtnOK.ModalResult := mrOk;
    BtnOK.Default := True;

    BtnCancel := TNewButton.Create(Form);
    BtnCancel.Parent := Form;
    BtnCancel.Caption := CancelText;
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
        MsgBox(IncorrectPrefix + IntToStr(3 - Attempts), mbError, MB_OK)
      else
        MsgBox(TooManyText, mbError, MB_OK);
    end
    else
    begin
      Form.Free();
      Exit;
    end;
  end;
end;

function GetUpdateVsUninstallText(): String;
var
  Lang: String;
begin
  Lang := GetAppLanguage();

  if Lang = 'pl' then
    Result :=
      'Jeśli planujesz zainstalować nowszą wersję HOTS Hosts, nie musisz najpierw ' +
      'odinstalowywać programu — wystarczy uruchomić nowy instalator bezpośrednio. ' +
      'Zaktualizuje on program w miejscu, bez utraty ustawień, hasła ani list blokad.' + #13#10 + #13#10 +
      'Czy mimo to chcesz kontynuować i całkowicie usunąć HOTS Hosts, cofając zmiany ' +
      'wprowadzone w systemie?'
  else if Lang = 'fr' then
    Result :=
      'Si vous êtes sur le point d''installer une version plus récente de HOTS Hosts, ' +
      'il n''est pas nécessaire de désinstaller d''abord - lancez simplement le nouvel ' +
      'installateur directement. Il mettra à jour le programme sur place, sans perdre ' +
      'vos paramètres, votre mot de passe ni vos listes de blocage.' + #13#10 + #13#10 +
      'Voulez-vous tout de même continuer et supprimer complètement HOTS Hosts, en ' +
      'annulant les modifications apportées à ce système ?'
  else if Lang = 'de' then
    Result :=
      'Wenn Sie eine neuere Version von HOTS Hosts installieren möchten, müssen Sie ' +
      'das Programm nicht vorher deinstallieren - führen Sie einfach das neue ' +
      'Installationsprogramm direkt aus. Es aktualisiert das Programm an Ort und Stelle, ' +
      'ohne Ihre Einstellungen, Ihr Passwort oder Ihre Sperrlisten zu verlieren.' + #13#10 + #13#10 +
      'Möchten Sie trotzdem fortfahren und HOTS Hosts vollständig entfernen und die am ' +
      'System vorgenommenen Änderungen rückgängig machen?'
  else if Lang = 'es' then
    Result :=
      'Si estás a punto de instalar una versión más reciente de HOTS Hosts, no es ' +
      'necesario desinstalar primero - simplemente ejecuta el nuevo instalador ' +
      'directamente. Actualizará el programa en su lugar, sin perder tu configuración, ' +
      'contraseña ni listas de bloqueo.' + #13#10 + #13#10 +
      '¿Deseas continuar de todos modos y eliminar completamente HOTS Hosts, revirtiendo ' +
      'los cambios realizados en este sistema?'
  else if Lang = 'ru' then
    Result :=
      'Если вы собираетесь установить более новую версию HOTS Hosts, вам не нужно ' +
      'сначала удалять программу - просто запустите новый установщик напрямую. Он ' +
      'обновит программу на месте, не потеряв ваши настройки, пароль и списки блокировки.' + #13#10 + #13#10 +
      'Всё равно хотите продолжить и полностью удалить HOTS Hosts, отменив изменения, ' +
      'внесённые в систему?'
  else if Lang = 'pt' then
    Result :=
      'Se está prestes a instalar uma versão mais recente do HOTS Hosts, não precisa de ' +
      'desinstalar primeiro - basta executar o novo instalador diretamente. Ele ' +
      'atualizará o programa no local, sem perder as suas definições, palavra-passe ou ' +
      'listas de bloqueio.' + #13#10 + #13#10 +
      'Ainda assim, deseja continuar e remover completamente o HOTS Hosts, revertendo as ' +
      'alterações feitas neste sistema?'
  else
    Result :=
      'If you are about to install a newer version of HOTS Hosts, you do NOT need to ' +
      'uninstall first - just run the new installer directly. It will update the ' +
      'program in place, without losing your settings, password or blocklists.' + #13#10 + #13#10 +
      'Do you want to continue and completely remove HOTS Hosts, undoing the changes ' +
      'it made to this system?';
end;

function InitializeUninstall(): Boolean;
var
  Hash: String;
begin
  Result := True;

  if not UninstallSilent then
  begin
    if MsgBox(GetUpdateVsUninstallText(), mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDNO then
    begin
      Result := False;
      Exit;
    end;
  end;

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
