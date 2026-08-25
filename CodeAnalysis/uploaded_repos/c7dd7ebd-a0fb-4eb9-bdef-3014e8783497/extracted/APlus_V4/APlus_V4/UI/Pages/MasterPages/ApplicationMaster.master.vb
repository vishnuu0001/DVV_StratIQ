#Region " Imports"
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.CustomControls
Imports System.IO
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class ApplicationMaster
        Inherits System.Web.UI.MasterPage

#Region " Private Variables"
        Private _EnvironmentMessage As String = String.Empty
        Private _hideAPlusIcon As Boolean = False
        Private _minimalicons As Boolean = False
        Private _hideicons As Boolean
        Private _hideenvironmentmessage As Boolean
        Private _imageurl As String = String.Empty
        Private _WelcomeMessage As String = String.Empty
        Private _HideHeader As Boolean = False
        Private _ProgramName As String = ""
        Private _ScrollPosition As Integer = 0
        Private _ShowWorkingSiteDropDown As Boolean = False
#End Region

#Region " Public Properties / Events"
        Public Event RefreshWorkingSite()

        Public WriteOnly Property HideHeader() As Boolean
            Set(ByVal value As Boolean)
                _HideHeader = value
            End Set
        End Property
        Public WriteOnly Property IconImage() As String
            Set(ByVal value As String)
                _imageurl = value
            End Set
        End Property
        Public WriteOnly Property HeaderMessage() As String
            Set(ByVal value As String)
                _WelcomeMessage = value.Trim
            End Set
        End Property
        Public WriteOnly Property HideIcons() As Boolean
            Set(ByVal value As Boolean)
                _hideicons = value
            End Set
        End Property
        Public WriteOnly Property HideAPlusIcon() As Boolean
            Set(ByVal value As Boolean)
                _hideAPlusIcon = value
            End Set
        End Property
        Public Property MinimalIcons() As Boolean
            Get
                Return _minimalicons
            End Get
            Set(ByVal Value As Boolean)
                _minimalicons = Value
            End Set
        End Property
        Public WriteOnly Property HideEnvironmentMessage() As Boolean
            Set(ByVal value As Boolean)
                _hideenvironmentmessage = value
            End Set
        End Property
        Public ReadOnly Property MasterScriptManager() As ScriptManager
            Get
                Return ScriptManager1
            End Get
        End Property
        Public WriteOnly Property EnableTeamLink() As Boolean
            Set(ByVal value As Boolean)
                lbPreviousTeam.Visible = value
            End Set
        End Property
        Public Property ProgramName() As String
            Get
                Return _ProgramName.Trim
            End Get
            Set(ByVal value As String)
                _ProgramName = value.Trim
            End Set
        End Property
        Public ReadOnly Property LastPixelPosition() As Integer
            Get
                Return _ScrollPosition
            End Get
        End Property
        Public ReadOnly Property CurrentPixelPosition() As Integer
            Get
                If scrollPositionPx.Text = String.Empty Then
                    Return 0
                Else
                    Return CType(scrollPositionPx.Text, Integer)
                End If
            End Get
        End Property
        Public Property ShowWorkingSiteDropDown() As Boolean
            Get
                Return _ShowWorkingSiteDropDown
            End Get
            Set(ByVal value As Boolean)
                _ShowWorkingSiteDropDown = value
            End Set
        End Property
#End Region

#Region "Event Handlers"
        Protected Sub Page_Init(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Init
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim js As New HtmlGenericControl("script")
            js.Attributes("type") = "text/javascript"
            js.Attributes("src") = ResolveUrl("~/Scripts/CommonFunctions.js")
            Page.Header.Controls.Add(js)

            Page.ClientScript.RegisterOnSubmitStatement(Page.GetType(), "submit-handler", "onUploadStarted();")
            AddBodyAttribute("onkeydown", "fnTrapKD(window.event)")
        End Sub
        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not Page.IsPostBack Then
                _ScrollPosition = LastPixelPositionGet(_ProgramName)

                If _ShowWorkingSiteDropDown AndAlso ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, "ChangeWorkingSite") Then
                    SiteMaster.SelectSiteMasterActiveList(ddlSite)
                    'ddlSite.Items.Insert(0, New ListItem("No Working Site", 0))
                    Dim objItem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        ddlSite.Visible = True
                        lblSelectedSite.Visible = False
                    Else
                        ddlSite.Visible = False
                        lblSelectedSite.Visible = True

                        If Not String.IsNullOrEmpty(SessionManager.WorkingSite) Then
                            lblSelectedSite.Text = SessionManager.WorkingSite.ToString
                        Else
                            lblSelectedSite.Visible = False
                            lblSeperator1.Visible = False
                        End If
                    End If
                Else
                    ddlSite.Visible = False
                    lblSelectedSite.Visible = True

                    If Not String.IsNullOrEmpty(SessionManager.WorkingSite) Then
                        lblSelectedSite.Text = SessionManager.WorkingSite.ToString
                    Else
                        lblSelectedSite.Visible = False
                        lblSeperator1.Visible = False
                    End If
                End If
            End If

            If _HideHeader Then
                pnlHeader.Visible = False
            Else
                pnlHeader.Visible = True

                Dim ProgramURL As String = HttpContext.Current.Request.Path.Substring(HttpContext.Current.Request.ApplicationPath.Length + 1)

                LoadCultureTranslations()

                'get the environment message if one exists
                If ConfigurationManager.AppSettings("EnvironmentMessage").Trim <> String.Empty Then
                    _EnvironmentMessage = ConfigurationManager.AppSettings("EnvironmentMessage").Trim

                    If ConfigurationManager.AppSettings("ShowEnvironmentMessage") = "True" Then
                        lblEnvironmentMessage.Visible = True
                    Else
                        lblEnvironmentMessage.Visible = False
                    End If
                Else
                    lblEnvironmentMessage.Visible = False
                End If

                Dim cnMasterConnection As System.Data.SqlClient.SqlConnection = ApplicationConnection.OpenMasterConnection()
                Dim strHelpFile As String = ProgramMaster.GetHelpFile(ProgramURL, cnMasterConnection)
                Dim strHelpURL As String = ""
                Dim strSessionID As String = Session.SessionID.ToString
                strSessionID = "(S(" + strSessionID + "))"

                'If strHelpFile.Trim.Length > 0 Then
                '    strHelpURL = "http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & ConfigurationManager.AppSettings("HelpAttachmentsVirtualRootDirectory").ToString & strHelpFile.Trim
                'Else
                '    strHelpURL = HttpContext.Current.Request.ApplicationPath & "/" & strSessionID & "/UI/Pages/MasterFileMaintenance/HelpAttachmentsPopup.aspx"
                'End If
                strHelpURL = ConfigurationManager.AppSettings("HelpAttachmentsURL").ToString
                ' Try to get this URL based on the logged in persons site
                Dim iSiteID As Integer = 0

                'Check the working site first
                If SessionManager.WorkingSiteID > 0 Then
                    iSiteID = SessionManager.WorkingSiteID
                End If

                'if we still don't have a site then get it from the database
                If iSiteID = 0 Then
                    If (SessionManager.UserID) IsNot Nothing Then
                        If Not String.IsNullOrEmpty(SessionManager.UserID.ToString.Trim()) Then
                            iSiteID = UserMaster.GetUserSite(SessionManager.UserID.ToString)
                        End If
                    End If
                End If

                'if user is admin then enable session info page
                If SessionManager.IsAdministrator = True Then
                    imgAplus.Attributes.Add("onclick", "window.open('/APlus/" + strSessionID + "/UI/Pages/MasterFileMaintenance/SessionInfo.aspx','newWin','height=500, width=500, left=400, top=100, resizable=yes, scrollbars=1');")
                End If

                'Check web.config setting for feedback
                If ConfigurationManager.AppSettings("DisableFeedback") IsNot Nothing AndAlso ConfigurationManager.AppSettings("DisableFeedback").ToString.Trim.ToUpper = "TRUE" Then
                    'only show feedback if user is admin
                    If Not SessionManager.IsAdministrator Then
                        imgFeedback.Visible = False
                    End If
                End If

                If _hideAPlusIcon Then
                    imgApplicationLogo.Visible = False
                End If

                If _minimalicons Then
                    imgPrint.Visible = False
                    imgHelp.Visible = False
                    imgDoc.Visible = False
                    imgAplus.Src = "../../../Images/company_logo.png"

                    If SessionManager.IsAdministrator Then
                        imgFeedback.Attributes.Add("onclick", "window.showModalDialog('/APlus/" + strSessionID + "/UI/Pages/MasterFileMaintenance/Feedback.aspx','newWin','dialogHeight:416px; dialogWidth:439px; status=no; resizable=no; help: No;');")
                    Else
                        If ConfigurationManager.AppSettings("ServiceDeskLink") IsNot Nothing AndAlso ConfigurationManager.AppSettings("ServiceDeskLink").ToString.Trim.Length > 0 Then
                            imgFeedback.Alt = "Create IT Request..."
                            imgFeedback.Attributes.Add("onclick", "window.open('" & ConfigurationManager.AppSettings("ServiceDeskLink").ToString.Trim & "','newWin','');")
                        Else
                            imgFeedback.Visible = False
                        End If
                    End If
                Else
                    If _hideicons = False Then
                        Dim strLinkFolder As String = ""

                        If SessionManager.SelectedTeamID > 0 Then
                            strLinkFolder = Teams.GetTeamFolder(SessionManager.SelectedTeamID)
                        End If
                        If strLinkFolder.Trim.Length = 0 Then
                            If iSiteID > 0 Then
                                strLinkFolder = SiteMaster.GetSiteFolderIconLink(iSiteID)
                            Else
                                strLinkFolder = "about:blank"
                            End If

                        End If

                        strLinkFolder = strLinkFolder.Replace("\", "\\")
                        imgDoc.Attributes.Add("onclick", "javascript:LaunchExplorer('" + strLinkFolder + "');")

                        If SessionManager.IsAdministrator Then
                            imgFeedback.Attributes.Add("onclick", "window.showModalDialog('/APlus/" + strSessionID + "/UI/Pages/MasterFileMaintenance/Feedback.aspx','newWin','dialogHeight:416px; dialogWidth:439px; status=no; resizable=no; help: No;');")
                        Else
                            If ConfigurationManager.AppSettings("ServiceDeskLink") IsNot Nothing AndAlso ConfigurationManager.AppSettings("ServiceDeskLink").ToString.Trim.Length > 0 Then
                                imgFeedback.Alt = "Create IT Request..."
                                imgFeedback.Attributes.Add("onclick", "window.open('" & ConfigurationManager.AppSettings("ServiceDeskLink").ToString.Trim & "','newWin','');")
                            Else
                                imgFeedback.Visible = False
                            End If
                        End If

                        imgHelp.Attributes.Add("onclick", "window.open('" & strHelpURL & "','newWin','height=500, width=500, left=400, top=100, resizable=yes, scrollbars=1');")
                    Else
                        imgFeedback.Visible = False
                        imgPrint.Visible = False
                        imgHelp.Visible = False
                        imgDoc.Visible = False
                        imgAplus.Src = "../../../images/company_logo.png"
                    End If
                End If

                If _hideenvironmentmessage = False Then
                    lblEnvironmentMessage.Visible = True
                Else
                    lblEnvironmentMessage.Visible = False
                End If

                If SessionManager.SelectedTeamID > 0 Then
                    pnlTeamSubheader.Visible = True

                    lblSelectedTeam.Text = "Team: " & SessionManager.SelectedTeam.ToString
                    lblSelectedTeamName.Text = SessionManager.SelectedTeamName.ToString

                    If Not (SessionManager.TeamStack Is Nothing) Then
                        If CType(SessionManager.TeamStack, Stack).Count > 0 Then
                            Dim objTeamStack As TeamStackItem = CType(SessionManager.TeamStack, Stack).Peek

                            If objTeamStack.TeamName = "" And objTeamStack.ProgramName.Trim.Length > 0 Then
                                lbPreviousTeam.Text = GetTranslationString("return", "Return")
                            Else
                                lbPreviousTeam.Text = GetTranslationString("return", "Return") & ": " & objTeamStack.TeamName & " - " & DataAccess.Tables.Teams.GetTeamName(objTeamStack.TeamID)
                            End If

                            lbPreviousTeam.ID = "PreviousTeam"

                            lbPreviousTeam.Attributes.Add("onclick", "javascript:__doPostBack('PreviousTeam','')")
                            AddHandler lbPreviousTeam.Click, AddressOf PreviousTeam_Click
                        Else
                            lbPreviousTeam.Text = ""
                        End If
                    End If

                    If SessionManager.SelectedOPI IsNot Nothing AndAlso SessionManager.SelectedOPI.ToString.Trim.Length > 0 Then
                        lblSelectedOPI.Text = "OPI: " & SessionManager.SelectedOPI.ToString.Trim
                    End If
                Else
                    pnlTeamSubheader.Visible = False
                End If

                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End If
        End Sub
        Protected Sub Page_PreRender(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreRender
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'initialize header information
            imgIcon.ImageUrl = _imageurl
            lblWelcome.Text = _WelcomeMessage.Trim
            lblEnvironmentMessage.Text = _EnvironmentMessage.Trim

            If SessionManager.UserID <> "" Then
                lblUserID.Text = SessionManager.UserID.ToString
            Else
                lblUserID.Visible = False
                lblSeperator2.Visible = False
            End If
            lblDate.Text = Now.ToLongDateString

        End Sub
        Private Sub PreviousTeam_Click(ByVal sender As Object, ByVal e As System.EventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim objTeamStack As TeamStackItem = CType(SessionManager.TeamStack, Stack).Pop

            If objTeamStack.TeamName = "" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamName)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeam)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPI)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedTeamAllowEdit)

                If objTeamStack.LastMenu.Trim.Length > 0 Then
                    SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                End If
                If objTeamStack.ProgramName.ToString.Trim.Length > 0 Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
                End If
            Else
                SessionManager.SelectedOPI = objTeamStack.OPIName
                SessionManager.SelectedTeamID = objTeamStack.TeamID
                SessionManager.SelectedTeam = objTeamStack.TeamName
                SessionManager.SelectedTeamName = DataAccess.Tables.Teams.GetTeamName(SessionManager.SelectedTeamID)
                SessionManager.CurrentMenuProgram = objTeamStack.LastMenu
                SessionManager.SelectedTeamAllowEdit = UserSiteMaster.SelectTeamAllowEdit(SessionManager.SelectedTeamID, SessionManager.UserID)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & DataAccess.Custom.ProgramSecurity.GetProgramURL(objTeamStack.ProgramName), False)
            End If
        End Sub
        Protected Sub ddlSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlSite.SelectedIndexChanged
            If ddlSite.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlSite.SelectedItem.Value) Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.WorkingSite)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.WorkingSiteID)

                If Convert.ToInt32(ddlSite.SelectedItem.Value) > 0 Then
                    SessionManager.WorkingSite = ddlSite.SelectedItem.Text
                    SessionManager.WorkingSiteID = ddlSite.SelectedItem.Value
                End If

                RaiseEvent RefreshWorkingSite()
            End If
        End Sub
#End Region

#Region "Error Control Methods"
        Public Sub DisplayError(ByVal passErrorMessage As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passErrorMessage)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayError(passErrorMessage)
        End Sub
        Public Sub DisplayManualErrors(ByVal passEventName As String, ByVal passException As String, ByVal passUserID As String, ByVal passErrorType As ApplicationErrorControl.ApplicationErrorMessages)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException, _
                                                                                     passUserID, _
                                                                                     passErrorType)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayManualErrors(passEventName, passException, passUserID)
        End Sub
        Public Sub DisplayErrors(ByVal passEventName As String, ByVal passException As UnauthorizedAccessException, ByVal passUserID As String, ByVal passErrorType As ApplicationErrorControl.ApplicationErrorMessages)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException.ToString, _
                                                                                     passUserID, _
                                                                                     passErrorType)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayErrors(passEventName, passException, passUserID, passErrorType)
        End Sub
        Public Sub DisplayErrors(ByVal passEventName As String, ByVal passException As Exception, ByVal passUserID As String, ByVal passErrorType As ApplicationErrorControl.ApplicationErrorMessages)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException.ToString, _
                                                                                     passUserID, _
                                                                                     passErrorType)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.DisplayErrors(passEventName, passException, passUserID, passErrorType)
        End Sub
        Public Sub WriteErrors(ByVal passEventName As String, ByVal passException As Exception, ByVal passUserID As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passException.ToString, _
                                                                                     passUserID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.WriteErrors(passEventName, passException, passUserID)
        End Sub
        Public Sub WriteErrors(ByVal passEventName As String, ByVal passMessage As String, ByVal passUserID As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passEventName, _
                                                                                     passMessage, _
                                                                                     passUserID)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            ErrorControl.WriteErrors(passEventName, passMessage, passUserID)
        End Sub
#End Region

#Region "Custom Methods"
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            imgFeedback.Attributes("Title") = GetTranslationString("feedback", "Feedback")
            imgPrint.Attributes("Title") = GetTranslationString("print", "Print")
            imgHelp.Attributes("Title") = GetTranslationString("help", "Help")
            imgDoc.Attributes("Title") = GetTranslationString("teamfolder", "Team Folder")
        End Sub
        Public Sub AddHeaderStyleSheetLink(ByVal passLinkHref As String)
            ' Calling Convention
            ' Master.AddHeaderStyleSheetLink("~/Styles/ApplicationMasterStyles.css")
            '

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passLinkHref)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objLink As New HtmlLink()
                objLink.Attributes.Add("type", "text/css")
                objLink.Attributes.Add("rel", "stylesheet")
                objLink.Attributes.Add("href", passLinkHref)

                Me.Head1.Controls.Add(objLink)
            Catch ex As Exception
                'exit gracefully
            End Try
        End Sub
        Public Sub AddBodyAttribute(ByVal passEvent As String, ByVal passAction As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passEvent, passAction)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Body1.Attributes.Item(passEvent) Is Nothing Then
                Body1.Attributes.Add(passEvent, passAction)
            ElseIf Body1.Attributes.Item(passEvent).Trim.Length > 0 Then
                If Body1.Attributes.Item(passEvent).ToString.Contains(passAction) = False Then
                    passAction = Body1.Attributes.Item(passEvent).ToString + ";" + passAction
                    Body1.Attributes.Add(passEvent, passAction)
                End If
            Else
                Body1.Attributes.Add(passEvent, passAction)
            End If
        End Sub
        Public Sub RemoveBodyAttribute(ByVal passEvent As String, ByVal passAction As String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passEvent, passAction)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Body1.Attributes.Item(passEvent).Trim.Length > 0 Then
                If Body1.Attributes.Item(passEvent).Contains(passAction) Then
                    Dim iFunctionStart As Integer = Body1.Attributes.Item(passEvent).IndexOf(passAction)
                    Dim iFunctionEnd As Integer = Body1.Attributes.Item(passEvent).IndexOf(";", iFunctionStart)
                    If iFunctionEnd = -1 Then
                        iFunctionEnd = Body1.Attributes.Item(passEvent).Length
                    End If
                    Dim strEvent As String = Body1.Attributes.Item(passEvent).Substring(0, iFunctionStart - 1).Trim
                    strEvent += Body1.Attributes.Item(passEvent).Substring(iFunctionEnd, Body1.Attributes.Item(passEvent).Length - iFunctionEnd).Trim

                    Body1.Attributes.Item(passEvent) = strEvent
                End If
            End If
        End Sub
#End Region

    End Class
End Namespace

