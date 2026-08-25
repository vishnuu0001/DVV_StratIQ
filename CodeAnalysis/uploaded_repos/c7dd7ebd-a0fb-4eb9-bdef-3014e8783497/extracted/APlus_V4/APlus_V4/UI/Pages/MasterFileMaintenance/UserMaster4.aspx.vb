#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster4
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "User Profile"
        Private Shared ReadOnly ProgramName As String = "UserMaster4"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlUserID, _
                                          chkAllUsers, _
                                          txtPassword, _
                                          txtPassword2}

            Dim TabKeyDownArr() As String = {Tab(chkAllUsers, txtPassword2, "No"), _
                                             Tab(txtPassword, ddlUserID, "No"), _
                                             Tab(txtPassword2, chkAllUsers, "No"), _
                                             Tab(ddlUserID, txtPassword, "No")}

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

            Master.IconImage = Request.ApplicationPath + "/images/user1_preferences.gif"
            Master.HeaderMessage = FormName
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            LoadEditModeJavaScripts()

            If Not Page.IsPostBack Then
                LoadUserCombo()
                ddlUserID.Focus()
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

            If chkAllUsers.Checked = True AndAlso ddlUserID.SelectedItem.Text.Trim.Length > 0 Then
                Master.DisplayError("All users selected and user selected in drop down list")
                Return
            ElseIf Not chkAllUsers.Checked AndAlso ddlUserID.SelectedItem.Text.Trim.Length = 0 Then
                Master.DisplayError("All users not selected and no user selected in drop down list")
                Return
            End If

            If txtPassword.Text <> txtPassword2.Text Then
                Master.DisplayError("Passwords do not match")
                Return
            End If

            If chkAllUsers.Checked = True Then
                If ProcessAllUsers() = False Then
                    Return
                End If
            Else
                If ProcessSingleUser() = False Then
                    Return
                End If
            End If
            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
#End Region

#Region " Custom Methods"
        Private Function ProcessAllUsers() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strPWD As String = String.Empty
            Dim iCounter As Integer = 0
            Dim strUser As String = String.Empty

            Try
                For iCounter = 0 To ddlUserID.Items.Count - 1
                    strUser = ddlUserID.Items(iCounter).Value.ToUpper.Trim
                    strPWD = FormsAuthentication.HashPasswordForStoringInConfigFile(txtPassword.Text.ToUpper.Trim + strUser, "sha1")
                    UserMaster.AddNewPassword(strUser, strPWD)
                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, strUser.Trim.ToUpper.Trim(), "User Password Changed", SessionManager.UserID)
                Next
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ProcessAllUsers", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
        Private Function ProcessSingleUser() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strUser As String = ddlUserID.SelectedItem.Value.ToUpper.Trim
                Dim strPWD As String = FormsAuthentication.HashPasswordForStoringInConfigFile(txtPassword.Text.ToUpper.Trim + strUser, "sha1")
                UserMaster.AddNewPassword(strUser, strPWD)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, strUser.Trim.ToUpper.Trim(), "User Password Changed", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ProcessSingleUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
        Private Sub LoadUserCombo()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, ddlUserID)
                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadUserCombo", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

