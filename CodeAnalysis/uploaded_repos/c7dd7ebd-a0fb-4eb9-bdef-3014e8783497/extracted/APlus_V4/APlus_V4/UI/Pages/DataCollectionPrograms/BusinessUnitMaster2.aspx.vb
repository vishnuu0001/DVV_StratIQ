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
    Partial Class BusinessUnitMaster2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Business Unit Maintenance"
        Private Shared ReadOnly ProgramName As String = "BusinessUnitMaster2"
        Private Shared ReadOnly DBTableName As String = "BusinessUnitMaster"
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
            Dim myTabArray() As Object = {txtBusinessUnit, _
                                          txtBusinessUnitAbbrev, _
                                          ddlBusinessArea, _
                                          ckActive}

            Dim TabKeyDownArr() As String = {Tab(txtBusinessUnitAbbrev, ckActive, "No"), _
                                             Tab(ddlBusinessArea, txtBusinessUnit, "No"), _
                                             Tab(ckActive, txtBusinessUnitAbbrev, "No"), _
                                             Tab(txtBusinessUnit, ddlBusinessArea, "No")}

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

            Master.HeaderMessage = FormName & " - " & SessionManager.BusinessUnitMode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/boss.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            LoadCommonJavaScripts()

            If Not Page.IsPostBack Then
                LoadDropDowns()

                Select Case SessionManager.BusinessUnitMode
                    Case "ViewRow"
                        pnlExit.Visible = True
                        pnlOKCancel.Visible = False
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        pnlOKCancel.Visible = True
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this Business Unit.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        txtBusinessUnitID.Text = "New"
                        LoadAddEditModeJavaScripts()
                        txtBusinessUnit.Focus()
                    Case "EditRow"
                        LoadAddEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                        txtBusinessUnit.Focus()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("BusinessUnitMaster1"), False)
                End Select
            End If
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
            Select Case SessionManager.BusinessUnitMode
                Case "AddRow"
                    blnSuccess = InsertBusinessUnit()
                Case "EditRow"
                    blnSuccess = UpdateBusinessUnit()
                Case "DeleteRow"
                    blnSuccess = DeleteBusinessUnit()
            End Select

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueBusinessUnitID)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.BusinessUnitMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("BusinessUnitMaster1"), False)
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

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedValueBusinessUnitID)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.BusinessUnitMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("BusinessUnitMaster1"), False)
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDropDowns()
            Try
                BusinessAreaMaster.GetBusinessAreaMasterAbbrevList(ddlBusinessArea)
                ddlBusinessArea.Items.Insert(0, "")
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - Error Loading DropDowns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
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

            Dim objDT As DataTable = BusinessUnitMaster.SelectBusinessUnitByID(SessionManager.SelectedValueBusinessUnitID)
            If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                Dim dtRow As DataRow = objDT.Rows(0)

                txtBusinessUnitID.Text = SessionManager.SelectedValueBusinessUnitID
                txtBusinessUnit.Text = dtRow("BusinessUnit").ToString
                txtBusinessUnitAbbrev.Text = dtRow("BusinessUnitAbbrev").ToString
                Dim objItem As ListItem = ddlBusinessArea.Items.FindByValue(dtRow("BAID").ToString)
                If objItem IsNot Nothing Then
                    objItem.Selected = True
                    txtBusinessArea.Text = objItem.Text
                End If
                ckActive.Checked = Convert.ToBoolean(dtRow("Active"))

                TransactionHistory1.TableName = DBTableName
                TransactionHistory1.RecordID = SessionManager.SelectedValue.Trim()

                Dim objDic As New Dictionary(Of String, String)
                objDic.Add("BusinessUnit", txtBusinessUnit.Text.Trim())
                objDic.Add("BusinessUnitAbbrev", txtBusinessUnitAbbrev.Text.Trim())
                objDic.Add("BusinessArea", txtBusinessArea.Text.Trim)
                objDic.Add("Active", ckActive.Checked.ToString)
                SessionManager.RecordTransactionCurrentValues = objDic
            End If
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

            Select Case SessionManager.BusinessUnitMode
                Case "ViewRow", "DeleteRow"
                    pnlOKCancel.Visible = False
                    txtBusinessUnit.ReadOnly = True
                    txtBusinessUnit.CssClass = "Textbox_Display"
                    txtBusinessUnitAbbrev.ReadOnly = True
                    txtBusinessUnitAbbrev.CssClass = "Textbox_Display"
                    ddlBusinessArea.Visible = False
                    txtBusinessArea.Visible = True
                    ckActive.Enabled = False
            End Select
        End Sub
        Private Function InsertBusinessUnit() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iBusinessAreaID As Integer = -1
                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                    iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
                End If

                Dim iBusinessUnitID As Integer = BusinessUnitMaster.InsertBusinessUnit(txtBusinessUnit.Text.Trim, txtBusinessUnitAbbrev.Text.Trim, iBusinessAreaID, ckActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, iBusinessUnitID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertBusinessUnit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateBusinessUnit() As Boolean
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
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim iBusinessAreaID As Integer = -1
                If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                    iBusinessAreaID = ddlBusinessArea.SelectedItem.Value
                End If

                BusinessUnitMaster.UpdateBusinessUnit(SessionManager.SelectedValueBusinessUnitID, txtBusinessUnit.Text, txtBusinessUnitAbbrev.Text, iBusinessAreaID, ckActive.Checked)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueBusinessUnitID.ToString, strChangeLog, SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateBusinessUnit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteBusinessUnit() As Boolean
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
                BusinessUnitMaster.DeleteBusinessUnit(SessionManager.SelectedValueBusinessUnitID)

                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.SelectedValueBusinessUnitID.ToString, "Business Unit Deleted", SessionManager.UserID)

                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteBusinessUnit", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
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
            objDic.Add("BusinessUnit", txtBusinessUnit.Text.Trim())
            objDic.Add("BusinessUnitAbbrev", txtBusinessUnitAbbrev.Text.Trim())
            If ddlBusinessArea.SelectedItem IsNot Nothing AndAlso IsNumeric(ddlBusinessArea.SelectedItem.Value) Then
                objDic.Add("BusinessArea", ddlBusinessArea.SelectedItem.Text.Trim)
            Else
                objDic.Add("BusinessArea", String.Empty)
            End If
            objDic.Add("Active", ckActive.Checked.ToString)

            Return objDic
        End Function
#End Region

    End Class
End Namespace
