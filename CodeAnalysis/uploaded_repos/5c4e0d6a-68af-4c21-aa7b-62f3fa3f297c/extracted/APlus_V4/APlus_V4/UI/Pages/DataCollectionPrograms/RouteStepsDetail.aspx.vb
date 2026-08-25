#Region " Imports"
Imports System.IO
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Data
#End Region

Namespace WebApp.APlus.UI.Pages
Partial Class RouteStepsDetail
        Inherits PrinterFriendlyBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Route Steps Detail"
        Private Shared ReadOnly ProgramName As String = "RouteStepsDetail"
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

            If (SessionManager.SelectedTeamID = 0) AndAlso (SessionManager.SelectedRoute = String.Empty) Then
                Return
            End If

            BindRouteStepsGrid()
            lblPrintDate.Text = "Printed : " + Now.ToString("yyyy/MM/dd")
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindRouteStepsGrid()
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
                'before we do anything, we need to get the route from the team if required
                Dim strRoute As String = ""

                If Not IsNothing(SessionManager.SelectedRoute) Then
                    If SessionManager.SelectedRoute <> String.Empty Then
                        strRoute = SessionManager.SelectedRoute
                    End If
                End If

                If strRoute.Trim.Length = 0 Then
                    If SessionManager.SelectedTeamID > 0 Then
                        strRoute = Teams.GetTeamRoute(SessionManager.SelectedTeamID)
                    End If
                End If

                If strRoute.Trim.Length = 0 Then
                    lblRoute.Text = "No Route information assigned to this Team."

                    Return
                End If

                Dim objDT As DataTable = Routes.GetRouteStepDetail(strRoute)
                Dim ParentRow As TableRow
                Dim ParentCell As TableCell

                'first, if the dataset if empty, get out of here
                If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                    'not good
                    lblRoute.Text = "No Route information assigned to this Team."

                    Return
                End If

                'plug in Route
                lblRoute.Text = objDT.Rows(0)("RouteAbbrev") + " - " + objDT.Rows(0)("Route")

                'plug in the team
                lblTeam.Text = SessionManager.SelectedTeam

                If Not objDT.Rows(objDT.Rows.Count - 1)("StepNo") Is DBNull.Value Then
                    'headers first
                    ParentRow = New TableRow

                    ParentCell = New TableCell
                    ParentCell.BackColor = Drawing.Color.LightGray
                    ParentCell.BorderColor = System.Drawing.Color.Black
                    ParentCell.BorderStyle = BorderStyle.Solid
                    ParentCell.BorderWidth = New Unit(1)
                    ParentCell.ColumnSpan = 2
                    ParentCell.Width = New Unit("30%")
                    ParentCell.Text = "Step Title"
                    ParentCell.HorizontalAlign = HorizontalAlign.Center
                    ParentRow.Cells.Add(ParentCell)

                    ParentCell = New TableCell
                    ParentCell.BackColor = Drawing.Color.LightGray
                    ParentCell.BorderColor = System.Drawing.Color.Black
                    ParentCell.BorderStyle = BorderStyle.Solid
                    ParentCell.BorderWidth = New Unit(1)
                    ParentCell.Width = New Unit("50%")
                    ParentCell.Text = "Key Actions"
                    ParentCell.HorizontalAlign = HorizontalAlign.Center
                    ParentRow.Cells.Add(ParentCell)

                    ParentCell = New TableCell
                    ParentCell.BackColor = Drawing.Color.LightGray
                    ParentCell.BorderColor = System.Drawing.Color.Black
                    ParentCell.BorderStyle = BorderStyle.Solid
                    ParentCell.BorderWidth = New Unit(1)
                    'ParentCell.Width = New Unit(175)
                    ParentCell.Text = "Tools Utilized"
                    ParentCell.HorizontalAlign = HorizontalAlign.Center
                    ParentRow.Cells.Add(ParentCell)

                    tblRouteSteps.Rows.Add(ParentRow)

                    'now, loop through the rows and add step information
                    Dim iRowHolder As Integer = objDT.Rows(objDT.Rows.Count - 1)("StepNo")
                    Dim iRowCounter As Integer
                    Dim objDataView As DataView

                    For iRowCounter = 1 To iRowHolder
                        objDataView = objDT.DefaultView
                        objDataView.RowFilter = "StepNo = " + iRowCounter.ToString

                        ParentRow = New TableRow
                        ParentRow.Height = New Unit(5)
                        ParentCell = New TableCell
                        ParentRow.Cells.Add(ParentCell)
                        tblRouteSteps.Rows.Add(ParentRow)

                        If objDataView.Count > 0 Then
                            'new row, add the step information
                            ParentRow = New TableRow

                            ParentCell = New TableCell
                            ParentCell.BorderColor = Drawing.Color.Black
                            ParentCell.BorderStyle = BorderStyle.Solid
                            ParentCell.BorderWidth = New Unit(1)
                            ParentCell.Width = New Unit(10)
                            ParentCell.Text = objDataView(0)("StepNo")
                            ParentCell.HorizontalAlign = HorizontalAlign.Center
                            ParentRow.Cells.Add(ParentCell)

                            ParentCell = New TableCell
                            ParentCell.BorderColor = Drawing.Color.Black
                            ParentCell.BorderStyle = BorderStyle.Solid
                            ParentCell.BorderWidth = New Unit(1)
                            ParentCell.Text = objDataView(0)("Step")
                            ParentCell.HorizontalAlign = HorizontalAlign.Left
                            ParentRow.Cells.Add(ParentCell)

                            Dim ChildRow As TableRow
                            Dim ChildCell As TableCell

                            'key actions
                            Dim objKTable As New Table
                            objKTable.Width = New Unit("100%")
                            objKTable.Height = New Unit("100%")
                            objKTable.GridLines = GridLines.Horizontal
                            objKTable.CellPadding = 0
                            objKTable.CellSpacing = 0

                            Dim objTTable As New Table
                            objTTable.Width = New Unit("100%")
                            objTTable.Height = New Unit("100%")
                            objTTable.GridLines = GridLines.Horizontal
                            objTTable.CellPadding = 0
                            objTTable.CellSpacing = 0

                            Dim strPrevAction As String = ""

                            ParentCell = New TableCell
                            ParentCell.BorderColor = Drawing.Color.Black
                            ParentCell.BorderStyle = BorderStyle.Solid
                            ParentCell.BorderWidth = New Unit(1)

                            For Each objRow As DataRowView In objDataView
                                If objRow("KeyActionNo").ToString <> strPrevAction Then
                                    strPrevAction = objRow("KeyActionNo").ToString
                                    ChildRow = New TableRow

                                    ChildCell = New TableCell
                                    ChildCell.HorizontalAlign = HorizontalAlign.Left
                                    ChildCell.Width = New Unit(10)
                                    ChildCell.Text = objRow("KeyActionNo").ToString.Trim
                                    ChildRow.Cells.Add(ChildCell)

                                    ChildCell = New TableCell
                                    ChildCell.HorizontalAlign = HorizontalAlign.Left
                                    ChildCell.Text = objRow("KeyAction").ToString.Trim
                                    ChildRow.Cells.Add(ChildCell)

                                    objKTable.Rows.Add(ChildRow)
                                Else
                                    strPrevAction = objRow("KeyActionNo").ToString
                                    ChildRow = New TableRow

                                    ChildCell = New TableCell
                                    ChildCell.HorizontalAlign = HorizontalAlign.Left
                                    ChildCell.Width = New Unit(10)
                                    ChildCell.ColumnSpan = 2
                                    ChildCell.Text = "&nbsp"
                                    ChildRow.Cells.Add(ChildCell)

                                    objKTable.Rows.Add(ChildRow)
                                End If

                                'Tool
                                ChildRow = New TableRow
                                ChildCell = New TableCell
                                ChildCell.Text = objRow("Tool").ToString.Trim + "&nbsp"
                                ChildRow.Cells.Add(ChildCell)
                                objTTable.Rows.Add(ChildRow)
                            Next
                            ParentCell.Controls.Add(objKTable)
                            ParentRow.Cells.Add(ParentCell)

                            ParentCell = New TableCell
                            ParentCell.BorderColor = Drawing.Color.Black
                            ParentCell.BorderStyle = BorderStyle.Solid
                            ParentCell.BorderWidth = New Unit(1)
                            ParentCell.Controls.Add(objTTable)
                            ParentRow.Cells.Add(ParentCell)

                            tblRouteSteps.Rows.Add(ParentRow)
                        End If
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors("RouteStepsDetail - BindRouteStepsGrid ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace
