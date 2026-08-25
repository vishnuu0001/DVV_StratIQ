#Region "Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Text
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.DataAccess.Connections
Imports Microsoft.Office.Interop
Imports System.Web.Security
#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class ActivityImport
        Inherits ApplicationBase

#Region " Private Members "
        Private Shared ReadOnly FormName As String = "SLICE Activity Import"
        Private Shared ReadOnly ProgramName As String = "ActivityImport"
        Private Shared ReadOnly TOTAL_COLS As Integer = 10
        Private Shared ReadOnly ERROR_COL As Integer = 11
        Private Shared ReadOnly ACTIVITY_GRP_ERROR As Integer = -1
        Private Shared ReadOnly ENTITY_ERROR As Integer = -2
        Private Shared ReadOnly POSITION_ERROR As Integer = -3
        Private Shared ReadOnly SLICE_TYPE_ERROR As Integer = -4
        Private Shared ReadOnly SLICE_FREQ_ERROR As Integer = -5
        Private Shared ReadOnly SLICE_RESULTS_ERROR As Integer = -6

        Private cells As Owc11.Range 'Cells collection
        Protected mStrExcelData As String ' holds excel data for redisplay
        Protected mObjDT As DataTable ' holds the validated, duplicate free excel import data

        Enum EXCEL_COLUMNS
            ACTIVITY_GROUP = 1
            ENTITY = 2
            POSITION = 3
            TYPE = 4
            PRESENTATION_SEQUENCE = 5
            FREQUENCY = 6
            MEASUREMENT = 7
            DESIRED_CONDITION = 8
            RESULTS = 9
            TARGET_TIME = 10
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

            SessionManager.CurrentProgram = Request.Path

            If SessionManager.SelectedWorkCenterID <= 0 Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("WorkcenterSelection"), False)
            End If

            ' set up javascript
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnCancel.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
            Master.AddBodyAttribute("onload", "SetSpreadSheetTitle()")

            Master.HeaderMessage = FormName
            Master.IconImage = Request.ApplicationPath + "/images/clipboard.png"

            SetUpGridColumns()

            If Not btnValidate Is Nothing Then
                btnValidate.Attributes.Add("onclick", "ImportFromExcel()")
            End If

            If Not Page.IsPostBack Then
                pnlImport.Visible = False
            End If
        End Sub
        Private Sub btnValidate_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnValidate.Click
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
                    pnlSpreadsheet.Visible = False
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
        Private Sub btnCancel2_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel2.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ActivityImport"), False)
        End Sub
        Private Sub btnImportData_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnImportData.Click
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("ActivityImport"), False)
        End Sub
#End Region

#Region " Custom Methods "
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
            Dim strErrorMsg As String = ""
            Dim intSLICEInfo As Integer

            Try
                If HTMLData.Text.Length > 0 Then
                    ' get data hidden in textbox
                    objExcel.HTMLData = Me.HTMLData.Text

                    'Get a reference to Cells collection
                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.Selection.Cells

                    iRowIdx = 1 ' SKIP the Headers 
                    iColIdx = 1

                    Do
                        If cells(iRowIdx, iColIdx).Text.ToString().Trim().Length() < 1 AndAlso iColIdx <> ActivityImport.EXCEL_COLUMNS.MEASUREMENT Then
                            strErrorMsg &= " " & Me.GetCurrentColumn(iColIdx) & " cannot be empty! "

                            blnResult = False
                            blnRowError = True
                        ElseIf iColIdx = ActivityImport.EXCEL_COLUMNS.TARGET_TIME Then
                            If Not IsNumeric(cells(iRowIdx, ActivityImport.EXCEL_COLUMNS.TARGET_TIME).Text) Then
                                strErrorMsg &= " " & Me.GetCurrentColumn(ActivityImport.EXCEL_COLUMNS.TARGET_TIME) & " must be numeric! "
                                blnResult = False
                                blnRowError = True
                            End If
                        ElseIf Not IsNumeric(cells(iRowIdx, ActivityImport.EXCEL_COLUMNS.PRESENTATION_SEQUENCE).Text) Then
                            strErrorMsg &= " " & Me.GetCurrentColumn(ActivityImport.EXCEL_COLUMNS.PRESENTATION_SEQUENCE) & " must be numeric! "
                            blnResult = False
                            blnRowError = True
                        End If

                        iColIdx += 1

                        If iColIdx > ActivityImport.TOTAL_COLS Then
                            If cells(iRowIdx, ERROR_COL).Text.ToString.Trim.Length() > 1 Then
                                If Not blnRowError Then
                                    cells(iRowIdx, ERROR_COL).Value = ""
                                    cells(iRowIdx, iColIdx).EntireRow.Interior.Color = ""
                                End If
                            End If

                            ' AT end of row so check data in each column to see if valid
                            intSLICEInfo = SLICEActivityMaster.CheckSLICEActivityInformation(SessionManager.SelectedWorkCenterID, _
                                            cells(iRowIdx, 1).Text, cells(iRowIdx, 2).Text, cells(iRowIdx, 3).Text, _
                                            cells(iRowIdx, 4).Text, cells(iRowIdx, 6).Text, cells(iRowIdx, 9).Text)

                            If (intSLICEInfo < 0) Then
                                strErrorMsg += GetActivityDataErrorString(intSLICEInfo)
                                blnResult = False
                                blnRowError = True
                            End If

                            If cells(iRowIdx, ActivityImport.EXCEL_COLUMNS.PRESENTATION_SEQUENCE).Text.Trim() <> "" Then
                                ' now check for Unique PresSeqNum
                                intSLICEInfo = SLICEActivityMaster.CheckSLICEActivityGrpForUniqPresSeqNum( _
                                                                                cells(iRowIdx, 1).Text, _
                                                                                CInt(cells(iRowIdx, _
                                                                                ActivityImport.EXCEL_COLUMNS.PRESENTATION_SEQUENCE).Text))

                                If intSLICEInfo < 0 Then
                                    strErrorMsg &= " PRESENTATION SEQUENCE # for current activity group already exists in database! "
                                    blnResult = False
                                    blnRowError = True

                                    cells(iRowIdx).EntireRow.Interior.Color = "Red"
                                    cells(iRowIdx, ERROR_COL).Value = strErrorMsg
                                End If
                            End If

                            If blnRowError Then
                                cells(iRowIdx, iColIdx).EntireRow.Interior.Color = "Red"
                                cells(iRowIdx, ERROR_COL).Value = strErrorMsg
                            End If

                            iRowIdx += 1
                            iColIdx = 1
                            blnRowError = False
                            strErrorMsg = ""
                        End If

                    Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                    And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" And cells(iRowIdx, 5).Text = "" _
                    And cells(iRowIdx, 6).Text = "" And cells(iRowIdx, 7).Text = "" And cells(iRowIdx, 8).Text = "" _
                    And cells(iRowIdx, 9).Text = "" And cells(iRowIdx, 10).Text = ""

                    If blnResult Then
                        LoadExcelDataToDataTable(objExcel)
                    Else
                        If iRowIdx = 1 And blnRowError Then
                            cells(iRowIdx, iColIdx).EntireRow.Interior.Color = "Red"
                            cells(iRowIdx, ERROR_COL).Value = strErrorMsg
                        End If

                        Master.DisplayError("Invalid Activity value(s)!")
                    End If

                    mStrExcelData = objExcel.HTMLData
                End If 'If Me.HTMLData.Text.Length > 0

                Return blnResult
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - ValidateExcelRows()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Function
        Private Function GetCurrentColumn(ByVal intCol As Integer) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, intCol)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strCol As String = String.Empty
            Try
                Select Case intCol
                    Case EXCEL_COLUMNS.ACTIVITY_GROUP
                        strCol = "ACTIVITY GROUP"
                    Case EXCEL_COLUMNS.ENTITY
                        strCol = "ENTITY"
                    Case EXCEL_COLUMNS.POSITION
                        strCol = "POSITION"
                    Case EXCEL_COLUMNS.TYPE
                        strCol = "TYPE"
                    Case EXCEL_COLUMNS.PRESENTATION_SEQUENCE
                        strCol = "PRESENTATION SEQUENCE"
                    Case EXCEL_COLUMNS.FREQUENCY
                        strCol = "FREQUENCY"
                    Case EXCEL_COLUMNS.MEASUREMENT
                        strCol = "MEASUREMENT"
                    Case EXCEL_COLUMNS.DESIRED_CONDITION
                        strCol = "DESIRED CONDITION"
                    Case EXCEL_COLUMNS.RESULTS
                        strCol = "RESULTS"
                    Case EXCEL_COLUMNS.TARGET_TIME
                        strCol = "TARGET TIME"
                    Case Else
                        strCol = "UNKOWN COLUMN VALUE"
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetCurrentColumn()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return strCol
        End Function
        Public Function GetActivityDataErrorString(ByVal intError As Integer) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, intError)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strErrorMsg As String = String.Empty
            Try
                Select Case (intError)
                    Case ACTIVITY_GRP_ERROR
                        strErrorMsg = " Invalid ACTIVITY Group Value! "
                    Case ENTITY_ERROR
                        strErrorMsg = " Invalid ENTITY Value! "
                    Case POSITION_ERROR
                        strErrorMsg = " Invalid POSITION Value! "
                    Case SLICE_TYPE_ERROR
                        strErrorMsg = " Invalid TYPE Value! "
                    Case SLICE_FREQ_ERROR
                        strErrorMsg = " Invalid FREQUENCY Value! "
                    Case SLICE_RESULTS_ERROR
                        strErrorMsg = " Invalid RESULTS Value! "
                    Case Else
                        strErrorMsg = " Unknown Error Value: " & intError.ToString()
                End Select
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetActivityDataErrorString()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Return strErrorMsg
        End Function
        Public Sub LoadExcelDataToDataTable(ByRef objExcel As Owc11.Spreadsheet)
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

                    If iColIdx = ActivityImport.TOTAL_COLS Then
                        dr.Item(iColIdx) = cells(iRowIdx, iColIdx).Text
                        iColIdx = 1
                        iRowIdx += 1
                        mObjDT.Rows.Add(dr)
                        dr = mObjDT.NewRow
                        dr.Item(0) = SessionManager.SelectedWorkCenter
                    End If

                Loop Until cells(iRowIdx, 1).Text = "" And cells(iRowIdx, 2).Text = "" And cells(iRowIdx, 3).Text = "" _
                And cells(iRowIdx, 3).Text = "" And cells(iRowIdx, 4).Text = "" And cells(iRowIdx, 5).Text = "" _
                And cells(iRowIdx, 6).Text = "" And cells(iRowIdx, 7).Text = "" And cells(iRowIdx, 8).Text = "" _
                And cells(iRowIdx, 9).Text = "" And cells(iRowIdx, 10).Text = ""
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadExcelDataToDataTable()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Public Sub SetExcelColumns()
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

                objExcel.ActiveSheet.Cells(1, 1).Value = " Activity Group "
                objExcel.ActiveSheet.Cells(1, 2).Value = " SAPEntity "
                objExcel.ActiveSheet.Cells(1, 3).Value = "  Position "
                objExcel.ActiveSheet.Cells(1, 4).Value = "  Type "
                objExcel.ActiveSheet.Cells(1, 5).Value = " Presentation Sequence "
                objExcel.ActiveSheet.Cells(1, 6).Value = " Frequency "
                objExcel.ActiveSheet.Cells(1, 7).Value = " Measurement "
                objExcel.ActiveSheet.Cells(1, 8).Value = " Desired Condition "
                objExcel.ActiveSheet.Cells(1, 9).Value = " Results "
                objExcel.ActiveSheet.Cells(1, 10).Value = " Target Time "

                objExcel.ActiveSheet.Rows().Locked = True

                HTMLData.Text = objExcel.HTMLData
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetExcelColumns()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SetupDataTable(ByRef dt As DataTable, ByRef gv As GridView)
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
        Public Function CheckForDuplicates() As Boolean
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
                Dim dr As DataRow
                Dim drCompare As DataRow
                Dim strErrorMsg As String = "Duplicate Row(s) detected!"

                If Not mObjDT Is Nothing Then
                    dt = mObjDT
                End If

                If HTMLData.Text.Trim.Length > 0 Then
                    objExcel.HTMLData = mStrExcelData

                    'Get a reference to Cells collection
                    objExcel.Cells(1, 1).Select()
                    cells = objExcel.ActivePane.VisibleRange.Cells

                    For iCnt = 0 To dt.Rows.Count - 1
                        dr = dt.Rows(iCnt)

                        For iRowCnt = iCnt + 1 To dt.Rows.Count - 1
                            drCompare = dt.Rows(iRowCnt)
                            If dr(5) = drCompare(5) Then
                                blnResult = True
                                iColIdx = 5
                                cells(iRowCnt + 1).EntireRow.Interior.Color = "Red"
                                cells(iRowCnt + 1, ERROR_COL).Value = " Presentation Sequence Number must be unique! "
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
        Public Sub SetUpGridColumns()
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
                objCol.HeaderText = "Activity Group"
                objCol.DataField = "SLICEActivityGroupDescription"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "SAPEntity"
                objCol.DataField = "SAPEntity"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Position"
                objCol.DataField = "PositionID"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "SLICE Type"
                objCol.DataField = "SLICEType"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Presentation Sequence"
                objCol.DataField = "PresentationSequence"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Frequency"
                objCol.DataField = "SLICEFrequencyID"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Measurement"
                objCol.DataField = "Measurement"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Desired Condition"
                objCol.DataField = "DesiredCondition"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Results"
                objCol.DataField = "Results"
                gvImport.Columns.Add(objCol)

                objCol = New BoundField
                objCol.HeaderText = "Target Time"
                objCol.DataField = "TargetTime"
                gvImport.Columns.Add(objCol)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetUpGridColumns", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Public Sub ImportExcelDataToDataGrid()
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
        Public Function SaveGridToDatabase() As Boolean
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
            Dim blnResult As Boolean = True
            Dim dr As DataRow

            Try
                If mObjDT IsNot Nothing Then
                    For i As Integer = 0 To mObjDT.Rows.Count - 1
                        dr = mObjDT.Rows(i)
                        SLICEActivityMaster.AddSLICEActivityExcelImportData(SessionManager.SelectedWorkCenterID, _
                                                                                        dr(1), dr(2), dr(3), dr(4), dr(5), _
                                                                                        dr(6), dr(7), dr(8), dr(9), dr(10))
                    Next

                    If Not blnResult Then
                        trans.Rollback()
                    Else
                        trans.Commit()
                    End If
                End If
            Catch Exc As Exception
                blnResult = False
                trans.Rollback()
                Master.DisplayErrors(ProgramName & " - BindWorkcenters", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
            Return blnResult
        End Function
#End Region

    End Class
End Namespace

