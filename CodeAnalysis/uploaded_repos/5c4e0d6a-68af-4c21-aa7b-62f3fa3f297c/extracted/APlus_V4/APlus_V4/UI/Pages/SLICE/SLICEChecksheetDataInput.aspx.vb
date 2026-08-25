#Region " Imports "

Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports System.Math
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Connections
Imports System.Drawing
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEChecksheetDataInput
        Inherits ApplicationBase

#Region " Constants "
        Private Shared ReadOnly FormName As String = "SLICE Checksheet Data Input"
        Private Shared ReadOnly ProgramName As String = "SLICEChecksheetDataInput"
        Private Shared ReadOnly CANCEL_TARGET As String = "SLICEChecksheetMaster1.aspx" ' Page to go to when CANCEL clicked
        Private Shared ReadOnly COMMENTS_COL As Integer = 8
        Private Shared ReadOnly EDIT_CLEAR_COL As Integer = 9
        Private Shared ReadOnly ACTIVITY_ID_COL As Integer = 10
        Private Shared ReadOnly SLICE_CHECKSHEET_ACT_ID_COL As Integer = 11
        Private Shared ReadOnly TARGET_TIME_COL As Integer = 12
        Private Shared ReadOnly ROUNDING_AMOUNT As Integer = 5
#End Region

#Region " Member Variables "
        Protected mIntTargetTime As Integer
        Protected mIntElapsedTime As Integer
        Protected mDblProRatedElapseTimePerRow As Double
        Protected mIntTotalDisabledRows As Integer
        Protected mIntCurControl As Integer = 1 ' used to track which control is being printed
        Protected mIntActualTargetTime As Integer  ' the target time that of items where data collection has taken place
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

            Master.IconImage = Request.ApplicationPath & "/images/SLICEChecksheet.gif"
            Master.HeaderMessage = FormName '& " - " & SessionManager.SLICEChecksheetMasterMode .ToString
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnOK.UniqueID + "'))")
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            btnExit.Visible = False

            If Not Page.IsPostBack Then
                LoadDataEntryGrid()
                SetElapsedTimeLabel()
                lblDbUpdateInfo.Text = ""
                lblDbUpdateInfo.Visible = False
                lblDbUpdateInfoTop.Text = ""
                lblDbUpdateInfoTop.Visible = False
                txtEnterElapsedTime.Text = ""
            End If

            btnOK.Attributes.Add("onclick", "return CheckRequiredFieldsOnForm();")
            txtEnterElapsedTime.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")
        End Sub
        Protected Sub grdChecksheetDataInput_ItemDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.DataGridItemEventArgs) Handles grdChecksheetDataInput.ItemDataBound
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.Item.ItemType = ListItemType.Item Or e.Item.ItemType = ListItemType.AlternatingItem Then
                ' add <br> to Component/Location column
                If InStr(e.Item.Cells(2).Text.Trim(), Chr(13)) Then
                    e.Item.Cells(2).Text = Replace(e.Item.Cells(2).Text.Trim(), Chr(13), "<br>")
                End If

                ' add <br> for each slice type
                If InStr(e.Item.Cells(4).Text.Trim(), Chr(13)) Then
                    e.Item.Cells(4).Text = Replace(e.Item.Cells(4).Text.Trim(), Chr(13), "<br>")
                End If
            End If
        End Sub
        Protected Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetMaster1"), False)
        End Sub
        Protected Sub btnExit_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.MasterControlExitProgram = "SLICEChecksheetDataInput"
            RemoveCurrentProgramandGoBack()
        End Sub
        Protected Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim intResult As Integer = SaveResultsAndCommentsToDb()

            If intResult = 0 Then
                'grdChecksheetDataInput.Visible = False
                lblDbUpdateInfo.Text = "Checksheet Data saved to database!"
                lblDbUpdateInfo.Visible = True

                lblDbUpdateInfoTop.Text = "Checksheet Data saved to database!"
                lblDbUpdateInfoTop.Visible = True

                pnlSetRadioBtnsBottom.Visible = True
                pnlSetRadioBtnsTop.Visible = True


                ' reload data for display
                LoadDataEntryGrid()
                'CalcProRatedTimePerRow()
                SetElapsedTimeLabel()
                SetGridElapsedTimeTextBoxes()
                txtEnterElapsedTime.Text = ""

                lblDbUpdateInfo.ForeColor = Color.Black
                lblDbUpdateInfo.Font.Bold = True

                lblDbUpdateInfoTop.ForeColor = Color.Black
                lblDbUpdateInfoTop.Font.Bold = True

            ElseIf intResult = -4 Then
                lblDbUpdateInfo.Text = "No items selected! No data to save to database!"
                lblDbUpdateInfo.Font.Bold = True
                lblDbUpdateInfo.ForeColor = Color.Red
                lblDbUpdateInfo.Visible = True

                lblDbUpdateInfoTop.Text = "No items selected! No data to save to database!"
                lblDbUpdateInfoTop.Font.Bold = True
                lblDbUpdateInfoTop.ForeColor = Color.Red
                lblDbUpdateInfoTop.Visible = True
            End If
        End Sub
        Protected Sub dgItemCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.DataGridCommandEventArgs)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName.ToString() = "Edit" Then
                SessionManager.SLICEChecksheetActivityID = e.CommandArgument.ToString().Trim()
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetDataInput2"), False)
            End If
        End Sub

#End Region

#Region " Custom Methods "
        Private Sub LoadDataEntryGrid()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim dt As DataTable
            Dim dteTemp As Date
            Dim blnEnabledControl As Boolean = False

            Try
                dt = SLICEChecksheetMaster.SelectChecksheetDataForInputScreen(CInt(SessionManager.SelectedValueCheckSheetID.ToString()))
                If dt.Rows.Count > 0 Then
                    grdChecksheetDataInput.DataSource = dt
                    grdChecksheetDataInput.DataBind()
                    ' set labels above grid
                    lblShowChecksheetId.Text = dt.Rows(0)("SLICEChecksheetID").ToString().Trim()
                    lblShowStatus.Text = dt.Rows(0)("Status").ToString().Trim()

                    If lblShowStatus.Text.ToUpper = "CLOSED" Then
                        btnOK.Visible = False
                        grdChecksheetDataInput.Columns(9).Visible = False

                        btnAllConditionMet.Visible = False
                        btnAllConditionMet2.Visible = False
                        btnAllConditionNotMet.Visible = False
                        btnAllConditionNotMet2.Visible = False
                    End If

                    dteTemp = dt.Rows(0)("Release Date")
                    lblShowReleaseDate.Text = dteTemp.ToString("MM/dd/yyyy")
                    dteTemp = dt.Rows(0)("Due Date")
                    lblShowDueDate.Text = dteTemp.ToString("MM/dd/yyyy")
                    lblShowSAPEntity.Text = dt.Rows(0)("SLICEActivityGroup").ToString().Trim()

                    ' sum target time
                    For i As Integer = 0 To dt.Rows.Count - 1

                        If CInt(dt.Rows(i)("Result Selected").ToString()) <> 0 Then
                            ' only sum target times that have data for desired conditions
                            mIntActualTargetTime += CInt(dt.Rows(i)("TargetTime"))
                        End If

                        mIntTargetTime += CInt(dt.Rows(i)("TargetTime"))

                        If Not IsDBNull(dt.Rows(i)("ElapsedTime")) Then
                            mIntElapsedTime += CInt(dt.Rows(i)("ElapsedTime"))
                        End If
                    Next

                    ' set controls
                    For j As Integer = 0 To dt.Rows.Count - 1
                        mIntCurControl += 1
                        Dim objTxtBox As TextBox = DirectCast(grdChecksheetDataInput.Items(j).FindControl("txtExpandComments"), TextBox)
                        If dt.Rows(j)("Comments").ToString().Trim().Length > 0 Then

                            ' if comments exist, put 'em in textbox
                            objTxtBox.Text = dt.Rows(j)("Comments").ToString().Trim()

                            ' disable textbox w/comment
                            objTxtBox.Enabled = False

                            ' set style
                            objTxtBox.CssClass = "Textbox_Display"
                        End If

                        ' set up radio buttons
                        Dim objRdoList As RadioButtonList = DirectCast(grdChecksheetDataInput.Items(j).FindControl("rdoResults"), RadioButtonList)

                        If dt.Rows(j)("SLICEResultDesc").ToString().Trim.Length > 0 Then
                            If dt.Rows(j)("SLICEResultDesc").ToString().Trim().ToUpper() = "YES" Then
                                objRdoList.SelectedIndex = 0
                            ElseIf dt.Rows(j)("SLICEResultDesc").ToString().Trim().ToUpper() = "NO" Then
                                objRdoList.SelectedIndex = 1
                            End If
                            objRdoList.Enabled = False
                        End If

                        ' check to see if Result field is null
                        ' or that there are no comments 
                        If IsDBNull(dt.Rows(j)("ElapsedTime")) OrElse Not objTxtBox.Enabled Then
                            objRdoList.Enabled = False
                        End If

                        ' set link buttons
                        Dim objLnk As LinkButton = DirectCast(grdChecksheetDataInput.Items(j).FindControl("lbtnEditClear"), LinkButton)

                        ' get hyperlink control
                        Dim objHLnk As HyperLink = DirectCast(grdChecksheetDataInput.Items(j).FindControl("lnkClear"), HyperLink)

                        ' get elapsed time controls
                        Dim objTxtElapseTime As TextBox = DirectCast(grdChecksheetDataInput.Items(j).FindControl("txtElapsedTime"), TextBox)

                        ' get workorder number
                        Dim objTxtWrkOrdNum As TextBox = DirectCast(grdChecksheetDataInput.Items(j).FindControl("txtWorkorderNum"), TextBox)

                        ' prorate time for textboxes

                        If Not IsDBNull(dt.Rows(j)("ElapsedTime")) Then
                            If CInt(dt.Rows(j)("Result Selected")) > 0 Then
                                objTxtElapseTime.Text = dt.Rows(j)("ElapsedTime").ToString()
                            End If
                            If Not objRdoList.Enabled Then
                                objTxtElapseTime.Enabled = False
                                objTxtElapseTime.CssClass = "Textbox_Display"
                            End If
                        Else
                            objTxtElapseTime.Enabled = False
                            objTxtElapseTime.CssClass = "Textbox_Display"
                        End If

                        If objRdoList.Enabled Then
                            objLnk.Text = ""
                            objLnk.CommandName = "CLEAR"
                            objLnk.Visible = False
                            objHLnk.NavigateUrl = "javascript:ClearControlsInRow(" + mIntCurControl.ToString() + ");"

                            ' set javascript functions for textboxes
                            objTxtElapseTime.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")
                            objTxtWrkOrdNum.Attributes.Add("onkeydown", "javascript:AllowIntegers(window.event);")
                            blnEnabledControl = True
                        Else
                            ' disable textbox that has no comments
                            objTxtBox.Enabled = False
                            ' set style
                            objTxtBox.CssClass = "Textbox_Display"

                            ' hide hyperlink w/javascript function
                            objHLnk.Visible = False
                            objLnk.Text = "Edit"
                            objLnk.CommandName = "Edit"
                            objLnk.CommandArgument = dt.Rows(j)("SLICEChecksheetActivityID").ToString().Trim()
                            mIntTotalDisabledRows += 1

                            dt.Rows(j)("WorkorderNumber").ToString()
                            objTxtWrkOrdNum.Enabled = False
                            objTxtWrkOrdNum.CssClass = "Textbox_Display"
                        End If
                    Next
                    lblShowTargetTime.Text = mIntTargetTime.ToString()

                    ' if no controls were enabled then
                    ' make sure enterelapsedtime txtbox is
                    ' read only
                    If Not blnEnabledControl Then
                        txtEnterElapsedTime.Enabled = False
                        txtEnterElapsedTime.CssClass = "Textbox_Display"
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadDataEntryGrid()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function SaveResultsAndCommentsToDb() As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)

            Dim bResult As Boolean = True
            Dim intResult As Integer
            Dim intEnabledCnt As Integer = 0 ' count of controls that have a value and enabled 
            Dim objRadio As RadioButtonList
            Dim iResult As Integer
            Dim objText As TextBox
            Dim strComments As String = String.Empty
            Dim strActivityID As String = String.Empty
            Dim strChecksheetActivityID As String = String.Empty
            Dim intElapsedTime As Integer
            Dim objElapsedTime As TextBox
            Dim objWorkorderNum As TextBox
            Dim intProRatedTime As Integer

            Try
                If txtEnterElapsedTime.Text.Trim().Length > 0 Then
                    intElapsedTime = CInt(txtEnterElapsedTime.Text.Trim())
                Else
                    intElapsedTime = -1
                End If

                Dim mDblTotalTargetTimeUsed As Double = CalcTotalTargetTimeForResultsSubmitted()

                For i As Integer = 0 To grdChecksheetDataInput.Items.Count - 1
                    objRadio = DirectCast(grdChecksheetDataInput.Items(i).FindControl("rdoResults"), RadioButtonList)
                    objText = DirectCast(grdChecksheetDataInput.Items(i).FindControl("txtExpandComments"), TextBox)

                    If objRadio IsNot Nothing AndAlso objText IsNot Nothing Then
                        If objRadio.SelectedValue.ToString().Trim() <> "" And objRadio.Enabled = True Or objText.Text.Trim.Length() > 0 AndAlso objText.Enabled = True Then
                            intEnabledCnt += 1

                            objElapsedTime = DirectCast(grdChecksheetDataInput.Items(i).FindControl("txtElapsedTime"), TextBox)
                            objWorkorderNum = DirectCast(grdChecksheetDataInput.Items(i).FindControl("txtWorkorderNum"), TextBox)

                            If Not objWorkorderNum.Text.Trim().Length > 0 Then
                                objWorkorderNum.Text = "0"
                            End If

                            ' is user using main textbox input or 
                            ' dynamic inputs in datagrid?
                            If intElapsedTime = -1 Then
                                If objElapsedTime.Text.Trim.Length > 0 Then
                                    intProRatedTime = CInt(objElapsedTime.Text.Trim())
                                    ' prorated time needs to be calculated here
                                    ' if the main elapsed time textbox is used
                                    ' otherwise just insert the dynamic textbox val
                                Else
                                    intProRatedTime = -1
                                End If
                            Else
                                If Not objRadio.SelectedItem Is Nothing Then
                                    ' calc the prorated time!
                                    intProRatedTime = CalculateProratedTime(intElapsedTime, CInt(grdChecksheetDataInput.Items(i).Cells(TARGET_TIME_COL).Text.Trim()), mDblTotalTargetTimeUsed)
                                Else
                                    intProRatedTime = -1
                                End If
                            End If

                            If Not objRadio.SelectedItem Is Nothing Then
                                iResult = objRadio.SelectedItem.Value
                            Else
                                iResult = ""
                            End If

                            If Not objText.Text Is Nothing Then
                                strComments = objText.Text.Trim()
                            End If

                            strActivityID = grdChecksheetDataInput.Items(i).Cells(ACTIVITY_ID_COL).Text
                            strChecksheetActivityID = grdChecksheetDataInput.Items(i).Cells(SLICE_CHECKSHEET_ACT_ID_COL).Text.Trim()

                            SLICEChecksheetMaster.InsertSLICEChecksheetResultsCommentsData(strActivityID, intProRatedTime, SessionManager.UserID.ToString(), objWorkorderNum.Text, iResult, strComments, SessionManager.UserID.ToString(), strChecksheetActivityID, cnMasterConnection, trans)
                        End If
                    End If
                Next

                trans.Commit()
            Catch Exc As Exception
                trans.Rollback()
                Master.DisplayErrors(ProgramName & " - SaveResultsAndCommentsToDb", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection, trans)
            End Try

            If intEnabledCnt < 1 Then
                intResult = -4
            End If

            Return intResult
        End Function
        Private Sub CalcProRatedTimePerRow()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            mDblProRatedElapseTimePerRow = Round(mIntElapsedTime / mIntTotalDisabledRows, ROUNDING_AMOUNT)
        End Sub
        Private Sub SetElapsedTimeLabel()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            lblDisplayElapsedTime.Text = mIntElapsedTime
        End Sub
        Private Sub SetGridElapsedTimeTextBoxes()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objR As RadioButtonList
            Dim objT As TextBox
            Dim intCnt As Integer = grdChecksheetDataInput.Items.Count

            Try
                For i As Integer = 0 To intCnt - 1
                    objR = DirectCast(grdChecksheetDataInput.Items(i).FindControl("rdoResults"), RadioButtonList)

                    If objR.Enabled = False Then
                        objT = DirectCast(grdChecksheetDataInput.Items(i).FindControl("txtElapsedTime"), TextBox)
                        objT.Enabled = False
                    End If
                Next
            Catch ex As Exception
                ' do nothing
            End Try
        End Sub
        Private Function CalculateProratedTime(ByVal intElapseTime As Integer, ByVal intTargetTime As Integer, ByVal intTargetTimeSum As Integer) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, intElapseTime, intTargetTime, intTargetTimeSum)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim dblTime As Double = intElapseTime * (intTargetTime / intTargetTimeSum)
            Return Round(dblTime)
        End Function
        Private Function CalcTotalTargetTimeForResultsSubmitted() As Double
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objRadio As RadioButtonList
            Dim mDblTotalTargetTimeUsed As Double = 0

            For i As Integer = 0 To grdChecksheetDataInput.Items.Count - 1
                objRadio = DirectCast(grdChecksheetDataInput.Items(i).FindControl("rdoResults"), RadioButtonList)

                If objRadio.SelectedValue.ToString().Trim() <> "" And objRadio.Enabled = True Then
                    mDblTotalTargetTimeUsed += CDbl(grdChecksheetDataInput.Items(i).Cells(12).Text.Trim())
                End If
            Next

            Return mDblTotalTargetTimeUsed
        End Function
#End Region

    End Class
End Namespace

