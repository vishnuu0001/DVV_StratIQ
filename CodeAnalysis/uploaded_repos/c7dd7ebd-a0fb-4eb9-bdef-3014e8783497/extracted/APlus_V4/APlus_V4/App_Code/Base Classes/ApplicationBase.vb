#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports System.IO
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus
    Public Class ApplicationBase
        Inherits Web.UI.Page

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            CheckSessionTimeout()
            DisablePageCaching()

            'open connection to use for page load processing
            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection()

            'Store the current program URL in a Session variable
            SessionManager.CurrentProgramURL = HttpContext.Current.Request.Path.Substring(HttpContext.Current.Request.ApplicationPath.Length + 1)

            'Make sure that we do not do this
            'Login.aspx, do it for other programs
            'because all users can access Login.aspx
            If Request.Path.IndexOf("Login.aspx") = -1 Then
                If SessionManager.UserID <> "" Then
                    'if this is a menu page then we have to authenticate by the program
                    'NOT the URL
                    If Request.Path.IndexOf("Menu.aspx") = -1 Then
                        If Not ProgramSecurity.CanUserAccessCurrentProgramURL(cnMasterConnection) Then
                            'Go back to previous menu
                            RemoveCurrentProgramandGoBack()
                        Else
                            ProgramSecurityFromProgramURL(cnMasterConnection)
                        End If
                    Else
                        If Not ProgramSecurity.CanUserAccessProgram(SessionManager.UserID, SessionManager.CurrentMenuProgram) Then
                            'Go back to previous menu
                            RemoveCurrentProgramandGoBack()
                        Else
                            ProgramSecurityFromProgram(cnMasterConnection)
                        End If
                    End If
                End If
            End If

            Try
                RegionalConversion.ValidateRegionalSettings()
            Catch Tex As Threading.ThreadAbortException
                'This is the top of the trap 'Bubble'
                'exceptions will not be raised any further than this
            Catch Exc As Exception
                EventTracker.Add("ApplicationBase", Exc.ToString(), SessionManager.UserID)
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
                cnMasterConnection.Dispose()
            End Try
        End Sub

        Protected Overrides Sub Render(ByVal writer As System.Web.UI.HtmlTextWriter)
            DisableF1()
            Dim strMessage As String = MessagesMaster.ShowMessageForSession(Session.SessionID, SessionManager.UserID)
            If strMessage.Length > 0 Then
                Dim popupScript As String = "<script language='javascript'>" & "alert('" & strMessage.Replace("'", "`").Replace(vbCrLf, "\n") & "')" & "</script>"
                ClientScript.RegisterStartupScript(Me.GetType, "PopupScript", popupScript)
                MessagesMaster.UpdateMessageSessionID(Session.SessionID, SessionManager.UserID)
            End If
            If SessionManager.ShowPopups.ToString = "YES" Then
                Dim objDS As DataTable = AttachmentsMaster.SelectPopupsByUser(SessionManager.UserID.ToString, SessionManager.WorkingSiteID)

                If Not objDS Is Nothing AndAlso objDS.Rows.Count > 0 Then
                    Dim strDir As String = ConfigurationManager.AppSettings("PopupAttachmentsVirtualRootDirectory")
                    Dim strScript As String
                    For Each dtRow As DataRow In objDS.Rows
                        strScript = "<script language='javascript'>LaunchExplorer('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString
                        strScript += strDir & dtRow("Attachment").ToString & "')" & "</script>"

                        ClientScript.RegisterStartupScript(Me.GetType, "POPUP" + dtRow("AttachmentID").ToString, strScript)
                    Next
                End If
                SessionManager.ShowPopups = "NO"
            End If
            MyBase.Render(writer)
        End Sub
#End Region

#Region " Custom Methods"

#Region " Disable F1/Help Key"
        Private Sub DisableF1()
            Dim sScript As New System.Text.StringBuilder
            sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
            sScript.Append("window.document.onhelp=openHelp;" & vbCrLf)
            sScript.Append("</SCRIPT>" & vbCrLf)
            ClientScript.RegisterStartupScript(Me.GetType, "DisableF1Script", sScript.ToString)
        End Sub
#End Region

#End Region

#Region " Team Stack Functions"
        Public Sub PushTeamOntoStack(ByVal passTeamID As Integer, ByVal passTeam As String, ByVal passOPI As String, ByVal passProgram As String, ByVal passLastMenu As String)
            Dim objStack As Stack

            If SessionManager.TeamStack Is Nothing Then
                objStack = New Stack
                SessionManager.TeamStack = objStack
            End If

            objStack = CType(SessionManager.TeamStack, Stack)
            Dim objStackItem As TeamStackItem = New TeamStackItem()
            objStackItem.TeamID = passTeamID
            objStackItem.TeamName = passTeam
            objStackItem.OPIName = passOPI
            objStackItem.ProgramName = passProgram
            objStackItem.LastMenu = passLastMenu
            objStack.Push(objStackItem)
            SessionManager.TeamStack = objStack
        End Sub
        Public Shared Function PopTeamFromStack() As TeamStackItem
            If Not (SessionManager.TeamStack Is Nothing) Then
                If CType(SessionManager.TeamStack, Stack).Count > 0 Then
                    Return CType(SessionManager.TeamStack, Stack).Pop
                End If
            End If
            Return Nothing
        End Function
#End Region

      
    End Class
End Namespace
