#Region " Imports"
Imports System.IO
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class DataQuery1
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "Database Query"
        Private Shared ReadOnly ProgramName As String = "DataQuery1"
        Private strSQL As String = String.Empty
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Exit"}
            Dim OutMessageArr() As String = {"", ""}

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadJavaScripts()
            Dim myTabArray() As Object = {txtExpandSelect, txtExpandFrom, txtExpandWhere, txtExpandGroupBy, txtExpandOrderBy, btnOK}
            Dim TabKeyDownArr() As String = {Tab(txtExpandFrom, btnOK, "No"), _
                                             Tab(txtExpandWhere, txtExpandSelect, "No"), _
                                             Tab(txtExpandGroupBy, txtExpandFrom, "No"), _
                                             Tab(txtExpandOrderBy, txtExpandWhere, "No"), _
                                             Tab(btnOK, txtExpandGroupBy, "No"), _
                                             Tab(txtExpandSelect, txtExpandOrderBy, "No")}

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

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/data_scroll.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()
            LoadJavaScripts()
            txtExpandSelect.Focus()

            If Not Page.IsPostBack Then
                ReadSessionVariablesIntoFields()
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
            ReadFieldsIntoSessionVariables()
            strSQL = BuildQueryString()
            If strSQL.Length > 0 Then
                BindQueryGrid()
            End If
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
            ReadFieldsIntoSessionVariables()
            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnClear_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnClear.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'clear fields
            txtExpandSelect.Text = String.Empty
            txtExpandFrom.Text = String.Empty
            txtExpandWhere.Text = String.Empty
            txtExpandGroupBy.Text = String.Empty
            txtExpandOrderBy.Text = String.Empty
            gvQueryResults.DataSource = Nothing
            gvQueryResults.DataBind()
        End Sub
        Private Sub btnExport_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExport.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim stringWrite As New System.IO.StringWriter
            Dim htmlWrite As New System.Web.UI.HtmlTextWriter(stringWrite)
            gvQueryResults.RenderControl(htmlWrite)
            SessionManager.ExportString = stringWrite.ToString
            Response.Redirect(Request.ApplicationPath.ToString + "/UI/UserControls/Export.aspx")
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ReadFieldsIntoSessionVariables()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If txtExpandSelect.Text.Trim.Length > 0 Then
                SessionManager.QuerySelect = txtExpandSelect.Text.Trim
            End If
            If txtExpandFrom.Text.Trim.Length > 0 Then
                SessionManager.QueryFrom = txtExpandFrom.Text.Trim
            End If
            If txtExpandWhere.Text.Trim.Length > 0 Then
                SessionManager.QueryWhere = txtExpandWhere.Text.Trim
            End If
            If txtExpandGroupBy.Text.Trim.Length > 0 Then
                SessionManager.QueryGroupBy = txtExpandGroupBy.Text.Trim
            End If
            If txtExpandOrderBy.Text.Trim.Length > 0 Then
                SessionManager.QueryOrderBy = txtExpandOrderBy.Text.Trim
            End If
        End Sub
        Private Sub ReadSessionVariablesIntoFields()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If SessionManager.QuerySelect <> "" Then
                txtExpandSelect.Text = SessionManager.QuerySelect
            End If
            If SessionManager.QueryFrom <> "" Then
                txtExpandFrom.Text = SessionManager.QueryFrom
            End If
            If SessionManager.QueryWhere <> "" Then
                txtExpandWhere.Text = SessionManager.QueryWhere
            End If
            If SessionManager.QueryGroupBy <> "" Then
                txtExpandGroupBy.Text = SessionManager.QueryGroupBy
            End If
            If SessionManager.QueryOrderBy <> "" Then
                txtExpandOrderBy.Text = SessionManager.QueryOrderBy
            End If
        End Sub
        Private Function BuildQueryString() As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strSQL As String = String.Empty

            'first, verify that we have enough information to run a query
            'we need to at least have select information
            If txtExpandSelect.Text.Length > 0 AndAlso txtExpandFrom.Text.Length > 0 Then
                'seems like we have at least enough data to query the database
                'Select and From 
                strSQL = "Select " + Replace(txtExpandSelect.Text.Trim, """", """""")
                strSQL += " From " + Replace(txtExpandFrom.Text.Trim, """", """""")

                'if we have a where clause
                If txtExpandWhere.Text.Trim.Length > 0 Then
                    strSQL += " where " + Replace(txtExpandWhere.Text.Trim, """", """""")
                End If

                'if we have any group by information
                If txtExpandGroupBy.Text.Trim.Length > 0 Then
                    strSQL += " group by " + Replace(txtExpandGroupBy.Text.Trim, """", """""")
                End If

                'if we have an order by clause
                If txtExpandOrderBy.Text.Trim.Length > 0 Then
                    strSQL += " order by " + Replace(txtExpandOrderBy.Text.Trim, """", """""")
                End If

                Return strSQL
            Else
                Return ""
            End If
        End Function
        Private Sub BindQueryGrid()
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
                Dim dsHolder As DataTable = GeneralDataAccess.DatabaseQuery(strSQL)
                If Not IsNothing(dsHolder) Then
                    gvQueryResults.DataSource = dsHolder
                    gvQueryResults.DataBind()
                End If
                btnExport.Visible = True
            Catch Exc As Exception
                btnExport.Visible = False
                Master.DisplayErrors(ProgramName & " - BindQueryGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

    End Class
End Namespace

