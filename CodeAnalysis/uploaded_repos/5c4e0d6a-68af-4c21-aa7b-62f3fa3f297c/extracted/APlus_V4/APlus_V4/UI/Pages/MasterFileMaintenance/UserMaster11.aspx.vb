#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Web.Security
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster11
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "User Master"
        Private Shared ReadOnly ProgramName As String = "UserMaster11"
#End Region

#Region " Load JavaScripts"
        Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnExit, btnUserMaster}
            Dim OverMessageArr() As String = {"OK - Enter", "Exit", "User Master"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Dim myTabArray() As Object = {txtUserID, txtPwd}
            Dim TabKeyDownArr() As String = {Tab(txtPwd, txtPwd, "No"), Tab(txtUserID, txtUserID, "No")}
            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.IconImage = Request.ApplicationPath + "/images/user1_add.gif"
            Master.HeaderMessage = "Add User by AD UserID"
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                txtUserID.Text = String.Empty
                txtUserID.Focus()
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If txtUserID.Text.Trim.Length > 0 Then
                    Dim strPwd As String = txtPwd.Text.Trim
                    Dim retValue As InsertADUserError = UserMaster.InsertUserMasterFromAD(txtUserID.Text.Trim, SessionManager.CulturePref, strPwd)
                    Select Case retValue
                        Case InsertADUserError.NoError
                            Master.DisplayError(txtUserID.Text + " added to UserMaster")
                            txtUserID.Text = ""
                            txtUserID.Focus()
                        Case InsertADUserError.InActiveUser
                            Master.DisplayError(txtUserID.Text + " exists in APlus but is not active")
                        Case InsertADUserError.NotValidADUser
                            Master.DisplayError(txtUserID.Text + " is not a valid AD User")
                        Case InsertADUserError.SQLError
                            Master.DisplayError("Database Error")
                        Case InsertADUserError.UnknownError
                            Master.DisplayError("Unknown Error occurred adding user")
                        Case InsertADUserError.UserExistsInAPlus
                            Master.DisplayError(txtUserID.Text + " is already a user in the APlus system")
                        Case Else
                            'nothing
                    End Select
                    Return
                Else
                    Master.DisplayError("Enter UserID")
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnOK_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnUserMaster_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnUserMaster.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMasterMaintenance"), False)
        End Sub
#End Region

    End Class

End Namespace