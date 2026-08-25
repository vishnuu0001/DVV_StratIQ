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
    Partial Class PillarMembership2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Pillar Membership "
        Private Shared ReadOnly ProgramName As String = "PillarMembership2"
        Private Shared ReadOnly DBTableName As String = "PillarMembership"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtDateJoined_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim myTabArray() As Object = {ddlSites, _
                                          ddlPillar, _
                                          ddlUserID, _
                                          ddlRole, _
                                          txtDateJoined _
                                         }

            Dim TabKeyDownArr() As String = {Tab(ddlPillar, txtDateJoined, "No"), _
                                                      Tab(ddlUserID, ddlSites, "No"), _
                                                      Tab(ddlRole, ddlPillar, "No"), _
                                                      Tab(txtDateJoined, ddlUserID, "No"), _
                                                      Tab(ddlSites, ddlRole, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {ddlRole, _
                                          txtDateJoined _
                                         }

            Dim TabKeyDownArr() As String = {Tab(txtDateJoined, txtDateJoined, "No"), _
                                                      Tab(ddlRole, ddlRole, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
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

            Master.HeaderMessage = FormName & " - " & SessionManager.PillarMembershipMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/PillarMemeberShip.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                Select Case SessionManager.PillarMembershipMode.ToString()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Pillar Membership.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtDateJoined.Text = DateTime.Now.Year.ToString & "/" & DateTime.Now.Month.ToString & "/" & DateTime.Now.Day.ToString
                        LoadAddModeJavaScripts()
                        LoadDropdownList()
                        UnEnableRecords()

                        If SessionManager.WorkingSiteID > 0 Then
                            Dim objItem As ListItem = ddlSites.Items.FindByValue(SessionManager.WorkingSiteID)
                            If objItem IsNot Nothing Then
                                objItem.Selected = True
                                txtSite.Text = objItem.Text

                                ddlSites.Visible = False
                                txtSite.Visible = True
                            End If
                            ddlPillar.Focus()
                        Else
                            ddlSites.Focus()
                        End If
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadDropdownList()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        ddlRole.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("RoutesMasterMaintenance"))
                End Select
            End If
        End Sub
        Protected Sub ddlUserSite_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlUserSite.SelectedIndexChanged
            BindUserDDL()
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

            Dim blnSuccess As Boolean
            Select Case SessionManager.PillarMembershipMode.ToString()
                Case "DeleteRow"
                    blnSuccess = DeletePillarMembership()
                Case "AddRow"
                    blnSuccess = InsertPillarMembership()
                Case "EditRow"
                    blnSuccess = UpdatePillarMembership()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.PillarMembershipMode)

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PillarMembershipMasterMaintenance"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValue3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.PillarMembershipMode)

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("PillarMembershipMasterMaintenance"), False)
        End Sub
#End Region

#Region " Custom Methods"
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

            Try
                Dim objDT As DataTable = PillarMembership.SelectPillarMembershipByKey(SessionManager.SelectedValue1, SessionManager.SelectedValue, SessionManager.SelectedValue2)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim dtRow As DataRow = objDT.Rows(0)

                    txtPillar.Text = SessionManager.SelectedValue & " - " & dtRow("Pillar").ToString
                    txtUserID.Text = dtRow("UserName").ToString
                    txtSite.Text = dtRow("Site").ToString
                    txtRole.Text = dtRow("Role").ToString
                    If IsDate(dtRow("DateJoined").ToString) Then
                        txtDateJoined.Text = Convert.ToDateTime(dtRow("DateJoined").ToString).ToString(SessionManager.DateFormat)
                    Else
                        txtDateJoined.Text = dtRow("DateJoined").ToString
                    End If

                    Dim objItems As New ListItem
                    objItems = ddlSites.Items.FindByText(txtSite.Text.Trim())
                    If objItems IsNot Nothing Then
                        objItems.Selected = True
                    End If

                    objItems = ddlPillar.Items.FindByValue(SessionManager.SelectedValue)
                    If objItems IsNot Nothing Then
                        objItems.Selected = True
                    End If

                    objItems = ddlUserID.Items.FindByText(txtUserID.Text)
                    If objItems IsNot Nothing Then
                        objItems.Selected = True
                    End If

                    objItems = ddlRole.Items.FindByText(txtRole.Text.Trim())
                    If objItems IsNot Nothing Then
                        objItems.Selected = True
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.SelectedValue1.Trim() & "," & SessionManager.SelectedValue.Trim()

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Site", ddlSites.SelectedItem.Text.Trim())
                    objDic.Add("Pillar", ddlPillar.SelectedItem.Text.Trim())
                    objDic.Add("User", ddlUserID.SelectedItem.Text.Trim())
                    objDic.Add("Role", ddlRole.SelectedItem.Text.Trim())
                    objDic.Add("DateJoined", txtDateJoined.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadDropdownList()
            Try
                BindSites()
                BindPillars()
                BindRole()
                BindUserSites()
                BindUserDDL()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDropdownList", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindSites()
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
                SiteMaster.SelectSiteMasterList(ddlSites)
                ddlSites.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindSites", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindPillars()
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
                Pillars.SelectPillarList(ddlPillar)
                ddlPillar.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindPillars", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub BindRole()
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
                RoleMaster.SelectPillarRoleList(ddlRole)
                ddlRole.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindRole", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

                SiteMaster.SelectSiteMasterActiveList(ddlUserSite)
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
        Private Sub BindUserDDL()
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
                ddlUserID.Items.Clear()

                If ddlUserSite.SelectedItem IsNot Nothing Then
                    UserMaster.SelectUserNameList(ddlUserSite.SelectedItem.Value, True, ddlUserID)
                Else
                    UserMaster.SelectUserNameList(SessionManager.WorkingSiteID, True, ddlUserID)
                End If

                ddlUserID.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - BindUserID", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
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

            Select Case SessionManager.PillarMembershipMode
                Case "ViewRow"
                    pnlOKCancel.Visible = False
                    ddlSites.Visible = False
                    ddlUserID.Visible = False
                    ddlUserSite.Visible = False
                    ddlPillar.Visible = False
                    ddlRole.Visible = False
                    imgDateJoined.Visible = False
                    txtDateJoined.ReadOnly = True
                    txtDateJoined.CssClass = "Textbox_Display"
                    txtDateJoined_CalendarExtender.Enabled = False
                Case "DeleteRow"
                    ddlSites.Visible = False
                    ddlUserID.Visible = False
                    ddlUserSite.Visible = False
                    ddlPillar.Visible = False
                    ddlRole.Visible = False
                    imgDateJoined.Visible = False
                    txtDateJoined.ReadOnly = True
                    txtDateJoined.CssClass = "Textbox_Display"
                    txtDateJoined_CalendarExtender.Enabled = False
                Case "EditRow"
                    ddlSites.Visible = False
                    txtUserID.Visible = True
                    ddlUserID.Visible = False
                    ddlUserSite.Visible = False
                    txtPillar.Visible = True
                    ddlPillar.Visible = False
                    txtRole.Visible = False
                    imgDateJoined.Visible = True
                    ddlRole.Focus()
                Case "AddRow"
                    txtSite.Visible = False
                    txtPillar.Visible = False
                    txtUserID.Visible = False
                    txtRole.Visible = False
                    imgDateJoined.Visible = True
            End Select
        End Sub
        Private Function InsertPillarMembership() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not String.IsNullOrEmpty(txtDateJoined.Text.Trim()) Then
                If Not IsDate(txtDateJoined.Text) Then
                    Master.DisplayError(GetTranslationString("invaliddate", "Invalid Date"))
                    txtDateJoined.Focus()
                    Exit Function
                End If
            End If

            Dim strDateJoined As String = RegionalConversion.FormatSQLDate(txtDateJoined.Text)

            Dim strUserID As String = ddlUserID.SelectedItem.Value.Trim()
            If String.IsNullOrEmpty(strUserID.Trim()) Then
                Master.DisplayError(GetTranslationString("selectuser", "Select User"))
                ddlUserID.Focus()
                Return False
            End If

            Dim strPillar As String = ddlPillar.SelectedItem.Value.Trim()
            If String.IsNullOrEmpty(strPillar.Trim()) Then
                Master.DisplayError(GetTranslationString("selectpillar", "Select Pillar"))
                ddlPillar.Focus()

                Return False
            End If

            Dim iSiteID As Integer = ddlSites.SelectedItem.Value
            If iSiteID = 0 Then
                Master.DisplayError(GetTranslationString("selectsite", "Select Site"))
                ddlSites.Focus()
                Return False
            End If

            Dim strRole As String = ddlRole.SelectedItem.Value.Trim()
            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                PillarMembership.AddPillarMembership(strUserID, strPillar, iSiteID, strRole, strDateJoined, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, strUserID.Trim() & "," & strPillar.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertPillarMembership ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdatePillarMembership() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not String.IsNullOrEmpty(txtDateJoined.Text.Trim()) Then
                If Not IsDate(txtDateJoined.Text) Then
                    Master.DisplayError(GetTranslationString("invaliddate", "Invalid Date"))
                    txtDateJoined.Focus()
                    Exit Function
                End If
            End If

            Dim strDateJoined As String = RegionalConversion.FormatSQLDate(txtDateJoined.Text)
            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                PillarMembership.UpdatePillarMembership(SessionManager.SelectedValue1.ToString.Trim, SessionManager.SelectedValue.ToString.Trim, Convert.ToInt16(SessionManager.SelectedValue2), ddlRole.SelectedValue, strDateJoined, SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue1.ToString.Trim() & "," & SessionManager.SelectedValue.ToString.Trim(), strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdatePillarMembership ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeletePillarMembership() As Boolean
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
                PillarMembership.DeletePillarMembership(SessionManager.SelectedValue1.ToString.Trim, SessionManager.SelectedValue.ToString.Trim, Convert.ToInt16(SessionManager.SelectedValue2))
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValue1.ToString.Trim() & "," & SessionManager.SelectedValue.ToString.Trim(), "Pillar Mambership Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeletePillarMembership ", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("Site", ddlSites.SelectedItem.Text.Trim())
            objDic.Add("Pillar", ddlPillar.SelectedItem.Text.Trim())
            objDic.Add("User", ddlUserID.SelectedItem.Text.Trim())
            objDic.Add("Role", ddlRole.SelectedItem.Text.Trim())
            objDic.Add("DateJoined", txtDateJoined.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
