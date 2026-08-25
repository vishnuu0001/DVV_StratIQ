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
    Partial Class TeamBoardMenuOptionMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team Board Menu Option Master"
        Private Shared ReadOnly ProgramName As String = "TeamBoardMenuOptionMaster2"
        Private Shared ReadOnly DBTableName As String = "TeamBoardMenuOptionMaster"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {txtBoardColumn, _
                                          txtBoardRow, _
                                          txtRCSequence, _
                                          txtBoardDescription, _
                                          ddlProgram, _
                                          txtLinkFileURL, _
                                          txtURLLink, _
                                          ddlJob, _
                                          ddlLinkTeams, _
                                          ckClosedTeams _
                                         }
            Dim TabKeyDownArr() As String = {Tab(txtBoardRow, ckClosedTeams, "Yes"), _
                                             Tab(txtRCSequence, txtBoardColumn, "Yes"), _
                                             Tab(txtBoardDescription, txtBoardRow, "Yes"), _
                                             Tab(ddlProgram, txtRCSequence, "No"), _
                                             Tab(txtLinkFileURL, txtBoardDescription, "No"), _
                                             Tab(txtURLLink, ddlProgram, "No"), _
                                             Tab(ddlJob, txtLinkFileURL, "No"), _
                                             Tab(ddlLinkTeams, txtURLLink, "No"), _
                                             Tab(ckClosedTeams, ddlJob, "No"), _
                                             Tab(txtBoardColumn, ddlLinkTeams, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtBoardDescription, _
                                          ddlProgram, _
                                          txtLinkFileURL, _
                                          txtURLLink, _
                                          ddlJob, _
                                          ddlLinkTeams, _
                                          ckClosedTeams _
                                         }
            Dim TabKeyDownArr() As String = {Tab(ddlProgram, ckClosedTeams, "No"), _
                                             Tab(txtLinkFileURL, txtBoardDescription, "No"), _
                                             Tab(txtURLLink, ddlProgram, "No"), _
                                             Tab(ddlJob, txtLinkFileURL, "No"), _
                                             Tab(ddlLinkTeams, txtURLLink, "No"), _
                                             Tab(ckClosedTeams, ddlJob, "No"), _
                                             Tab(txtBoardDescription, ddlLinkTeams, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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
                lblTeam.Text = GetTranslationString("team", lblTeam.Text.Replace(":", "")) & ":"
                lblBoardColumn.Text = GetTranslationString("boardcolumn", lblBoardColumn.Text.Replace(":", "")) & ":"
                lblBoardRow.Text = GetTranslationString("boardrow", lblBoardRow.Text.Replace(":", "")) & ":"
                lblRCSequence.Text = GetTranslationString("sequence", lblRCSequence.Text.Replace(":", "")) & ":"
                lblBoardDescription.Text = GetTranslationString("boarddescription", lblBoardDescription.Text.Replace(":", "")) & ":"
                Label3.Text = GetTranslationString("selectnomorethanoneofthefollowing", Label3.Text.Replace(":", "")) & ":"
                lblProgram.Text = GetTranslationString("program", lblProgram.Text.Replace(":", "")) & ":"
                lblLinkFileURL.Text = GetTranslationString("linkfileurl", lblLinkFileURL.Text.Replace(":", "")) & ":"
                Label4.Text = GetTranslationString("notefilemustexistintheteamfolder", Label4.Text)
                lblURLLink.Text = GetTranslationString("urllink", lblURLLink.Text.Replace(":", "")) & ":"
                lblTrainingMatrixLink.Text = GetTranslationString("trainingmatrixlink", lblTrainingMatrixLink.Text.Replace(":", "")) & ":"
                lblKPILink.Text = GetTranslationString("kpilink", lblKPILink.Text.Replace(":", "")) & ":"
                lblSavingsTrackerLink.Text = GetTranslationString("savingstrackerlink", lblSavingsTrackerLink.Text.Replace(":", "")) & ":"
                lblTeamLink.Text = GetTranslationString("teamlink", lblTeamLink.Text.Replace(":", "")) & ":"
                ckClosedTeams.Text = GetTranslationString("includeclosedteams", ckClosedTeams.Text)
                rblTeamProgram.Items(0).Text = GetTranslationString("teamboard", rblTeamProgram.Items(0).Text)
                rblTeamProgram.Items(1).Text = GetTranslationString("team status", rblTeamProgram.Items(1).Text)
                rblTeamProgram.Items(2).Text = GetTranslationString("opireports", rblTeamProgram.Items(2).Text)
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
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

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.TeamBoardMenuOptionMasterMode.Replace("Row", ""), SessionManager.TeamBoardMenuOptionMasterMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamBoard.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamBoardMenuOptionMasterMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Team Board Menu Option.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        BindProgram()
                        BindJobs()
                        BindTrackers()
                        BindKPISites()
                        BindKPIs()
                        BindTeams()
                        UnEnableRecords()

                        If SessionManager.MenuActionCoordinates <> String.Empty Then
                            Dim strArgs As String() = SessionManager.MenuActionCoordinates.Split("|")
                            Dim row As String = strArgs(0).ToString.Trim()
                            Dim column As String = strArgs(1).ToString.Trim()
                            Dim sequence As String = TeamBoardMenuOptionMaster.SelectNextAvailableSequenceNumber(SessionManager.SelectedTeamID, row, column)
                            txtBoardRow.Text = row
                            txtBoardColumn.Text = column
                            txtRCSequence.Text = sequence
                            txtBoardDescription.Focus()
                        End If
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster1"), False)
                End Select
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

            Dim blnValid As Boolean = ValidateLinkType()

            'on sucess then continue
            If blnValid Then
                Dim blnSuccess As Boolean
                If SessionManager.TeamBoardMenuOptionMasterMode = "DeleteRow" Then
                    blnSuccess = DeleteTeamBoardMenuOptionMaster()
                ElseIf SessionManager.TeamBoardMenuOptionMasterMode = "AddRow" Then
                    blnSuccess = InsertTeamBoardMenuOptionMaster()
                ElseIf SessionManager.TeamBoardMenuOptionMasterMode = "EditRow" Then
                    blnSuccess = UpdateTeamBoardMenuOptionMaster()
                End If

                If blnSuccess Then
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                    SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamBoardMenuOptionMasterMode)
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster1"), False)
                End If
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.TeamBoardMenuOptionMasterMode = "EditRow" Or SessionManager.TeamBoardMenuOptionMasterMode = "ViewRow" Or SessionManager.TeamBoardMenuOptionMasterMode = "DeleteRow" Or SessionManager.TeamBoardMenuOptionMasterMode = "AddRow" Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamBoardMenuOptionMasterMode)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamBoardMenuOptionMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamBoardMenuOptionMaster1"), False)
        End Sub
        Private Sub ddlProgram_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlProgram.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlProgram.SelectedItem.Text.Trim.Length > 0 Then
                txtBoardDescription.Text = ddlProgram.SelectedItem.Text
                txtLinkType.Text = ddlProgram.SelectedItem.Value.Substring(0, 1)
                ddlLinkTeams.SelectedIndex = -1
                ddlJob.SelectedIndex = -1
                ddlKPI.SelectedIndex = -1
                ddlTracker.SelectedIndex = -1
            Else
                txtBoardDescription.Text = String.Empty
                txtLinkType.Text = String.Empty
            End If
        End Sub
        Private Sub ddlJob_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlJob.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlJob.SelectedItem.Text.Trim.Length > 0 Then
                txtBoardDescription.Text = ddlJob.SelectedItem.Text
                txtLinkType.Text = "J"
                ddlProgram.SelectedIndex = -1
                ddlLinkTeams.SelectedIndex = -1
                ddlKPI.SelectedIndex = -1
                ddlTracker.SelectedIndex = -1
            Else
                txtBoardDescription.Text = String.Empty
                txtLinkType.Text = String.Empty
            End If
        End Sub
        Protected Sub ddlTracker_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlTracker.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlTracker.SelectedItem.Text.Trim.Length > 0 Then
                txtBoardDescription.Text = ddlTracker.SelectedItem.Text
                txtLinkType.Text = "S"

                ddlProgram.SelectedIndex = -1
                ddlJob.SelectedIndex = -1
                ddlKPI.SelectedIndex = -1
                ddlLinkTeams.SelectedIndex = -1
            Else
                txtBoardDescription.Text = String.Empty
                txtTracker.Text = String.Empty
            End If
        End Sub
        Protected Sub ddlKPISite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlKPISite.SelectedIndexChanged
            BindKPIs()
        End Sub
        Protected Sub ddlKPI_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlKPI.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlKPI.SelectedItem.Text.Trim.Length > 0 Then
                txtBoardDescription.Text = ddlKPI.SelectedItem.Text
                txtLinkType.Text = "K"

                ddlProgram.SelectedIndex = -1
                ddlJob.SelectedIndex = -1
                ddlTracker.SelectedIndex = -1
                ddlLinkTeams.SelectedIndex = -1
            Else
                txtBoardDescription.Text = String.Empty
                txtKPI.Text = String.Empty
            End If
        End Sub
        Private Sub ddlLinkTeams_SelectedIndexChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ddlLinkTeams.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ddlLinkTeams.SelectedItem.Text.Trim.Length > 0 Then
                Dim strTeam() As String = Split(ddlLinkTeams.SelectedItem.Text, " - ")

                txtBoardDescription.Text = strTeam(0).Trim
                txtLinkType.Text = "T"

                ddlProgram.SelectedIndex = -1
                ddlJob.SelectedIndex = -1
                ddlKPI.SelectedIndex = -1
                ddlTracker.SelectedIndex = -1
            Else
                txtBoardDescription.Text = String.Empty
                txtLinkType.Text = String.Empty
            End If
        End Sub
        Private Sub ckClosedTeams_CheckedChanged(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles ckClosedTeams.CheckedChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindTeams()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
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
                Dim dt As DataTable = TeamBoardMenuOptionMaster.SelectTeamBoardMenuOptionMasterByID(SessionManager.SelectedValue)
                Dim dr As DataRow = dt.Rows(0)
                Dim objItem As ListItem
                Dim objDT As DataTable = Nothing

                txtTeam.Text = dr.Item("Team").ToString.Trim()
                txtBoardColumn.Text = dr.Item("BoardColumn").ToString.Trim()
                txtBoardColumnOld.Text = dr.Item("BoardColumn").ToString.Trim()
                txtBoardRow.Text = dr.Item("BoardRow").ToString.Trim()
                txtBoardRowOld.Text = dr.Item("BoardRow").ToString.Trim()
                txtRCSequence.Text = dr.Item("RCSequence").ToString.Trim()
                txtRCSequenceOld.Text = dr.Item("RCSequence").ToString.Trim()
                txtBoardDescription.Text = dr("BoardDescription").ToString.Trim()
                txtLinkType.Text = dr("LinkType").ToString.Trim()

                BindProgram()
                BindJobs()
                BindTrackers()
                BindKPISites()
                BindKPIs()
                BindTeams()

                Select Case txtLinkType.Text
                    Case "T"
                        'set the link team
                        objItem = ddlLinkTeams.Items.FindByValue(dr("LinkFileURL").ToString.Trim)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtLinkTeam.Text = objItem.Text
                        Else
                            'if the team is closed then load closed teams, check the box and reselect item
                            ckClosedTeams.Checked = True
                            BindTeams()

                            objItem = ddlLinkTeams.Items.FindByValue(dr("LinkFileURL").ToString.Trim)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtLinkTeam.Text = objItem.Text
                            End If
                        End If

                        'now, check the correct radio button
                        If Not (dr("Program") Is DBNull.Value) Then
                            If Not IsNothing(rblTeamProgram.Items.FindByValue(dr("Program"))) Then
                                rblTeamProgram.Items.FindByValue(dr("Program")).Selected = True
                            End If
                        End If
                    Case "S"
                        'Savings Tracker
                        objItem = ddlTracker.Items.FindByValue(dr("LinkFileURL").ToString.Trim)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtTracker.Text = objItem.Text
                        Else
                            If IsNumeric(dr("LinkFileURL").ToString.Trim) Then
                                objDT = Trackers.SelectTracker(dr("LinkFileURL").ToString.Trim)
                                If objDT.Rows.Count = 1 Then
                                    objItem = New ListItem
                                    objItem.Text = objDT.Rows(0)("Tracker").ToString
                                    objItem.Value = objDT.Rows(0)("TrackerID").ToString

                                    objItem.Selected = True
                                    txtTracker.Text = objItem.Text

                                    ddlTracker.Items.Insert(1, objItem)
                                End If
                            End If
                        End If
                    Case "K"
                        'KPI
                        objItem = ddlKPI.Items.FindByValue(dr("LinkFileURL").ToString.Trim)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                            txtKPI.Text = objItem.Text
                        Else
                            If IsNumeric(dr("LinkFileURL").ToString.Trim) Then
                                objDT = KPIMaster.SelectKPIMasterByID(dr("LinkFileURL").ToString.Trim)
                                If objDT.Rows.Count = 1 Then
                                    objItem = New ListItem
                                    objItem.Text = objDT.Rows(0)("KPI").ToString
                                    objItem.Value = objDT.Rows(0)("KPIID").ToString

                                    objItem.Selected = True
                                    txtKPI.Text = objItem.Text

                                    ddlKPI.Items.Insert(1, objItem)
                                End If
                            End If
                        End If
                    Case "P", "F"
                        'program and printer friendly
                        txtProgram.Text = dr("TeamBoardMenuOptionMasterDescription").ToString

                        objItem = ddlProgram.Items.FindByValue(dr("LinkType").ToString.Trim + "-" + dr("Program").ToString.Trim)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                        End If
                    Case "J"
                        'job and training
                        txtLinkTeam.Text = dr("LinkFileURL").ToString

                        objItem = ddlJob.Items.FindByValue(dr("LinkFileURL").ToString.Trim)
                        If objItem IsNot Nothing Then
                            objItem.Selected = True
                        End If
                    Case "L"
                        'link to Team Document
                        txtLinkFileURL.Text = dr("LinkFileURL").ToString
                    Case "U"
                        'link to URL
                        txtURLLink.Text = dr("LinkFileURL").ToString
                    Case Else
                        'whoops!
                End Select

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Team", dr.Item("Team").ToString.Trim())
                objDic.Add("BoardColumn", dr.Item("BoardColumn").ToString.Trim())
                objDic.Add("BoardRow", dr.Item("BoardRow").ToString.Trim())
                objDic.Add("RCSequence", dr.Item("RCSequence").ToString.Trim())
                objDic.Add("BoardDescription", dr.Item("BoardDescription").ToString.Trim())
                objDic.Add("LinkType", dr.Item("LinkType").ToString.Trim())
                objDic.Add("Program", dr.Item("Program").ToString.Trim())
                objDic.Add("LinkFileURL", dr("LinkFileURL").ToString)
                SessionManager.RecordTransactionCurrentValues = objDic
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.TeamBoardMenuOptionMasterMode.ToString()
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    txtTeam.ReadOnly = True
                    txtTeam.CssClass = "Textbox_Display"
                    txtBoardRow.ReadOnly = True
                    txtBoardRow.CssClass = "Textbox_Display"
                    txtBoardColumn.ReadOnly = True
                    txtBoardColumn.CssClass = "Textbox_Display"
                    txtRCSequence.ReadOnly = True
                    txtRCSequence.CssClass = "Textbox_Display"
                    txtBoardDescription.ReadOnly = True
                    txtBoardDescription.CssClass = "Textbox_Display"
                    txtProgram.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
                    txtProgram.Visible = True
                    ddlProgram.Visible = False
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlKPISite.Visible = False
                    ddlTracker.Visible = False
                    txtTracker.Visible = True
                    txtLinkTeam.ReadOnly = True
                    txtLinkTeam.Visible = True
                    txtLinkTeam.CssClass = "Textbox_Display"
                    ckClosedTeams.Visible = False
                    ddlLinkTeams.Visible = False
                    rblTeamProgram.Enabled = False
                    txtLinkFileURL.ReadOnly = True
                    txtLinkFileURL.CssClass = "Textbox_Display"
                    txtURLLink.ReadOnly = True
                    txtURLLink.CssClass = "Textbox_Display"
                    ddlJob.Visible = False
                    txtJob.Visible = True
                Case "DeleteRow"
                    txtTeam.ReadOnly = True
                    txtTeam.CssClass = "Textbox_Display"
                    txtBoardRow.ReadOnly = True
                    txtBoardRow.CssClass = "Textbox_Display"
                    txtBoardColumn.ReadOnly = True
                    txtBoardColumn.CssClass = "Textbox_Display"
                    txtRCSequence.ReadOnly = True
                    txtRCSequence.CssClass = "Textbox_Display"
                    txtBoardDescription.ReadOnly = True
                    txtBoardDescription.CssClass = "Textbox_Display"
                    txtProgram.ReadOnly = True
                    txtProgram.CssClass = "Textbox_Display"
                    txtProgram.Visible = True
                    ddlProgram.Visible = False
                    ddlKPI.Visible = False
                    txtKPI.Visible = True
                    ddlKPISite.Visible = False
                    ddlTracker.Visible = False
                    txtTracker.Visible = True
                    txtLinkTeam.ReadOnly = True
                    txtLinkTeam.Visible = True
                    txtLinkTeam.CssClass = "Textbox_Display"
                    ckClosedTeams.Visible = False
                    ddlLinkTeams.Visible = False
                    rblTeamProgram.Enabled = False
                    txtLinkFileURL.ReadOnly = True
                    txtLinkFileURL.CssClass = "Textbox_Display"
                    txtURLLink.ReadOnly = True
                    txtURLLink.CssClass = "Textbox_Display"
                    ddlJob.Visible = False
                    txtJob.Visible = True
                Case "EditRow"
                    txtTeam.ReadOnly = True
                    txtTeam.CssClass = "Textbox_Display"
                    ddlProgram.Visible = True
                    ddlLinkTeams.Visible = True
                    txtProgram.Visible = False
                    txtLinkTeam.Visible = False
                    txtBoardDescription.Focus()
                Case "AddRow"
                    txtTeam.Text = SessionManager.SelectedTeam
                    txtTeam.ReadOnly = True
                    txtProgram.Visible = False
                    txtLinkTeam.Visible = False
                    txtBoardColumn.Focus()
            End Select
        End Sub
        Private Sub BindProgram()
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
                ProgramMaster.GetTeamBoardProgramList(ddlProgram)
                ddlProgram.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindProgram", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindJobs()
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
                JobMaster.GetJobListForTeamBoard(ddlJob, SessionManager.WorkingSiteID, SessionManager.SelectedTeamID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindJobs", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTrackers()
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
                If ddlTracker.SelectedIndex > 0 Then
                    txtBoardDescription.Text = ""
                End If
                ddlTracker.Items.Clear()

                Trackers.GetMyTrackerList(ddlTracker, SessionManager.UserID, SessionManager.WorkingSiteID)
                ddlTracker.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTrackers", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindKPISites()
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
                Dim objItem As ListItem = Nothing

                SiteMaster.SelectSiteMasterActiveList(ddlKPISite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlKPISite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlKPISite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlKPISite.Items.Count > 0 Then
                        ddlKPISite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindKPISites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindKPIs()
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
                If ddlKPI.SelectedIndex > 0 Then
                    txtBoardDescription.Text = ""
                End If

                ddlKPI.Items.Clear()

                If ddlKPISite.SelectedItem IsNot Nothing Then
                    KPIMaster.GetKPISelectionList(ddlKPI, SessionManager.UserID, ddlKPISite.SelectedItem.Value)
                Else
                    KPIMaster.GetKPISelectionList(ddlKPI, SessionManager.UserID, SessionManager.WorkingSiteID)
                End If

                ddlKPI.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindKPIs", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindTeams()
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
                If ddlLinkTeams.SelectedIndex > 0 Then
                    txtBoardDescription.Text = ""
                End If
                ddlLinkTeams.Items.Clear()

                Teams.FillTeamSelectionList(ddlLinkTeams, SessionManager.UserID, SessionManager.WorkingSiteID, ckClosedTeams.Checked)
                ddlLinkTeams.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindTeams", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function ValidateLinkType() As Boolean
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
                If ddlProgram.SelectedValue.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a Program, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtLinkFileURL.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Program or LinkFileURL, not both ")
                        ddlProgram.Focus()
                        Return False
                    ElseIf txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Program or URL Link, not both ")
                        ddlProgram.Focus()
                        Return False
                    End If
                ElseIf ddlJob.SelectedItem.Value.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a Job Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtLinkFileURL.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Job or LinkFileURL, not both ")
                        ddlLinkTeams.Focus()
                        Return False
                    ElseIf txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Job or URL Link, not both ")
                        ddlLinkTeams.Focus()
                        Return False
                    End If
                ElseIf ddlLinkTeams.SelectedValue.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a Team Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtLinkFileURL.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Team or LinkFileURL, not both ")
                        ddlLinkTeams.Focus()
                        Return False
                    ElseIf txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Team or URL Link, not both ")
                        ddlLinkTeams.Focus()
                        Return False
                    End If
                ElseIf ddlKPI.SelectedValue.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a KPI Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtLinkFileURL.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either KPI or LinkFileURL, not both ")
                        ddlKPI.Focus()
                        Return False
                    ElseIf txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either KPI or URL Link, not both ")
                        ddlKPI.Focus()
                        Return False
                    End If
                ElseIf ddlTracker.SelectedValue.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a Savings Tracker Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtLinkFileURL.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Savings Tracker or LinkFileURL, not both ")
                        ddlTracker.Focus()
                        Return False
                    ElseIf txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Savings Tracker or URL Link, not both ")
                        ddlTracker.Focus()
                        Return False
                    End If
                ElseIf txtLinkFileURL.Text.Trim.Length > 0 Then
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    If txtURLLink.Text.Trim.Length > 0 Then
                        Master.DisplayError("Select either Program or URL Link, not both ")
                        ddlProgram.Focus()
                        Return False
                    End If
                    txtLinkType.Text = "L"
                ElseIf txtURLLink.Text.Trim.Length > 0 Then
                    'we have a link file with no program
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("This is a URL Link, you must enter Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If

                    'if we have anything that looks like an A+ URL, reject it
                    If InStr(txtURLLink.Text, "UI/Pages") > 0 Then
                        Master.DisplayError("URL Link not allowed")
                        txtURLLink.Focus()
                        Return False
                    End If
                    txtLinkType.Text = "U"
                Else
                    'we must have at LEAST the board description
                    If txtBoardDescription.Text.Trim.Length = 0 Then
                        Master.DisplayError("Must have a Board Description")
                        txtBoardDescription.Focus()
                        Return False
                    End If
                    txtLinkType.Text = "D"
                End If
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateLinkType", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
        Private Function InsertTeamBoardMenuOptionMaster() As Boolean
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
                Dim strProgram As String = String.Empty
                Dim strLinkFile As String = String.Empty

                If txtLinkType.Text = "T" Then
                ElseIf txtLinkType.Text = "J" Then
                ElseIf txtLinkType.Text = "L" Then
                Else
                End If

                Select Case txtLinkType.Text
                    Case "T"
                        If ddlLinkTeams.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlLinkTeams.SelectedItem.Value.ToString
                        End If
                        strProgram = rblTeamProgram.SelectedItem.Value
                    Case "S"
                        If ddlTracker.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlTracker.SelectedItem.Value.ToString
                        End If
                        strProgram = "SavingsTracker1"
                    Case "K"
                        If ddlKPI.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlKPI.SelectedItem.Value.ToString
                        End If
                        strProgram = "KPIValues1"
                    Case "J"
                        If ddlJob.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlJob.SelectedItem.Value
                        End If
                        strProgram = "UserSkillRatings1"
                    Case Else
                        If txtLinkType.Text = "L" Then
                            strLinkFile = txtLinkFileURL.Text.Trim
                        Else
                            strLinkFile = txtURLLink.Text.Trim
                        End If
                        If ddlProgram.SelectedItem.Value.Trim.Length > 0 Then
                            strProgram = ddlProgram.SelectedItem.Value.Substring(2)
                        End If
                End Select

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Team", txtTeam.Text.Trim())
                objDic.Add("BoardColumn", txtBoardColumn.Text.Trim())
                objDic.Add("BoardRow", txtBoardRow.Text.Trim())
                objDic.Add("RCSequence", txtRCSequence.Text.Trim())
                objDic.Add("BoardDescription", txtBoardDescription.Text.Trim())
                objDic.Add("LinkType", txtLinkType.Text.Trim())
                objDic.Add("Program", strProgram.Trim())
                objDic.Add("LinkFileURL", strLinkFile.Trim())
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim intResult As Integer = TeamBoardMenuOptionMaster.AddTeamBoardMenuOptionMaster(SessionManager.SelectedTeamID, txtBoardColumn.Text.Trim, txtBoardRow.Text.Trim, txtRCSequence.Text.Trim, txtBoardDescription.Text.Trim, txtLinkType.Text, strProgram, strLinkFile)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intResult, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptions", SessionManager.SelectedTeamID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamBoardMenuOptionMaster ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamBoardMenuOptionMaster() As Boolean
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
                Dim strProgram As String = String.Empty
                Dim strLinkFile As String = String.Empty

                Select Case txtLinkType.Text
                    Case "T"
                        If ddlLinkTeams.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlLinkTeams.SelectedItem.Value.Substring(0, ddlLinkTeams.SelectedItem.Value.IndexOf("|")).Trim
                        End If
                        strProgram = rblTeamProgram.SelectedItem.Value
                    Case "S"
                        If ddlTracker.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlTracker.SelectedItem.Value.ToString
                        End If
                        strProgram = "SavingsTracker1"
                    Case "K"
                        If ddlKPI.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlKPI.SelectedItem.Value.ToString
                        End If
                        strProgram = "KPIValues1"
                    Case "J"
                        If ddlJob.SelectedItem.Value.Trim.Length > 0 Then
                            strLinkFile = ddlJob.SelectedItem.Value
                        End If
                        strProgram = "UserSkillRatings1"
                    Case Else
                        If txtLinkType.Text = "L" Then
                            strLinkFile = txtLinkFileURL.Text.Trim
                        Else
                            strLinkFile = txtURLLink.Text.Trim
                        End If
                        If ddlProgram.SelectedItem.Value.Trim.Length > 0 Then
                            strProgram = ddlProgram.SelectedItem.Value.Substring(2)
                        End If
                End Select

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Team", txtTeam.Text.Trim())
                objDic.Add("BoardColumn", txtBoardColumn.Text.Trim())
                objDic.Add("BoardRow", txtBoardRow.Text.Trim())
                objDic.Add("RCSequence", txtRCSequence.Text.Trim())
                objDic.Add("BoardDescription", txtBoardDescription.Text.Trim())
                objDic.Add("LinkType", txtLinkType.Text.Trim())
                objDic.Add("Program", strProgram.Trim())
                objDic.Add("LinkFileURL", strLinkFile.Trim())

                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)
                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamBoardMenuOptionMaster.UpdateTeamBoardMenuOptionMaster(CInt(SessionManager.SelectedValue), SessionManager.SelectedTeamID, txtBoardColumn.Text.Trim, txtBoardColumnOld.Text.Trim, txtBoardRow.Text.Trim, txtBoardRowOld.Text.Trim, txtRCSequence.Text.Trim, txtRCSequenceOld.Text.Trim, txtBoardDescription.Text.Trim, txtLinkType.Text, strProgram, strLinkFile)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptions", SessionManager.SelectedTeamID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamBoardMenuOptionMaster ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamBoardMenuOptionMaster() As Boolean
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
                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Team", txtTeam.Text.Trim())
                objDic.Add("BoardColumn", txtBoardColumn.Text.Trim())
                objDic.Add("BoardRow", txtBoardRow.Text.Trim())
                objDic.Add("RCSequence", txtRCSequence.Text.Trim())
                objDic.Add("BoardDescription", txtBoardDescription.Text.Trim())
                objDic.Add("LinkType", txtLinkType.Text.Trim())
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                TeamBoardMenuOptionMaster.DeleteTeamBoardMenuOptionMaster(CInt(SessionManager.SelectedValue))

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory("TeamBoardMenuOptions", SessionManager.SelectedTeamID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamBoardMenuOptionMaster ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace