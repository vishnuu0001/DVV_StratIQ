#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserJobMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "User Job Master"
        Private Shared ReadOnly ProgramName As String = "UserJobMaster2"
        Private Shared ReadOnly DBTableName As String = "UserJobMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - Add User"
            Master.IconImage = Request.ApplicationPath + "/images/usergroup.gif"

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.UserJobMode = "AddRow" OrElse SessionManager.UserJobMode = "AddFromRatings" Then
                    BindUserGrid()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
                End If
            End If
        End Sub

        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            blnSuccess = InsertUserJob()

            If blnSuccess Then
                If SessionManager.UserJobMode = "AddRow" Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobSortOrder)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
                Else
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobSortOrder)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings1"), False)
                End If
            End If
        End Sub

        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.UserJobMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobSortOrder)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserJobMaster1"), False)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobMode)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.UserJobSortOrder)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserSkillRatings1"), False)
            End If
        End Sub

        Protected Sub gvUsers_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvUsers.RowDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Row.RowType = DataControlRowType.DataRow Then
                If CType(e.Row.FindControl("chkAssigned"), CheckBox).Checked = True Then
                    CType(e.Row.FindControl("chkAssigned"), CheckBox).Enabled = False
                End If
            End If
        End Sub

        Protected Sub gvUsers_Sorting(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewSortEventArgs) Handles gvUsers.Sorting
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindUserGrid(e.SortExpression)
        End Sub
#End Region

#Region " Custom Functions"
        Private Function InsertUserJob() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            For Each row As GridViewRow In gvUsers.Rows
                If row.RowType = DataControlRowType.DataRow Then
                    If CType(row.FindControl("chkAssigned"), CheckBox).Checked = True Then
                        Try
                            Dim objDic As New Dictionary(Of String, String)
                            objDic.Add("JobID", SessionManager.SelectedValueJob)
                            objDic.Add("UserID", row.Cells(3).Text.ToUpper.Trim())
                            Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                            If strChangeLog.Trim.Length = 0 Then
                                Return True
                            End If

                            Dim strUser As String = row.Cells(3).Text
                            UserJobMaster.AddUserJob(SessionManager.SelectedValueJob, strUser)
                            RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueJob & "," & row.Cells(3).Text.ToUpper.Trim(), strChangeLog, SessionManager.UserID)
                        Catch Exc As Exception
                            Master.DisplayErrors(ProgramName & " - InsertUserJob", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                            Return False
                        End Try
                    End If
                End If
            Next

            Return True
        End Function
        Private Sub BindUserGrid(Optional ByVal passSortColumn As String = "")
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITraining) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSortColumn)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                If SessionManager.WorkingSite = "" Then
                    Master.DisplayError("Invalid Working Site")
                    Return
                End If

                Dim objDT As DataTable = UserJobMaster.SelectUsersByJob(SessionManager.SelectedValueJob, SessionManager.WorkingSiteID)
                If objDT.Rows.Count > 0 Then
                    Dim objDV As DataView = objDT.DefaultView
                    If passSortColumn.Trim.Length > 0 Then
                        Dim strSortOrder As String = "DESC"
                        If SessionManager.UserJobSortOrder <> "" Then
                            Select Case SessionManager.UserJobSortOrder.ToString.ToUpper
                                Case "ASC"
                                    strSortOrder = "DESC"
                                Case "DESC"
                                    strSortOrder = "ASC"
                                Case Else
                                    strSortOrder = "DESC"
                            End Select
                        Else
                            strSortOrder = "DESC"
                        End If

                        Select Case passSortColumn.Trim.ToUpper
                            Case "NAME"
                                objDV.Sort = "LastName " + strSortOrder + ", FirstName"
                            Case "DEPT"
                                objDV.Sort = "Department " + strSortOrder
                        End Select
                        SessionManager.UserJobSortOrder = strSortOrder
                    End If

                    gvUsers.DataSource = objDV
                    gvUsers.DataBind()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
#End Region

    End Class
End Namespace