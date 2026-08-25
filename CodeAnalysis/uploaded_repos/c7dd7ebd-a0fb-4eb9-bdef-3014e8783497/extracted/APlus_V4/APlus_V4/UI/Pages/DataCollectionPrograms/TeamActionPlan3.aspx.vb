#Region " Imports"
Imports System.IO
Imports System.Data.SqlClient
Imports System.Data
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Drawing
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamActionPlan3
        Inherits System.Web.UI.Page

#Region " Members / Variables"
        Private Shared ReadOnly ProgramName As String = "TeamActionPlan3"
        Private objCompletedColor As Color = System.Drawing.Color.Green
        Private objInProgressColor As Color = System.Drawing.Color.Yellow
        Private objLateColor As Color = System.Drawing.Color.Red
        Private objLateCompletedColor As Color = System.Drawing.Color.Orange
        Private objCancelledColor As Color = System.Drawing.Color.Gray
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
                lblTeamActionPlan.Text = GetTranslationString("teamaction plan", lblTeamActionPlan.Text)
                lblClosed.Text = GetTranslationString("completed", lblClosed.Text)
                lblInProgress.Text = GetTranslationString("inprogress", lblInProgress.Text)
                lblLate.Text = GetTranslationString("late", lblLate.Text)
                lblClosedLate.Text = GetTranslationString("completedlate", lblClosedLate.Text)
                For i As Integer = 0 To gvTeamActionPlan.Columns.Count - 1
                    gvTeamActionPlan.Columns(i).HeaderText = GetTranslationString(gvTeamActionPlan.Columns(i).HeaderText, gvTeamActionPlan.Columns(i).HeaderText)
                Next
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

            If SessionManager.SelectedTeamID = 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamRouteSteps1"), False)
                Return
            End If

            CompletedCell.BackColor = objCompletedColor
            CompletedCell.HorizontalAlign = HorizontalAlign.Center
            InprogressCell.BackColor = objInProgressColor
            InprogressCell.HorizontalAlign = HorizontalAlign.Center
            LateCell.BackColor = objLateColor
            LateCell.HorizontalAlign = HorizontalAlign.Center
            LateCompletedCell.BackColor = objLateCompletedColor
            LateCompletedCell.HorizontalAlign = HorizontalAlign.Center
            CancelledCell.backcolor = objCancelledColor
            CancelledCell.horizontalalign = HorizontalAlign.Center
            lblTeamName.Text = SessionManager.SelectedTeamName
            lblTeam.Text = SessionManager.SelectedTeam
            lblPrintDate.Text = GetTranslationString("printed", "Printed") & ": " & Now.ToLongDateString & "   " & Now.ToLongTimeString
            SelectTeamActionPlansByTeam()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub SelectTeamActionPlansByTeam()
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
                Dim bShowClosedActions As Boolean = SessionManager.DisplayClosedTeamActions
                Dim ds As DataTable = TeamActionPlan.SelectTeamActionPlansByTeam(SessionManager.SelectedTeamID, bShowClosedActions)

                gvTeamActionPlan.DataSource = ds
                gvTeamActionPlan.DataBind()

                For Each row As GridViewRow In gvTeamActionPlan.Rows
                    If row.RowType = DataControlRowType.DataRow Then
                        Dim dtClosedDate As DateTime

                        If IsDate(row.Cells(5).Text) Then
                            Dim dtTargetDate As DateTime = Convert.ToDateTime(row.Cells(5).Text)

                            If IsDate(row.Cells(6).Text) Then
                                dtClosedDate = Convert.ToDateTime(row.Cells(6).Text)

                                If Convert.ToBoolean(gvTeamActionPlan.DataKeys(row.RowIndex)("Cancelled").ToString) = True Then
                                    row.Cells(6).BackColor = Color.Gray
                                ElseIf DateTime.Compare(dtClosedDate, dtTargetDate) <= 0 Then
                                    row.Cells(6).BackColor = Color.Green
                                Else
                                    row.Cells(6).BackColor = Color.Orange
                                End If
                            Else
                                If DateTime.Compare(dtTargetDate, Date.Now) >= 0 Then
                                    row.Cells(6).BackColor = Color.Yellow
                                Else
                                    row.Cells(6).BackColor = Color.Red
                                End If

                            End If
                        End If

                        row.Cells(0).BackColor = Color.White
                        row.Cells(1).BackColor = Color.LemonChiffon
                        row.Cells(2).Text = "&nbsp;&nbsp;&nbsp;" & row.Cells(2).Text & "&nbsp;"
                        row.Cells(2).BackColor = Color.LemonChiffon
                        row.Cells(3).BackColor = Color.LemonChiffon
                        row.Cells(4).Text = "&nbsp;&nbsp;&nbsp;" & row.Cells(4).Text
                        row.Cells(4).BackColor = Color.LemonChiffon
                        row.Cells(5).BackColor = Color.LemonChiffon
                    End If
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SelectTeamActionPlansByTeam", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
#End Region

    End Class
End Namespace