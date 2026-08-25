#Region " Imports"

Imports System.IO
Imports System.Data
Imports System.Text
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.SLICETables
Imports WebApp.APlus.UI.CustomControls
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.SLICE
    Partial Class SLICEChecksheetDataInput2
        Inherits ApplicationBase

#Region " Private Constants "
        Private Shared ReadOnly FormName As String = "Edit SLICE Checksheet Data "
        Private Shared ReadOnly ProgramName As String = "SLICEChecksheetDataInput2"
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
            Master.HeaderMessage = FormName
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/en-US/DataEntry.js")

            If Not Page.IsPostBack Then
                btnExit.Visible = False
                LoadPageControls()
            End If

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnOK.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:IgnoreTab(window.event)")
        End Sub
        Protected Sub btnClear_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnClear.Click
            rdoMeetsDesiredCon.SelectedIndex = -1
            txtElapsedTime.Text = ""
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

            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetDataInput"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If UpdateRecord() Then
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("SLICEChecksheetDataInput"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods "
        Public Sub LoadPageControls()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim intChecksheetID As Integer
            If SessionManager.SLICEChecksheetActivityID > 0 Then
                intChecksheetID = SessionManager.SLICEChecksheetActivityID

                Try
                    Dim dt As DataTable = SLICEChecksheetMaster.SelectChecksheetRowDataForEdit(intChecksheetID)
                    If dt.Rows.Count > 0 Then
                        txtEntityNum.Text = dt.Rows(0)("SAPEntity").ToString()
                        txtExpandCoLoc.Text = dt.Rows(0)("CoLoc").ToString()
                        txtPosition.Text = dt.Rows(0)("Position").ToString()
                        txtElapsedTime.Text = dt.Rows(0)("ElapsedTime").ToString()
                        txtExpandComments.Text = dt.Rows(0)("Comments").ToString()
                        txtWorkOrderNum.Text = dt.Rows(0)("WorkorderNumber").ToString()
                        If dt.Rows(0)("SLICEResultDesc").ToString().Trim().ToUpper() = "YES" Then
                            rdoMeetsDesiredCon.SelectedIndex = 0
                        ElseIf dt.Rows(0)("SLICEResultDesc").ToString().Trim().ToUpper() = "NO" Then
                            rdoMeetsDesiredCon.SelectedIndex = 1
                        End If
                    End If
                Catch Exc As Exception
                    Master.DisplayErrors(ProgramName & " - LoadPageControls()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                End Try
            End If
        End Sub
        Public Function UpdateRecord() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UISlice) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim intWorkOrdNum As Integer = -1
                Dim iResultID As Integer = -1
                Dim strMessage As String = ""

                If IsNumeric(txtWorkOrderNum.Text) Then
                    intWorkOrdNum = Convert.ToInt16(txtWorkOrderNum.Text)
                End If
                If rdoMeetsDesiredCon.SelectedItem IsNot Nothing Then
                    If rdoMeetsDesiredCon.SelectedItem.Text = "No" Then
                        If txtExpandComments.Text.Trim.Length = 0 Then
                            strMessage = "Comments are required when desired condition not met."
                        End If
                        If Not IsNumeric(txtElapsedTime.Text) Then
                            If strMessage.Trim.Length > 0 Then
                                strMessage += "<br />"
                            End If
                            strMessage += "Elapsed time required."
                        End If
                    End If
                    iResultID = rdoMeetsDesiredCon.SelectedItem.Value
                End If

                If strMessage.Trim.Length > 0 Then
                    Master.DisplayError(strMessage)
                    Return False
                End If

                SLICEChecksheetMaster.UpdateSLICEActivityResultsRow(SessionManager.SLICEChecksheetActivityID.ToString(), txtElapsedTime.Text.Trim(), txtExpandComments.Text.Trim(), intWorkOrdNum, SessionManager.UserID.ToString(), iResultID)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateRecord()", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try

            Return True
        End Function
#End Region

    End Class
End Namespace

