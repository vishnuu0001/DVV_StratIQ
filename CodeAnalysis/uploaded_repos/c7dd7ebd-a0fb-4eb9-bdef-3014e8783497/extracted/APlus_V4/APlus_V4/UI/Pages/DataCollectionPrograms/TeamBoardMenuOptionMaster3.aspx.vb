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
    Partial Class TeamBoardMenuOptionMaster3
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Board Menu Option Master"
        Private Shared ReadOnly ProgramName As String = "TeamBoardMenuOptionMaster3"
        Private Shared ReadOnly DBTableName As String = "TeamBoardMenuOptionMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
#End Region

#Region " Load Culture Translations "
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.IconImage = Request.ApplicationPath + "/images/TeamBoard.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.SelectedTeamID = 0 AndAlso SessionManager.SelectedValueTeamID = 0 Then
                    RemoveCurrentProgramandGoBack()
                End If

                LoadCultureTranslations()

                LoadGrids()
            End If
        End Sub
        Protected Sub gvMenuOptions_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvMenuOptions.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If Convert.ToBoolean(gvMenuOptions.DataKeys(e.Row.RowIndex)("BoardDefault")) Then
                    Try
                        DirectCast(e.Row.Cells(0).FindControl("chkSelected"), CheckBox).Checked = True
                    Catch ex As Exception
                    End Try
                End If
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim iTeamID As Integer = SessionManager.SelectedValueTeamID
                If iTeamID = 0 Then
                    iTeamID = SessionManager.SelectedTeamID
                End If

                TeamBoardMenuOptionMaster.DeleteTeamBoardMenuOptionMasterByTeam(iTeamID)
                RecordTransactionHistory.InsertRecordTransactionHistory("Teams", iTeamID, "Team Board Menu Reset", SessionManager.UserID)

                Dim iOptionID As Integer = 0
                Dim objDic As Dictionary(Of String, String)
                Dim strChangeLog As String = String.Empty
                Dim strTeam As String = mcTeam.Rows(0).Cells(1).Text
                Dim strOptions As String = String.Empty

                For Each row As GridViewRow In gvMenuOptions.Rows
                    If row.RowType = DataControlRowType.DataRow Then
                        Try
                            If DirectCast(row.FindControl("chkSelected"), CheckBox).Checked Then
                                iOptionID = Convert.ToInt16(gvMenuOptions.DataKeys(row.RowIndex)("TeamBoardMenuDefaultsID"))

                                If iOptionID > 0 Then
                                    If strOptions.Trim.Length > 0 Then
                                        strOptions += ","
                                    End If

                                    strOptions += iOptionID.ToString.Trim
                                End If
                            End If
                        Catch ex As Exception

                        End Try
                    End If
                Next

                If strOptions.Trim.Length > 0 Then
                    TeamBoardMenuDefaults.UpdateTeamBoardMenuOptionsDefault(iTeamID, strOptions)

                    Dim dt As DataTable = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterByTeam(iTeamID)
                    If dt.Rows.Count > 0 Then
                        For Each row As DataRow In dt.Rows
                            objDic = New Dictionary(Of String, String)
                            objDic.Add("Team", strTeam.Trim())
                            objDic.Add("BoardColumn", row.Item("BoardColumn").ToString.Trim())
                            objDic.Add("BoardRow", row.Item("BoardRow").ToString.Trim())
                            objDic.Add("RCSequence", row.Item("RCSequence").ToString.Trim())
                            objDic.Add("BoardDescription", row.Item("BoardDescription").ToString.Trim())
                            objDic.Add("LinkType", row.Item("LinkType").ToString.Trim())
                            objDic.Add("Program", row.Item("Program").ToString.Trim())
                            objDic.Add("LinkFileURL", row.Item("LinkFileURL").ToString.Trim())
                            strChangeLog = TransactionProcessing.GetDictionaryValues(objDic)
                            RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptionMaster", row.Item("MenuOptionID"), strChangeLog, SessionManager.UserID)
                        Next
                    End If
                End If

                If chkRoute.Checked Then
                    InsertRouteStepKeyActionToolsByRouteAbbrevToTeamBoardMenuOptionMaster()
                End If

                Dim strProgram As String = ""
                If Not String.IsNullOrEmpty(SessionManager.RedirectProgram) Then
                    strProgram = SessionManager.RedirectProgram.Trim
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RedirectProgram)
                ElseIf Not String.IsNullOrEmpty(SessionManager.MasterControlExitProgram2) Then
                    strProgram = SessionManager.MasterControlExitProgram2.Trim
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram2)
                End If

                If Not String.IsNullOrEmpty(strProgram) Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
                Else
                    RemoveCurrentProgramandGoBack()
                End If
            Catch ex As Exception

            End Try
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strProgram As String = ""
            If Not String.IsNullOrEmpty(SessionManager.RedirectProgram) Then
                strProgram = SessionManager.RedirectProgram.Trim
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.RedirectProgram)
            ElseIf Not String.IsNullOrEmpty(SessionManager.MasterControlExitProgram2) Then
                strProgram = SessionManager.MasterControlExitProgram2.Trim
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.MasterControlExitProgram2)
            End If

            If Not String.IsNullOrEmpty(strProgram) Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
            Else
                RemoveCurrentProgramandGoBack()
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadGrids()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim iTeamID As Integer = SessionManager.SelectedTeamID
                If iTeamID = 0 Then
                    iTeamID = SessionManager.SelectedValueTeamID
                End If

                mcTeam.StoredProcedureParams.Add("@TeamID", iTeamID)
                mcTeam.DataBind()

                Dim objDT As DataTable = TeamBoardMenuDefaults.SelectTeamBoardMenuDefaultsByTeam(iTeamID)
                gvMenuOptions.DataSource = objDT
                gvMenuOptions.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function InsertRouteStepKeyActionToolsByRouteAbbrevToTeamBoardMenuOptionMaster() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim iTeamID As Integer = SessionManager.SelectedValueTeamID
                If iTeamID = 0 Then
                    iTeamID = SessionManager.SelectedTeamID
                End If

                Dim strRoute As String = Teams.GetTeamRoute(iTeamID)
                If String.IsNullOrEmpty(strRoute) Then
                    Return True
                End If

                Dim dt As DataTable = RouteStepsKeyActionsTools.SelectRouteStepsKeyActionsToolsByRouteAbbrev(strRoute)
                If dt.Rows.Count <> 0 Then
                    Dim iBoardColumn As Integer = 0
                    Dim iBoardRow As Integer = 0
                    Dim intRCSequence As Integer = 0
                    Dim strBoardDescription As String = String.Empty
                    Dim strLinkType As String = String.Empty
                    Dim strLinkFileURL As String = String.Empty
                    Dim strTeam As String = mcTeam.Rows(0).Cells(0).Text

                    For Each dr As DataRow In dt.Rows
                        iBoardColumn = Convert.ToInt32(dr("StepNo")) + 2
                        iBoardRow = Convert.ToInt32(dr("KeyActionNo"))
                        If iBoardRow >= 4 Then
                            iBoardRow = 4
                        End If
                        intRCSequence = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterNextSequence(SessionManager.SelectedValueTeamID, iBoardRow, iBoardColumn)
                        strBoardDescription = dr("Tool")

                        If Not dr("AttachmentID") Is DBNull.Value AndAlso dr("AttachmentID") > 0 Then
                            strLinkFileURL = dr.Item("Attachment").ToString.Trim()
                            If dr.Item("AttachmentType").ToString.Trim() = "Template" Then
                                strLinkType = "L"
                            ElseIf dr.Item("AttachmentType").ToString.Trim() = "Training" Then
                                strLinkType = "Z"
                            End If
                        ElseIf Not dr("URLLink") Is DBNull.Value AndAlso dr("URLLink").ToString.Trim.Length > 0 Then
                            strLinkFileURL = dr("URLLink").ToString
                            strLinkType = "U"
                        Else
                            strLinkFileURL = ""
                            strLinkType = "D"
                        End If

                        Try
                            Dim intResult As Integer = TeamBoardMenuOptionMaster.AddTeamBoardMenuOptionMaster(SessionManager.SelectedValueTeamID, iBoardColumn, iBoardRow, intRCSequence, strBoardDescription, strLinkType, "", strLinkFileURL)
                            Dim objDic As New Dictionary(Of String, String)
                            objDic.Add("Team", strTeam)
                            objDic.Add("BoardColumn", iBoardColumn.ToString.Trim())
                            objDic.Add("BoardRow", iBoardRow.ToString.Trim())
                            objDic.Add("RCSequence", intRCSequence.ToString.Trim())
                            objDic.Add("BoardDescription", strBoardDescription.Trim())
                            objDic.Add("LinkType", strLinkType.Trim())
                            objDic.Add("Program", "")
                            objDic.Add("LinkFileURL", strLinkFileURL.Trim())
                            Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                            RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptionMaster", intResult, strChangeLog, SessionManager.UserID)
                        Catch Exc As Exception
                            Throw
                        End Try
                    Next
                End If

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertRouteStepKeyActionByRouteAbbrevToTeamBoardMenuOptionMaster", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace