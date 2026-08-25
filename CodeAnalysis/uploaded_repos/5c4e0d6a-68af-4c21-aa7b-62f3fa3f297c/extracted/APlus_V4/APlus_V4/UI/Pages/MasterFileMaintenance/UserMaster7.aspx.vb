#Region " Imports"
Imports System.IO
Imports System.DirectoryServices
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class UserMaster7
        Inherits ApplicationBase

#Region " Constants"
        Private Shared ReadOnly FormName As String = "Active Directory Users"
        Private Shared ReadOnly ProgramName As String = "UserMaster7"
        Private Shared ReadOnly DBTableName As String = "UserMaster"
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

            Master.IconImage = Request.ApplicationPath & "/images/user1_view.gif"
            Master.HeaderMessage = FormName

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnExit.UniqueID + "'),window.event)")

            If SessionManager.WorkingSite = String.Empty Then
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
            lblRecords.Text = grdUsers.Rows.Count.ToString + " users not in UserMaster"
        End Sub
        Protected Sub grdUsers_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdUsers.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                If e.Row.Cells(3).Text.Contains(" ") OrElse e.Row.Cells(3).Text.Contains(".") Then
                    CType(e.Row.Cells(6).Controls(0), WebControl).Enabled = False
                    CType(e.Row.Cells(7).FindControl("chkSelected"), CheckBox).Enabled = False
                End If
            End If
        End Sub
        Protected Sub grdUsers_RowCommand(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewCommandEventArgs) Handles grdUsers.RowCommand
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", e.CommandName)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If e.CommandName = "AddRow" Then
                Dim dtGrid As GridView = CType(sender, GridView)
                Dim iRow As Integer = CInt(e.CommandArgument)

                SessionManager.UserMasterMode = "ADAdd"
                SessionManager.ADUserID = dtGrid.Rows(iRow).Cells(3).Text
                If SessionManager.ADUserID = "&nbsp;" Then
                    SessionManager.ADUserID = ""
                End If
                SessionManager.ADLastName = dtGrid.Rows(iRow).Cells(0).Text
                If SessionManager.ADLastName = "&nbsp;" Then
                    SessionManager.ADLastName = ""
                End If
                SessionManager.ADFirstName = dtGrid.Rows(iRow).Cells(1).Text
                If SessionManager.ADFirstName = "&nbsp;" Then
                    SessionManager.ADFirstName = ""
                End If
                SessionManager.ADMiddleInitial = dtGrid.Rows(iRow).Cells(2).Text
                If SessionManager.ADMiddleInitial = "&nbsp;" Then
                    SessionManager.ADMiddleInitial = ""
                End If
                SessionManager.ADEmail = dtGrid.Rows(iRow).Cells(5).Text
                If SessionManager.ADEmail = "&nbsp;" Then
                    SessionManager.ADEmail = ""
                End If

                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster2"), False)
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
        Protected Sub btnProcessSelected_Click(ByVal sender As Object, ByVal e As System.EventArgs) Handles btnProcessSelected.Click
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
                Dim strUserID As String = String.Empty
                Dim strMI As String = String.Empty
                Dim strFirstName As String = String.Empty
                Dim strLastName As String = String.Empty
                Dim strEmail As String = String.Empty

                For iRow As Integer = 0 To grdUsers.Rows.Count - 1
                    Try
                        objCheck = DirectCast(grdUsers.Rows(iRow).FindControl("chkSelected"), CheckBox)
                    Catch Exc As Exception

                    End Try

                    If Not objCheck Is Nothing AndAlso objCheck.Checked Then
                        strUserID = grdUsers.Rows(iRow).Cells(3).Text
                        If Not strUserID.Contains(" ") AndAlso strUserID.Trim.Length <= 15 Then
                            strFirstName = grdUsers.Rows(iRow).Cells(1).Text
                            strLastName = grdUsers.Rows(iRow).Cells(0).Text
                            strMI = grdUsers.Rows(iRow).Cells(2).Text
                            strEmail = grdUsers.Rows(iRow).Cells(5).Text
                            If strFirstName.ToUpper.Contains("&NBSP") Then
                                strFirstName = ""
                            End If
                            If strLastName.ToUpper.Contains("&NBSP") Then
                                strLastName = ""
                            End If
                            If strMI.ToUpper.Contains("&NBSP") Then
                                strMI = ""
                            End If
                            If strEmail.ToUpper.Contains("&NBSP") Then
                                strEmail = ""
                            End If

                            Dim strDomain As String = ConfigurationManager.AppSettings("DefaultEmailFromDomain")
                            Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                            strEmail = strEmail.ToLower.Replace(strADDomain & ".net", strDomain)

                            Dim dt As DataTable = CultureMaster.SelectCultureMaster(2)

                            Dim objDic As New Dictionary(Of String, String)
                            objDic.Add("FirstName", StrConv(strFirstName, VbStrConv.ProperCase).Trim())
                            objDic.Add("LastName", StrConv(strLastName, VbStrConv.ProperCase).Trim())
                            objDic.Add("MiddleInitial", strMI.ToUpper.Trim())
                            objDic.Add("Suffix", "")
                            objDic.Add("DeptNumber", "")
                            objDic.Add("InitialProgram", "MainMenu")
                            objDic.Add("Site", SessionManager.WorkingSite)
                            objDic.Add("Culture", dt.Rows(0).Item("CultureDescription").ToString.Trim())
                            objDic.Add("Title", "-")
                            objDic.Add("EmailAddress", strEmail)
                            objDic.Add("IsAdministrator", False)
                            objDic.Add("RegTemp", False)
                            objDic.Add("Active", True)

                            Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)
                            UserMaster.AddUserMaster(strUserID, SessionManager.WorkingSiteID, "", "MainMenu", False, StrConv(strLastName, VbStrConv.ProperCase), StrConv(strFirstName, VbStrConv.ProperCase), strMI.ToUpper, "", "-", "", True, strEmail, False, 2, False)
                            RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, strUserID.ToUpper.Trim(), strChangeLog, SessionManager.UserID)

                            objDic.Clear()
                            objDic.Add("User", strUserID)
                            objDic.Add("SecurityGroup", "TEAMMEMBER")
                            Dim strChangeLog1 As String = TransactionProcessing.GetDictionaryValues(objDic)
                            UserSecurityGroupMaster.AddUserSecurityGroupMaster(strUserID, 4)
                            RecordTransactionHistory.InsertRecordTransactionHistory("UserSecurityGroupMaster", strUserID.ToUpper.Trim() & ",4", strChangeLog1, SessionManager.UserID)
                        End If
                    End If
                Next
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - btnProcessSelected_Click", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
            Response.Redirect(Context.Request.ApplicationPath + Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("UserMaster7"), False)
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
                Dim objDT As DataTable = GetADUsers()
                If objDT Is Nothing OrElse objDT.Rows.Count = 0 Then
                    Master.DisplayError("No AD Users for Site: " + SessionManager.WorkingSite.ToString)
                    Return
                End If

                Dim dv As DataView = objDT.DefaultView
                dv.Sort = "Site, LastName, FirstName"
                grdUsers.DataSource = dv
                grdUsers.DataBind()
                lblRecords.Visible = True
                lblRecords.Text = grdUsers.Rows.Count.ToString + " users not in User Master"
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadUserGrid", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Function GetADUsers() As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strSite As String = String.Empty
            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection

            Try
                strSite = SiteMaster.GetADSite(SessionManager.WorkingSiteID, cnMasterConnection)

                If strSite.Trim.Length = 0 Then
                    Master.DisplayError("Invalid Working Site")

                    Return Nothing
                End If

                Dim strADDomain As String = ConfigurationManager.AppSettings("ADDomain")
                Dim strADUserOU As String = ConfigurationManager.AppSettings("ADUserOU")

                Dim dvUsers As DataView = UserMaster.SelectUsersBySite(0, cnMasterConnection).DefaultView

                Dim dirE As DirectoryEntry = New DirectoryEntry("LDAP://" & strADDomain & "/" + strADUserOU, ConfigurationManager.AppSettings("ADUserID"), ConfigurationManager.AppSettings("ADPassword"))
                Dim dirSrc As DirectorySearcher = New DirectorySearcher("(&(objectCategory=organizationalunit)(ou=" + strSite.Trim.ToUpper + "))")

                dirSrc.SearchRoot = dirE
                dirSrc.SearchScope = SearchScope.Subtree

                'build a new dataset to return
                Dim objTable As DataTable = New DataTable
                Dim objC As DataColumn

                'Last Name
                objC = New DataColumn("LastName")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                'First Name
                objC = New DataColumn("FirstName")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                'Middle Initial
                objC = New DataColumn("MiddleInitial")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                'UserID
                objC = New DataColumn("UserID")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                'Site
                objC = New DataColumn("Site")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                'Email
                objC = New DataColumn("EmailAddress")
                objC.DataType = System.Type.GetType("System.String")
                objTable.Columns.Add(objC)

                For Each SrcRes As SearchResult In dirSrc.FindAll()
                    Dim objSRC As DirectorySearcher = New DirectorySearcher("(&(objectCategory=Person)(objectClass=user))")
                    Dim objRow As System.Data.DataRow
                    Dim objProps As System.DirectoryServices.PropertyCollection
                    objSRC.SearchRoot = SrcRes.GetDirectoryEntry
                    objSRC.Sort = New SortOption("sn", SortDirection.Ascending)

                    For Each objChild As SearchResult In objSRC.FindAll()
                        dvUsers.RowFilter = "UserID = '" & objChild.Properties("samaccountname")(0) & "'"
                        If dvUsers.Count = 0 Then
                            objProps = objChild.GetDirectoryEntry.Properties

                            Dim strOU As String

                            If Not IsNothing(objChild.GetDirectoryEntry.Path.ToString.Trim()) Then
                                Dim strPath As String = objChild.GetDirectoryEntry.Path.ToString.Trim()
                                Dim intOU As Integer = strPath.IndexOf("OU=", 0)
                                Dim intComma As Integer = strPath.IndexOf(",", intOU)
                                If intOU > 0 Then
                                    strOU = strPath.Substring(intOU + 3, intComma - intOU - 3)
                                Else
                                    strOU = SessionManager.WorkingSite
                                End If
                            Else
                                strOU = SessionManager.WorkingSite
                            End If

                            If strOU <> "Test Accounts" AndAlso strOU <> "Terminated" And strOU <> "Disabled" Then
                                objRow = objTable.NewRow

                                If Not IsNothing(objProps("sn").Value) Then
                                    objRow("LastName") = objProps("sn").Value.ToString
                                End If

                                If Not IsNothing(objProps("givenname").Value) Then
                                    objRow("FirstName") = objProps("givenname").Value.ToString
                                End If

                                If Not IsNothing(objProps("initials").Value) Then
                                    objRow("MiddleInitial") = objProps("initials").Value.ToString()
                                End If

                                objRow("UserID") = objChild.Properties("samaccountname")(0).ToString.ToUpper

                                objRow("Site") = strOU

                                If Not IsNothing(objProps("userprincipalname").Value) Then
                                    objRow("EmailAddress") = objProps("userprincipalname").Value.ToString
                                End If
                                If Not IsNothing(objProps("givenname").Value) AndAlso objProps("givenname").Value.ToString.Trim.ToUpper <> strSite.ToUpper Then
                                    objTable.Rows.Add(objRow)
                                End If
                            End If
                        End If
                    Next
                Next
                Return objTable
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - GetADUsers", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return Nothing
            Finally
                If cnMasterConnection.State = ConnectionState.Open Then
                    cnMasterConnection.Close()
                End If
            End Try
        End Function
#End Region

    End Class
End Namespace

