#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyMaster1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Anomaly Master"
        Private Shared ReadOnly ProgramName As String = "AnomalyMaster1"
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
                lblAnomalyType.Text = GetTranslationString("anomalytype", lblAnomalyType.Text.Replace(":", "")) & ":"
                lblArea.Text = GetTranslationString("area", lblArea.Text.Replace(":", "")) & ":"
                lblAnomalyStatus.Text = GetTranslationString("anomalystatus", lblAnomalyStatus.Text.Replace(":", "")) & ":"
                lblAnomalyID.Text = GetTranslationString("anomalyid", lblAnomalyID.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
                lblResponsibleUser.Text = GetTranslationString("responsibleuser", lblResponsibleUser.Text.Replace(":", "")) & ":"
                lblOrigin.Text = GetTranslationString("origin", lblOrigin.Text.Replace(":", "")) & ":"
                ckAllAreas.Text = GetTranslationString("allareas", ckAllAreas.Text)
                ckSGI.Text = GetTranslationString("showsgi", ckSGI.Text)
                btnApplyFilter.Text = GetTranslationString("applyfilter", btnApplyFilter.Text)
                btnClearFilter.Text = GetTranslationString("clearfilter", btnClearFilter.Text)
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

            Master.IconImage = Request.ApplicationPath & "/images/data_information.gif"
            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.ProgramName = ProgramName

            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")
            Master.AddBodyAttribute("onkeydown", "TrapEnterKey(document.getElementById('" + MasterControl1.AddButtonID + "'),window.event)")

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            MasterControl1.GridColumns(9).DataFormatString = "{0:yyyy/MM/dd}"
            MasterControl1.GridColumns(11).DataFormatString = "{0:yyyy/MM/dd}"
            MasterControl1.GridColumns(12).DataFormatString = "{0:yyyy/MM/dd}"

            Dim objCol As ButtonField
            objCol = New ButtonField
            objCol.ButtonType = ButtonType.Link
            objCol.Text = GetTranslationString("actions", "Actions")
            objCol.CommandName = "Actions"
            MasterControl1.GridColumns.Add(objCol)

            If Not Page.IsPostBack Then
                LoadFilterDropDowns()
                ApplyFiltersFromCookie()
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

            BindGrid()
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles MasterControl1.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsNumeric(e.Row.Cells(6).Text) AndAlso IsDate(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("OpenTargetDate").ToString) Then
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("OpenTargetDate").ToString)

                    If DateTime.Compare(dtTargetDate, Date.Now) <= 0 Then
                        e.Row.Cells(6).BackColor = Drawing.Color.Red
                    End If
                End If

                If IsDate(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("ClosedDateTime").ToString) Then
                    Try
                        CType(e.Row.Cells(23).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                ElseIf IsNumeric(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditAnomaly").ToString) AndAlso Convert.ToInt16(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("EditAnomaly").ToString) <> 1 Then
                    Try
                        CType(e.Row.Cells(22).Controls(0), LinkButton).Enabled = False
                        CType(e.Row.Cells(23).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                ElseIf MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("AutoGenerated").ToString.ToUpper = "TRUE" Then
                    Try
                        CType(e.Row.Cells(23).Controls(0), LinkButton).Enabled = False
                    Catch ex As Exception
                        'do nothing
                    End Try
                End If

                If Convert.ToBoolean(MasterControl1.MasterControlGrid.DataKeys(e.Row.RowIndex)("Attachments")) Then
                    e.Row.Cells(15).Text = ""
                    Dim img As New Image()
                    img.ImageUrl = "~/images/small_mail_attachment.gif"
                    e.Row.Cells(15).Controls.Add(img)
                Else
                    e.Row.Cells(15).Text = ""
                End If
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
                Case "ViewRow", "EditRow", "DeleteRow"
                    SessionManager.SelectedValueAnomalyID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    SessionManager.AnomalyMode = e.CommandName
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
                Case "Actions"
                    SessionManager.SelectedValueAnomalyID = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("AnomalyID").ToString
                    If IsDate(MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("ClosedDateTime").ToString) Then
                        SessionManager.AnomalyMode = "ViewRow"
                    Else
                        SessionManager.AnomalyMode = "EditRow"
                    End If
                    LastPixelPositionUpdate(ProgramName, Master.CurrentPixelPosition)
                    SessionManager.MasterControlExitProgram = "AnomalyMaster1"

                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
            End Select
        End Sub
        Protected Sub btnApplyFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnApplyFilter.Click
            Dim cookie As New HttpCookie("AnomalyMasterFilter")
            cookie.Expires = Now.AddDays(Convert.ToInt16(ConfigurationManager.AppSettings("CookieExpirationTime")))

            If ddlAnomalyType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyType.SelectedItem.Value) Then
                cookie.Values("AnomalyTypeID") = ddlAnomalyType.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("AnomalyTypeID")
            End If

            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                cookie.Values("AreaGroupID") = ddlArea.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("AreaGroupID")
            End If

            If ckAllAreas.Checked Then
                cookie.Values("AllAreas") = ckAllAreas.Checked
            Else
                cookie.Values.Remove("AllAreas")
            End If

            If ckSGI.Checked Then
                cookie.Values("ShowSGI") = ckSGI.Checked
            Else
                cookie.Values.Remove("ShowSGI")
            End If

            If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso ddlResponsibleUser.SelectedItem.Value.ToString.Trim.Length > 0 Then
                cookie.Values("ResponsibleUser") = ddlResponsibleUser.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("ResponsibleUser")
            End If

            If ddlOrigin1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin1.SelectedItem.Value) Then
                cookie.Values("Origin1") = ddlOrigin1.SelectedItem.Value.ToString
                If Request.Cookies("AnomalyMasterFilter") IsNot Nothing AndAlso Request.Cookies("AnomalyMasterFilter")("Origin1") IsNot Nothing AndAlso ddlOrigin1.SelectedItem.Value.ToString <> Request.Cookies("AnomalyMasterFilter")("Origin1") Then
                    LoadOrigin2DDL()
                ElseIf Request.Cookies("AnomalyMasterFilter") Is Nothing OrElse Request.Cookies("AnomalyMasterFilter")("Origin1") Is Nothing Then
                    LoadOrigin2DDL()
                End If
            Else
                cookie.Values.Remove("Origin1")
                LoadOrigin2DDL()
            End If
            If ddlOrigin2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin2.SelectedItem.Value) Then
                cookie.Values("Origin2") = ddlOrigin2.SelectedItem.Value.ToString
                If Request.Cookies("AnomalyMasterFilter") IsNot Nothing AndAlso Request.Cookies("AnomalyMasterFilter")("Origin2") IsNot Nothing AndAlso ddlOrigin2.SelectedItem.Value.ToString <> Request.Cookies("AnomalyMasterFilter")("Origin2") Then
                    LoadOrigin3DDL()
                ElseIf Request.Cookies("AnomalyMasterFilter") Is Nothing OrElse Request.Cookies("AnomalyMasterFilter")("Origin2") Is Nothing Then
                    LoadOrigin3DDL()
                End If
            Else
                cookie.Values.Remove("Origin2")
                LoadOrigin3DDL()
            End If
            If ddlOrigin3.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin3.SelectedItem.Value) Then
                cookie.Values("Origin3") = ddlOrigin3.SelectedItem.Value.ToString
            Else
                cookie.Values.Remove("Origin3")
            End If

            Response.Cookies.Add(cookie)

            If ddlAnomalyStatus.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyStatus.SelectedItem.Value) Then
                SessionManager.AnomalyMasterFilterStatus = ddlAnomalyStatus.SelectedItem.Value
            Else
                SessionManager.AnomalyMasterFilterStatus = "0"
            End If

            If IsNumeric(txtAnomalyID.Text) AndAlso Convert.ToInt32(txtAnomalyID.Text) > 0 Then
                SessionManager.AnomalyMasterFilterAnomalyID = Convert.ToInt32(txtAnomalyID.Text)
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMasterFilterAnomalyID)
            End If

            If Not String.IsNullOrEmpty(txtDescription.Text.Trim) Then
                SessionManager.AnomalyMasterFilterSearch = txtDescription.Text.Trim
            Else
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMasterFilterSearch)
            End If

            BindGrid()
        End Sub
        Protected Sub btnClearFilter_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClearFilter.Click
            Response.Cookies("AnomalyMasterFilter").Expires = Now
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMasterFilterStatus)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMasterFilterAnomalyID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMasterFilterSearch)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadFilterDropDowns()
            Try
                AnomalyTypeMaster.GetAnomalyTypeMasterList(ddlAnomalyType)
                ddlAnomalyType.Items.Insert(0, "")

                AreaGroupMaster.GetAreaGroupMasterList(ddlArea, SessionManager.WorkingSiteID)
                ddlArea.Items.Insert(0, "")

                AnomalyMaster.SelectAnomalyUserNameList(SessionManager.WorkingSiteID, ddlResponsibleUser)
                ddlResponsibleUser.Items.Insert(0, "")

                AnomalyOrigins.GetAnomalyOrigins1(SessionManager.WorkingSiteID, ddlOrigin1)
                ddlOrigin1.Items.Insert(0, "")

                If ddlOrigin1.Items.Count > 1 Then
                    pnlOrigin.Visible = True
                Else
                    pnlOrigin.Visible = False
                End If
            Catch ex As Exception

            End Try
        End Sub
        Private Sub LoadOrigin2DDL()
            ddlOrigin2.Items.Clear()
            ddlOrigin3.Items.Clear()

            If ddlOrigin1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin1.SelectedItem.Value) Then
                AnomalyOrigins.GetAnomalyOrigins2(ddlOrigin1.SelectedItem.Value, ddlOrigin2)
                ddlOrigin2.Items.Insert(0, "")
            End If
        End Sub
        Private Sub LoadOrigin3DDL()
            ddlOrigin3.Items.Clear()

            If ddlOrigin2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin2.SelectedItem.Value) Then
                AnomalyOrigins.GetAnomalyOrigins3(ddlOrigin2.SelectedItem.Value, ddlOrigin3)
                ddlOrigin3.Items.Insert(0, "")
            End If
        End Sub
        Private Sub ApplyFiltersFromCookie()
            Dim objItem As ListItem

            If Request.Cookies("AnomalyMasterFilter") IsNot Nothing Then
                Dim cookie As HttpCookie = Request.Cookies("AnomalyMasterFilter")

                If cookie.Values("AnomalyTypeID") IsNot Nothing AndAlso IsNumeric(cookie.Values("AnomalyTypeID")) Then
                    objItem = ddlAnomalyType.Items.FindByValue(cookie.Values("AnomalyTypeID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("AreaGroupID") IsNot Nothing AndAlso IsNumeric(cookie.Values("AreaGroupID")) Then
                    objItem = ddlArea.Items.FindByValue(cookie.Values("AreaGroupID"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("AllAreas") IsNot Nothing Then
                    ckAllAreas.Checked = cookie.Values("AllAreas")
                End If

                If cookie.Values("ShowSGI") IsNot Nothing Then
                    ckSGI.Checked = cookie.Values("ShowSGI")
                End If

                If cookie.Values("ResponsibleUser") IsNot Nothing AndAlso Not String.IsNullOrEmpty(cookie.Values("ResponsibleUser")) Then
                    objItem = ddlResponsibleUser.Items.FindByValue(cookie.Values("ResponsibleUser"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                If cookie.Values("Origin1") IsNot Nothing AndAlso IsNumeric(cookie.Values("Origin1")) Then
                    objItem = ddlOrigin1.Items.FindByValue(cookie.Values("Origin1"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                LoadOrigin2DDL()
                If cookie.Values("Origin2") IsNot Nothing AndAlso IsNumeric(cookie.Values("Origin2")) Then
                    objItem = ddlOrigin2.Items.FindByValue(cookie.Values("Origin2"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If

                LoadOrigin3DDL()
                If cookie.Values("Origin3") IsNot Nothing AndAlso IsNumeric(cookie.Values("Origin3")) Then
                    objItem = ddlOrigin3.Items.FindByValue(cookie.Values("Origin3"))
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                    End If
                End If
            End If

            If IsNumeric(SessionManager.AnomalyMasterFilterStatus) Then
                objItem = ddlAnomalyStatus.Items.FindByValue(SessionManager.AnomalyMasterFilterStatus)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                ElseIf SessionManager.AnomalyMasterFilterStatus = "0" Then
                    ddlAnomalyStatus.Items(0).Selected = True
                Else
                    ddlAnomalyStatus.Items(2).Selected = True
                End If
            Else
                ddlAnomalyStatus.Items(2).Selected = True
            End If
            If SessionManager.AnomalyMasterFilterAnomalyID > 0 Then
                txtAnomalyID.Text = SessionManager.AnomalyMasterFilterAnomalyID
            End If

            txtDescription.Text = SessionManager.AnomalyMasterFilterSearch
        End Sub
        Private Sub BindGrid()
            MasterControl1.StoredProcedureParams.Add("@UserID", SessionManager.UserID)
            MasterControl1.StoredProcedureParams.Add("@SiteID", SessionManager.WorkingSiteID)
            If IsNumeric(txtAnomalyID.Text) AndAlso Convert.ToInt32(txtAnomalyID.Text) > 0 Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyID", txtAnomalyID.Text)
            End If
            If ddlAnomalyType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyType.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyTypeID", ddlAnomalyType.SelectedItem.Value.ToString)
            End If
            If ddlAnomalyStatus.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyStatus.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyStatusID", ddlAnomalyStatus.SelectedItem.Value)
            End If
            If ddlArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlArea.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AreaGroupID", ddlArea.SelectedItem.Value)
            End If
            MasterControl1.StoredProcedureParams.Add("@AllAreas", ckAllAreas.Checked)
            MasterControl1.StoredProcedureParams.Add("@SGI", ckSGI.Checked)
            If ddlResponsibleUser.SelectedItem IsNot Nothing AndAlso Not String.IsNullOrEmpty(ddlResponsibleUser.SelectedItem.Value.ToString) Then
                MasterControl1.StoredProcedureParams.Add("@ResponsibleUserID", ddlResponsibleUser.SelectedItem.Value.ToString.Trim)
            End If
            If ddlOrigin1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin1.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyOrigin1", ddlOrigin1.SelectedItem.Value)
            End If
            If ddlOrigin2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin2.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyOrigin2", ddlOrigin2.SelectedItem.Value)
            End If
            If ddlOrigin3.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigin3.SelectedItem.Value) Then
                MasterControl1.StoredProcedureParams.Add("@AnomalyOrigin3", ddlOrigin3.SelectedItem.Value)
            End If
            If Not String.IsNullOrEmpty(txtDescription.Text.Trim) Then
                MasterControl1.StoredProcedureParams.Add("@Description", txtDescription.Text.Trim)
            End If

            MasterControl1.DataBind(True)
        End Sub
#End Region

    End Class
End Namespace
