#Region " Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.DataAccess.Tables
Imports System.DirectoryServices
Imports System.Data
Imports System.Data.SqlClient
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster12
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "User Master Attendance Conflicts"
        Private Shared ReadOnly ProgramName As String = "UserMaster12"
#End Region

#Region " Event Handlers"
        Protected Sub UserMaster1_PreInit(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.PreInit
            AddHandler Master.RefreshWorkingSite, AddressOf RefreshWorkingSite
        End Sub
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

            Master.IconImage = Request.ApplicationPath & "/images/user1_add.gif"
            Master.HeaderMessage = FormName
            Master.ProgramName = ProgramName
            Master.ShowWorkingSiteDropDown = True
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If SessionManager.WorkingSite Is Nothing OrElse String.IsNullOrEmpty(SessionManager.WorkingSite.Trim()) Then
                Master.DisplayError("You must have a Working Site selected.")
                Return
            End If
        End Sub
        Protected Sub Timer1_Tick(ByVal sender As Object, ByVal e As System.EventArgs) Handles Timer1.Tick
            Timer1.Enabled = False
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, functionInfo.Name, SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            LoadUserGrid()
        End Sub
        Protected Sub gvUsers_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles gvUsers.RowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "EditRow" Then
                SessionManager.SelectedValue = gvUsers.Rows(e.CommandArgument).Cells(2).Text
                SessionManager.UserITMode = "EditRow"
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster13"), False)
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

            RemoveCurrentProgramandGoBack()
        End Sub
        Private Sub btnSelectAll_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnSelectAll.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objCheck As CheckBox = Nothing
            For Each row As GridViewRow In gvUsers.Rows
                If row.RowType = DataControlRowType.DataRow Then
                    Try
                        objCheck = DirectCast(row.FindControl("chkSelected"), CheckBox)
                    Catch ex As Exception

                    End Try

                    If Not objCheck Is Nothing Then
                        objCheck.Checked = True
                    End If
                End If
            Next
        End Sub
        Private Sub btnProcessSelected_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnProcessSelected.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objCheck As CheckBox = Nothing
                Dim dtUser As DataTable
                Dim strUserID As String = String.Empty
                Dim strTitle As String = String.Empty
                Dim cnAPlusMaster As SqlConnection
                Dim cnITMaster As SqlConnection

                cnAPlusMaster = ApplicationConnection.OpenMasterConnection
                cnITMaster = AttendanceConnection.OpenMasterConnection

                For Each row As GridViewRow In gvUsers.Rows
                    If row.RowType = DataControlRowType.DataRow Then
                        Try
                            objCheck = DirectCast(row.FindControl("chkSelected"), CheckBox)

                            If objCheck IsNot Nothing AndAlso objCheck.Checked Then
                                strUserID = row.Cells(2).Text

                                If Not strUserID.IndexOf(" ") > -1 AndAlso strUserID.Trim.Length <= 15 Then
                                    dtUser = AttendanceAccess.SelectUserMaster(strUserID, cnITMaster)
                                    If Not dtUser Is Nothing AndAlso dtUser.Rows.Count = 1 Then
                                        strTitle = dtUser.Rows(0)("Title").ToString
                                        UserMaster.UpdateTitle(strUserID, strTitle, cnAPlusMaster)
                                    End If
                                End If
                            End If
                        Catch ex As Exception
                            'just go to the next record
                        End Try
                    End If
                Next

                cnAPlusMaster.Close()
                cnITMaster.Close()

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster12"), False)
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadUserGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Custom Functions"
        Private Sub LoadUserGrid()
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
                Dim dt As DataTable = UserMaster.SelectUsersBySite(SessionManager.WorkingSiteID)
                If IsNothing(dt) OrElse dt.Rows.Count = 0 Then
                    Master.DisplayError("No users for Site: " + SessionManager.WorkingSite.ToString)
                    Return
                End If

                Dim objC As DataColumn
                objC = New DataColumn("AttendanceConflict")
                objC.DataType = System.Type.GetType("System.Boolean")
                dt.Columns.Add(objC)

                objC = New DataColumn("AttendanceActive")
                objC.DataType = System.Type.GetType("System.Boolean")
                dt.Columns.Add(objC)

                objC = New DataColumn("AttendanceConflictInformation")
                objC.DataType = System.Type.GetType("System.String")
                dt.Columns.Add(objC)

                Dim dtRowIT As DataRow
                Dim strReturn As String = String.Empty

                For Each objRow As DataRow In dt.Rows
                    dtRowIT = GetAttendanceUser(objRow("UserID"))

                    If dtRowIT IsNot Nothing Then
                        strReturn = CheckUser(objRow, dtRowIT)

                        If Not String.IsNullOrEmpty(strReturn) Then
                            objRow("AttendanceConflict") = True
                            objRow("AttendanceActive") = dtRowIT("Active")
                            objRow("AttendanceConflictInformation") = strReturn
                        Else
                            objRow.Delete()
                        End If
                    Else
                        objRow("AttendanceConflict") = False
                        objRow("AttendanceActive") = False
                        objRow("AttendanceConflictInformation") = String.Empty
                    End If
                Next

                gvUsers.DataSource = dt
                gvUsers.DataBind()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadUserGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function CheckUser(ByVal APlusUser As DataRow, ByVal ITRequestUser As DataRow) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                Dim sb As New StringBuilder
                Dim strHolder As String = String.Empty

                If Replace(ITRequestUser("EmailAddress").ToString, strADDomain & ".net", strDomain).ToUpper <> APlusUser("EmailAddress").ToString.ToUpper Then
                    sb.Append("Email Address: " & APlusUser("EmailAddress").ToString.Trim & " -> " & ITRequestUser("EmailAddress").ToString.Trim())
                End If
                If ITRequestUser("LastName").ToString.ToUpper <> APlusUser("LastName").ToString.ToUpper Then
                    If sb.Length > 0 Then sb.Append("<BR />")
                    sb.Append("Last Name: " & APlusUser("LastName").ToString.Trim & " -> " & ITRequestUser("LastName").ToString.Trim)
                End If
                If ITRequestUser("FirstName").ToString.ToUpper <> APlusUser("FirstName").ToString.ToUpper Then
                    If sb.Length > 0 Then sb.Append("<BR />")
                    sb.Append("First Name: " & APlusUser("FirstName").ToString.Trim & " -> " & ITRequestUser("FirstName").ToString.Trim())
                End If
                If ITRequestUser("MiddleInitial").ToString.ToUpper <> APlusUser("MiddleInitial").ToString.ToUpper Then
                    If sb.Length > 0 Then sb.Append("<BR />")
                    sb.Append("Middle Initial: " & APlusUser("MiddleInitial").ToString.Trim & " -> " & ITRequestUser("MiddleInitial").ToString.Trim())
                End If
                If ITRequestUser("Title").ToString.ToUpper <> APlusUser("Title").ToString.ToUpper AndAlso ITRequestUser("Title").ToString.ToUpper <> Replace(APlusUser("Title").ToString.ToUpper, "-", "") Then
                    If sb.Length > 0 Then sb.Append("<BR />")

                    sb.Append("Title: " & APlusUser("Title").ToString.Trim & " -> " & ITRequestUser("Title").ToString.Trim())
                End If
                If ITRequestUser("ADSite").ToString.ToUpper <> APlusUser("ADSite").ToString.ToUpper Then
                    If sb.Length > 0 Then sb.Append("<BR />")

                    sb.Append("Site: " & APlusUser("ADSite").ToString.Trim & " -> " & ITRequestUser("ADSite").ToString.Trim())
                End If
                If ITRequestUser("Active").ToString.ToUpper <> APlusUser("Active").ToString.ToUpper Then
                    If sb.Length > 0 Then sb.Append("<BR />")

                    sb.Append("Active: " & APlusUser("Active").ToString.Trim & " -> " & ITRequestUser("Active").ToString.Trim())
                End If

                Return sb.ToString
            Catch Exc As Exception
                Throw
            End Try
        End Function
        Private Function GetAttendanceUser(ByVal passUser As String) As DataRow
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim objDT As DataTable = AttendanceAccess.SelectUserMaster(passUser)
                If Not objDT Is Nothing AndAlso objDT.Rows.Count = 1 Then
                    Return objDT.Rows(0)
                Else
                    Return Nothing
                End If
            Catch Exc As Exception
                Throw
            End Try
        End Function
        Private Sub RefreshWorkingSite()
            LoadUserGrid()
        End Sub
#End Region

    End Class
End Namespace