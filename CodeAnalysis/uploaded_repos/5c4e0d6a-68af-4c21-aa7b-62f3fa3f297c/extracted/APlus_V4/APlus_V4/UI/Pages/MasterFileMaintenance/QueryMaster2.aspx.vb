#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class QueryMaster2
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Query Master"
        Private Shared ReadOnly ProgramName As String = "QueryMaster2"
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel"}
            Dim OutMessageArr() As String = {"", ""}
            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray() As Object = {txtQueryDescription, _
                                          txtExpandSelect, _
                                          txtExpandFrom, _
                                          txtExpandWhere, _
                                          txtExpandGroupBy, _
                                          txtExpandOrderBy}

            Dim TabKeyDownArr() As String = {Tab(txtExpandSelect, txtExpandOrderBy, "No"), _
                                             Tab(txtExpandFrom, txtQueryDescription, "No"), _
                                             Tab(txtExpandWhere, txtExpandSelect, "No"), _
                                             Tab(txtExpandGroupBy, txtExpandFrom, "No"), _
                                             Tab(txtExpandOrderBy, txtExpandWhere, "No"), _
                                             Tab(txtQueryDescription, txtExpandGroupBy, "No")}

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)
        End Sub
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

            Master.HeaderMessage = FormName & " - " & SessionManager.QueryMasterMode.Replace("Row", "")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            Select Case SessionManager.QueryMasterMode
                Case "EditRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_preferences.gif"
                Case "ViewRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_information.gif"
                Case "DeleteRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_delete.gif"
                Case "AddRow"
                    Master.IconImage = Request.ApplicationPath + "/images/data_add.gif"
            End Select

            If Not Page.IsPostBack Then
                Select Case SessionManager.QueryMasterMode
                    Case "EditRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        LoadEditModeJavaScripts()
                        txtQueryDescription.Focus()
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Query and Parameters.');")
                        UnEnableRecords()
                    Case "AddRow"
                        txtSite.Text = SessionManager.WorkingSite
                        LoadEditModeJavaScripts()
                        btnParameters.Visible = False
                        txtQueryDescription.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster1"), False)
                End Select
            End If
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            Select Case SessionManager.QueryMasterMode
                Case "EditRow"
                    blnSuccess = UpdateQuery()
                Case "DeleteRow"
                    blnSuccess = DeleteQuery()
                Case "AddRow"
                    blnSuccess = InsertQuery()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueQueryID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryMasterMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster1"), False)
            End If
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueQueryID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster1"), False)
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueQueryID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.QueryMasterMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster1"), False)
        End Sub
        Private Sub btnParameters_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnParameters.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.QueryMasterMode = "EditRow" Then
                Page.Validate()
                If UpdateQuery() = False Then
                    Master.DisplayError("Error Saving Query")
                    Return
                End If
            End If
            SessionManager.MasterControlExitProgram = ProgramName
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("QueryMaster3"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadSelectedRecord()
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
                Dim ds As DataSet = QueryMaster.SelectQuery(SessionManager.SelectedValueQueryID)

                If ds.Tables.Count > 0 Then
                    Dim dr As DataRow = ds.Tables(0).Rows(0)

                    lblQueryID.Text = dr("QueryID").ToString.Trim()
                    txtQueryDescription.Text = dr("QueryDescription").ToString.Trim()
                    txtExpandSelect.Text = dr("QuerySelect").ToString.Trim()
                    txtExpandFrom.Text = dr("QueryFrom").ToString.Trim()
                    txtExpandWhere.Text = dr("QueryWhere").ToString.Trim()
                    txtExpandGroupBy.Text = dr("QueryGroupBy").ToString.Trim()
                    txtExpandOrderBy.Text = dr("QueryOrderBy").ToString.Trim()
                    txtSite.Text = dr("Site").ToString.Trim()
                    lblSiteID.Text = dr("SiteID").ToString
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.QueryMasterMode = "ViewRow" Or SessionManager.QueryMasterMode = "DeleteRow" Then
                If SessionManager.QueryMasterMode = "ViewRow" Then
                    pnlOKCancel.Visible = False
                End If

                txtQueryDescription.ReadOnly = True
                txtQueryDescription.CssClass = "Textbox_Display"
                txtExpandSelect.ReadOnly = True
                txtExpandSelect.CssClass = "Textbox_Display"
                txtExpandFrom.ReadOnly = True
                txtExpandFrom.CssClass = "Textbox_Display"
                txtExpandWhere.ReadOnly = True
                txtExpandWhere.CssClass = "Textbox_Display"
                txtExpandGroupBy.ReadOnly = True
                txtExpandGroupBy.CssClass = "Textbox_Display"
                txtExpandOrderBy.ReadOnly = True
                txtExpandOrderBy.CssClass = "Textbox_Display"
            End If
        End Sub
        Private Function InsertQuery() As Boolean
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
                QueryMaster.InsertQueryMaster(Convert.ToInt32("0" + SessionManager.WorkingSiteID), txtQueryDescription.Text, txtExpandSelect.Text, txtExpandFrom.Text, txtExpandWhere.Text, txtExpandGroupBy.Text, txtExpandOrderBy.Text, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertQuery", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateQuery() As Boolean
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
                QueryMaster.UpdateQueryMaster(SessionManager.SelectedValueQueryID, Convert.ToInt32("0" + lblSiteID.Text), txtQueryDescription.Text, txtExpandSelect.Text, txtExpandFrom.Text, txtExpandWhere.Text, txtExpandGroupBy.Text, txtExpandOrderBy.Text, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateQuery", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function

        Private Function DeleteQuery() As Boolean
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
                QueryMaster.DeleteQueryMaster(SessionManager.SelectedValueQueryID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteQuery", Exc, SessionManager.UserID, ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
#End Region

    End Class
End Namespace

