#Region " Imports "
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class WebReportPrintPreview
        Inherits Page

        Protected Sub WebReportPrintPreview_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            If Not Page.IsPostBack Then
                Try
                    Dim dtReport As DataTable = ReportMaster.SelectReportMasterByReportKey(Request.Params("ReportKey").ToString)
                    If dtReport IsNot Nothing AndAlso dtReport.Rows.Count > 0 Then
                        ReportViewer1.ProcessingMode = Microsoft.Reporting.WebForms.ProcessingMode.Remote
                        ReportViewer1.ZoomMode = Microsoft.Reporting.WebForms.ZoomMode.FullPage
                        ReportViewer1.ServerReport.ReportServerUrl = New Uri(ConfigurationManager.AppSettings("SQLReportServer"))
                        ReportViewer1.ServerReport.ReportPath = dtReport.Rows(0)("ReportURL").ToString
                        ReportViewer1.ShowParameterPrompts = False
                        If Not Request.Params("ReportParams") Is Nothing AndAlso Request.Params("ReportParams").ToString.Trim.Length > 0 Then
                            Dim strParams As String() = Request.Params("ReportParams").ToString.Split("|")
                            Dim iParamCount As Integer = strParams.Length
                            If iParamCount > 0 Then
                                Dim parameters(iParamCount - 1) As Microsoft.Reporting.WebForms.ReportParameter
                                For iParam As Integer = 0 To strParams.Length - 1
                                    parameters(iParam) = New Microsoft.Reporting.WebForms.ReportParameter(strParams(iParam).Split("=")(0), strParams(iParam).Split("=")(1))
                                Next
                                ReportViewer1.ServerReport.SetParameters(parameters)
                            End If
                        End If
                    Else
                        btnExit_Click(Nothing, Nothing)
                        Return
                    End If
                Catch Sxc As SqlException
                    EventTracker.Add("WebReportPrintPreview - " & Request.Params("ReportKey").ToString, Sxc.Message.Trim(), SessionManager.UserID)
                Catch Exc As Exception
                    EventTracker.Add("WebReportPrintPreview - " & Request.Params("ReportKey").ToString, Exc.Message.Trim(), SessionManager.UserID)
                End Try
            End If
        End Sub
        Protected Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Dim sScript As New System.Text.StringBuilder
            sScript.Append("<SCRIPT language=""javascript"">" & vbCrLf)
            sScript.Append("window.close();" & vbCrLf)
            sScript.Append("</SCRIPT>" & vbCrLf)
            ClientScript.RegisterStartupScript(Me.GetType, "ForceDefaultToScript", sScript.ToString)
        End Sub
    End Class
End Namespace