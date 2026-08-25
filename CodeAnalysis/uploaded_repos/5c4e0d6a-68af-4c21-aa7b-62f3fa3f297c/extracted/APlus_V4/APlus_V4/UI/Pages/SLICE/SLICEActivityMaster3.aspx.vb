#Region " Imports"

Imports System.IO
Imports System.Data
Imports System.Drawing
Imports WebApp.APlus.UI
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEActivityMaster3
        Inherits PrinterFriendlyBase

#Region " Private Constants "
        Private Shared ReadOnly COLUMN_COUNT As Integer = 1
        Private Shared ReadOnly RESULTS_COLUMN As Integer = 9
#End Region

#Region " Member Variables "
        Protected mIntTargetTime As Integer
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            mIntTargetTime = 0
            tblSLICEActivityData.BorderWidth = New Unit(1)
            lblPrintDate.Text = Now.ToLongDateString
            BindActivityGroupDataToGrid()
            If mIntTargetTime > 0 Then
                lblShowTargetTime.Text = mIntTargetTime.ToString()
            End If
        End Sub

#End Region

#Region " Custom Methods "
        Public Sub BindActivityGroupDataToGrid()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim ParentRow As TableRow
            Dim ParentCell As TableCell
            Dim iColCount As Integer

            Try
                Dim dt As DataTable = SLICEActivityMaster.SelectSLICEActivityMasterDataAsDataTable(SessionManager.SLICEActivityGroupMasterID)
                If dt.Rows.Count > 0 Then
                    lblActivityGroup.Text = "SLICE Activity Group: " & dt.Rows(0)("SLICEActivityGroup").ToString().Trim()
                    For iCount As Integer = 0 To dt.Rows.Count - 1
                        mIntTargetTime += CInt(dt.Rows(iCount)("TargetTime"))
                    Next

                    iColCount = dt.Columns.Count
                    ParentRow = New TableRow
                    For i As Integer = 0 To iColCount - COLUMN_COUNT
                        If i <> 0 And i <> 2 Then
                            ParentCell = New TableCell
                            If i = 1 Then
                                ParentCell.Width = New Unit(40)
                            ElseIf i = 3 Then
                                ParentCell.Width = New Unit(60)
                            ElseIf i = 7 Then
                                ParentCell.Width = New Unit(75)
                            ElseIf i = 8 Then
                                ParentCell.Width = New Unit(65)
                            ElseIf i = 9 Then
                                ParentCell.Width = New Unit(90)
                            End If
                            ParentCell.Height = New Unit(25)
                            ParentCell.HorizontalAlign = HorizontalAlign.Left
                            ParentCell.VerticalAlign = VerticalAlign.Top
                            ParentCell.BorderStyle = BorderStyle.Solid
                            ParentCell.BorderWidth = New Unit(1)
                            ParentCell.BorderColor = System.Drawing.Color.Black
                            ParentCell.Font.Bold = True
                            If i = iColCount - COLUMN_COUNT Then
                                ParentCell.Text = "Comments"
                            Else
                                ParentCell.Text = dt.Columns(i).ColumnName.ToString().Trim()
                            End If
                            ParentRow.Cells.Add(ParentCell)
                            tblSLICEActivityData.Rows.Add(ParentRow)
                        End If
                    Next
                    For Each objRow As DataRow In dt.Rows
                        ParentRow = New TableRow
                        ParentRow.BorderWidth = New Unit(1)
                        For i As Integer = 0 To iColCount - COLUMN_COUNT
                            If i <> 0 And i <> 2 Then
                                Dim strTemp As String
                                ParentCell = New TableCell
                                ParentCell.HorizontalAlign = HorizontalAlign.Left
                                ParentCell.VerticalAlign = VerticalAlign.Top
                                ParentCell.BorderColor = Color.Black
                                ParentCell.BorderWidth = New Unit(1)
                                ParentCell.Height = New Unit(20)
                                If i = 1 Then
                                    ParentCell.Width = New Unit(40)
                                ElseIf i = 3 Then
                                    ParentCell.Width = New Unit(60)
                                ElseIf i = 8 Then
                                    ParentCell.Width = New Unit(65)
                                ElseIf i = 7 Then
                                    ParentCell.Width = New Unit(75)
                                ElseIf i = 9 Then
                                    ParentCell.Width = New Unit(90)
                                Else
                                    ParentCell.Width = New Unit(85)
                                End If
                                If i = RESULTS_COLUMN Then
                                    Dim arryStrings As String()
                                    strTemp = objRow.Item(RESULTS_COLUMN).ToString().Replace(Chr(13), "")
                                    If strTemp <> "" Then
                                        arryStrings = Split(strTemp, Chr(10))
                                        For iCnt As Integer = 0 To arryStrings.Length - 1
                                            If arryStrings(iCnt).Length > 0 Then
                                                Dim objCheck As New System.Web.UI.WebControls.CheckBox
                                                objCheck.Text = Trim(arryStrings(iCnt)) & "<br>"
                                                ParentCell.Controls.Add(objCheck)

                                            End If
                                        Next
                                    Else
                                        ParentCell.Text = "<br><br><br>"
                                    End If
                                ElseIf i = (iColCount - COLUMN_COUNT) Then
                                    ParentCell = New TableCell
                                    ParentCell.HorizontalAlign = HorizontalAlign.Left
                                    ParentCell.VerticalAlign = VerticalAlign.Top
                                    ParentCell.BorderColor = Color.Black
                                    ParentCell.BorderWidth = New Unit(1)
                                    ParentCell.Text = "&nbsp;&nbsp;&nbsp;"
                                Else
                                    ParentCell.Text = objRow.Item(i).ToString().Trim()
                                End If
                                ParentRow.Cells.Add(ParentCell)
                            End If
                        Next
                        tblSLICEActivityData.Rows.Add(ParentRow)
                    Next
                Else
                    Exit Sub
                End If
            Catch Exc As Exception
                Master.DisplayErrors("SLICEActivityMaster3 - BindActivityGroupDataToGrid() ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

