#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.SessionState
Imports System.Web.Security
Imports System.Text
Imports System.DirectoryServices
Imports System.Threading
Imports System.Resources
Imports System.Globalization
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.dataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class Login
        Inherits Page

#Region " Load JavaScripts"
        Private Sub LoadJavaScripts()
            btnLogin.Attributes.Add("onclick", "display_status();")

            Dim myTabArray() As Object = {txtLogin, txtPwd}
            Dim TabKeyDownArr() As String = {Tab(txtPwd, txtPwd, "No"), Tab(txtLogin, txtLogin, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Init(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Init
            Response.Cache.SetCacheability(HttpCacheability.NoCache)
            Response.Cache.SetExpires(Now())
        End Sub
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If Not Page.IsPostBack Then
                    Session.RemoveAll()
                End If

                lblVersion.Text = "Version: " + Helper.GetVersionNumber

                ClientScript.RegisterClientScriptInclude("EditScript", "Scripts/en-US/DataEntry.js")

                'If the current culture is nothing then create the current culture from the browser settings
                If SessionManager.CulturePref.Trim.Length = 0 Then
                    SessionManager.CulturePref = Request.UserLanguages(0).ToString()
                End If

                'Set the threads culture to what is saved in the session variable
                Thread.CurrentThread.CurrentCulture = CultureInfo.CreateSpecificCulture(SessionManager.CulturePref)
                Thread.CurrentThread.CurrentUICulture = Thread.CurrentThread.CurrentCulture

                lblTime.Text = Now.ToLongDateString

                'Set this here according to the threads current culture, not down below
                SessionManager.CulturePref = Thread.CurrentThread.CurrentCulture.Name

                'turn off the network login checkbox if network login is disabled
                If ConfigurationManager.AppSettings("UseNetworkLogin") = "False" Then
                    chkWindowsLogin.Visible = False
                End If

                If ConfigurationManager.AppSettings("EventTrackerLevel") IsNot Nothing AndAlso IsNumeric(ConfigurationManager.AppSettings("EventTrackerLevel")) Then
                    SessionManager.EventTrackerLevel = ConfigurationManager.AppSettings("EventTrackerLevel")
                End If

                'Try to auto login using Windows User Name if user is setup for Auto Login
                AutoLogin()
                If SessionManager.ConnectionError <> "" Then
                    If Not SessionManager.ConnectionError.ToString = String.Empty Then
                        ErrorControl.DisplayError(SessionManager.ConnectionError.ToString)
                        SessionManager.ConnectionError = String.Empty
                    End If
                End If
                LoadJavaScripts()

                txtLogin.Focus()

                If Not Page.IsPostBack Then
                    SetCultureButtons()

                    'set the winlogin checkbox
                    If Not IsNothing(Request.Cookies("WinLogin")) Then
                        If Request.Cookies("WinLogin").Value = "TRUE" Then
                            chkWindowsLogin.Checked = True
                        End If
                    End If
                End If
            Catch ex As Exception
                ErrorControl.DisplayErrors("Login", ex, Request("REMOTE_USER").ToString(), CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Protected Sub ChangeLanguage(ByVal sender As Object, ByVal e As System.Web.UI.ImageClickEventArgs)
            If TypeOf (sender) Is ImageButton Then
                Dim strCulture As String = Mid(CType(sender, ImageButton).ID, 5)
                strCulture = strCulture.Replace("_", "-")
                Thread.CurrentThread.CurrentCulture = CultureInfo.CreateSpecificCulture(strCulture)
                Thread.CurrentThread.CurrentUICulture = Thread.CurrentThread.CurrentCulture

                ''SessionManager.Culture = Thread.CurrentThread.CurrentCulture
                SessionManager.CulturePref = strCulture

                chkWindowsLogin.Text = GetTranslationString("usenetworklogin", "Use my Network Login")
                btnLogin.Text = GetTranslationString("ok", "OK")
                lblUserName.Text = GetTranslationString("username", lblUserName.Text.Replace(":", "")) & ":"
                lblPassword.Text = GetTranslationString("password", lblPassword.Text.Replace(":", "")) & ":"
                lblLoginHeader.Text = GetTranslationString("login", "Login")

                'Yes the date was set in the page load but if the language was changed then the page_load
                'event would have set the date according to the previous culture because of the way that the page lifecycle
                'happens in asp.net
                lblTime.Text = Now.ToLongDateString
            End If
        End Sub
        Private Sub btnLogin_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnLogin.Click
            If Request.QueryString("Auto") = "Y" OrElse Request.QueryString("Auto") = "y" Then
                'We do not have a cookie but user is set up for Auto Login
                'so we create a cookie
                Dim cookie As New HttpCookie("UserID", txtLogin.Text.Trim.ToUpper)
                'if we dont find a valid config setting cookie will expire in 3 hours
                If IsNothing(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                    cookie.Expires = DateTime.Now.AddDays(90)
                Else
                    If IsNumeric(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                        cookie.Expires = DateTime.Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))
                    Else
                        cookie.Expires = DateTime.Now.AddDays(90)
                    End If
                End If
                Response.Cookies.Add(cookie)
            End If

            Dim blnLoggedIn As Boolean = False
            Dim strPwd As String
            Dim strUser As String = String.Empty

            If txtLogin.Text.Trim.Length > 0 Then
                strUser = txtLogin.Text.Trim.ToUpper

                If chkWindowsLogin.Checked = False Then
                    If Not IsNothing(Request.Cookies("WinLogin")) Then
                        Response.Cookies("WinLogin").Value = "FALSE"
                    End If
                End If
            ElseIf chkWindowsLogin.Checked = True Then
                'if the user requests login via windows account, just let them in
                strUser = Request("REMOTE_USER")

                'remove the domain
                If InStr(strUser, "\", CompareMethod.Binary) > 0 Then
                    strUser = strUser.Substring(InStr(strUser, "\", CompareMethod.Binary)).ToUpper
                End If

                'double check the user id
                If strUser.Trim.Length > 0 Then
                    blnLoggedIn = True

                    'Save the checkbox state
                    Dim cookie As New HttpCookie("WinLogin", "TRUE")

                    'if we dont find a valid config setting cookie will expire in 3 hours
                    If IsNothing(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                        cookie.Expires = DateTime.Now.AddDays(90)
                    Else
                        If IsNumeric(ConfigurationManager.AppSettings("CookieExpirationTime")) Then
                            cookie.Expires = DateTime.Now.AddHours(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))
                        Else
                            cookie.Expires = DateTime.Now.AddDays(90)
                        End If
                    End If

                    Response.Cookies.Add(cookie)
                End If
            End If

            If blnLoggedIn = False Then
                'try to log in via ADS
                If ADSValidation() Then
                    blnLoggedIn = True
                End If
            End If

            'if we are authenticated already, set a session variable to indicate the
            'user validated outside of the application
            If blnLoggedIn = True Then
                SessionManager.NetworkLogin = True
            Else
                SessionManager.NetworkLogin = False
            End If

            Dim dt As DataTable = UserMaster.VerifyUserAccess(strUser)
            Dim culture As CultureInfo = Thread.CurrentThread.CurrentCulture

            If dt.Rows.Count = 0 Then
                'if the user is already logged in then add them to the user master
                If SessionManager.NetworkLogin AndAlso txtLogin.Text.Trim.Length = 0 Then
                    Dim retValue As InsertADUserError = UserMaster.InsertUserMasterFromAD(strUser, SessionManager.CulturePref)
                    If retValue = InsertADUserError.InvalidSite Then
                        ErrorControl.DisplayError(GetTranslationString("error_invalidsite", "Invalid Site"))
                        Return
                    ElseIf retValue = InsertADUserError.NoError Then
                        'good to go!
                        dt = UserMaster.VerifyUserAccess(strUser)
                        If dt.Rows.Count = 0 Then
                            'The error control needs to be adjusted so that it gets the display string according to the 
                            'culture but always logs the error in English
                            ErrorControl.DisplayError(GetTranslationString("error_invalidusername", "Invalid User Name"))
                            Return
                        End If
                    Else
                        Return
                    End If
                Else
                    ErrorControl.DisplayError(GetTranslationString("error_invalidusername", "Invalid User Name"))
                    Return
                End If
            End If

            'Generate encrypted password from UserID and Password entered
            'and compare with encrypted password stored in the database
            If blnLoggedIn = True Then
                strPwd = dt.Rows(0).Item("Password").ToString.Trim()
            Else
                strPwd = FormsAuthentication.HashPasswordForStoringInConfigFile(txtPwd.Text.ToUpper.Trim & txtLogin.Text.ToUpper.Trim, "sha1")
            End If

            If dt.Rows.Count = 0 Then
                ErrorControl.DisplayError(GetTranslationString("error_invalidusername", "Invalid User Name"))
                Exit Sub
            ElseIf Not Convert.ToBoolean(dt.Rows(0)("SiteActive")) Then
                ErrorControl.DisplayError(GetTranslationString("error_invalidsite", "Invalid Site"))
                Exit Sub
            ElseIf dt.Rows(0).Item("Password").ToString.Trim() <> strPwd.Trim Then
                ErrorControl.DisplayError(GetTranslationString("error_invalidpassword", "Invalid Password, please check your input"))
                Exit Sub
            Else
                Dim dtRow As DataRow = dt.Rows(0)
                SessionManager.UserID = dtRow("UserID").ToString.Trim().ToUpper
                SessionManager.UserName = dtRow("UserName").ToString.Trim()
                SessionManager.WorkingSite = dtRow("Site").ToString.Trim()
                SessionManager.WorkingSiteID = dtRow("SiteID").ToString.Trim()

                'Save the culture preference to the database based upon the flag that the user clicked
                'If for some reason the culture pref was not set then get it from the database
                Dim cp As String = SessionManager.CulturePref
                If (cp.Length = 5) Then
                    UserMaster.UpdateUserCulture(SessionManager.UserID, SessionManager.CulturePref)
                Else
                    'verify that the culture is formatted properly
                    If dtRow("CultureCode").ToString.Trim.Length = 5 Then
                        SessionManager.CulturePref = dtRow("CultureCode").ToString.Substring(0, 2).ToLower & "-" & dtRow("CultureCode").ToString.Substring(3, 2).ToUpper
                    Else
                        SessionManager.CulturePref = dtRow("CultureCode").ToString.Trim()
                    End If
                End If

                SessionManager.ShowMenuOptionNumbers = dtRow("ShowMenuOptionNumbers").ToString.Trim()
                SessionManager.Authenticated = True
                If Convert.ToBoolean(dtRow("IsAdministrator")) = True Then
                    SessionManager.IsAdministrator = True
                Else
                    SessionManager.IsAdministrator = False
                End If

                'if network login is turned off then ONLY ADMINS can log in
                If ConfigurationManager.AppSettings("UseNetworkLogin") = "False" Then
                    If SessionManager.NetworkLogin Then
                        If Not SessionManager.IsAdministrator Then
                            'get out of here
                            ErrorControl.DisplayError(GetTranslationString("error_networkvalidationoff", "Network Validation is turned off.") & vbCrLf & vbCrLf & GetTranslationString("error_loginusernamepassword", "You must supply your A+ Username and Password to login."))

                            Return
                        End If
                    End If
                End If

                Dim strInitialMenu As String = String.Empty
                Dim strURL As String = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.ProgramVerification(SessionManager.UserID.ToString, SessionManager.IsAdministrator, strInitialMenu).Trim
                If String.IsNullOrEmpty(strURL) Then
                    ErrorControl.DisplayError(GetTranslationString("error_noaccess", "You do not have access to the program"))
                    Exit Sub
                Else
                    If strInitialMenu.Trim.Length > 0 Then
                        If ProgramMaster.ProgramIsMenu(strInitialMenu) Then
                            SessionManager.CurrentMenuProgram = strInitialMenu
                        Else
                            SessionManager.CurrentMenuProgram = "MainMenu"
                        End If
                    Else
                        ErrorControl.DisplayError(SessionManager.UserID & " " & GetTranslationString("error_noinitmenu", "has no initial menu configured"))
                        Return
                    End If
                End If

                'make note of the user login
                PopupUserLogins.UpdatePopupUserLogins(strUser)
                SessionManager.ShowPopups = "YES"
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.Login) Then
                    Dim stackFrame As Diagnostics.StackFrame = New Diagnostics.StackTrace(True).GetFrame(0)
                    Dim strMessage As String = stackFrame.GetMethod().DeclaringType.FullName.Trim() & ":" & vbCrLf & "Login - Culture " & SessionManager.CulturePref
                    strMessage += vbCrLf & "Browser : " & Request.UserAgent.ToString

                    EventTracker.AddNoEmail(stackFrame.GetMethod().Name.Trim(), strMessage, SessionManager.UserID)
                    stackFrame = Nothing
                End If
                Response.Redirect(strURL, False)
            End If
        End Sub
#End Region

#Region " Private Methods"
        Private Sub SetCultureButtons()
            Dim strCulture As String = ""

            For Each objCtl As Control In CultureButtons.Controls
                If TypeOf objCtl Is ImageButton Then
                    strCulture = objCtl.ID.Replace("btn_", "").Replace("_", "-")

                    'Always show the english button
                    If strCulture.ToUpper = "EN-US" Or strCulture.ToUpper = "EN-GB" Then
                        objCtl.Visible = True
                    ElseIf ConfigurationManager.AppSettings(strCulture) IsNot Nothing AndAlso ConfigurationManager.AppSettings(strCulture).Trim.ToUpper = "ON" Then
                        objCtl.Visible = True
                    Else
                        objCtl.Visible = False
                    End If
                End If
            Next
        End Sub
        Private Sub AutoLogin()
            If ("" & Request.QueryString("Auto")).ToUpper = "Y" Then
                Dim strUser As String = Request("REMOTE_USER")
                Dim strURL As String = String.Empty

                If Request.QueryString.Count > 1 Then
                    SessionManager.ShowPopups = "NO"
                Else
                    SessionManager.ShowPopups = "YES"
                End If

                'remove the domain
                If InStr(strUser, "\", CompareMethod.Binary) > 0 Then
                    strUser = strUser.Substring(InStr(strUser, "\", CompareMethod.Binary))
                End If
                Dim dt As DataTable = UserMaster.VerifyUserAccess(strUser)

                'Note: Here we are not checking the password as we are getting User from Windows
                If dt.Rows.Count > 0 Then
                    Dim dtRow As DataRow = dt.Rows(0)

                    If Not Convert.ToBoolean(dtRow("SiteActive")) Then
                        ErrorControl.DisplayError(GetTranslationString("error_invalidsite", "Invalid Site"))
                        Exit Sub
                    End If

                    SessionManager.Authenticated = True
                    SessionManager.UserID = strUser.ToUpper
                    SessionManager.UserName = dtRow("UserName").ToString.Trim()
                    SessionManager.WorkingSite = dtRow("Site").ToString.Trim()
                    SessionManager.WorkingSiteID = dtRow("SiteID").ToString.Trim()

                    'verify that the culture is formatted properly
                    If dtRow("CultureCode").ToString.Trim.Length = 5 Then
                        SessionManager.CulturePref = dtRow("CultureCode").ToString.Substring(0, 2).ToLower & "-" & dtRow("CultureCode").ToString.Substring(3, 2).ToUpper
                    Else
                        SessionManager.CulturePref = dtRow("CultureCode").ToString.Trim()
                    End If

                    SessionManager.ShowMenuOptionNumbers = dtRow("ShowMenuOptionNumbers").ToString.Trim()
                    If dtRow("IsAdministrator") = -1 Then
                        SessionManager.IsAdministrator = True
                    Else
                        SessionManager.IsAdministrator = False
                    End If

                    'if network login is turned off then ONLY ADMINS can log in
                    If ConfigurationManager.AppSettings("UseNetworkLogin") = "False" Then
                        If Not SessionManager.IsAdministrator Then
                            ErrorControl.DisplayError("Network Validation is turned off." & vbCrLf & vbCrLf & "You must supply your Username and Password to login.")
                            Return
                        End If
                    End If

                    'set the default menu just in case we need it
                    Dim strInitialMenu As String = String.Empty
                    strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.ProgramVerification(SessionManager.UserID, SessionManager.IsAdministrator, strInitialMenu).Trim

                    'Now, if have any additional parameters
                    If ("" + Request.Params("CloseOnLogout")).Trim.Length > 0 Then
                        SessionManager.CloseOnLogout = True
                    End If

                    If ("" & Request.Params("Team")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("Team"))) Then
                        ' Team Status
                        If Teams.UserHasAccessToTeam(SessionManager.UserID, Request.Params("Team"), SessionManager.WorkingSiteID) Then
                            Dim objDT As DataTable = Teams.SelectTeams(Request.Params("Team"))
                            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                                Dim drTeam As DataRow = objDT.Rows(0)

                                SessionManager.SelectedTeamID = Request.Params("Team")
                                SessionManager.SelectedTeam = drTeam("Team").ToString
                                If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                                    SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                                Else
                                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                                End If

                                strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamStatus")
                            End If
                        End If
                    ElseIf ("" & Request.Params("ActionPlan")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("ActionPlan"))) Then
                        ' Team Action Plan
                        If Teams.UserHasAccessToTeam(SessionManager.UserID, Request.Params("ActionPlan"), SessionManager.WorkingSiteID) Then
                            Dim objDT As DataTable = Teams.SelectTeams(Request.Params("ActionPlan"))
                            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                                Dim drTeam As DataRow = objDT.Rows(0)

                                SessionManager.SelectedTeamID = Request.Params("ActionPlan")
                                SessionManager.SelectedTeam = drTeam("Team").ToString
                                If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                                    SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                                Else
                                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                                End If
                                SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)

                                strInitialMenu = "TeamBoardMenu"
                                strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamActionPlanMaintenance")
                            End If
                        End If
                    ElseIf ("" & Request.Params("TeamBoard")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("TeamBoard"))) Then
                        ' Team Board
                        If Teams.UserHasAccessToTeam(SessionManager.UserID, Request.Params("TeamBoard"), SessionManager.WorkingSiteID) Then
                            Dim objDT As DataTable = Teams.SelectTeams(Request.Params("TeamBoard"))
                            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                                Dim drTeam As DataRow = objDT.Rows(0)

                                SessionManager.SelectedTeamID = Request.Params("TeamBoard")
                                SessionManager.SelectedTeam = drTeam("Team").ToString
                                If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                                    SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                                Else
                                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                                End If

                                strInitialMenu = "TeamBoardMenu"
                                strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenu")
                            End If
                        End If
                    ElseIf ("" & Request.Params("TeamLog")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("TeamLog"))) Then
                        ' Team Log
                        If Teams.UserHasAccessToTeam(SessionManager.UserID, Request.Params("TeamLog"), SessionManager.WorkingSiteID) Then
                            Dim objDT As DataTable = Teams.SelectTeams(Request.Params("TeamLog"))
                            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                                Dim drTeam As DataRow = objDT.Rows(0)

                                SessionManager.SelectedTeamID = Request.Params("TeamLog")
                                SessionManager.SelectedTeam = drTeam("Team").ToString
                                If (New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper = "EN") Then
                                    SessionManager.SelectedTeamName = Teams.GetTeamNameOther(SessionManager.SelectedTeamID)
                                Else
                                    SessionManager.SelectedTeamName = Teams.GetTeamName(SessionManager.SelectedTeamID)
                                End If

                                strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamLog1")
                            End If
                        End If
                    ElseIf ("" & Request.Params("MyActions")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("MyActions"))) Then
                        ' My Actions
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("MyActions")
                    ElseIf ("" & Request.Params("AnomalyAction")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("AnomalyAction"))) _
                    AndAlso ("" & Request.Params("Anomaly")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("Anomaly"))) Then
                        ' Anomaly Action
                        SessionManager.SelectedValueAnomalyID = Request.Params("Anomaly")
                        SessionManager.SelectedValueAnomalyActionID = Request.Params("AnomalyAction")
                        SessionManager.AnomalyActionMode = "EditRow"
                        SessionManager.CallingProgram = "MyActions"
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions2")
                    ElseIf ("" & Request.Params("Anomaly")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("Anomaly"))) Then
                        ' Anomaly
                        SessionManager.SelectedValueAnomalyID = Request.Params("Anomaly")
                        SessionManager.AnomalyMode = "EditRow"
                        SessionManager.CallingProgram = "MyActions"
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2")
                    ElseIf ("" & Request.Params("KPI")).Trim.Length > 0 AndAlso IsNumeric(("" & Request.Params("KPI"))) Then
                        ' KPI
                        SessionManager.SelectedValueKPIID = Request.Params("KPI")
                        SessionManager.CallingProgram = "KPICollection"
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIValues1")
                    ElseIf ("" & Request.Params("RoomReservations")).Trim.Length > 0 Then
                        ' Room Reservations parameters
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoomReservations1")
                        SessionManager.RoomReservations = "Y"
                        If Not Request.Params("Site") Is Nothing AndAlso Request.Params("Site").ToString.Trim.Length > 0 Then
                            SessionManager.WorkingSite = SiteMaster.GetSiteNameFromADSite(Request.Params("Site"))
                            SessionManager.WorkingSiteID = SiteMaster.GetSiteFromADSite(Request.Params("Site")).Rows(0).Item(0)
                            If SessionManager.WorkingSite.ToString.Trim.Length = 0 Then
                                ErrorControl.DisplayError(GetTranslationString("error_invalidsitecode", "Invalid Site Code: ") + " " + Request.Params("Site").ToString)
                                Exit Sub
                            End If
                        End If
                    ElseIf ("" & Request.Params("OperationsKPIs")).Trim.Length > 0 Then
                        ' Operations KPIs
                        strURL = Context.Request.ApplicationPath & System.IO.Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("KPIReport2")
                    End If

                    If String.IsNullOrEmpty(strURL) Then
                        ErrorControl.DisplayError(GetTranslationString("error_noaccess"))
                        Exit Sub
                    Else
                        If strInitialMenu.Length = 0 Then
                            ErrorControl.DisplayError(GetTranslationString("error_noaccess"))
                            Exit Sub
                        Else
                            If ProgramMaster.ProgramIsMenu(strInitialMenu) Then
                                SessionManager.CurrentMenuProgram = strInitialMenu
                            Else
                                SessionManager.CurrentMenuProgram = "MainMenu"
                            End If
                        End If
                    End If

                    If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.Login) Then
                        Dim stackFrame As Diagnostics.StackFrame = New Diagnostics.StackTrace(True).GetFrame(0)
                        Dim strMessage As String = stackFrame.GetMethod().DeclaringType.FullName.Trim() & ":" & vbCrLf & "AutoLogin - Culture " & SessionManager.CulturePref
                        strMessage += vbCrLf & "Browser : " & Request.UserAgent.ToString

                        EventTracker.AddNoEmail(stackFrame.GetMethod().Name.Trim(), strMessage, SessionManager.UserID)
                        stackFrame = Nothing
                    End If

                    Response.Redirect(strURL, False)
                Else
                    ErrorControl.DisplayError(GetTranslationString("error_invalidusername"))
                    Return
                End If
            End If
        End Sub
        Private Function ADSValidation() As Boolean
            Dim de As DirectoryEntry
            If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.Login) Then
                EventTracker.AddNoEmail("ADSVAlidation", "", SessionManager.UserID)
            End If
            If txtLogin.Text.Trim.Length = 0 Then
                Return False
            End If

            Try
                Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                de = New DirectoryEntry("LDAP://" & strADDomain, txtLogin.Text.Trim, txtPwd.Text.Trim)
                If de.Name.Length > 0 Then
                    'good
                End If
            Catch ex As Exception
                Return False
            End Try
            Return True
        End Function
#End Region

    End Class
End Namespace
