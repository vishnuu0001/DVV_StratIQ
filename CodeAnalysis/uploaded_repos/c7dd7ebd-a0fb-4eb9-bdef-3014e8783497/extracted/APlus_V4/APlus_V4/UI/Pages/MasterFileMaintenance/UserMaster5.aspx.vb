#Region " Imports"
Imports System.IO
Imports System.DirectoryServices
Imports System.Data
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster5
        Inherits ApplicationBase

#Region " Private Constants"
        Private Shared ReadOnly FormName As String = "User Master Active Directory Conflicts"
        Private Shared ReadOnly ProgramName As String = "UserMaster5"
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

            Master.IconImage = Request.ApplicationPath & "/images/user1_view.gif"
            Master.HeaderMessage = FormName
            Master.ProgramName = ProgramName
            Master.ShowWorkingSiteDropDown = True
            Master.AddBodyAttribute("onkeydown", "TrapEscKey(document.getElementById('" + MasterControl1.ExitButtonID + "'),window.event)")

            If SessionManager.WorkingSite = "" Then
                Master.DisplayError("You must have a Working Site selected.")
                Return
            Else
                If SessionManager.WorkingSite.ToString.Trim.Length = 0 Then
                    Master.DisplayError("You must have a Working Site selected.")
                    Return
                End If
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
            Master.MasterScriptManager.RegisterPostBackControl(MasterControl1.ExportButton)
        End Sub
        Protected Sub MasterControl1_onRowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles MasterControl1.onRowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case e.CommandName
                Case "EditRow"
                    SessionManager.SelectedValue = MasterControl1.MasterControlGrid.DataKeys(e.CommandArgument)("UserID").ToString
                    SessionManager.UserADMode = "EditRow"
                    Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster6"), False)
            End Select
        End Sub
        Protected Sub MasterControl1_Sorted(sender As Object, e As System.EventArgs) Handles MasterControl1.Sorted
            UpdatePanel1.Update()
        End Sub
#End Region

#Region " Custom Functions"
        Private Sub LoadUserGrid()
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
                Dim dt As DataTable = UserMaster.SelectUsersBySite(SessionManager.WorkingSiteID)
                If dt Is Nothing OrElse dt.Rows.Count = 0 Then
                    Master.DisplayError("No users for Site: " + SessionManager.WorkingSite.ToString)
                    Return
                End If

                'Add new column to indicate if the AD information is different
                Dim objC As DataColumn = New DataColumn("ADConflict")
                objC.DataType = System.Type.GetType("System.Boolean")
                dt.Columns.Add(objC)

                'Add new column to indicate if the AD information is different
                objC = New DataColumn("ADConflictInformation")
                objC.DataType = System.Type.GetType("System.String")
                dt.Columns.Add(objC)

                'loop through the rows and indicate if there are any conflicts
                Dim objEntry As DirectoryEntry

                For Each objRow As DataRow In dt.Rows
                    'first, try to get the AD information
                    objEntry = ADAccess.GetADUser(objRow.Item("UserID").ToString.Trim())

                    If Not IsNothing(objEntry) Then
                        Dim strReturn As String = CheckUser(objRow, objEntry)
                        If strReturn <> String.Empty Then
                            objRow("ADConflict") = True
                            objRow("ADConflictInformation") = strReturn
                        Else
                            objRow.Delete()
                        End If
                    Else
                        objRow("ADConflict") = False
                        objRow("ADConflictInformation") = "Not an AD User"
                    End If
                Next

                Dim dv1 As DataView = dt.DefaultView
                dv1.Sort = "UserID" & " " & "ASC"
                MasterControl1.DataSource = dv1
                MasterControl1.DataBind(True)
                UpdatePanel1.Update()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadUserGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function CheckUser(ByVal APlusUser As DataRow, ByVal ADUser As DirectoryEntry) As String
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
                Dim sb As New StringBuilder
                Dim objProps As System.DirectoryServices.PropertyCollection
                Dim strHolder As String = String.Empty
                Dim strADSite As String = String.Empty
                objProps = ADUser.Properties

                Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                If Replace(objProps("userprincipalname").Value.ToString, strADDomain & ".net", strDomain).ToUpper <> APlusUser("EmailAddress").ToString.ToUpper Then
                    sb.Append("Email Address: " & APlusUser("EmailAddress").ToString.Trim & " -> " & objProps("userprincipalname").Value.ToString.Trim())
                End If

                If objProps("sn").Value IsNot Nothing Then
                    strHolder = objProps("sn").Value.ToString.ToUpper
                Else
                    strHolder = ""
                End If
                If strHolder <> APlusUser("LastName").ToString.ToUpper Then
                    'Check Last Name
                    If sb.Length > 0 Then
                        sb.Append("<BR />")
                    End If
                    sb.Append("Last Name: " & APlusUser("LastName").ToString.Trim & " -> " & strHolder)
                End If

                If objProps("givenname").Value.ToString.ToUpper <> APlusUser("FirstName").ToString.ToUpper Then
                    If sb.Length > 0 Then
                        sb.Append("<BR />")
                    End If
                    sb.Append("First Name: " & APlusUser("FirstName").ToString.Trim & " -> " & objProps("givenname").Value.ToString.Trim())
                End If

                If Not IsNothing(objProps("initials").Value) Then
                    strHolder = objProps("initials").Value.ToString()
                Else
                    strHolder = ""
                End If
                If strHolder.Trim.ToUpper <> APlusUser("MiddleInitial").ToString.ToUpper Then
                    If sb.Length > 0 Then
                        sb.Append("<BR />")
                    End If
                    sb.Append("Middle Initial: " & APlusUser("MiddleInitial").ToString.Trim & " -> " & strHolder.Trim.ToUpper.Trim())
                End If

                If Not IsNothing(objProps("distinguishedname").Value) Then
                    strHolder = APlusUser("ADSite").ToString
                    strADSite = ADAccess.GetADSite(objProps("distinguishedname").Value.ToString)
                    If strHolder <> strADSite Then
                        If sb.Length > 0 Then
                            sb.Append("<BR />")
                        End If
                        sb.Append("Site: " & strHolder & " -> " & strADSite)
                    End If
                Else
                    If sb.Length > 0 Then
                        sb.Append("<BR />")
                    End If
                    sb.Append("Site: " & APlusUser("ADSite").ToString.Trim & " -> ")
                End If

                Return sb.ToString
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - CheckUser", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return String.Empty
            End Try
        End Function
        Private Sub RefreshWorkingSite()
            LoadUserGrid()
        End Sub
#End Region

    End Class
End Namespace

