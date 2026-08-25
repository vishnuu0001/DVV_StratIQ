#Region "Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Text
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.UI.CustomControls
Imports Microsoft.Office.Interop
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class EntityImport
        Inherits ApplicationBase

#Region " Page Members "
        Protected WithEvents Spreadsheet1 As Owc11.Spreadsheet
        Private cells As Owc11.Range 'Cells collection
        Protected mStrExcelData As String ' holds excel data for redisplay
        Protected mObjDT As DataTable ' holds the validated, duplicate free excel import data

        Private Shared ReadOnly FormName As String = "Entity Import"
        Private Shared ReadOnly ProgramName As String = "EntityImport"
        Private Shared ReadOnly TOTAL_ROWS As Integer = 4
        Private Shared ReadOnly TOTAL_COLS As Integer = 3

        Enum EXCEL_COLUMNS
            SAP_ENTITY = 1
            ENTITY = 2
            LOCATION = 3
        End Enum
#End Region

#Region " Event Handlers "
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Master.HeaderMessage = FormName & " - " & SessionManager.Mode.Replace("Row", "")
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"
            SessionManager.CurrentProgram = Request.Path

            If SessionManager.SelectedWorkCenterID <= 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterSelection"), False)
            End If
            ' set up javascript
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnCancel.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            Master.AddBodyAttribute("onload", "SetSpreadSheetTitle()")

            SetUpGridColumns()
            If Not btnValidate Is Nothing Then
                btnValidate.Attributes.Add("onclick", "ImportFromExcel()")
            End If

            If Not Page.IsPostBack Then
                pnlImport.Visible = False
            End If
        End Sub
        Private Sub btnValidate_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnValidate.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If ValidateExcelRows() Then
                If Not CheckForDuplicates() Then
                    pnlImport.Visible = True
                    If Not mObjDT Is Nothing Then
                        gvImport.DataSource = mObjDT
                        gvImport.DataBind()
                        gvImport.Visible = True
                    End If
                Else
                    HTMLData.Text = mStrExcelData
                End If
            Else
                HTMLData.Text = mStrExcelData
            End If
        End Sub
        Private Sub btnCancel2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("EntityImport"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnImportData_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnImportData.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                ImportExcelDataToDataGrid()
                If SaveGridToDatabase() Then
                    gvImport.Visible = False
                    pnlDbUpdate.Visible = True
                    lblDbUpdateInfo.Text = "Excel data successfully imported to database!"
                    lblDbUpdateInfo.Font.Bold = True
                    btnImportData.Visible = False
                    btnCancel2.Visible = False
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnImportData_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub btnExitImport_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExitImport.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("EntityImport"), False)
        End Sub
#End Region

#Region " Custom Methods "
        Private Sub SetUpGridColumns()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objCol As BoundField

                objCol = New BoundField
                objCol.HeaderText = "Workcenter"
                objCol.DataField = "WorkcenterID"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Entity#"
                objCol.DataField = "SAPEntity"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Entity"
                objCol.DataField = "Entity"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Location"
                objCol.DataField = "Location"
                gvImport.Columns.Add(objCol)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetUpGridColumns()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SetupDataTable(ByRef dt As DataTable, ByRef grd As GridView)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                For Each col As DataControlField In gvImport.Columns
                    If TypeOf col Is BoundField Then
                        dt.Columns.Add(New DataColumn(CType(col, BoundField).DataField))
                    End If
                Next
                dt.Columns.Add(New DataColumn("Errors"))
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetupDataTable()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub ImportExcelDataToDataGrid()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objExcel As New Owc11.Spreadsheet
                If HTMLData.Text.Length > 0 Then
                    objExcel.HTMLData = HTMLData.Text
                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.Selection.Cells
                    LoadExcelDataToDataTable(objExcel)
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ImportExcelDataToDataGrid()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function ValidateExcelRows() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnResult As Boolean = True
            Dim blnRowError As Boolean = False
            Dim objExcel As New Owc11.Spreadsheet
            Dim iColIdx As Integer
            Dim iRowIdx As Integer
            Dim iRowCnt As Integer ' Row counter
            Dim strErrorMsg As String = String.Empty

            Try
                If HTMLData.Text.Length > 0 Then
                    ' get data hidden in textbox
                    objExcel.HTMLData = HTMLData.Text

                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.Selection.Cells

                    iRowIdx = 1 ' SKIP the Headers 
                    iColIdx = 1
                    iRowCnt = 1

                    Do
                        If cells(iRowIdx, iColIdx).Text.ToString().Length() < 1 Then
                            strErrorMsg = " Column " & GetCurrentColumn(iColIdx) & " cannot be empty! "
                            blnResult = False
                            blnRowError = True
                        End If

                        If blnRowError Then
                            cells(iRowIdx, iColIdx).EntireRow.Interior.Color = "Red"
                            cells(iRowIdx, 4).Value = strErrorMsg
                        End If

                        iColIdx += 1
                        iRowCnt += 1

                        If iColIdx > TOTAL_COLS Then
                            If cells(iRowIdx, 4).Text.ToString.Trim.Length() > 1 Then
                                If Not blnRowError Then
                                    'clear error message
                                    cells(iRowIdx, 4).Value = ""
                                    cells(iRowIdx, iColIdx).EntireRow.Interior.Color = ""
                                End If

                            End If
                            iRowIdx += 1
                            iColIdx = 1
                            blnRowError = False
                            strErrorMsg = ""
                        End If
                    Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                                    And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" _
                                     And cells(iRowIdx, 5).Text = ""

                    ' check to make sure ENtity Values are unique in Database
                    If blnResult Then
                        iRowIdx = 1
                        Do
                            If IsSAPEntityInDatabase(cells(iRowIdx, 1).Text.ToString().Trim()) Then
                                blnResult = False
                                strErrorMsg = " SAPEntity Not Unique! "
                                cells(iRowIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, 4).Value = strErrorMsg
                            End If
                            iRowIdx += 1

                        Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                                    And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" _
                                    And cells(iRowIdx, 5).Text = ""

                    End If
                    mStrExcelData = objExcel.HTMLData
                    If blnResult Then
                        LoadExcelDataToDataTable(objExcel)
                    Else
                        Master.DisplayError("Invalid Entity Master value(s)!")
                    End If

                End If 'If HTMLData.Text.Length > 0
                Return blnResult
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateExcelRows()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Function GetCurrentColumn(ByVal intCol As Integer) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strCol As String = ""
            Try
                Select Case intCol
                    Case EXCEL_COLUMNS.ENTITY
                        strCol = "ENTITY"
                    Case EXCEL_COLUMNS.LOCATION
                        strCol = "LOCATION"
                    Case EXCEL_COLUMNS.SAP_ENTITY
                        strCol = ("SAP ENTITY")
                    Case Else
                        strCol = "UNKOWN COLUMN VALUE"
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetCurrentColumn()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return strCol
        End Function
        Private Function CheckForDuplicates() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnResult As Boolean = False

            Try
                Dim objExcel As New Owc11.Spreadsheet
                Dim iColIdx As Integer
                Dim iRowCnt As Integer ' Row counter
                Dim iCnt As Integer
                Dim dt As DataTable = Nothing
                Dim dr As DataRow = Nothing
                Dim drCompare As DataRow
                Dim strErrorMsg As String = "Duplicate Row(s) detected!"

                If Not mObjDT Is Nothing Then
                    dt = mObjDT
                End If

                If HTMLData.Text.Trim.Length > 0 Then
                    objExcel.HTMLData = mStrExcelData
                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.Selection.Cells

                    For iCnt = 0 To dt.Rows.Count - 1
                        dr = dt.Rows(iCnt)
                        For iRowCnt = iCnt + 1 To dt.Rows.Count - 1
                            drCompare = dt.Rows(iRowCnt)
                            If dr(1) = drCompare(1) Then
                                blnResult = True
                                iColIdx = 1

                                cells(iRowCnt + 1).EntireRow.Interior.Color = "Red"
                                cells(iRowCnt + 1, 4).Value = strErrorMsg
                            End If
                        Next
                    Next

                    If blnResult Then
                        Master.DisplayError(strErrorMsg)
                        mStrExcelData = objExcel.HTMLData
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - CheckForDuplicates()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return blnResult
        End Function
        Private Function SaveGridToDatabase() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)
            Dim dr As DataRow
            Try
                If Not mObjDT Is Nothing Then
                    For i As Integer = 0 To mObjDT.Rows.Count - 1
                        dr = mObjDT.Rows(i)
                        EntityMaster.AddEntityMaster(SessionManager.SelectedWorkCenterID, dr(1), dr(2), dr(3), cnMasterConnection, trans)
                    Next
                End If
                trans.Commit()
                Return True
            Catch Exc As Exception
                trans.Rollback()
                Master.DisplayErrors(ProgramName & " - SaveGridToDatabase()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection, trans)
            End Try
        End Function
        Private Sub SetExcelColumns()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            'Get an instance of Spreadsheet component
            Try
                Dim objExcel As New Owc11.Spreadsheet
                objExcel.ActiveSheet.Cells(1, 1).Value = " SAP Entity TEST "
                objExcel.ActiveSheet.Cells(1, 2).Value = " Entity "
                objExcel.ActiveSheet.Cells(1, 3).Value = "  Location "
                objExcel.ActiveSheet.Rows().Locked = True
                HTMLData.Text = objExcel.HTMLData
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetExcelColumns()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub LoadExcelDataToDataTable(ByRef objExcel As Owc11.Spreadsheet)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim iColIdx As Integer
                Dim iRowIdx As Integer
                Dim dr As DataRow

                'Get a reference to Cells collection
                objExcel.Cells(1, 1).Select()
                cells = objExcel.Selection.Cells

                iRowIdx = 1 ' SKIP the Headers 
                iColIdx = 1

                mObjDT = New DataTable
                ' set up mObjDT to DataGrid structure
                SetupDataTable(mObjDT, gvImport)
                dr = mObjDT.NewRow
                dr.Item(0) = SessionManager.SelectedWorkCenter
                Do
                    dr.Item(iColIdx) = cells(iRowIdx, iColIdx).Text
                    iColIdx += 1
                    If iColIdx = TOTAL_COLS Then
                        dr.Item(iColIdx) = cells(iRowIdx, iColIdx).Text
                        iColIdx = 1
                        iRowIdx += 1
                        mObjDT.Rows.Add(dr)
                        dr = mObjDT.NewRow
                        dr.Item(0) = SessionManager.SelectedWorkCenter
                    End If

                Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                            And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" And cells(iRowIdx, 5).Text = ""

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadExcelDataToDataTable", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function IsSAPEntityInDatabase(ByVal strSAPEntity As String) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnResult As Boolean = False
            Try
                If EntityMaster.SelectSAPEntityField(strSAPEntity) < 0 Then
                    blnResult = True
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - IsSAPEntityInDatabase()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return blnResult
        End Function
#End Region

    End Class
End Namespace

