#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class FeedbackMaster2
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Feedback Master"
        Private Shared ReadOnly ProgramName As String = "FeedbackMaster2"
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
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtExpandComments, _
                                          ddlFeedbackType, _
                                          ddlFeedbackPriority, _
                                          txtExpandDevComments, _
                                          chkProcessed, _
                                          chkSendEmail}
            Dim TabKeyDownArr() As String = {Tab(ddlFeedbackType, chkSendEmail, "No"), _
                                             Tab(ddlFeedbackPriority, txtExpandComments, "No"), _
                                             Tab(txtExpandDevComments, ddlFeedbackType, "No"), _
                                             Tab(chkProcessed, ddlFeedbackPriority, "No"), _
                                             Tab(chkSendEmail, txtExpandDevComments, "No"), _
                                             Tab(txtExpandComments, chkProcessed, "No")}

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

            Master.IconImage = Request.ApplicationPath + "/images/FeedbackMaster.gif"
            Master.HeaderMessage = FormName & " - " & SessionManager.FeedbackMode.Replace("Row", "") & " Feedback"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                If SessionManager.FeedbackMode = "EditRow" Then
                    LoadSelectedRecord()
                    LoadEditModeJavaScripts()
                    txtExpandComments.Focus()
                Else
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FeedbackMasterMaintenance"), False)
                End If
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

            Dim blnSuccess As Boolean

            If SessionManager.FeedbackMode = "EditRow" Then
                blnSuccess = UpdateFeedback()
            End If

            If blnSuccess Then
                If chkSendEmail.Checked = True Then
                    Dim strTo As String = UserMaster.GetUserEmail(txtUserID.Text)
                    Dim strFrom As String = UserMaster.GetUserEmail(SessionManager.UserID)
                    If strFrom.Trim.Length = 0 Then
                        strFrom = SessionManager.UserName

                        If strFrom.Trim.Length = 0 Then
                            strFrom = SessionManager.UserID
                        End If
                    End If

                    If strTo.Trim.Length > 0 Then
                        If SendEmail(strTo, strFrom, "Feedback Notification: " + txtID.Text, txtExpandComments.Text.Trim) = False Then
                            Master.WriteErrors(FormName, "Error Sending Feedback Email : " & txtID.Text, SessionManager.UserID)
                        End If
                    End If
                End If
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.FeedbackMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FeedbackMasterMaintenance"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("FeedbackMasterMaintenance"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDownBoxes()
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
                ddlFeedbackType.Items.Clear()
                FeedbackTypeMaster.SelectFeedbackTypeMasterList(ddlFeedbackType)

                ddlFeedbackPriority.Items.Clear()
                FeedbackPriorityMaster.SelectFeedbackPriorityMasterList(ddlFeedbackPriority)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropDownBoxes", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
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
                LoadDropDownBoxes()

                Dim dt As DataTable = FeedbackMaster.SelectFeedback(CInt(SessionManager.SelectedValue))
                Dim objItem As ListItem

                If dt.Rows.Count > 0 Then
                    Dim dr As DataRow = dt.Rows(0)
                    txtID.Text = dr("ID").ToString
                    If IsDate(dr("CreateDateTime")) Then
                        txtDateTime.Text = Convert.ToDateTime("" + dr.Item("CreateDateTime")).ToString(SessionManager.DateTimeFormat)
                    Else
                        txtDateTime.Text = ""
                    End If
                    txtExpandFeedback.Text = dr("Feedback").ToString
                    txtUserID.Text = dr("UserID").ToString
                    txtProgram.Text = dr("Program").ToString
                    chkProcessed.Checked = CType(dr.Item("Processed"), Boolean)
                    txtExpandComments.Text = dr("Comments").ToString
                    txtExpandDevComments.Text = dr("DevComments").ToString

                    objItem = ddlFeedbackType.Items.FindByValue(dr("FeedbackTypeID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtFeedbackType.Text = objItem.Text
                    End If

                    objItem = ddlFeedbackPriority.Items.FindByValue(dr("FeedbackPriorityID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtFeedbackPriority.Text = objItem.Text
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function UpdateFeedback() As Boolean
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
                Dim iFeedbackType As Integer = -1
                Dim iFeedbackPriority As Integer = -1

                If ddlFeedbackType.SelectedItem.Value.Trim.Length > 0 Then
                    iFeedbackType = ddlFeedbackType.SelectedItem.Value
                End If
                If ddlFeedbackPriority.SelectedItem.Value.Trim.Length > 0 Then
                    iFeedbackPriority = ddlFeedbackPriority.SelectedItem.Value
                End If

                FeedbackMaster.UpdateFeedback(CInt(SessionManager.SelectedValue), chkProcessed.Checked, txtExpandComments.Text, iFeedbackType, iFeedbackPriority, txtExpandDevComments.Text.Trim)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateFeedback", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace

