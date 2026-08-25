#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class KPIMaster

#Region " Select Methods"
        Public Shared Function IsKPIDaily(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim bReturn As Boolean = False

            Try
                Dim objDT As DataTable = SelectKPIMasterByID(passKPIID, cnMasterConnection)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    If Convert.ToBoolean(objDT.Rows(0)("DailyKPI").ToString) Then
                        bReturn = True
                    End If
                End If
            Catch ex As Exception
                Throw
            End Try

            Return bReturn
        End Function
        Public Shared Function IsKPIInterface(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim bReturn As Boolean = False

            Try
                Dim objDT As DataTable = SelectKPIMasterByID(passKPIID, cnMasterConnection)
                If objDT IsNot Nothing AndAlso objDT.Rows.Count = 1 Then
                    If Convert.ToBoolean(objDT.Rows(0)("Interface").ToString) Then
                        bReturn = True
                    End If
                End If
            Catch ex As Exception
                Throw
            End Try

            Return bReturn
        End Function
        Public Shared Function SelectKPIMasterByID(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIMasterByID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIAccess(ByVal passUserID As String, ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIAccess", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPISelectionList(ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passUserID, passSiteID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPISelectionList", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@UserID", passUserID)
                da.SelectCommand.Parameters.AddWithValue("@SiteID", passSiteID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub GetKPIList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelKPIMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListIteam As ListItem = New ListItem
                    myListIteam.Text = drList.GetString(1)
                    myListIteam.Value = drList.GetInt32(0)

                    ddlList.Items.Add(myListIteam)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub GetKPISelectionList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelKPISelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListIteam As ListItem = New ListItem
                    myListIteam.Text = drList.GetString(1)
                    myListIteam.Value = drList.GetInt32(0)

                    ddlList.Items.Add(myListIteam)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub GetKPISelectionList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelKPISelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)

                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListIteam As ListItem = New ListItem
                    myListIteam.Text = drList.GetString(1)
                    myListIteam.Value = drList.GetInt32(0)

                    ddlList.Items.Add(myListIteam)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub GetPrimaryKPISelectionList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passUserID As String, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelKPIPrimarySelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListIteam As ListItem = New ListItem
                    myListIteam.Text = drList.GetString(1)
                    myListIteam.Value = drList.GetInt32(0)

                    ddlList.Items.Add(myListIteam)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub GetKPISiteList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            GetKPISiteList(ddlList, SessionManager.WorkingSiteID, cnMasterConnection)
        End Sub
        Public Shared Sub GetKPISiteList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passSiteID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim strCulture As String = New System.Globalization.CultureInfo(SessionManager.CulturePref).TwoLetterISOLanguageName.ToUpper
            GetKPISiteList(ddlList, passSiteID, strCulture, cnMasterConnection)
        End Sub
        Public Shared Sub GetKPISiteList(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passSiteID As Integer, ByVal passCulture As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelKPISiteMasterList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@SiteID", passSiteID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                Dim objItem As ListItem = Nothing

                While drList.Read()
                    objItem = New ListItem
                    objItem.Value = drList.Item("KPIID")

                    If (passCulture = "EN") Then
                        objItem.Text = drList.Item("SiteAbbrev").ToString.Trim & " - " & drList.Item("KPIOther").ToString.Trim
                    Else
                        objItem.Text = drList.Item("SiteAbbrev").ToString.Trim & " - " & drList.Item("KPI").ToString.Trim
                    End If

                    ddlList.Items.Add(objItem)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function SelectSupportingKPIsByKPIID(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelSupportingKPIs", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@KPIID", passKPIID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIMasterByBusinessAreaID(ByVal passBusinessAreaID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passBusinessAreaID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIMasterByBusinessAreaID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passBusinessAreaID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectKPIMasterByBusinessUnitID(ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passBusinessUnitID.ToString, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelKPIMasterByBusinessUnitID", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                If passBusinessUnitID > 0 Then
                    da.SelectCommand.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                da.Fill(dt)

                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Table Methods"
        Public Shared Function AddKPIMaster(ByVal passKPI As String, ByVal passKPIOther As String, ByVal passDescription As String, ByVal passSortSequence As Integer, _
                                            ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, ByVal passBusinessAreaID As Integer, ByVal passBusinessUnitID As Integer, _
                                            ByVal passTeamCategoryID As Integer, ByVal passUOM As String, ByVal passAreaID As Integer, _
                                            ByVal passSummaryType As String, ByVal passReportingLevelID As Integer, ByVal passResponsibleUserID As String, _
                                            ByVal passTargetUp As Boolean, ByVal passInterface As Boolean, ByVal passInterfaceFormula As String, _
                                            ByVal passDataElements As String, ByVal passScheduleCode As String, ByVal passScheduleTime As String, _
                                            ByVal passNextExecute As String, ByVal passOnDemandExecute As String, ByVal passNoNotifications As Boolean, _
                                            ByVal passActive As Boolean, ByVal passPrimaryKPIID As Integer, ByVal passAutoGenearateAnomalyMonth As Boolean, _
                                            ByVal passAutoGenerateAnomalyYTD As Boolean, ByVal passAnomalyResponsibleUserID As String, ByVal passDailyKPI As Boolean, _
                                            ByVal passDailyInterface As Boolean, ByVal passDailyKPICompare As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPI, passKPIOther, passDescription, passSortSequence, passSiteID, passPillarAbbrev, _
                                                                                     passBusinessAreaID, passBusinessUnitID, passTeamCategoryID, passUOM, _
                                                                                     passAreaID, passSummaryType, passReportingLevelID, passResponsibleUserID, passTargetUp, _
                                                                                     passInterface, passInterfaceFormula, passDataElements, passScheduleCode, passScheduleTime, _
                                                                                     passNextExecute, passOnDemandExecute, passNoNotifications, passActive, passPrimaryKPIID, passAutoGenearateAnomalyMonth, _
                                                                                     passAutoGenerateAnomalyYTD, passAnomalyResponsibleUserID, passDailyKPI, passDailyInterface, passDailyKPICompare, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsKPIMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure
                cmAdd.Parameters.AddWithValue("@KPI", passKPI)
                cmAdd.Parameters.AddWithValue("@KPIOther", passKPIOther)
                If passDescription.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@Description", passDescription.Trim)
                End If
                cmAdd.Parameters.AddWithValue("@SortSequence", passSortSequence)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                If passBusinessAreaID > 0 Then
                    cmAdd.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    cmAdd.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                cmAdd.Parameters.AddWithValue("@TeamCategoryID", passTeamCategoryID)
                cmAdd.Parameters.AddWithValue("@UOM", passUOM)
                cmAdd.Parameters.AddWithValue("@AreaID", passAreaID)
                cmAdd.Parameters.AddWithValue("@SummaryType", passSummaryType)
                cmAdd.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
                cmAdd.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                cmAdd.Parameters.AddWithValue("@TargetUp", passTargetUp)
                cmAdd.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If
                cmAdd.Parameters.AddWithValue("@SupressEmailNotification", passNoNotifications)
                cmAdd.Parameters.AddWithValue("@Active", passActive)
                If passPrimaryKPIID > 0 Then
                    cmAdd.Parameters.AddWithValue("@PrimaryKPIID", passPrimaryKPIID)
                End If
                cmAdd.Parameters.AddWithValue("@AutoGenerateAnomalyMonth", passAutoGenearateAnomalyMonth)
                cmAdd.Parameters.AddWithValue("@AutoGenerateAnomalyYTD", passAutoGenerateAnomalyYTD)
                If passAnomalyResponsibleUserID.Trim.Length > 0 Then
                    cmAdd.Parameters.AddWithValue("@AnomalyResponsibleUserID", passAnomalyResponsibleUserID)
                End If
                cmAdd.Parameters.AddWithValue("@DailyKPI", passDailyKPI)
                cmAdd.Parameters.AddWithValue("@DailyInterface", passDailyInterface)
                cmAdd.Parameters.AddWithValue("@DailyKPICompare", passDailyKPICompare)

                Return cmAdd.ExecuteScalar
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub UpdateKPIMaster(ByVal passKPIID As Integer, ByVal passKPI As String, ByVal passKPIOther As String, ByVal passDescription As String, _
                                          ByVal passSortSequence As Integer, ByVal passSiteID As Integer, ByVal passPillarAbbrev As String, ByVal passBusinessAreaID As Integer, _
                                          ByVal passBusinessUnitID As Integer, ByVal passTeamCategoryID As Integer, ByVal passUOM As String, _
                                          ByVal passAreaID As Integer, ByVal passSummaryType As String, ByVal passReportingLevelID As Integer, _
                                          ByVal passResponsibleUserID As String, ByVal passTargetUp As Boolean, ByVal passInterface As Boolean, _
                                          ByVal passInterfaceFormula As String, ByVal passDataElements As String, ByVal passScheduleCode As String, _
                                          ByVal passScheduleTime As String, ByVal passNextExecute As String, ByVal passOnDemandExecute As String, ByVal passNoNotifications As Boolean, _
                                          ByVal passActive As Boolean, ByVal passPrimaryKPIID As Integer, ByVal passAutoGenearateAnomalyMonth As Boolean, _
                                          ByVal passAutoGenerateAnomalyYTD As Boolean, ByVal passAnomalyResponsibleUserID As String, _
                                          ByVal passDailyKPI As Boolean, ByVal passDailyInterface As Boolean, ByVal passDailyKPICompare As Boolean, _
                                          Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passKPI, passKPIOther, passDescription, passSortSequence, passSiteID, passPillarAbbrev, _
                                                                                     passBusinessAreaID, passBusinessUnitID, passTeamCategoryID, passUOM, _
                                                                                     passAreaID, passSummaryType, passReportingLevelID, passResponsibleUserID, passTargetUp, _
                                                                                     passInterface, passInterfaceFormula, passDataElements, passScheduleCode, passScheduleTime, _
                                                                                     passNextExecute, passOnDemandExecute, passActive, passPrimaryKPIID, passAutoGenearateAnomalyMonth, _
                                                                                     passAutoGenerateAnomalyYTD, passAnomalyResponsibleUserID, passDailyKPI, passDailyInterface, passDailyKPICompare, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@KPI", passKPI)
                cmUpdate.Parameters.AddWithValue("@KPIOther", passKPIOther)
                If passDescription.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@Description", passDescription.Trim)
                End If
                cmUpdate.Parameters.AddWithValue("@SortSequence", passSortSequence)
                cmUpdate.Parameters.AddWithValue("@SiteID", passSiteID)
                cmUpdate.Parameters.AddWithValue("@PillarAbbrev", passPillarAbbrev)
                If passBusinessAreaID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If
                If passBusinessUnitID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If
                cmUpdate.Parameters.AddWithValue("@TeamCategoryID", passTeamCategoryID)
                cmUpdate.Parameters.AddWithValue("@UOM", passUOM)
                cmUpdate.Parameters.AddWithValue("@AreaID", passAreaID)
                cmUpdate.Parameters.AddWithValue("@SummaryType", passSummaryType)
                cmUpdate.Parameters.AddWithValue("@ReportingLevelID", passReportingLevelID)
                cmUpdate.Parameters.AddWithValue("@ResponsibleUserID", passResponsibleUserID)
                cmUpdate.Parameters.AddWithValue("@TargetUp", passTargetUp)
                cmUpdate.Parameters.AddWithValue("@Interface", passInterface)
                If passInterfaceFormula.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@InterfaceFormula", passInterfaceFormula.Trim)
                End If
                If passDataElements.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@DataElements", passDataElements.Trim)
                End If
                If passScheduleCode.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleCode", passScheduleCode)
                End If
                If passScheduleTime.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@ScheduleTime", passScheduleTime)
                End If
                If passNextExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@NextExecution", passNextExecute)
                End If
                If passOnDemandExecute.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)
                End If
                cmUpdate.Parameters.AddWithValue("@SupressEmailNotification", passNoNotifications)
                cmUpdate.Parameters.AddWithValue("@Active", passActive)
                If passPrimaryKPIID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@PrimaryKPIID", passPrimaryKPIID)
                End If
                cmUpdate.Parameters.AddWithValue("@AutoGenerateAnomalyMonth", passAutoGenearateAnomalyMonth)
                cmUpdate.Parameters.AddWithValue("@AutoGenerateAnomalyYTD", passAutoGenerateAnomalyYTD)
                If passAnomalyResponsibleUserID.Trim.Length > 0 Then
                    cmUpdate.Parameters.AddWithValue("@AnomalyResponsibleUserID", passAnomalyResponsibleUserID)
                End If
                cmUpdate.Parameters.AddWithValue("@DailyKPI", passDailyKPI)
                cmUpdate.Parameters.AddWithValue("@DailyInterface", passDailyInterface)
                cmUpdate.Parameters.AddWithValue("@DailyKPICompare", passDailyKPICompare)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIMasterOnDemand(ByVal passKPIID As Integer, ByVal passOnDemandExecute As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passOnDemandExecute, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIMasterOnDemand", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                cmUpdate.Parameters.AddWithValue("@OnDemandExecute", passOnDemandExecute)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIMasterBusinessArea(ByVal passKPIID As Integer, ByVal passBusinessAreaID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passBusinessAreaID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIMasterBusinessArea", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                If passBusinessAreaID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessAreaID", passBusinessAreaID)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateKPIMasterBusinessUnit(ByVal passKPIID As Integer, ByVal passBusinessUnitID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, passBusinessUnitID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdKPIMasterBusinessUnit", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure
                cmUpdate.Parameters.AddWithValue("@KPIID", passKPIID)
                If passBusinessUnitID > 0 Then
                    cmUpdate.Parameters.AddWithValue("@BusinessUnitID", passBusinessUnitID)
                End If

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteKPIMaster(ByVal passKPIID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passKPIID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelKPIMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@KPIID", passKPIID)
                cmDelete.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

