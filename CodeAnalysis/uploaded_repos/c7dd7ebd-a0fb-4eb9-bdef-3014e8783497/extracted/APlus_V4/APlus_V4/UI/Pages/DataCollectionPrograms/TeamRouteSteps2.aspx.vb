#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper

Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamRouteSteps2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Team Master Plan"
        Private Shared ReadOnly ProgramName As String = "TeamRouteSteps2"
        Private Shared ReadOnly DBTableName As String = "TeamRouteSteps"
#End Region

#Region " Load Culture Translations"
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
                lblRouteAbbrev.Text = GetTranslationString("route", lblRouteAbbrev.Text.Replace(":", "")) & ":"
                lblRoute.Text = GetTranslationString("stepnumber", lblRoute.Text.Replace(":", "")) & ":"
                lblRouteDefinition.Text = GetTranslationString("step", lblRouteDefinition.Text.Replace(":", "")) & ":"
                lblMasterTemplatePath.Text = GetTranslationString("stepdefinition", lblMasterTemplatePath.Text.Replace(":", "")) & ":"
                Label1.Text = GetTranslationString("plannedstartdate", Label1.Text.Replace(":", "")) & ":"
                Label2.Text = GetTranslationString("plannedenddate", Label2.Text.Replace(":", "")) & ":"
                Label3.Text = GetTranslationString("actualstartdate", Label3.Text.Replace(":", "")) & ":"
                Label4.Text = GetTranslationString("actualenddate", Label4.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            'load the javascripts for the date controls
            txtPlannedStartDate_CalendarExtender.Format = strDateFormat
            txtPlannedEndDate_CalendarExtender.Format = strDateFormat
            txtActualStartDate_CalendarExtender.Format = strDateFormat
            txtActualEndDate_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtPlannedStartDate, _
                                         txtPlannedEndDate, _
                                         txtActualStartDate, _
                                         txtActualEndDate _
                                         }
            Dim TabKeyDownArr() As String = {Tab(txtPlannedEndDate, txtActualEndDate, "No"), _
                                                     Tab(txtActualStartDate, txtPlannedStartDate, "No"), _
                                                     Tab(txtActualEndDate, txtPlannedEndDate, "No"), _
                                                     Tab(txtPlannedStartDate, txtActualStartDate, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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

            Try
                If Not SessionManager.SelectedTeamAllowEdit AndAlso Not SessionManager.IsAdministrator Then
                    SessionManager.Mode = "ViewRow"
                    pnlOKCancel.Visible = False
                    pnlExit.Visible = True
                Else
                    Dim dt As DataTable = ProgramSecurity.ProgramModeFromProgram(SessionManager.UserID, "TeamRouteSteps1")
                    If dt.Rows.Count > 0 Then
                        If dt.Rows(0).Item("AllowEdit") Then
                            SessionManager.Mode = "EditRow"
                            pnlOKCancel.Visible = True
                            pnlExit.Visible = False
                        Else
                            SessionManager.Mode = "ViewRow"
                            pnlOKCancel.Visible = False
                            pnlExit.Visible = True
                        End If
                    Else
                        SessionManager.Mode = "ViewRow"
                        pnlOKCancel.Visible = False
                        pnlExit.Visible = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Page_Load (ProgramModeFromProgram)", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.Mode.Replace("Row", ""), SessionManager.Mode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/TeamRouteSteps.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + Me.btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event")

            If Not Page.IsPostBack Then
                LoadEditModeJavaScripts()
                LoadSelectedRecord()
                UnEnableRecords()
                txtPlannedStartDate.Focus()
            End If
        End Sub

        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean = UpdateTeamRouteStep()
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
            End If
        End Sub

        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
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
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
        End Sub
#End Region

#Region " Custom Functions"
        Private Function UpdateTeamRouteStep() As Boolean
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
                Dim passStepNumber As Integer = SessionManager.SelectedValue
                Dim passPlannedStartDate As String = RegionalConversion.FormatSQLDate(txtPlannedStartDate.Text)
                Dim passPlannedEndDate As String = RegionalConversion.FormatSQLDate(txtPlannedEndDate.Text)
                Dim passActualStartDate As String = RegionalConversion.FormatSQLDate(txtActualStartDate.Text)
                Dim passActualEndDate As String = RegionalConversion.FormatSQLDate(txtActualEndDate.Text)
                Dim passUserID As String = SessionManager.UserID

                If passPlannedEndDate.Trim.Length > 0 Then
                    If String.IsNullOrEmpty(passPlannedStartDate.Trim()) Then
                        Master.DisplayError(GetTranslationString("mustenterplanneddate", "You must enter a planned start date"))
                        Return False
                    End If
                End If

                If passPlannedEndDate < passPlannedStartDate Then
                    Master.DisplayError(GetTranslationString("planneddatestartbeforeend", "Planned End Date must be after start date"))
                    Return False
                End If

                If passActualStartDate.Trim.Length > 0 Then
                    If passActualStartDate > Today Then
                        Master.DisplayError(GetTranslationString("startcantoccur", "Actual Start Date can not occur after today"))
                        Return False
                    End If
                End If

                If passActualEndDate.Trim.Length > 0 Then
                    If passActualStartDate.Trim.Length = 0 Then
                        Master.DisplayError(GetTranslationString("mustenteractualstart", "You must enter an actual start date"))
                        Return False
                    End If
                End If

                If passActualEndDate.Trim.Length > 0 Then
                    If passActualEndDate < passActualStartDate Then
                        Master.DisplayError(GetTranslationString("actualendafterstart", "Actual End Date must be after Start Date"))
                        Return False
                    End If
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamRouteSteps.UpdateTeamRouteStep(SessionManager.SelectedTeamID, passStepNumber, passPlannedStartDate, passPlannedEndDate, passActualStartDate, passActualEndDate, passUserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedTeamID & "," & SessionManager.SelectedValue, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamRouteStep", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
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

            Dim dt As DataTable = TeamRouteSteps.SelectTeamRouteStep(SessionManager.SelectedTeamID, SessionManager.SelectedValue)
            If dt.Rows.Count <> 0 Then
                Dim dr As DataRow = dt.Rows(0)

                txtRoute.Text = dr("Route").ToString
                txtStepNumber.Text = dr("StepNo").ToString
                txtStep.Text = dr("Step").ToString
                txtExpandStepDefinition.Text = dr("StepDefinition").ToString
                If IsDate(dr("PlannedStartDate")) Then
                    txtPlannedStartDate.Text = Convert.ToDateTime(dr("PlannedStartDate")).ToShortDateString
                Else
                    txtPlannedStartDate.Text = ""
                End If
                If IsDate(dr("PlannedEndDate")) Then
                    txtPlannedEndDate.Text = Convert.ToDateTime(dr("PlannedEndDate")).ToShortDateString
                Else
                    txtPlannedEndDate.Text = ""
                End If
                If IsDate(dr("ActualStartDate")) Then
                    txtActualStartDate.Text = Convert.ToDateTime(dr("ActualStartDate")).ToShortDateString
                Else
                    txtActualStartDate.Text = ""
                End If
                If IsDate(dr("ActualEndDate")) Then
                    txtActualEndDate.Text = Convert.ToDateTime(dr("ActualEndDate")).ToShortDateString
                Else
                    txtActualEndDate.Text = ""
                End If

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedTeamID & "," & SessionManager.SelectedValue

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Team", SessionManager.SelectedTeam)
                objDic.Add("RouteAbbrev", txtRoute.Text.Trim())
                objDic.Add("StepNo", txtStepNumber.Text.Trim())
                objDic.Add("StepDefinition", txtExpandStepDefinition.Text.Trim())
                objDic.Add("PlannedStartDate", txtPlannedStartDate.Text.Trim())
                objDic.Add("PlannedEndDate", txtPlannedEndDate.Text.Trim())
                objDic.Add("ActualStartDate", txtActualStartDate.Text.Trim())
                objDic.Add("ActualEndDate", txtActualEndDate.Text.Trim())
                SessionManager.RecordTransactionCurrentValues = objDic
            End If
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

            txtRoute.ReadOnly = True
            txtStepNumber.ReadOnly = True
            txtStep.ReadOnly = True
            txtExpandStepDefinition.ReadOnly = True
            If SessionManager.Mode = "ViewRow" Then
                txtPlannedStartDate.ReadOnly = True
                txtPlannedEndDate.ReadOnly = True
                txtActualStartDate.ReadOnly = True
                txtActualEndDate.ReadOnly = True
                txtPlannedStartDate.CssClass = "Textbox_Display"
                txtPlannedEndDate.CssClass = "Textbox_Display"
                txtActualStartDate.CssClass = "Textbox_Display"
                txtActualEndDate.CssClass = "Textbox_Display"
                imgPlannedStartDate.Visible = False
                imgPlannedEndDate.Visible = False
                imgActualStartDate.Visible = False
                imgActualEndDate.Visible = False
                txtPlannedStartDate_CalendarExtender.Enabled = False
                txtPlannedEndDate_CalendarExtender.Enabled = False
                txtActualStartDate_CalendarExtender.Enabled = False
                txtActualEndDate_CalendarExtender.Enabled = False
            End If
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Team", SessionManager.SelectedTeam)
            objDic.Add("RouteAbbrev", txtRoute.Text.Trim())
            objDic.Add("StepNo", txtStepNumber.Text.Trim())
            objDic.Add("StepDefinition", txtExpandStepDefinition.Text.Trim())
            objDic.Add("PlannedStartDate", txtPlannedStartDate.Text.Trim())
            objDic.Add("PlannedEndDate", txtPlannedEndDate.Text.Trim())
            objDic.Add("ActualStartDate", txtActualStartDate.Text.Trim())
            objDic.Add("ActualEndDate", txtActualEndDate.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace

