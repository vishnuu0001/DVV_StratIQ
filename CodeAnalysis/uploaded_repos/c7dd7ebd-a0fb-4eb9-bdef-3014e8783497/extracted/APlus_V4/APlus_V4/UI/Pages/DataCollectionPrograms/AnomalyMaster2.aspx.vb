#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class AnomalyMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Anomaly Master"
        Private Shared ReadOnly ProgramName As String = "AnomalyMaster2"
        Private Shared ReadOnly DBTableName As String = "AnomalyMaster"
        Private bCloseAnomaly As Boolean = False
        Private bEvaluateAnomaly As Boolean = False
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
                lblAnomalyID.Text = GetTranslationString("anomalyid", lblAnomalyID.Text.Replace(":", "")) & ":"
                lblSite.Text = GetTranslationString("site", lblSite.Text.Replace(":", "")) & ":"
                lblAnomalyType.Text = GetTranslationString("anomalytype", lblAnomalyType.Text.Replace(":", "")) & ":"
                lblArea.Text = GetTranslationString("area", lblArea.Text.Replace(":", "")) & ":"
                lblAnomaly.Text = GetTranslationString("anomaly", lblAnomaly.Text.Replace(":", "")) & ":"
                lblDescription.Text = GetTranslationString("description", lblDescription.Text.Replace(":", "")) & ":"
                lblKPI.Text = GetTranslationString("kpi", lblKPI.Text.Replace(":", "")) & ":"
                lblSGI.Text = GetTranslationString("sgi", lblSGI.Text.Replace(":", "")) & ":"
                rblSGI.Items(0).Text = GetTranslationString("Yes")
                rblSGI.Items(1).Text = GetTranslationString("No")
                lblChangeFEMEA.Text = GetTranslationString("changefemea", lblChangeFEMEA.Text.Replace(":", "")) & ":"
                rblFEMEA.Items(0).Text = GetTranslationString("Yes")
                rblFEMEA.Items(1).Text = GetTranslationString("No")
                lblFEMEADescription.Text = GetTranslationString("femeadescription", lblFEMEADescription.Text.Replace(":", "")) & ":"
                lblFEMEAJustification.Text = GetTranslationString("justification", lblFEMEAJustification.Text.Replace(":", "")) & ":"
                lblRiskAnalysis.Text = GetTranslationString("riskanalysis", lblRiskAnalysis.Text.Replace(":", "")) & ":"
                rblRiskAnalysis.Items(0).Text = GetTranslationString("rblrisk1", rblRiskAnalysis.Items(0).Text)
                rblRiskAnalysis.Items(1).Text = GetTranslationString("rblrisk2", rblRiskAnalysis.Items(1).Text)
                lblRiskJustification.Text = GetTranslationString("justification", lblRiskJustification.Text.Replace(":", "")) & ":"
                lblRiskResult.Text = GetTranslationString("riskresult", lblRiskResult.Text.Replace(":", "")) & ":"
                ckRiskResult1.Text = GetTranslationString("riskresult1", ckRiskResult1.Text)
                ckRiskResult2.Text = GetTranslationString("riskresult2", ckRiskResult2.Text)
                ckRiskResult3.Text = GetTranslationString("riskresult3", ckRiskResult3.Text)
                lblRiskResultJustification.Text = GetTranslationString("riskresultjustification", lblRiskResultJustification.Text.Replace(":", "")) & ":"
                lblSystemAgainstError.Text = GetTranslationString("systemagainsterror", lblSystemAgainstError.Text.Replace(":", "")) & ":"
                lblResponsibleUser.Text = GetTranslationString("responsibleuser", lblResponsibleUser.Text.Replace(":", "")) & ":"
                lblOrigin.Text = GetTranslationString("origin", lblOrigin.Text.Replace(":", "")) & ":"
                lblObservations.Text = GetTranslationString("observations", lblObservations.Text.Replace(":", "")) & ":"
                lblClosedDate.Text = GetTranslationString("closeddate", lblClosedDate.Text.Replace(":", "")) & ":"
                rblCancelled.Items(0).Text = GetTranslationString("completed", rblCancelled.Items(0).Text)
                rblCancelled.Items(1).Text = GetTranslationString("cancelled", rblCancelled.Items(1).Text)
                lblEvaluation.Text = GetTranslationString("evaluation", lblEvaluation.Text.Replace(":", "")) & ":"
                lblEvaluatedDate.Text = GetTranslationString("evaluateddate", lblEvaluatedDate.Text.Replace(":", "")) & ":"
                rblEffective.Items(0).Text = GetTranslationString("effective", rblEffective.Items(0).Text)
                rblEffective.Items(1).Text = GetTranslationString("ineffective", rblEffective.Items(1).Text)
                lblAutoGenerated.Text = GetTranslationString("autogenerated", lblAutoGenerated.Text.Replace(":", "")) & ":"
                lblCreatedDate.Text = GetTranslationString("createddate", lblCreatedDate.Text.Replace(":", "")) & ":"
                lblCreatedUser.Text = GetTranslationString("createduser", lblCreatedUser.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)
                btnAnomalyActions.Text = GetTranslationString("anomalyactions", btnAnomalyActions.Text)
                btnAnomalyActions1.Text = GetTranslationString("anomalyactions", btnAnomalyActions1.Text)
                lblAnomalyCauses.Text = GetTranslationString("anomalycauses", lblAnomalyCauses.Text)
                lblAnomalyActions.Text = GetTranslationString("anomalyactions", lblAnomalyActions.Text)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddEditModeJavaScripts()
            If pnlSGI.Visible Then
                Dim myTabArray() As Object = {ddlAnomalyType, _
                                              ddlArea, _
                                              ddlKPIID, _
                                              txtAnomaly, _
                                              txtExpandSubject, _
                                              rblSGI, _
                                              rblFEMEA, _
                                              txtFEMEADescription, _
                                              txtExpandFEMEAJustification, _
                                              rblRiskAnalysis, _
                                              txtExpandRiskJustification, _
                                              ckRiskResult1, _
                                              ckRiskResult2, _
                                              ckRiskResult3, _
                                              txtExpandRiskResultJustification, _
                                              txtExpandSystemAgainstError, _
                                              ddlResponsibleUser, _
                                              txtExpandObservations, _
                                              rblCancelled, _
                                              rblEffective}

                Dim TabKeyDownArr() As String = {Tab(ddlArea, rblEffective, "No"), _
                                                 Tab(ddlKPIID, ddlAnomalyType, "No"), _
                                                 Tab(txtAnomaly, ddlArea, "No"), _
                                                 Tab(txtExpandSubject, ddlKPIID, "No"), _
                                                 Tab(rblSGI, txtAnomaly, "No"), _
                                                 Tab(rblFEMEA, txtExpandSubject, "No"), _
                                                 Tab(txtFEMEADescription, rblSGI, "No"), _
                                                 Tab(txtExpandFEMEAJustification, rblFEMEA, "No"), _
                                                 Tab(rblRiskAnalysis, txtFEMEADescription, "No"), _
                                                 Tab(txtExpandRiskJustification, txtExpandFEMEAJustification, "No"), _
                                                 Tab(ckRiskResult1, rblRiskAnalysis, "No"), _
                                                 Tab(ckRiskResult2, txtExpandRiskJustification, "No"), _
                                                 Tab(ckRiskResult3, ckRiskResult1, "No"), _
                                                 Tab(txtExpandRiskResultJustification, ckRiskResult2, "No"), _
                                                 Tab(txtExpandSystemAgainstError, ckRiskResult3, "No"), _
                                                 Tab(ddlResponsibleUser, txtExpandRiskResultJustification, "No"), _
                                                 Tab(txtExpandObservations, txtExpandSystemAgainstError, "No"), _
                                                 Tab(rblCancelled, ddlResponsibleUser, "No"), _
                                                 Tab(rblEffective, txtExpandObservations, "No"), _
                                                 Tab(ddlAnomalyType, rblCancelled, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            Else
                Dim myTabArray() As Object = {ddlAnomalyType, _
                                              ddlArea, _
                                              ddlKPIID, _
                                              txtAnomaly, _
                                              txtExpandSubject, _
                                              ddlResponsibleUser, _
                                              txtExpandObservations, _
                                              rblCancelled, _
                                              rblEffective}

                Dim TabKeyDownArr() As String = {Tab(ddlArea, rblEffective, "No"), _
                                                 Tab(ddlKPIID, ddlAnomalyType, "No"), _
                                                 Tab(txtAnomaly, ddlArea, "No"), _
                                                 Tab(txtExpandSubject, ddlKPIID, "No"), _
                                                 Tab(ddlResponsibleUser, txtAnomaly, "No"), _
                                                 Tab(txtExpandObservations, txtExpandSubject, "No"), _
                                                 Tab(rblCancelled, ddlResponsibleUser, "No"), _
                                                 Tab(rblEffective, txtExpandObservations, "No"), _
                                                 Tab(ddlAnomalyType, rblCancelled, "No")}

                AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
            End If
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

            Master.HeaderMessage = GetTranslationString(FormName, FormName) & " - " & GetTranslationString(SessionManager.AnomalyMode.Replace("Row", ""), SessionManager.AnomalyMode.Replace("Row", ""))
            Master.IconImage = Request.ApplicationPath + "/images/data_information.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            mcCauses.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)
            mcActions.StoredProcedureParams.Add("@AnomalyID", SessionManager.SelectedValueAnomalyID)

            mcActions.GridColumns(5).DataFormatString = "{0:yyyy/MM/dd}"
            mcActions.GridColumns(8).DataFormatString = "{0:yyyy/MM/dd}"

            Dim objDT As DataTable = AnomalyMaster.SelectAnomalyEditAuthority(SessionManager.SelectedValueAnomalyID, SessionManager.UserID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                bCloseAnomaly = Convert.ToBoolean(dtRow("EditAnomaly"))
                bEvaluateAnomaly = Convert.ToBoolean(dtRow("Evaluate"))
            End If

            If Not Page.IsPostBack Then
                If SessionManager.WorkingSiteID = 0 Then
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster1"), False)

                    Return
                End If

                If Not bCloseAnomaly AndAlso Not bEvaluateAnomaly AndAlso SessionManager.AnomalyMode = "EditRow" Then
                    SessionManager.AnomalyMode = "ViewRow"
                End If

                objDT = SiteMaster.GetSiteMasterAttributesBySite(SessionManager.WorkingSiteID)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    If objDT.Rows(0)("ShowAnomalySGI") IsNot DBNull.Value AndAlso Convert.ToBoolean(objDT.Rows(0)("ShowAnomalySGI")) Then
                        pnlSGI.Visible = True
                    End If
                End If

                LoadCultureTranslations()
                BindDropDownLists()
                LoadAnomalyOrigins1()

                Select Case SessionManager.AnomalyMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "AddAttachment"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()

                        btnAnomalyActions1.Visible = False
                        btnReOpenAnomaly1.Visible = False
                        pnlAddAttachment.Visible = True
                        If bCloseAnomaly Then
                            gvAttachments.Columns(1).Visible = True
                        End If
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Anomaly.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtAnomalyID.Text = "New"

                        If SessionManager.WorkingSiteID > 0 Then
                            Dim objItem As ListItem = ddlSite.Items.FindByValue(SessionManager.WorkingSiteID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtSite.Text = objItem.Text
                            Else
                                Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(SessionManager.WorkingSiteID)
                                If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                                    Dim drSite As DataRow = dtSite.Rows(0)
                                    objItem = New ListItem(drSite("SiteAbbrev").ToString & " - " & drSite("Site").ToString, drSite("SiteID").ToString)
                                    ddlSite.Items.Add(objItem)
                                    objItem.Selected = True
                                    txtSite.Text = objItem.Text
                                End If
                            End If
                        End If

                        LoadAddEditModeJavaScripts()
                        UnEnableRecords()
                        txtAnomaly.Focus()
                    Case "EditRow"
                        pnlAddAttachment.Visible = True
                        gvAttachments.Columns(1).Visible = True
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtAnomaly.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster1"), False)
                End Select
            End If
        End Sub
        Protected Sub mcActions_onRowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles mcActions.onRowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If IsDate(e.Row.Cells(6).Text) AndAlso Not IsDate(e.Row.Cells(9).Text) Then
                    Dim dtTargetDate As DateTime = Convert.ToDateTime(e.Row.Cells(5).Text)

                    If DateTime.Compare(dtTargetDate, Date.Now) <= 0 Then
                        e.Row.Cells(6).BackColor = Drawing.Color.Red
                    End If
                End If
            End If
        End Sub
        Protected Sub ddlKPIID_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlKPIID.SelectedIndexChanged
            If ddlKPIID.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlKPIID.SelectedItem.Value) Then
                txtAnomaly.Text = ddlKPIID.SelectedItem.Text.Trim

                Dim dtExternal As DataTable = KPIMaster.SelectKPIMasterByID(ddlKPIID.SelectedItem.Value)
                If dtExternal IsNot Nothing AndAlso dtExternal.Rows.Count = 1 Then
                    Dim strUser As String = dtExternal.Rows(0)("AnomalyResponsibleUserID").ToString
                    If strUser.Trim.Length > 0 Then
                        If ddlResponsibleUser.SelectedItem IsNot Nothing Then
                            ddlResponsibleUser.SelectedItem.Selected = False
                        End If

                        Dim objItem As ListItem = ddlResponsibleUser.Items.FindByValue(strUser)

                        If objItem Is Nothing Then
                            objItem = New ListItem
                            objItem.Value = strUser
                            Dim strHolder As String = UserMaster.GetUserFullNameLastNameFirst(strUser)
                            If strHolder.Trim.Length > 0 Then
                                strHolder += " (" & strUser & ")"
                                objItem.Text = strHolder
                            Else
                                objItem.Text = strUser
                            End If
                            objItem.Selected = True
                            ddlResponsibleUser.Items.Insert(0, objItem)
                        ElseIf objItem IsNot Nothing Then
                            objItem.Selected = True
                        End If
                    End If
                End If
            End If
        End Sub
        Protected Sub ddlUserSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlUserSite.SelectedIndexChanged
            LoadResponsibleUserDDL()
        End Sub
        Protected Sub ddlOrigins1_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlOrigins1.SelectedIndexChanged
            LoadAnomalyOrigins2()
        End Sub
        Protected Sub ddlOrigins2_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlOrigins2.SelectedIndexChanged
            LoadAnomalyOrigins3()
        End Sub
        Protected Sub btnAnomalyActions_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAnomalyActions.Click, btnAnomalyActions1.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.AnomalyMode
                Case "ViewRow", "DeleteRow"
                    SessionManager.MasterControlExitProgram = "AnomalyMaster2"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
                Case "AddRow"
                    If SaveRecord() Then
                        ViewState("Actions") = "True"
                        ViewModeObjectStyle()
                        mpAddAttachments.Show()
                        Return
                    End If
                Case Else
                    If SaveRecord() Then
                        RedirectToActions()
                    End If
            End Select
        End Sub
        Protected Sub btnReOpenAnomaly_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnReOpenAnomaly.Click, btnReOpenAnomaly1.Click
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
                AnomalyMaster.UpdateAnomalyReOpen(SessionManager.SelectedValueAnomalyID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID.ToString, "Anomaly ReOpened", SessionManager.UserID)

                SessionManager.AnomalyMode = "EditRow"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ReOpen Anomaly", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
            End Try
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean = SaveRecord()
            If blnSuccess Then
                Select Case SessionManager.AnomalyMode
                    Case "AddRow"
                        ViewModeObjectStyle()
                        mpAddAttachments.Show()
                        Return
                    Case Else
                        RedirectGoBack()
                End Select
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click, btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RedirectGoBack()
        End Sub
        Protected Sub btnAttach_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAttach.Click
            If fil.PostedFile.FileName.Trim.Length = 0 Then
                Return
            End If

            If fil.PostedFile.InputStream.Length = 0 Then
                Return
            End If

            Try
                Dim byteDoc As Byte()
                ReDim byteDoc(fil.PostedFile.InputStream.Length)
                fil.PostedFile.InputStream.Read(byteDoc, 0, fil.PostedFile.InputStream.Length)

                If Not AnomalyAttachments.InsertAttachment(SessionManager.SelectedValueAnomalyID, Path.GetFileName(fil.PostedFile.FileName.Trim), byteDoc) Then
                    Master.DisplayError("Error Inserting Attachment.")
                Else
                    RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID.ToString, "Attachment: " & Path.GetFileName(fil.PostedFile.FileName.Trim), SessionManager.UserID)
                    LoadAttachments()
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - AttachAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
            End Try
        End Sub
        Protected Sub btnAddAttachmentsOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAddAttachmentsOK.Click
            'ViewState("AddAttachments") = "True"
            SessionManager.AnomalyMode = "EditRow"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyMaster2"), False)
        End Sub
        Protected Sub btnAddAttachementsCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnAddAttachementsCancel.Click
            If ViewState("Actions") IsNot Nothing AndAlso ViewState("Actions") = "True" Then
                ViewState.Remove("Actions")
                RedirectToActions()
            Else
                RedirectGoBack()
            End If
        End Sub
        Protected Sub gvAttachments_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles gvAttachments.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                Try
                    Dim objLinkButton As LinkButton = DirectCast(e.Row.FindControl("btnLink"), LinkButton)
                    objLinkButton.Text = gvAttachments.DataKeys(e.Row.RowIndex)("FileName").ToString
                    objLinkButton.CommandArgument = gvAttachments.DataKeys(e.Row.RowIndex)("AttachmentID").ToString

                    Dim objImageButton As ImageButton = DirectCast(e.Row.FindControl("btnDelete"), ImageButton)
                    objImageButton.CommandArgument = gvAttachments.DataKeys(e.Row.RowIndex)("AttachmentID").ToString & "|" & objLinkButton.Text
                    objImageButton.Attributes.Add("onclick", "return confirm('Click OK to Delete this Attachment.');")
                Catch ex As Exception

                End Try
            End If
        End Sub
        Protected Sub gvAttachments_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles gvAttachments.RowCommand
            Select Case e.CommandName
                Case "ViewAttachment"
                    Response.Redirect("ViewDocument.aspx?AttachmentID=" & e.CommandArgument.ToString)
                Case "DeleteAttachment"
                    Try
                        Dim strArgs As String() = e.CommandArgument.ToString.Split("|")
                        Dim iAttachmentID As Integer = Convert.ToInt32(strArgs(0))
                        Dim strFile As String = strArgs(1)

                        If AnomalyAttachments.DeleteAttachment(iAttachmentID) Then
                            RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID.ToString, "Attachment: " & strFile & " deleted", SessionManager.UserID)

                            LoadAttachments()
                        End If
                    Catch Exc As Exception
                        Master.DisplayErrors(ProgramName & " - DeleteAttachment", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                    End Try
            End Select
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub BindDropDownLists()
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
                SiteMaster.SelectSiteMasterActiveList(ddlSite)
                ddlSite.Items.Insert(0, "")

                AnomalyTypeMaster.GetAnomalyTypeMasterList(ddlAnomalyType)
                ddlAnomalyType.Items.Insert(0, "")

                KPIMaster.GetKPISelectionList(ddlKPIID, SessionManager.UserID, SessionManager.WorkingSiteID)
                ddlKPIID.Items.Insert(0, "")

                AreaMaster.GetAreaMasterList(ddlArea, SessionManager.WorkingSiteID)
                ddlArea.Items.Insert(0, "")

                BindUserSites()

                LoadResponsibleUserDDL()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindDropDownLists", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return
            End Try
        End Sub
        Private Sub BindUserSites()
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
                Dim objItem As ListItem = Nothing

                SiteMaster.SelectSiteMasterList(ddlUserSite)
                If SessionManager.WorkingSiteID > 0 Then
                    objItem = ddlUserSite.Items.FindByValue(SessionManager.WorkingSiteID)
                Else
                    objItem = ddlUserSite.Items.FindByValue(UserMaster.GetUserSite(SessionManager.UserID))
                End If
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                Else
                    If ddlUserSite.Items.Count > 0 Then
                        ddlUserSite.Items(0).Selected = True
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserSites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadResponsibleUserDDL()
            Try
                ddlResponsibleUser.Items.Clear()

                If ddlUserSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlUserSite.SelectedItem.Value, True, ddlResponsibleUser)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlResponsibleUser)
                End If

                ddlResponsibleUser.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadAnomalyOrigins1()
            Try
                ddlOrigins1.Items.Clear()

                AnomalyOrigins.GetAnomalyOrigins1(SessionManager.WorkingSiteID, ddlOrigins1)

                If ddlOrigins1.Items.Count = 0 Then
                    pnlOrigins.Visible = False

                    Return
                End If

                ddlOrigins1.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadAnomalyOrigins2()
            Try
                ddlOrigins2.Items.Clear()
                ddlOrigins3.Items.Clear()

                If ddlOrigins1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins1.SelectedItem.Value) Then
                    AnomalyOrigins.GetAnomalyOrigins2(ddlOrigins1.SelectedItem.Value, ddlOrigins2)
                    ddlOrigins2.Items.Insert(0, "")
                    ddlOrigins3.Items.Insert(0, "")
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadAnomalyOrigins3()
            Try
                ddlOrigins3.Items.Clear()

                If ddlOrigins2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins2.SelectedItem.Value) Then
                    AnomalyOrigins.GetAnomalyOrigins3(ddlOrigins2.SelectedItem.Value, ddlOrigins3)
                    ddlOrigins3.Items.Insert(0, "")
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadResponsibleUserDDL", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDT As DataTable = AnomalyMaster.SelectAnomalyMasterByID(SessionManager.SelectedValueAnomalyID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)
                Dim objItem As ListItem = Nothing

                txtAnomalyID.Text = SessionManager.SelectedValueAnomalyID.ToString

                objItem = ddlSite.Items.FindByValue(dtRow("SiteID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtSite.Text = objItem.Text
                Else
                    Dim dtSite As DataTable = SiteMaster.GetSiteMasterBySite(dtRow("SiteID").ToString)
                    If dtSite IsNot Nothing AndAlso dtSite.Rows.Count = 1 Then
                        Dim drSite As DataRow = dtSite.Rows(0)
                        objItem = New ListItem(drSite("Site").ToString, drSite("SiteID").ToString)
                        ddlSite.Items.Add(objItem)
                        objItem.Selected = True
                        txtSite.Text = objItem.Text
                    End If
                End If

                objItem = ddlAnomalyType.Items.FindByValue(dtRow("AnomalyTypeID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtAnomalyType.Text = objItem.Text
                End If

                objItem = ddlArea.Items.FindByValue(dtRow("AreaID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtArea.Text = objItem.Text
                End If

                If IsNumeric(dtRow("KPIID").ToString) Then
                    objItem = ddlKPIID.Items.FindByValue(dtRow("KPIID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtKPIID.Text = objItem.Text
                    Else
                        Dim dtKPI As DataTable = KPIMaster.SelectKPIMasterByID(dtRow("KPIID"))
                        If dtKPI IsNot Nothing AndAlso dtKPI.Rows.Count = 1 Then
                            objItem = New ListItem(dtKPI.Rows(0)("KPI").ToString, dtRow("KPIID"))
                            objItem.Selected = True
                            txtKPIID.Text = objItem.Text

                            ddlKPIID.Items.Add(objItem)
                        End If
                    End If
                End If
                txtAnomaly.Text = dtRow("Anomaly").ToString
                txtExpandSubject.Text = dtRow("Subject").ToString.Trim
                If pnlSGI.Visible Then
                    If dtRow("SGI") IsNot DBNull.Value Then
                        If Convert.ToBoolean(dtRow("SGI")) Then
                            rblSGI.SelectedValue = 1
                        Else
                            rblSGI.SelectedValue = 0
                        End If
                    End If
                    If dtRow("ChangeFEMEA") IsNot DBNull.Value Then
                        If Convert.ToBoolean(dtRow("ChangeFEMEA")) Then
                            rblFEMEA.SelectedValue = 1
                        Else
                            rblFEMEA.SelectedValue = 0
                        End If
                    End If
                    txtFEMEADescription.Text = dtRow("FEMEADescription").ToString.Trim
                    txtExpandFEMEAJustification.Text = dtRow("FEMEAJustification").ToString.Trim
                    If dtRow("RiskAnalysis") IsNot DBNull.Value Then
                        If Convert.ToBoolean(dtRow("RiskAnalysis")) Then
                            rblRiskAnalysis.SelectedValue = 1
                        Else
                            rblRiskAnalysis.SelectedValue = 0
                        End If
                    End If
                    txtExpandRiskJustification.Text = dtRow("RiskJustification").ToString.Trim
                    ckRiskResult1.Checked = Convert.ToBoolean(dtRow("RiskResult1").ToString)
                    ckRiskResult2.Checked = Convert.ToBoolean(dtRow("RiskResult2").ToString)
                    ckRiskResult3.Checked = Convert.ToBoolean(dtRow("RiskResult3").ToString)
                    txtExpandRiskResultJustification.Text = dtRow("RiskResultJustification").ToString.Trim
                    txtExpandSystemAgainstError.Text = dtRow("SystemAgainstError").ToString.Trim
                End If
                objItem = ddlResponsibleUser.Items.FindByValue(dtRow("ResponsibleUserID").ToString)
                If objItem Is Nothing AndAlso dtRow("ResponsibleUserID").ToString.Trim.Length > 0 Then
                    objItem = New ListItem
                    objItem.Value = dtRow("ResponsibleUserID").ToString
                    Dim strHolder As String = UserMaster.GetUserFullNameLastNameFirst(dtRow("ResponsibleUserID").ToString)
                    If strHolder.Trim.Length > 0 Then
                        strHolder += " (" & dtRow("ResponsibleUserID").ToString & ")"
                        objItem.Text = strHolder
                    Else
                        objItem.Text = dtRow("ResponsibleUserID").ToString
                    End If
                    objItem.Selected = True
                    txtResponsibleUser.Text = objItem.Text
                    ddlResponsibleUser.Items.Insert(0, objItem)
                ElseIf objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtResponsibleUser.Text = objItem.Text
                End If
                If pnlOrigins.Visible Then
                    objItem = ddlOrigins1.Items.FindByValue(dtRow("AnomalyOrigin1ID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOrigins1.Text = objItem.Text
                        LoadAnomalyOrigins2()
                    End If
                    objItem = ddlOrigins2.Items.FindByValue(dtRow("AnomalyOrigin2ID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOrigins2.Text = objItem.Text
                        LoadAnomalyOrigins3()
                    End If
                    objItem = ddlOrigins3.Items.FindByValue(dtRow("AnomalyOrigin3ID").ToString)
                    If objItem IsNot Nothing Then
                        objItem.Selected = True
                        txtOrigins3.Text = objItem.Text
                    End If
                End If
                txtExpandObservations.Text = dtRow("Observations").ToString.Trim
                If IsDate(dtRow("ClosedDateTime").ToString) Then
                    txtClosedDate.Text = Convert.ToDateTime(dtRow("ClosedDateTime").ToString).ToString(SessionManager.DateFormat)
                Else
                    txtClosedDate.Text = dtRow("ClosedDateTime").ToString
                End If
                If txtClosedDate.Text.Trim.Length > 0 Then
                    If Convert.ToBoolean(dtRow("Cancelled")) Then
                        rblCancelled.SelectedValue = 1
                    Else
                        rblCancelled.SelectedValue = 0
                    End If
                End If
                txtExpandEvaluation.Text = dtRow("Evaluation").ToString.Trim
                If IsDate(dtRow("EvaluatedDateTime").ToString) Then
                    txtEvaluatedDate.Text = Convert.ToDateTime(dtRow("EvaluatedDateTime").ToString).ToString(SessionManager.DateFormat)
                Else
                    txtEvaluatedDate.Text = dtRow("EvaluatedDateTime").ToString
                End If
                If txtEvaluatedDate.Text.Trim.Length > 0 Then
                    If Convert.ToBoolean(dtRow("Ineffective")) Then
                        rblEffective.SelectedValue = 1
                    Else
                        rblEffective.SelectedValue = 0
                    End If
                End If
                ckAutoGenerated.Checked = Convert.ToBoolean(dtRow("AutoGenerated").ToString)
                If IsDate(dtRow("CreatedDateTime").ToString) Then
                    txtCreatedDate.Text = Convert.ToDateTime(dtRow("CreatedDateTime").ToString).ToString(SessionManager.DateTimeFormat)
                Else
                    txtCreatedDate.Text = dtRow("CreatedDateTime").ToString
                End If
                txtCreatedUser.Text = dtRow("CreatedUser").ToString

                LoadAttachments()

                mcCauses.DataBind()
                mcActions.DataBind()

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValueAnomalyID.ToString

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("Site", txtSite.Text)
                objDic.Add("AnomalyType", txtAnomalyType.Text.Trim())
                objDic.Add("Area", txtArea.Text.Trim)
                objDic.Add("Anomaly", txtAnomaly.Text.Trim)
                objDic.Add("Subject", txtExpandSubject.Text.Trim)
                objDic.Add("KPI", txtKPIID.Text.Trim)
                If rblSGI.SelectedItem IsNot Nothing Then
                    If rblSGI.SelectedValue = 1 Then
                        objDic.Add("SGI", "Yes")
                    Else
                        objDic.Add("SGI", "No")
                    End If
                Else
                    objDic.Add("SGI", "")
                End If
                If rblFEMEA.SelectedItem IsNot Nothing Then
                    If rblFEMEA.SelectedValue = 1 Then
                        objDic.Add("ChangeFEMEA", "Yes")
                    Else
                        objDic.Add("ChangeFEMEA", "No")
                    End If
                Else
                    objDic.Add("ChangeFEMEA", "")
                End If
                objDic.Add("FEMEADescription", txtFEMEADescription.Text.Trim)
                objDic.Add("FEMEAJustification", txtExpandFEMEAJustification.Text.Trim)
                If rblRiskAnalysis.SelectedItem IsNot Nothing Then
                    If rblRiskAnalysis.SelectedValue = 1 Then
                        objDic.Add("RiskAnalysis", "Applicable")
                    Else
                        objDic.Add("RiskAnalysis", "Not Applicable")
                    End If
                Else
                    objDic.Add("RiskAnalysis", "")
                End If
                objDic.Add("RiskJustification", txtExpandRiskJustification.Text.Trim)
                objDic.Add("RiskResult1", ckRiskResult1.Checked.ToString)
                objDic.Add("RiskResult2", ckRiskResult2.Checked.ToString)
                objDic.Add("RiskResult3", ckRiskResult3.Checked.ToString)
                objDic.Add("RiskResultJustification", txtExpandRiskResultJustification.ToString.Trim)
                objDic.Add("SystemAgainstError", txtExpandSystemAgainstError.ToString.Trim)
                objDic.Add("ResponsibleUser", txtResponsibleUser.Text.Trim)
                objDic.Add("Origin1", txtOrigins1.Text.Trim)
                objDic.Add("Origin2", txtOrigins2.Text.Trim)
                objDic.Add("Origin3", txtOrigins3.Text.Trim)
                objDic.Add("Observations", txtExpandObservations.Text.Trim)
                objDic.Add("ClosedDate", RegionalConversion.FormatSQLDate(txtClosedDate.Text))
                If rblCancelled.SelectedItem IsNot Nothing Then
                    If rblCancelled.SelectedValue = 0 Then
                        objDic.Add("Cancelled", "Completed")
                    Else
                        objDic.Add("Cancelled", "Cancelled")
                    End If
                Else
                    objDic.Add("Cancelled", "")
                End If
                objDic.Add("Evaluation", txtExpandEvaluation.Text.Trim)
                objDic.Add("EvaluatedDate", RegionalConversion.FormatSQLDate(txtEvaluatedDate.Text))
                If rblEffective.SelectedItem IsNot Nothing Then
                    If rblEffective.SelectedValue = 0 Then
                        objDic.Add("Effective", "Effective")
                    Else
                        objDic.Add("Effective", "Ineffective")
                    End If
                Else
                    objDic.Add("Effective", "")
                End If

                SessionManager.RecordTransactionCurrentValues = objDic
            End If
        End Sub
        Private Sub LoadAttachments()
            Dim objDT As DataTable = AnomalyAttachments.SelectAnomalyAttachments(SessionManager.SelectedValueAnomalyID)

            If Not objDT Is Nothing AndAlso objDT.Rows.Count > 0 Then
                gvAttachments.DataSource = objDT
            Else
                gvAttachments.DataSource = Nothing
            End If

            gvAttachments.DataBind()
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.AnomalyMode
                Case "ViewRow", "DeleteRow", "AddAttachment"
                    pnlOKCancel.Visible = False
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    ddlAnomalyType.Visible = False
                    txtAnomalyType.Visible = True
                    ddlArea.Visible = False
                    txtArea.Visible = True
                    txtAnomaly.ReadOnly = True
                    txtAnomaly.CssClass = "Textbox_Display"
                    txtExpandSubject.ReadOnly = True
                    txtExpandSubject.CssClass = "Textbox_Display"
                    ddlKPIID.Visible = False
                    txtKPIID.Visible = True
                    If pnlSGI.Visible Then
                        rblSGI.Enabled = False
                        rblFEMEA.Enabled = False
                        txtFEMEADescription.ReadOnly = True
                        txtFEMEADescription.CssClass = "Textbox_Display"
                        txtExpandFEMEAJustification.ReadOnly = True
                        txtExpandFEMEAJustification.CssClass = "Textbox_Display"
                        rblRiskAnalysis.Enabled = False
                        txtExpandRiskJustification.ReadOnly = True
                        txtExpandRiskJustification.CssClass = "Textbox_Display"
                        ckRiskResult1.Enabled = False
                        ckRiskResult2.Enabled = False
                        ckRiskResult3.Enabled = False
                        txtExpandRiskResultJustification.ReadOnly = True
                        txtExpandRiskResultJustification.CssClass = "Textbox_Display"
                        txtExpandSystemAgainstError.ReadOnly = True
                        txtExpandSystemAgainstError.CssClass = "Textbox_Display"
                    End If
                    ddlResponsibleUser.Visible = False
                    txtResponsibleUser.Visible = True
                    ddlUserSite.Visible = False
                    If pnlOrigins.Visible Then
                        ddlOrigins1.Visible = False
                        txtOrigins1.Visible = True
                        ddlOrigins2.Visible = False
                        txtOrigins2.Visible = True
                        ddlOrigins3.Visible = False
                        txtOrigins3.Visible = True
                    End If
                    txtExpandObservations.ReadOnly = True
                    txtExpandObservations.CssClass = "Textbox_Display"
                    rblCancelled.Enabled = False
                    txtExpandEvaluation.ReadOnly = True
                    txtExpandEvaluation.CssClass = "Textbox_Display"
                    rblEffective.Enabled = False

                    If SessionManager.AnomalyMode <> "AddAttachment" AndAlso bCloseAnomaly AndAlso txtClosedDate.Text.Trim.Length > 0 Then
                        btnReOpenAnomaly1.Visible = True
                        btnReOpenAnomaly1.Attributes.Add("onclick", "return confirm('Click OK to ReOpen this Anomaly.');")
                    End If
                Case "AddRow"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    btnAnomalyActions.CausesValidation = True
                    pnlClose.Visible = False
                    pnlGrids.Visible = False
                    lblAutoGenerated.Visible = False
                    ckAutoGenerated.Visible = False
                    lblCreatedDate.Visible = False
                    txtCreatedDate.Visible = False
                    lblCreatedUser.Visible = False
                    txtCreatedUser.Visible = False
                Case "EditRow"
                    ddlSite.Visible = False
                    txtSite.Visible = True
                    btnAnomalyActions.CausesValidation = True

                    If txtClosedDate.Text.Trim.Length = 0 AndAlso bCloseAnomaly Then
                        txtClosedDate.Visible = False
                        ckClose.Visible = True
                        lblClosedDate.Text = GetTranslationString("close", "Close") & ":"
                    ElseIf txtClosedDate.Text.Trim.Length > 0 Then
                        ddlAnomalyType.Visible = False
                        txtAnomalyType.Visible = True
                        ddlArea.Visible = False
                        txtArea.Visible = True
                        txtAnomaly.ReadOnly = True
                        txtAnomaly.CssClass = "Textbox_Display"
                        txtExpandSubject.ReadOnly = True
                        txtExpandSubject.CssClass = "Textbox_Display"
                        ddlKPIID.Visible = False
                        txtKPIID.Visible = True
                        If pnlSGI.Visible Then
                            rblSGI.Enabled = False
                            rblFEMEA.Enabled = False
                            txtFEMEADescription.ReadOnly = True
                            txtFEMEADescription.CssClass = "Textbox_Display"
                            txtExpandFEMEAJustification.ReadOnly = True
                            txtExpandFEMEAJustification.CssClass = "Textbox_Display"
                            rblRiskAnalysis.Enabled = False
                            txtExpandRiskJustification.ReadOnly = True
                            txtExpandRiskJustification.CssClass = "Textbox_Display"
                            ckRiskResult1.Enabled = False
                            ckRiskResult2.Enabled = False
                            ckRiskResult3.Enabled = False
                            txtExpandRiskResultJustification.ReadOnly = True
                            txtExpandRiskResultJustification.CssClass = "Textbox_Display"
                            txtExpandSystemAgainstError.ReadOnly = True
                            txtExpandSystemAgainstError.CssClass = "Textbox_Display"
                        End If
                        ddlResponsibleUser.Visible = False
                        txtResponsibleUser.Visible = True
                        ddlUserSite.Visible = False
                        If pnlOrigins.Visible Then
                            ddlOrigins1.Visible = False
                            txtOrigins1.Visible = True
                            ddlOrigins2.Visible = False
                            txtOrigins2.Visible = True
                            ddlOrigins3.Visible = False
                            txtOrigins3.Visible = True
                        End If
                        pnlAddAttachment.Visible = False

                        txtExpandObservations.ReadOnly = True
                        txtExpandObservations.CssClass = "Textbox_Display"
                        rblCancelled.Enabled = False
                        If bCloseAnomaly Then
                            btnReOpenAnomaly.Visible = True
                            btnReOpenAnomaly.Attributes.Add("onclick", "return confirm('Click OK to ReOpen this Anomaly.');")
                        End If
                    End If
                    If txtEvaluatedDate.Text.Trim.Length = 0 AndAlso bEvaluateAnomaly AndAlso (txtClosedDate.Text.Trim.Length > 0 OrElse txtClosedDate.Visible = False) Then
                        txtEvaluatedDate.Visible = False
                        ckEvaluate.Visible = True
                        lblEvaluatedDate.Text = GetTranslationString("evaluate", "Evaluate") & ":"
                    Else
                        txtExpandEvaluation.ReadOnly = True
                        txtExpandEvaluation.CssClass = "Textbox_Display"
                        rblEffective.Enabled = False
                    End If

                    If ckAutoGenerated.Checked Then
                        ddlAnomalyType.Visible = False
                        txtAnomalyType.Visible = True
                        ddlArea.Visible = False
                        txtArea.Visible = True
                        txtAnomaly.ReadOnly = True
                        txtAnomaly.CssClass = "Textbox_Display"
                        txtExpandSubject.ReadOnly = True
                        txtExpandSubject.CssClass = "Textbox_Display"
                        ddlKPIID.Visible = False
                        txtKPIID.Visible = True
                    End If
            End Select
        End Sub
        Private Sub ViewModeObjectStyle()
            pnlOKCancel.Enabled = False
            pnlExit.Enabled = False
        End Sub
        Private Function SaveRecord() As Boolean
            Dim blnSuccess As Boolean = False

            Select Case SessionManager.AnomalyMode
                Case "AddRow"
                    blnSuccess = InsertAnomaly()
                Case "EditRow"
                    blnSuccess = UpdateAnomaly()
                Case "DeleteRow"
                    blnSuccess = DeleteAnomaly()
            End Select

            Return blnSuccess
        End Function
        Private Function InsertAnomaly() As Boolean
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
                If ddlAnomalyType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyType.SelectedItem.Value) Then
                    Dim objDT As DataTable = AnomalyTypeMaster.SelectAnomalyTypeMasterByID(ddlAnomalyType.SelectedItem.Value)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        If Convert.ToBoolean(objDT.Rows(0)("KPIRequired")) Then
                            If ddlKPIID.SelectedItem Is Nothing OrElse Not IsNumeric(ddlKPIID.SelectedItem.Value) Then
                                Master.DisplayError("You must select a KPI for this Anomaly Type")
                                Return False
                            End If
                        End If
                    End If
                Else
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iKPIID As Integer = 0
                Dim strCreatedDate As String = RegionalConversion.FormatSQLDate(Now(), True)

                If ddlKPIID.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlKPIID.SelectedItem.Value) Then
                    iKPIID = ddlKPIID.SelectedItem.Value
                End If

                Dim iSGI As Integer = -1
                If rblSGI.SelectedItem IsNot Nothing Then
                    iSGI = rblSGI.SelectedValue
                End If
                Dim iFEMEA As Integer = -1
                If rblFEMEA.SelectedItem IsNot Nothing Then
                    iFEMEA = rblFEMEA.SelectedValue
                End If
                Dim iRiskAnalysis As Integer = -1
                If rblRiskAnalysis.SelectedItem IsNot Nothing Then
                    iRiskAnalysis = rblRiskAnalysis.SelectedValue
                End If

                Dim strClosedDate As String = ""
                Dim bCancelled As Boolean = False
                If bCloseAnomaly AndAlso ckClose.Checked Then
                    If txtExpandObservations.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Observation text to Close an Anomaly.")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso rblSGI.SelectedIndex = Nothing Then
                        Master.DisplayError("SGI selection is required to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso iSGI = 1 AndAlso iFEMEA = -1 Then
                        Master.DisplayError("Change FEMEA selection is required to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso iFEMEA = 1 Then
                        If String.IsNullOrEmpty(txtFEMEADescription.Text) Then
                            Master.DisplayError("You must enter 'What' text to Close an Anomaly.")
                            Return False
                        ElseIf String.IsNullOrEmpty(txtExpandFEMEAJustification.Text) Then
                            Master.DisplayError("You must enter 'Justification' text to Close an Anomaly.")
                            Return False
                        End If
                    End If

                    strClosedDate = RegionalConversion.FormatSQLDate(DateTime.Now().ToString)
                    bCancelled = rblCancelled.SelectedValue
                End If

                Dim strEvaluateDate As String = ""
                Dim bIneffective As Boolean = False
                If bEvaluateAnomaly AndAlso ckEvaluate.Checked Then
                    If Not ckClose.Checked AndAlso strClosedDate.Trim.Length = 0 Then
                        Master.DisplayError("Anomaly must be closed to evaluate.")
                        Return False
                    End If

                    If txtExpandEvaluation.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Evaluation text when checking Evaluate.")
                        Return False
                    ElseIf rblEffective.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status when checking Evaluate.")
                        Return False
                    End If

                    strEvaluateDate = RegionalConversion.FormatSQLDate(DateTime.Now().ToString)
                    bIneffective = rblEffective.SelectedValue
                End If

                Dim iOrigin1 As Integer = 0
                Dim iOrigin2 As Integer = 0
                Dim iOrigin3 As Integer = 0
                If ddlOrigins1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins1.SelectedItem.Value) Then
                    iOrigin1 = ddlOrigins1.SelectedItem.Value
                End If
                If ddlOrigins2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins2.SelectedItem.Value) Then
                    iOrigin2 = ddlOrigins2.SelectedItem.Value
                End If
                If ddlOrigins3.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins3.SelectedItem.Value) Then
                    iOrigin3 = ddlOrigins3.SelectedItem.Value
                End If

                SessionManager.SelectedValueAnomalyID = AnomalyMaster.AddAnomaly(txtAnomaly.Text.Trim, Convert.ToInt16(ddlAnomalyType.SelectedItem.Value), Convert.ToInt16(ddlSite.SelectedItem.Value), Convert.ToInt16(ddlArea.SelectedItem.Value), txtExpandSubject.Text.Trim, iKPIID, "", "", strCreatedDate, SessionManager.UserID, ddlResponsibleUser.SelectedItem.Value.ToString.Trim, iOrigin1, iOrigin2, iOrigin3, txtExpandObservations.Text.Trim, strClosedDate, bCancelled, txtExpandEvaluation.Text.Trim, strEvaluateDate, bIneffective, 0, iSGI, iFEMEA, txtFEMEADescription.Text.Trim, txtExpandFEMEAJustification.Text.Trim, iRiskAnalysis, txtExpandRiskJustification.Text.Trim, ckRiskResult1.Checked, ckRiskResult2.Checked, ckRiskResult3.Checked, txtExpandRiskResultJustification.Text.Trim, txtExpandSystemAgainstError.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertAnomaly", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateAnomaly() As Boolean
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
                If ddlAnomalyType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyType.SelectedItem.Value) Then
                    Dim objDT As DataTable = AnomalyTypeMaster.SelectAnomalyTypeMasterByID(ddlAnomalyType.SelectedItem.Value)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                        If Convert.ToBoolean(objDT.Rows(0)("KPIRequired")) Then
                            If ddlKPIID.SelectedItem Is Nothing OrElse Not IsNumeric(ddlKPIID.SelectedItem.Value) Then
                                Master.DisplayError("You must select a KPI for this Anomaly Type")
                                Return False
                            End If
                        End If
                    End If
                Else
                    Return False
                End If

                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iKPIID As Integer = 0
                Dim iAnomalyTypeID As Integer = 0
                If ddlAnomalyType.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlAnomalyType.SelectedItem.Value) Then
                    iAnomalyTypeID = Convert.ToInt16(ddlAnomalyType.SelectedItem.Value)
                End If
                If ddlKPIID.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlKPIID.SelectedItem.Value) Then
                    iKPIID = ddlKPIID.SelectedItem.Value
                End If

                Dim iSGI As Integer = -1
                If rblSGI.SelectedItem IsNot Nothing Then
                    iSGI = rblSGI.SelectedValue
                End If
                Dim iFEMEA As Integer = -1
                If rblFEMEA.SelectedItem IsNot Nothing Then
                    iFEMEA = rblFEMEA.SelectedValue
                End If
                Dim iRiskAnalysis As Integer = -1
                If rblRiskAnalysis.SelectedItem IsNot Nothing Then
                    iRiskAnalysis = rblRiskAnalysis.SelectedValue
                End If

                Dim strClosedDate As String = ""
                Dim bCancelled As Boolean = False
                If bCloseAnomaly AndAlso ckClose.Checked Then
                    Dim objDT As DataTable = AnomalyActions.SelectOpenAnomalyActions(SessionManager.SelectedValueAnomalyID)
                    If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                        Master.DisplayError("Unable to close anomaly with open actions.")
                        Return False
                    End If

                    If txtExpandObservations.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Observation text to Close an Anomaly.")
                        Return False
                    ElseIf rblCancelled.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso rblSGI.SelectedIndex = Nothing Then
                        Master.DisplayError("SGI selection is required to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso iSGI = 1 AndAlso iFEMEA = -1 Then
                        Master.DisplayError("Change FEMEA selection is required to Close an Anomaly.")
                        Return False
                    ElseIf pnlSGI.Visible AndAlso iFEMEA = 1 Then
                        If String.IsNullOrEmpty(txtFEMEADescription.Text) Then
                            Master.DisplayError("You must enter 'What' text to Close an Anomaly.")
                            Return False
                        ElseIf String.IsNullOrEmpty(txtExpandFEMEAJustification.Text) Then
                            Master.DisplayError("You must enter 'Justification' text to Close an Anomaly.")
                            Return False
                        End If
                    End If

                    strClosedDate = RegionalConversion.FormatSQLDate(DateTime.Now().ToString)
                    bCancelled = rblCancelled.SelectedValue
                ElseIf txtClosedDate.Text.Trim.Length > 0 Then
                    strClosedDate = RegionalConversion.FormatSQLDate(txtClosedDate.Text.Trim)
                    bCancelled = rblCancelled.SelectedValue
                End If

                Dim strEvaluateDate As String = ""
                Dim bIneffective As Boolean = False
                If bEvaluateAnomaly AndAlso ckEvaluate.Checked Then
                    If Not ckClose.Checked AndAlso strClosedDate.Trim.Length = 0 Then
                        Master.DisplayError("Anomaly must be closed to evaluate.")
                        Return False
                    End If

                    If txtExpandEvaluation.Text.Trim.Length = 0 Then
                        Master.DisplayError("You must enter Evaluation text when checking Evaluate.")
                        Return False
                    ElseIf rblEffective.SelectedItem Is Nothing Then
                        Master.DisplayError("You must select a status when checking Evaluate.")
                        Return False
                    End If

                    strEvaluateDate = RegionalConversion.FormatSQLDate(DateTime.Now().ToString)
                    bIneffective = rblEffective.SelectedValue
                End If

                Dim iOrigin1 As Integer = 0
                Dim iOrigin2 As Integer = 0
                Dim iOrigin3 As Integer = 0
                If ddlOrigins1.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins1.SelectedItem.Value) Then
                    iOrigin1 = ddlOrigins1.SelectedItem.Value
                End If
                If ddlOrigins2.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins2.SelectedItem.Value) Then
                    iOrigin2 = ddlOrigins2.SelectedItem.Value
                End If
                If ddlOrigins3.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlOrigins3.SelectedItem.Value) Then
                    iOrigin3 = ddlOrigins3.SelectedItem.Value
                End If

                AnomalyMaster.UpdateAnomaly(SessionManager.SelectedValueAnomalyID, txtAnomaly.Text.Trim, iAnomalyTypeID, ddlSite.SelectedItem.Value, ddlArea.SelectedItem.Value, txtExpandSubject.Text.Trim, iKPIID, ddlResponsibleUser.SelectedItem.Value, iOrigin1, iOrigin2, iOrigin3, txtExpandObservations.Text.Trim, strClosedDate, bCancelled, txtExpandEvaluation.Text.Trim, strEvaluateDate, bIneffective, ckAutoGenerated.Checked, iSGI, iFEMEA, txtFEMEADescription.Text.Trim, txtExpandFEMEAJustification.Text.Trim, iRiskAnalysis, txtExpandRiskJustification.Text.Trim, ckRiskResult1.Checked, ckRiskResult2.Checked, ckRiskResult3.Checked, txtExpandRiskResultJustification.Text.Trim, txtExpandSystemAgainstError.Text.Trim)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateAnomaly", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteAnomaly() As Boolean
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
                AnomalyMaster.DeleteAnomaly(SessionManager.SelectedValueAnomalyID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueAnomalyID.ToString, "Anomaly Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteAnomaly", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Site", ddlSite.SelectedItem.Text)
            If ddlAnomalyType.SelectedItem IsNot Nothing Then
                objDic.Add("AnomalyType", ddlAnomalyType.SelectedItem.Text)
            Else
                objDic.Add("AnomalyType", "")
            End If
            If ddlArea.SelectedItem IsNot Nothing Then
                objDic.Add("Area", ddlArea.SelectedItem.Text)
            Else
                objDic.Add("Area", "")
            End If
            objDic.Add("Anomaly", txtAnomaly.Text.Trim)
            objDic.Add("Subject", txtExpandSubject.Text.Trim)
            If ddlKPIID.SelectedItem IsNot Nothing Then
                objDic.Add("KPI", ddlKPIID.SelectedItem.Text)
            Else
                objDic.Add("KPI", "")
            End If
            If rblSGI.SelectedItem IsNot Nothing Then
                If rblSGI.SelectedValue = 1 Then
                    objDic.Add("SGI", "Yes")
                Else
                    objDic.Add("SGI", "No")
                End If
            Else
                objDic.Add("SGI", "")
            End If
            If rblFEMEA.SelectedItem IsNot Nothing Then
                If rblFEMEA.SelectedValue = 1 Then
                    objDic.Add("ChangeFEMEA", "Yes")
                Else
                    objDic.Add("ChangeFEMEA", "No")
                End If
            Else
                objDic.Add("ChangeFEMEA", "")
            End If
            objDic.Add("FEMEADescription", txtFEMEADescription.Text.Trim)
            objDic.Add("FEMEAJustification", txtExpandFEMEAJustification.Text.Trim)
            If rblRiskAnalysis.SelectedItem IsNot Nothing Then
                If rblRiskAnalysis.SelectedValue = 1 Then
                    objDic.Add("RiskAnalysis", "Applicable")
                Else
                    objDic.Add("RiskAnalysis", "Not Applicable")
                End If
            Else
                objDic.Add("RiskAnalysis", "")
            End If
            objDic.Add("RiskJustification", txtExpandRiskJustification.Text.Trim)
            objDic.Add("RiskResult1", ckRiskResult1.Checked.ToString)
            objDic.Add("RiskResult2", ckRiskResult2.Checked.ToString)
            objDic.Add("RiskResult3", ckRiskResult3.Checked.ToString)
            objDic.Add("RiskResultJustification", txtExpandRiskResultJustification.ToString.Trim)
            objDic.Add("SystemAgainstError", txtExpandSystemAgainstError.ToString.Trim)
            If ddlResponsibleUser.SelectedItem IsNot Nothing Then
                objDic.Add("ResponsibleUser", ddlResponsibleUser.SelectedItem.Text)
            Else
                objDic.Add("ResponsibleUser", "")
            End If
            If ddlOrigins1.SelectedItem IsNot Nothing Then
                objDic.Add("Origin1", ddlOrigins1.SelectedItem.Text)
            Else
                objDic.Add("Origin1", "")
            End If
            If ddlOrigins2.SelectedItem IsNot Nothing Then
                objDic.Add("Origin2", ddlOrigins2.SelectedItem.Text)
            Else
                objDic.Add("Origin2", "")
            End If
            If ddlOrigins3.SelectedItem IsNot Nothing Then
                objDic.Add("Origin3", ddlOrigins3.SelectedItem.Text)
            Else
                objDic.Add("Origin3", "")
            End If
            objDic.Add("Observations", txtExpandObservations.Text.Trim)
            If txtClosedDate.Text.Trim.Length > 0 Then
                objDic.Add("ClosedDate", RegionalConversion.FormatSQLDate(txtClosedDate.Text))
            ElseIf ckClose.Checked Then
                objDic.Add("ClosedDate", RegionalConversion.FormatSQLDate(DateTime.Now().ToString))
            End If
            If rblCancelled.SelectedItem IsNot Nothing Then
                If rblCancelled.SelectedValue = 0 Then
                    objDic.Add("Cancelled", "Completed")
                Else
                    objDic.Add("Cancelled", "Cancelled")
                End If
            Else
                objDic.Add("Cancelled", "")
            End If
            objDic.Add("Evaluation", txtExpandEvaluation.Text.Trim)
            If txtEvaluatedDate.Text.Trim.Length > 0 Then
                objDic.Add("EvaluatedDate", RegionalConversion.FormatSQLDate(txtEvaluatedDate.Text))
            ElseIf ckEvaluate.Checked Then
                objDic.Add("EvaluatedDate", RegionalConversion.FormatSQLDate(DateTime.Now().ToString))
            End If
            If rblEffective.SelectedItem IsNot Nothing Then
                If rblEffective.SelectedValue = 0 Then
                    objDic.Add("Effective", "Effective")
                Else
                    objDic.Add("Effective", "Ineffective")
                End If
            Else
                objDic.Add("Effective", "")
            End If

            Return objDic
        End Function
        Private Sub RedirectToActions()
            SessionManager.AnomalyMode = "EditRow"
            SessionManager.MasterControlExitProgram = "AnomalyMaster2"
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("AnomalyActions1"), False)
        End Sub
        Private Sub RedirectGoBack()
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueAnomalyID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.AnomalyMode)

            Dim strProgram As String = "AnomalyMaster1"
            If SessionManager.CallingProgram.Trim.Length > 0 Then
                strProgram = SessionManager.CallingProgram
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.CallingProgram)
            End If
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL(strProgram), False)
        End Sub
#End Region

    End Class
End Namespace
