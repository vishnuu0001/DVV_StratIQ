#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyOrigins3Master2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Origin 3 Master"
        Private Shared ReadOnly ProgramName As String = "AnomalyOrigins3Master2"
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
            Master.HeaderMessage = FormName & " - " & SessionManager.Origin3Mode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/document.gif"

            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")
            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadOrigin2()

                Select Case SessionManager.Origin3Mode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtOrigin3.Focus()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Anomaly Origin 3.');")
                    Case "AddRow"
                        txtOrigin3ID.Text = "NEW"
                        txtOrigin3.Focus()
                        If SessionManager.SelectedValueOrigin2ID > 0 Then
                            Dim objItem As ListItem = ddlOrigin2.Items.FindByValue(SessionManager.SelectedValueOrigin2ID)
                            If Not objItem Is Nothing Then
                                objItem.Selected = True
                                txtOrigin2.Text = objItem.Text
                                ddlOrigin2.Visible = False
                                txtOrigin2.Visible = True
                            End If
                        Else
                            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins3Master1"))
                        End If
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins3Master1"))
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Dim blnSuccess As Boolean

            Select Case SessionManager.Origin3Mode
                Case "DeleteRow"
                    blnSuccess = DeleteCategory3()
                Case "EditRow"
                    blnSuccess = UpdateCategory3()
                Case "AddRow"
                    blnSuccess = InsertCategory3()
            End Select
            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin3ID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin3Mode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins3Master1"))
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click, btnExit.Click
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueOrigin3ID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Origin3Mode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyOrigins3Master1"))
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadOrigin2()
            Try
                ddlOrigin2.Items.Clear()
                AnomalyOrigins.GetAnomalyOrigins2(SessionManager.SelectedValueOrigin1ID, ddlOrigin2)
                ddlOrigin2.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCategory2", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                Dim objDT As DataTable = AnomalyOrigins.SelectAnomalyOrigins3(SessionManager.SelectedValueOrigin3ID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    Dim dtRow As DataRow = objDT.Rows(0)
                    Dim objItem As ListItem = ddlOrigin2.Items.FindByValue(dtRow("AnomalyOrigin2ID").ToString)
                    If Not objItem Is Nothing Then
                        objItem.Selected = True
                        txtOrigin2.Text = objItem.Text
                    End If

                    txtOrigin3ID.Text = dtRow("AnomalyOrigin3ID").ToString
                    txtOrigin3.Text = dtRow("AnomalyOrigin3").ToString
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Sub UnEnableRecords()
            Select Case SessionManager.Origin3Mode
                Case "EditRow"
                    ddlOrigin2.Visible = False
                    txtOrigin2.Visible = True
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    ddlOrigin2.Visible = False
                    txtOrigin2.Visible = True
                    txtOrigin3.ReadOnly = True
                    txtOrigin3.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function InsertCategory3() As Boolean
            Try
                AnomalyOrigins.InsertAnomalyOrigin3(Convert.ToInt32(ddlOrigin2.SelectedItem.Value.ToString), txtOrigin3.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertCategory3", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
            Return True
        End Function
        Private Function UpdateCategory3() As Boolean
            Try
                AnomalyOrigins.UpdateAnomalyOrigin3(SessionManager.SelectedValueOrigin3ID, Convert.ToInt32(ddlOrigin2.SelectedItem.Value.ToString), txtOrigin3.Text.Trim)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateCategory3", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
            Return True
        End Function
        Private Function DeleteCategory3() As Boolean
            Try
                AnomalyOrigins.DeleteAnomalyOrigin3(SessionManager.SelectedValueOrigin3ID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteCategory3", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace
