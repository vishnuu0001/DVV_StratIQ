#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class HelpAttachmentsPopup
        Inherits System.Web.UI.Page

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Attachments"
        Private Shared ReadOnly ProgramName As String = "Attachments"
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

            'If Not Page.IsPostBack Then
            Master.HideHeader = True
            'End If

            BindAttachments()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindAttachments()
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
                Dim objDS As DataSet = BuildDataSet()

                If objDS Is Nothing OrElse objDS.Tables.Count = 0 Then
                    Return
                End If

                Dim objRow As TableRow
                Dim objCell As TableCell
                Dim objLabel As Label
                Dim objLink As LinkButton
                Dim strCategory As String = ""

                If objDS.Tables.Count > 0 AndAlso objDS.Tables(0).Rows.Count > 0 Then
                    lblInfo.Text = "Help Attachments"
                    lblInfo.Text = GetTranslationString("Help Attachments", lblInfo.Text)

                    For Each objDataRow As DataRow In objDS.Tables(0).Rows
                        'Check Category
                        If strCategory.Trim.ToUpper <> objDataRow("AttachmentCategory").ToString.Trim.ToUpper Then
                            objRow = New TableRow
                            objRow.CssClass = "row"
                            objRow.BackColor = Drawing.Color.LightSteelBlue
                            objCell = New TableCell
                            objCell.ColumnSpan = 2
                            objCell.CssClass = "first"

                            objLabel = New Label
                            objLabel.Text = objDataRow("AttachmentCategory").ToString
                            objLabel.Font.Bold = True
                            objLabel.ForeColor = Drawing.Color.Black

                            objCell.Controls.Add(objLabel)
                            objRow.Cells.Add(objCell)
                            tblAttachments.Rows.Add(objRow)

                            strCategory = objDataRow("AttachmentCategory").ToString
                        End If

                        'Add Attachment
                        objRow = New TableRow
                        objRow.CssClass = "row"

                        'add empty column
                        objCell = New TableCell
                        objCell.Width = New Unit(25)
                        objCell.Text = "&nbsp;"
                        objRow.Cells.Add(objCell)

                        'only add the file and program
                        objCell = New TableCell
                        objCell.CssClass = "first"
                        objLink = New LinkButton
                        objLink.Text = objDataRow("AttachmentsText").ToString
                        objLink.Attributes.Add("onclick", objDataRow("AttachmentsURL"))
                        objCell.Controls.Add(objLink)
                        objRow.Cells.Add(objCell)

                        tblAttachments.Rows.Add(objRow)
                    Next
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindAttachments", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Public Function BuildDataSet() As DataSet
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim ds As DataSet = Nothing
            Try
                Dim strVirtualRoot As String = ""
                Dim strCultureLanguage As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName

                Try
                    strVirtualRoot = ConfigurationManager.AppSettings("HelpAttachmentsVirtualRootDirectory")
                Catch ex As Exception
                    'error - get out!
                    Return Nothing
                End Try
                If strVirtualRoot.Trim.Length = 0 Then
                    Return Nothing
                End If

                ds = New DataSet
                Dim ds1 As New DataTable
                ds1 = DataAccess.Tables.AttachmentsMaster.SelectAttachmentsByTypeCultureLanguage(AttachmentTypes.SelectAttachmentTypeIDByType("Help"), strCultureLanguage)

                Dim dt As New DataTable
                dt.Columns.Add(New DataColumn("AttachmentCategory"))
                dt.Columns.Add(New DataColumn("AttachmentsText"))
                dt.Columns.Add(New DataColumn("AttachmentsURL"))
                dt.Columns.Add(New DataColumn("Program"))

                For Each row As DataRow In ds1.Rows
                    'Add data to datatable
                    Dim dr As DataRow = dt.NewRow()

                    dr = dt.NewRow
                    dr("AttachmentCategory") = row("AttachmentCategory").ToString
                    dr("AttachmentsText") = row("Attachment").ToString
                    dr("AttachmentsURL") = GetNavigateURL(strVirtualRoot, row("CultureLanguage").ToString, row("Attachment"))
                    dr("Program") = row("Program").ToString

                    dt.Rows.Add(dr)
                Next

                ds.Tables.Add(dt)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BuildDataSet", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
            Return ds
        End Function
        Public Function GetNavigateURL(ByVal passRoot As String, ByVal passCultureLanguage As String, ByVal Attachment As String) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Return "javascript:window.open('http://" & ConfigurationManager.AppSettings("ApplicationServerDNS").ToString & passRoot & passCultureLanguage & "/" & Attachment & "')"
        End Function
#End Region

    End Class
End Namespace
