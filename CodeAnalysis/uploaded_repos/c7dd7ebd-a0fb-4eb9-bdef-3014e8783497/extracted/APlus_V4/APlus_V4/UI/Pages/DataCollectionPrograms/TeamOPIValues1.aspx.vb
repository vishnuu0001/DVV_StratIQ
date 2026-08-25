#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIValues1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Team OPI Data Entry"
        Private Shared ReadOnly ProgramName As String = "TeamOPIValues1"
        Private iOPICount As Integer = 0
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
                rblOPI.Items(0).Text = GetTranslationString("showtop100records", rblOPI.Items(0).Text)
                rblOPI.Items(1).Text = GetTranslationString("showtop500records", rblOPI.Items(1).Text)
                rblOPI.Items(2).Text = GetTranslationString("showallrecords", rblOPI.Items(2).Text)
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

            SessionManager.CurrentProgram = Request.Path

            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamSelection"))
                Return
            End If
            If SessionManager.SelectedOPI = String.Empty Or SessionManager.SelectedOPI = "" Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("OPISelection"))
                Return
            End If

            Master.IconImage = Request.ApplicationPath & "/images/TeamOPI.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            MasterControl1.StoredProcedureParams.Add("@TeamID", SessionManager.SelectedTeamID)
            MasterControl1.StoredProcedureParams.Add("@OPI", SessionManager.SelectedOPI)
            MasterControl1.StoredProcedureParams.Add("@TopRecords", rblOPI.SelectedItem.Value)

            'configure any parameter columns
            ConfigureParameterColumns()

            SessionManager.CurrentProgram = ""

            If Not SessionManager.SelectedTeamAllowEdit AndAlso Not SessionManager.IsAdministrator Then
                MasterControl1.ShowAdd = False
                MasterControl1.ShowEdit = False
                MasterControl1.ShowDelete = False
                MasterControl1.ShowFunctionButtonOne = False
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                Try
                    For i As Integer = 1 To iOPICount
                        If CType(MasterControl1.MasterControlGrid.Columns(i + 1), BoundField).DataFormatString.Contains("0:F") Then
                            e.Row.Cells(i + 1).Text = Convert.ToDecimal(e.Row.Cells(i + 1).Text.Replace(".", System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator))
                        End If
                    Next
                Catch ex As Exception

                End Try
            End If
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "ViewRow", "DeleteRow", "EditRow"
                    Dim dg As GridView = MasterControl1.MasterControlGrid

                    SessionManager.TeamOPIValueMode = e.CommandName
                    SessionManager.TeamOPIValueID = dg.DataKeys(e.CommandArgument)("TeamOPIValueID").ToString
                    SessionManager.SelectedOPIDate = dg.DataKeys(e.CommandArgument)("OPIValueDateTime").ToString

                    'get the attributes
                    SessionManager.Attribute1 = ""
                    SessionManager.Attribute2 = ""
                    SessionManager.Attribute3 = ""
                    SessionManager.Attribute4 = ""
                    SessionManager.Attribute5 = ""
                    SessionManager.Attribute6 = ""

                    If dg.Columns.Count - 7 > 0 Then
                        SessionManager.Attribute1 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(2).Text 'dg.DataKeys(e.CommandArgument)("Attribute1Value").ToString
                        If SessionManager.Attribute1 = "&nbsp;" Then
                            SessionManager.Attribute1 = ""
                        End If

                        If dg.Columns.Count - 7 > 1 Then
                            SessionManager.Attribute2 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(3).Text 'dg.DataKeys(e.CommandArgument)("Attribute2Value").ToString
                            If SessionManager.Attribute2 = "&nbsp;" Then
                                SessionManager.Attribute2 = ""
                            End If

                            If dg.Columns.Count - 7 > 2 Then
                                SessionManager.Attribute3 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(4).Text 'dg.DataKeys(e.CommandArgument)("Attribute3Value").ToString
                                If SessionManager.Attribute3 = "&nbsp;" Then
                                    SessionManager.Attribute3 = ""
                                End If

                                If dg.Columns.Count - 7 > 3 Then
                                    SessionManager.Attribute4 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(5).Text 'dg.DataKeys(e.CommandArgument)("Attribute4Value").ToString
                                    If SessionManager.Attribute4 = "&nbsp;" Then
                                        SessionManager.Attribute4 = ""
                                    End If

                                    If dg.Columns.Count - 7 > 4 Then
                                        SessionManager.Attribute5 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(6).Text 'dg.DataKeys(e.CommandArgument)("Attribute5Value").ToString
                                        If SessionManager.Attribute5 = "&nbsp;" Then
                                            SessionManager.Attribute5 = ""
                                        End If

                                        If dg.Columns.Count - 7 > 5 Then
                                            SessionManager.Attribute6 = MasterControl1.Rows(CInt(e.CommandArgument)).Cells(7).Text 'dg.DataKeys(e.CommandArgument)("Attribute6Value").ToString
                                            If SessionManager.Attribute6 = "&nbsp;" Then
                                                SessionManager.Attribute6 = ""
                                            End If
                                        End If
                                    End If
                                End If
                            End If
                        End If
                    End If

                    'Get the Program URL and redirect
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues2"), False)
            End Select
        End Sub
        Protected Sub MasterControl1_FunctionButtonOneClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles MasterControl1.FunctionButtonOneClick
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues3"), False)
        End Sub
        Private Sub rblOPI_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles rblOPI.SelectedIndexChanged
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            MasterControl1.DataBind(True)
        End Sub
#End Region

#Region "Custom Methods"
        Private Sub ConfigureParameterColumns()
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
                Dim ds As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                Dim dr As DataRow
                Try
                    dr = ds.Rows(0)
                Catch ex As Exception
                    Return
                End Try
                Dim dtColumn As BoundField

                'configure Date Column
                If dr("TimeEntryRequired") = True Then
                    MasterControl1.GridColumns(1).DataFormatString = "{0:" + SessionManager.DateTimeFormat + "}"
                Else
                    MasterControl1.GridColumns(1).DataFormatString = "{0:" + SessionManager.DateFormat + "}"
                End If

                'cycle through the paramters and add a column to the grid for each one
                Dim iCounter As Integer
                For iCounter = 1 To 6
                    If IsDBNull(dr("Attribute" + iCounter.ToString)) Then
                        'nothing
                        Exit For
                    Else
                        iOPICount += 1

                        dtColumn = New BoundField
                        dtColumn.HeaderText = dr("Attribute" + iCounter.ToString)
                        dtColumn.SortExpression = "Attribute" + iCounter.ToString + "Value"
                        dtColumn.DataField = "Attribute" + iCounter.ToString + "Value"
                        Select Case dr("Attribute" & iCounter.ToString & "EntryType").ToString
                            Case "N"
                                dtColumn.DataFormatString = "{0:F0}"
                            Case "D"
                                dtColumn.DataFormatString = "{0:F" & dr("Attribute" & iCounter.ToString & "Size") & "}"
                        End Select

                        MasterControl1.GridColumns.Add(dtColumn)
                    End If
                Next iCounter

                'now, add the Value and Notes columns
                'Value
                dtColumn = New BoundField
                dtColumn.HeaderText = "OPI Value"
                dtColumn.SortExpression = "OPIValue"
                dtColumn.DataField = "OPIValue"
                'determine how the column should be formmated
                Select Case dr("OPIEntryType").ToString
                    Case "D"
                        dtColumn.DataFormatString = "{0:F" + dr("OPISize").ToString + "}"
                    Case "N"
                        dtColumn.DataFormatString = "{0:F0}"
                End Select
                MasterControl1.GridColumns.Add(dtColumn)

                'OPIUOM
                dtColumn = New BoundField
                dtColumn.HeaderText = "OPI UOM"
                dtColumn.DataField = "OPIUOM"
                MasterControl1.GridColumns.Add(dtColumn)

                'Notes
                dtColumn = New BoundField
                dtColumn.HeaderText = "Notes"
                dtColumn.DataField = "Notes"
                MasterControl1.GridColumns.Add(dtColumn)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ConfigureParameterColumns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
            End Try
        End Sub
#End Region

    End Class
End Namespace
