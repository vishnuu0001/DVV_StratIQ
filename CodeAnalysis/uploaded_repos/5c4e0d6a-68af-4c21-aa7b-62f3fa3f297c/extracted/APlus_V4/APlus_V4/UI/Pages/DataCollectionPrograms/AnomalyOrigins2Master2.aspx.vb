#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyOrigins2Master2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Origin 2 Master"
        Private Shared ReadOnly ProgramName As String = "AnomalyOrigins2Master2"
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
            Master.HeaderMessage = FormName & " - " & SessionManager.Origin2Mode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/document.gif"

            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadOrigin1()

                Select Case SessionManager.Origin2Mode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtOrigin2.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Anomaly Origin 2.');")
                    Case "AddRow"
                        txtOrigin2ID.Text = "NEW"
                        txtOrigin2.Focus()
                        If SessionManager.SelectedValueOrigin1ID > 0 Then
                            Dim objItem As ListItem = ddlOrigin1.Items.FindByValue(SessionManager.SelectedValueOrigin1ID)
                            If Not objItem Is Nothing Then
                                objItem.Selected = True
                                txtOrigin1.Text = objItem.Text
                                ddlOrigin1.Visible = False
                                txtOrigin1.Visible = True
                            End If
                        Else
                            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
                        End If
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean = SaveRecord()

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin2ID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin2Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin2ID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin2Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins2Master1"))
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadOrigin1()
            Try
                ddlOrigin1.Items.Clear()
                AnomalyOrigins.GetAnomalyOrigins1(SessionManager.WorkingSiteID, ddlOrigin1)
                ddlOrigin1.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCategory1", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                Dim objDT As DataTable = AnomalyOrigins.SelectAnomalyOrigins2(SessionManager.SelectedValueOrigin2ID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem = ddlOrigin1.Items.FindByValue(SessionManager.SelectedValueOrigin1ID)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtOrigin1.Text = objItem.Text
                    End If
                    txtOrigin2ID.Text = dtRow("AnomalyOrigin2ID").ToString
                    txtOrigin2.Text = dtRow("AnomalyOrigin2").ToString
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Sub UnEnableRecords()
            Select Case SessionManager.Origin2Mode
                Case "EditRow"
                    ddlOrigin1.Visible = False
                    txtOrigin1.Visible = True
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    ddlOrigin1.Visible = False
                    txtOrigin1.Visible = True
                    txtOrigin2.ReadOnly = True
                    txtOrigin2.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function SaveRecord() As Boolean
            Dim blnSuccess As Boolean = False

            Try
                Select Case SessionManager.Origin2Mode
                    Case "DeleteRow"
                        blnSuccess = DeleteOrigin2()
                    Case "EditRow"
                        blnSuccess = UpdateOrigin2()
                    Case "AddRow"
                        blnSuccess = InsertOrigin2()
                End Select
            Catch ex As Exception
                Return False
            End Try

            Return blnSuccess
        End Function
        Private Function InsertOrigin2() As Boolean
            Try
                AnomalyOrigins.InsertAnomalyOrigin2(Convert.ToInt32(ddlOrigin1.SelectedItem.Value.ToString), txtOrigin2.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertOrigin2", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try

            Return True
        End Function
        Private Function UpdateOrigin2() As Boolean
            Try
                AnomalyOrigins.UpdateAnomalyOrigin2(SessionManager.SelectedValueOrigin2ID, Convert.ToInt32(ddlOrigin1.SelectedItem.Value.ToString), txtOrigin2.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateOrigin2", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteOrigin2() As Boolean
            Try
                AnomalyOrigins.DeleteAnomalyOrigin2(SessionManager.SelectedValueOrigin2ID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteOrigin2", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
            Return True
        End Function
#End Region

    End Class
End Namespace
