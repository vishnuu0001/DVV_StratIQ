#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Web.Security
Imports System.DirectoryServices
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster13
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "User Master Attendance Compare"
        Private Shared ReadOnly ProgramName As String = "UserMaster13"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
#End Region

#Region " Load JavaScripts"
        Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
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
            Master.HeaderMessage = FormName & " - Edit User"
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.UserITMode
                    Case "EditRow"
                        BindSite()
                        LoadSelectedRecord()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster12"), False)
                End Select
            End If
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

            Dim strParam As String = SessionManager.UserITMode
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserITMode)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster12"), False)
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

            Dim blnSuccess As Boolean = UpdateUser()
            If blnSuccess Then
                Dim strParam As String = SessionManager.UserITMode
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserITMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster12"), False)
            End If
        End Sub
#End Region

#Region " Custom Functions"
        Private Sub BindSite()
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
                SiteMaster.SelectSiteMasterList(ddlSite)
                ddlSite.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSite", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function UpdateUser() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If
                UserMaster.UpdateADUserMaster(txtUserID.Text.Trim, ddlSite.SelectedItem.Value, txtLastName.Text.Trim(), txtFirstName.Text.Trim(), txtMiddleInitial.Text.Trim(), txtTitle.Text.Trim(), txtEmailAddress.Text.Trim(), ckActive.Checked)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, txtUserID.Text.Trim, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateADUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Sub LoadSelectedRecord()
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
                Dim ds As DataTable = UserMaster.SelectUserMaster(SessionManager.SelectedValue)
                If ds.Rows.Count <> 0 Then
                    Dim dr As DataRow = ds.Rows(0)
                    Dim objItem As ListItem

                    txtUserID.Text = dr.Item("UserID").ToString.Trim()
                    txtFirstName.Text = dr.Item("FirstName").ToString.Trim()
                    txtLastName.Text = dr.Item("LastName").ToString.Trim()
                    txtMiddleInitial.Text = dr.Item("MiddleInitial").ToString
                    txtTitle.Text = dr.Item("Title").ToString
                    txtEmailAddress.Text = dr.Item("EmailAddress").ToString

                    objItem = ddlSite.Items.FindByValue(dr("SiteID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If

                    ckActive.Checked = dr("Active")

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("FirstName", txtFirstName.Text.Trim())
                    objDic.Add("LastName", txtLastName.Text.Trim())
                    objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
                    objDic.Add("Suffix", "")
                    objDic.Add("DeptNumber", "")
                    objDic.Add("InitialProgram", "")
                    objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
                    objDic.Add("Culture", "")
                    objDic.Add("Title", txtTitle.Text.Trim())
                    objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
                    objDic.Add("IsAdministrator", False)
                    objDic.Add("RegTemp", False)
                    objDic.Add("Active", ckActive.Checked)
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If

                Dim dtIT As DataTable = AttendanceAccess.SelectUserMaster(txtUserID.Text)
                If Not dtIT Is Nothing AndAlso dtIT.Rows.Count > 0 Then
                    Dim dtRow As DataRow = dtIT.Rows(0)

                    txtITUserID.Text = dtRow("UserID").ToString.Trim()
                    txtITFirstName.Text = dtRow("FirstName").ToString.Trim()
                    txtITLastName.Text = dtRow("LastName").ToString.Trim()
                    txtITMiddleInitial.Text = dtRow("MiddleInitial").ToString
                    txtITTitle.Text = dtRow("Title").ToString
                    txtITEmailAddress.Text = dtRow("EmailAddress").ToString
                    txtITSite.Text = dtRow("Site").ToString
                    ckITActive.Checked = dtRow("Active")
                End If

                'now, indicate what the differences are
                If txtFirstName.Text.ToUpper <> txtITFirstName.Text.ToUpper Then
                    lblDifFirstName.Visible = True
                End If
                If txtLastName.Text.ToUpper <> txtITLastName.Text.ToUpper Then
                    lblDifLastName.Visible = True
                End If
                If txtMiddleInitial.Text.ToUpper <> txtITMiddleInitial.Text.ToUpper Then
                    lblDifMiddle.Visible = True
                End If
                If ddlSite.SelectedItem.Text.ToUpper.IndexOf(txtITSite.Text.ToUpper) < 0 Then
                    lblDifSite.Visible = True
                End If

                Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")

                If txtEmailAddress.Text.ToUpper <> Replace(txtITEmailAddress.Text, strADDomain & ".net", strDomain).ToUpper Then
                    lblDifEmail.Visible = True
                End If
                If ckActive.Checked <> ckITActive.Checked Then
                    lblDifActive.Visible = True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("FirstName", txtFirstName.Text.Trim())
            objDic.Add("LastName", txtLastName.Text.Trim())
            objDic.Add("MiddleInitial", txtMiddleInitial.Text.Trim())
            objDic.Add("Suffix", "")
            objDic.Add("DeptNumber", "")
            objDic.Add("InitialProgram", "")
            objDic.Add("Site", ddlSite.SelectedItem.Text.Trim())
            objDic.Add("Culture", "")
            objDic.Add("Title", txtTitle.Text.Trim())
            objDic.Add("EmailAddress", txtEmailAddress.Text.Trim())
            objDic.Add("IsAdministrator", False)
            objDic.Add("RegTemp", False)
            objDic.Add("Active", ckActive.Checked)
            Return objDic
        End Function
#End Region

    End Class
End Namespace
