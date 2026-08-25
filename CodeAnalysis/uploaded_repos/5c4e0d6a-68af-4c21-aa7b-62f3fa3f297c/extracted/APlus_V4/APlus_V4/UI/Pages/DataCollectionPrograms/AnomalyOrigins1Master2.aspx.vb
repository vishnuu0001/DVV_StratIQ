#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyOrigins1Master2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Origins 1 Master"
        Private Shared ReadOnly ProgramName As String = "AnomalyOrigins1Master2"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.ClientID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.ClientID + "'),window.event)")
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Master.HeaderMessage = FormName & " - " & SessionManager.Origin1Mode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/document.gif"

            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.Origin1Mode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtOrigin1.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Category 1.');")
                    Case "AddRow"
                        txtOrigin1ID.Text = "NEW"
                        txtOrigin1.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins1Master1"))
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean = SaveRecord()

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin1ID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin1Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins1Master1"))
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin1ID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin1Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins1Master1"))
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
            Try
                Dim objDT As DataTable = AnomalyOrigins.SelectAnomalyOrigins1(SessionManager.SelectedValueOrigin1ID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)

                    txtOrigin1ID.Text = dtRow("AnomalyOrigin1ID").ToString
                    txtOrigin1.Text = dtRow("AnomalyOrigin1").ToString
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Select Case SessionManager.Origin1Mode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtOrigin1.ReadOnly = True
                    txtOrigin1.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function SaveRecord() As Boolean
            Dim blnSuccess As Boolean = False

            Try
                Select Case SessionManager.Origin1Mode
                    Case "DeleteRow"
                        blnSuccess = DeleteOrigin1()
                    Case "EditRow"
                        blnSuccess = UpdateOrigin1()
                    Case "AddRow"
                        blnSuccess = InsertOrigin1()
                End Select
            Catch ex As Exception
                Return False
            End Try

            Return blnSuccess
        End Function
        Private Function InsertOrigin1() As Boolean
            Try
                AnomalyOrigins.InsertAnomalyOrigin1(SessionManager.WorkingSiteID, txtOrigin1.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertOrigin1", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateOrigin1() As Boolean
            Try
                AnomalyOrigins.UpdateAnomalyOrigin1(SessionManager.SelectedValueOrigin1ID, SessionManager.WorkingSiteID, txtOrigin1.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateOrigin1", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteOrigin1() As Boolean
            Try
                AnomalyOrigins.DeleteAnomalyOrigin1(SessionManager.SelectedValueOrigin1ID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteOrigin1", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
#End Region

    End Class
End Namespace
