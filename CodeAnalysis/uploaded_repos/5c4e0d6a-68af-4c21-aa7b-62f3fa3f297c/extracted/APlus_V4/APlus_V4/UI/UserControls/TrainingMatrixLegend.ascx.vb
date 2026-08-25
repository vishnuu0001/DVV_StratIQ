#Region "Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Tables
Imports System.Configuration
Imports System.Data
#End Region


Namespace WebApp.APlus.UI.UserControls
    Partial Class TrainingMatrixLegend
        Inherits System.Web.UI.UserControl

        Private _bShowTargets As Boolean = False
        Private _JobID As Integer = 0


        Public Property JobID() As Integer
            Get
                Return _JobID
            End Get
            Set(ByVal Value As Integer)
                _JobID = Value
            End Set
        End Property
        Public Property ShowTargets() As Boolean
            Get
                Return _bShowTargets
            End Get
            Set(ByVal Value As Boolean)
                _bShowTargets = Value
            End Set
        End Property

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            'initialize the table
            If _JobID = 0 Then
                Return
            End If

            BindGrid()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindGrid()
            Dim objDT As DataTable = SkillRatingMaster.SelectSkillRatingsByJob(_JobID)
            Dim tbRow As TableRow
            Dim tbCell As TableCell
            Dim strWidth As String = objDT.Rows.Count.ToString & "%"

            tbRow = New TableRow

            If _bShowTargets = True Then
                tbCell = New TableCell
                tbCell.HorizontalAlign = HorizontalAlign.Center
                tbCell.BorderColor = Drawing.Color.Black
                tbCell.BorderStyle = BorderStyle.Solid
                tbCell.BorderWidth = New Unit(1)
                tbCell.Width = New Unit("25%")
                tbCell.BackColor = Drawing.Color.LightGray
                tbCell.Text = "No Rating"
                tbRow.Cells.Add(tbCell)

                tbCell = New TableCell
                tbCell.HorizontalAlign = HorizontalAlign.Center
                tbCell.BorderColor = Drawing.Color.Black
                tbCell.BorderStyle = BorderStyle.Solid
                tbCell.BorderWidth = New Unit(1)
                tbCell.Width = New Unit("25%")
                tbCell.BackColor = Drawing.Color.Crimson
                tbCell.Text = "Below Required"
                tbRow.Cells.Add(tbCell)

                tbCell = New TableCell
                tbCell.HorizontalAlign = HorizontalAlign.Center
                tbCell.BorderColor = Drawing.Color.Black
                tbCell.BorderStyle = BorderStyle.Solid
                tbCell.BorderWidth = New Unit(1)
                tbCell.Width = New Unit("25%")
                tbCell.BackColor = Drawing.Color.Yellow
                tbCell.Text = "Required"
                tbRow.Cells.Add(tbCell)

                tbCell = New TableCell
                tbCell.HorizontalAlign = HorizontalAlign.Center
                tbCell.BorderColor = Drawing.Color.Black
                tbCell.BorderStyle = BorderStyle.Solid
                tbCell.BorderWidth = New Unit(1)
                tbCell.Width = New Unit("25%")
                tbCell.BackColor = Drawing.Color.Green
                tbCell.Text = "Desired"
                tbRow.Cells.Add(tbCell)
            Else
                For Each dtRow As DataRow In objDT.Rows
                    tbCell = New TableCell

                    If Not (dtRow("DisplayColor") Is DBNull.Value) Then
                        tbCell.BackColor = Drawing.Color.FromName(dtRow("DisplayColor").ToString)
                    End If
                    tbCell.Text = dtRow("SkillRating").ToString & " - " & dtRow("Description").ToString
                    tbCell.HorizontalAlign = HorizontalAlign.Center
                    tbCell.BorderColor = Drawing.Color.Black
                    tbCell.BorderStyle = BorderStyle.Solid
                    tbCell.BorderWidth = New Unit(1)
                    tbCell.Width = New Unit(strWidth)
                    tbCell.ToolTip = dtRow("Definition").ToString
                    tbRow.Cells.Add(tbCell)
                Next
            End If

            tblLegend.Rows.Add(tbRow)
        End Sub
#End Region


    End Class
End Namespace