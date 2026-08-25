#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class TeamOPI

#Region " Select Methods"
        Public Shared Function SelectTeamOPI(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelTeamOPI", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.SelectCommand.Parameters.AddWithValue("@OPI", passOPI)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Sub SelectOPIsByTeam(ByRef ddlList As System.Web.UI.WebControls.DropDownList, ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ddlList.ID, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelOPIsByTeam", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    ddlList.Items.Add(New ListItem(drList.GetString(0), drList.GetString(0)))
                End While
                ddlList.Items.Insert(0, New ListItem("", ""))
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Function GetPresentationName(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelOPIPresentationName", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim retValue As String = ""

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    retValue = drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return retValue
        End Function
        Public Shared Function TeamHasOPIs(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelOPIsByTeam", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                If drList.HasRows Then
                    Return True
                Else
                    Return False
                End If
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectOPIsByTeam(ByVal passTeamID As Integer, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelOPIDataByTeam", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable

            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@TeamID", passTeamID)
                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function GetBenefitUOM(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelExpectedBenefitUOM", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim retValue As String = ""

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    retValue = drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
            Return retValue
        End Function
        Public Shared Function GetUOM(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelOPIUOM", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing
            Dim retValue As String = ""

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@TeamID", passTeamID)
                cmSelect.Parameters.AddWithValue("@OPI", passOPI)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    retValue = drList(0).ToString
                End While
            Catch Exc As Exception
                Throw
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try

            Return retValue
        End Function
#End Region

#Region " Add TeamOPI"
        Public Shared Sub AddTeamOPI(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passOPIShortName As String, _
                                     ByVal passOPIDescription As String, ByVal passOPICategory As String, ByVal passOPIUOM As String, _
                                     ByVal passOPIEntryType As String, ByVal passOPISize As Integer, ByVal passSummaryType As String, _
                                     ByVal passCollectionEvent As String, ByVal passCollectionInterval As String, ByVal passTimeEntryRequired As Boolean, _
                                     ByVal passNegativeEntryAllowed As Boolean, ByVal passCalculateValue As Boolean, _
                                     ByVal passOPIFormula As String, ByVal passBenefitFormula As String, _
                                     ByVal passAttribute1 As String, ByVal passAttribute1EntryType As String, _
                                     ByVal passAttribute1Size As Integer, ByVal passAttribute1Default As Boolean, _
                                     ByVal passAttribute2 As String, ByVal passAttribute2EntryType As String, _
                                     ByVal passAttribute2Size As Integer, ByVal passAttribute2Default As Boolean, _
                                     ByVal passAttribute3 As String, ByVal passAttribute3EntryType As String, _
                                     ByVal passAttribute3Size As Integer, ByVal passAttribute3Default As Boolean, _
                                     ByVal passAttribute4 As String, ByVal passAttribute4EntryType As String, _
                                     ByVal passAttribute4Size As Integer, ByVal passAttribute4Default As Boolean, _
                                     ByVal passAttribute5 As String, ByVal passAttribute5EntryType As String, _
                                     ByVal passAttribute5Size As Integer, ByVal passAttribute5Default As Boolean, _
                                     ByVal passAttribute6 As String, ByVal passAttribute6EntryType As String, _
                                     ByVal passAttribute6Size As Integer, ByVal passAttribute6Default As Boolean, _
                                     ByVal passPrimaryOPI As Boolean, ByVal passResponsibleUser As String, ByVal passDataCollectionOnline As Boolean, _
                                     ByVal passTarget As String, ByVal passHistoric As String, ByVal passStartDate As String, _
                                     ByVal passEndDate As String, ByVal passProjectedBenefit As String, ByVal passExpectedBenefit As String, _
                                     ByVal passUOM As String, ByVal passReportingInterval As String, ByVal passReportingPeriods As Integer, _
                                     ByVal passReportStartDate As String, ByVal passReportEndDate As String, ByVal passCustomYAxisValues As Boolean, _
                                     ByVal passChartYMin As String, ByVal passChartYMax As String, ByVal passChartYLines As String, _
                                     Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, passOPI, passOPIShortName, passOPIDescription, _
                                                                                     passOPICategory, passOPIUOM, passCalculateValue, passOPIFormula, _
                                                                                     passBenefitFormula, passOPIEntryType, passOPISize, passSummaryType, _
                                                                                     passCollectionEvent, passCollectionInterval, passTimeEntryRequired, passNegativeEntryAllowed, _
                                                                                     passAttribute1, passAttribute1EntryType, passAttribute1Size, passAttribute1Default, _
                                                                                     passAttribute2, passAttribute2EntryType, passAttribute2Size, passAttribute2Default, _
                                                                                     passAttribute3, passAttribute3EntryType, passAttribute3Size, passAttribute3Default, _
                                                                                     passAttribute4, passAttribute4EntryType, passAttribute4Size, passAttribute4Default, _
                                                                                     passAttribute5, passAttribute5EntryType, passAttribute5Size, passAttribute5Default, _
                                                                                     passAttribute6, passAttribute6EntryType, passAttribute6Size, passAttribute6Default, _
                                                                                     passPrimaryOPI, passDataCollectionOnline, passResponsibleUser, passTarget, _
                                                                                     passHistoric, passStartDate, _
                                                                                     passEndDate, passProjectedBenefit, passExpectedBenefit, passUOM, _
                                                                                     passReportingPeriods, passReportStartDate, passReportEndDate, passReportingInterval, _
                                                                                     passCustomYAxisValues, passChartYMin, passChartYMax, passChartYLines, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsTeamOPI", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@OPI", passOPI)

                    .Parameters.AddWithValue("@OPIShortName", passOPIShortName)
                    .Parameters.AddWithValue("@OPIDescription", passOPIDescription)
                    .Parameters.AddWithValue("@OPICategory", passOPICategory)
                    .Parameters.AddWithValue("@OPIUOM", passOPIUOM)
                    .Parameters.AddWithValue("@CalculateValue", passCalculateValue)
                    If Not String.IsNullOrEmpty(passOPIFormula.Trim()) Then .Parameters.AddWithValue("@OPIFormula", passOPIFormula)
                    If Not String.IsNullOrEmpty(passBenefitFormula.Trim()) Then .Parameters.AddWithValue("@BenefitFormula", passBenefitFormula)
                    .Parameters.AddWithValue("@OPIEntryType", passOPIEntryType)
                    .Parameters.AddWithValue("@OPISize", passOPISize)
                    .Parameters.AddWithValue("@SummaryType", passSummaryType)
                    .Parameters.AddWithValue("@CollectionEvent", passCollectionEvent)
                    .Parameters.AddWithValue("@CollectionInterval", passCollectionInterval)
                    .Parameters.AddWithValue("@TimeEntryRequired", passTimeEntryRequired)
                    .Parameters.AddWithValue("@NegativeEntryAllowed", passNegativeEntryAllowed)
                    If Not String.IsNullOrEmpty(passAttribute1.Trim()) Then
                        .Parameters.AddWithValue("@Attribute1", passAttribute1)
                        .Parameters.AddWithValue("@Attribute1EntryType", passAttribute1EntryType)
                        .Parameters.AddWithValue("@Attribute1Size", passAttribute1Size)
                        .Parameters.AddWithValue("@Attribute1Default", passAttribute1Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute2.Trim()) Then
                        .Parameters.AddWithValue("@Attribute2", passAttribute2)
                        .Parameters.AddWithValue("@Attribute2EntryType", passAttribute2EntryType)
                        .Parameters.AddWithValue("@Attribute2Size", passAttribute2Size)
                        .Parameters.AddWithValue("@Attribute2Default", passAttribute2Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute3.Trim()) Then
                        .Parameters.AddWithValue("@Attribute3", passAttribute3)
                        .Parameters.AddWithValue("@Attribute3EntryType", passAttribute3EntryType)
                        .Parameters.AddWithValue("@Attribute3Size", passAttribute3Size)
                        .Parameters.AddWithValue("@Attribute3Default", passAttribute3Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute4.Trim()) Then
                        .Parameters.AddWithValue("@Attribute4", passAttribute4)
                        .Parameters.AddWithValue("@Attribute4EntryType", passAttribute4EntryType)
                        .Parameters.AddWithValue("@Attribute4Size", passAttribute4Size)
                        .Parameters.AddWithValue("@Attribute4Default", passAttribute4Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute5.Trim()) Then
                        .Parameters.AddWithValue("@Attribute5", passAttribute5)
                        .Parameters.AddWithValue("@Attribute5EntryType", passAttribute5EntryType)
                        .Parameters.AddWithValue("@Attribute5Size", passAttribute5Size)
                        .Parameters.AddWithValue("@Attribute5Default", passAttribute5Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute6.Trim()) Then
                        .Parameters.AddWithValue("@Attribute6", passAttribute6)
                        .Parameters.AddWithValue("@Attribute6EntryType", passAttribute6EntryType)
                        .Parameters.AddWithValue("@Attribute6Size", passAttribute6Size)
                        .Parameters.AddWithValue("@Attribute6Default", passAttribute6Default)
                    End If
                    .Parameters.AddWithValue("@PrimaryOPI", passPrimaryOPI)
                    .Parameters.AddWithValue("@DataCollectionOnline", passDataCollectionOnline)
                    If Not String.IsNullOrEmpty(passResponsibleUser.Trim()) Then .Parameters.AddWithValue("@ResponsibleUser", passResponsibleUser)
                    .Parameters.AddWithValue("@Target", passTarget)
                    .Parameters.AddWithValue("@Historic", passHistoric)
                    .Parameters.AddWithValue("@HistoricStartDate", passStartDate)
                    .Parameters.AddWithValue("@HistoricEndDate", passEndDate)
                    If Not String.IsNullOrEmpty(passProjectedBenefit.Trim()) Then .Parameters.AddWithValue("@ProjectedBenefit", passProjectedBenefit)
                    .Parameters.AddWithValue("@ExpectedBenefit", passExpectedBenefit)
                    .Parameters.AddWithValue("@ExpectedbenefitUOM", passUOM)
                    If passReportingPeriods > 0 Then .Parameters.AddWithValue("@ReportingPeriods", passReportingPeriods)
                    .Parameters.AddWithValue("@ReportingInterval", passReportingInterval)
                    If Not String.IsNullOrEmpty(passReportStartDate.Trim()) Then .Parameters.AddWithValue("@ReportStartDate", passReportStartDate)
                    If Not String.IsNullOrEmpty(passReportEndDate.Trim()) Then .Parameters.AddWithValue("@ReportEndDate", passReportEndDate)
                    .Parameters.AddWithValue("@CustomYAxisValues", passCustomYAxisValues)
                    If Not String.IsNullOrEmpty(passChartYMin.Trim()) Then .Parameters.AddWithValue("@ChartYMin", passChartYMin)
                    If Not String.IsNullOrEmpty(passChartYMax.Trim()) Then .Parameters.AddWithValue("@ChartYMax", passChartYMax)
                    If Not String.IsNullOrEmpty(passChartYLines.Trim()) Then .Parameters.AddWithValue("@ChartYLines", passChartYLines)

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Update TeamOPI"
        Public Shared Sub UpdateTeamOPI(ByVal passTeamID As Integer, ByVal passOPI As String, ByVal passOPIShortName As String, _
                                        ByVal passOPIDescription As String, ByVal passOPICategory As String, ByVal passOPIUOM As String, _
                                        ByVal passOPIEntryType As String, ByVal passOPISize As Integer, ByVal passSummaryType As String, _
                                        ByVal passCollectionEvent As String, ByVal passCollectionInterval As String, ByVal passTimeEntryRequired As Boolean, _
                                        ByVal passNegativeEntryAllowed As Boolean, ByVal passCalculateValue As Boolean, _
                                        ByVal passOPIFormula As String, ByVal passBenefitFormula As String, _
                                        ByVal passAttribute1 As String, ByVal passAttribute1EntryType As String, _
                                        ByVal passAttribute1Size As Integer, ByVal passAttribute1Default As Boolean, _
                                        ByVal passAttribute2 As String, ByVal passAttribute2EntryType As String, _
                                        ByVal passAttribute2Size As Integer, ByVal passAttribute2Default As Boolean, _
                                        ByVal passAttribute3 As String, ByVal passAttribute3EntryType As String, _
                                        ByVal passAttribute3Size As Integer, ByVal passAttribute3Default As Boolean, _
                                        ByVal passAttribute4 As String, ByVal passAttribute4EntryType As String, _
                                        ByVal passAttribute4Size As Integer, ByVal passAttribute4Default As Boolean, _
                                        ByVal passAttribute5 As String, ByVal passAttribute5EntryType As String, _
                                        ByVal passAttribute5Size As Integer, ByVal passAttribute5Default As Boolean, _
                                        ByVal passAttribute6 As String, ByVal passAttribute6EntryType As String, _
                                        ByVal passAttribute6Size As Integer, ByVal passAttribute6Default As Boolean, _
                                        ByVal passPrimaryOPI As Boolean, ByVal passResponsibleUser As String, ByVal passDataCollectionOnline As Boolean, _
                                        ByVal passTarget As String, ByVal passHistoric As String, ByVal passStartDate As String, _
                                        ByVal passEndDate As String, ByVal passProjectedBenefit As String, ByVal passExpectedBenefit As String, _
                                        ByVal passUOM As String, ByVal passReportingInterval As String, ByVal passReportingPeriods As Integer, _
                                        ByVal passReportStartDate As String, ByVal passReportEndDate As String, ByVal passCustomYAxisValues As Boolean, _
                                        ByVal passChartYMin As String, ByVal passChartYMax As String, ByVal passChartYLines As String, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passTeamID, passOPI, passOPIShortName, passOPIDescription, _
                                                                                     passOPICategory, passOPIUOM, passCalculateValue, passOPIFormula, _
                                                                                     passBenefitFormula, passOPIEntryType, passOPISize, passSummaryType, _
                                                                                     passCollectionEvent, passCollectionInterval, passTimeEntryRequired, passNegativeEntryAllowed, _
                                                                                     passAttribute1, passAttribute1EntryType, passAttribute1Size, passAttribute1Default, _
                                                                                     passAttribute2, passAttribute2EntryType, passAttribute2Size, passAttribute2Default, _
                                                                                     passAttribute3, passAttribute3EntryType, passAttribute3Size, passAttribute3Default, _
                                                                                     passAttribute4, passAttribute4EntryType, passAttribute4Size, passAttribute4Default, _
                                                                                     passAttribute5, passAttribute5EntryType, passAttribute5Size, passAttribute5Default, _
                                                                                     passAttribute6, passAttribute6EntryType, passAttribute6Size, passAttribute6Default, _
                                                                                     passPrimaryOPI, passDataCollectionOnline, passResponsibleUser, passTarget, _
                                                                                     passHistoric, passStartDate, _
                                                                                     passEndDate, passProjectedBenefit, passExpectedBenefit, passUOM, _
                                                                                     passReportingPeriods, passReportStartDate, passReportEndDate, passReportingInterval, _
                                                                                     passCustomYAxisValues, passChartYMin, passChartYMax, passChartYLines, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spUpdTeamOPI", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@OPI", passOPI)

                    .Parameters.AddWithValue("@OPIShortName", passOPIShortName)
                    .Parameters.AddWithValue("@OPIDescription", passOPIDescription)
                    .Parameters.AddWithValue("@OPICategory", passOPICategory)
                    .Parameters.AddWithValue("@OPIUOM", passOPIUOM)
                    .Parameters.AddWithValue("@CalculateValue", passCalculateValue)
                    If Not String.IsNullOrEmpty(passOPIFormula.Trim()) Then .Parameters.AddWithValue("@OPIFormula", passOPIFormula)
                    If Not String.IsNullOrEmpty(passBenefitFormula.Trim()) Then .Parameters.AddWithValue("@BenefitFormula", passBenefitFormula)
                    .Parameters.AddWithValue("@OPIEntryType", passOPIEntryType)
                    .Parameters.AddWithValue("@OPISize", passOPISize)
                    .Parameters.AddWithValue("@SummaryType", passSummaryType)
                    .Parameters.AddWithValue("@CollectionEvent", passCollectionEvent)
                    .Parameters.AddWithValue("@CollectionInterval", passCollectionInterval)
                    .Parameters.AddWithValue("@TimeEntryRequired", passTimeEntryRequired)
                    .Parameters.AddWithValue("@NegativeEntryAllowed", passNegativeEntryAllowed)
                    If Not String.IsNullOrEmpty(passAttribute1.Trim()) Then
                        .Parameters.AddWithValue("@Attribute1", passAttribute1)
                        .Parameters.AddWithValue("@Attribute1EntryType", passAttribute1EntryType)
                        .Parameters.AddWithValue("@Attribute1Size", passAttribute1Size)
                        .Parameters.AddWithValue("@Attribute1Default", passAttribute1Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute2.Trim()) Then
                        .Parameters.AddWithValue("@Attribute2", passAttribute2)
                        .Parameters.AddWithValue("@Attribute2EntryType", passAttribute2EntryType)
                        .Parameters.AddWithValue("@Attribute2Size", passAttribute2Size)
                        .Parameters.AddWithValue("@Attribute2Default", passAttribute2Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute3.Trim()) Then
                        .Parameters.AddWithValue("@Attribute3", passAttribute3)
                        .Parameters.AddWithValue("@Attribute3EntryType", passAttribute3EntryType)
                        .Parameters.AddWithValue("@Attribute3Size", passAttribute3Size)
                        .Parameters.AddWithValue("@Attribute3Default", passAttribute3Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute4.Trim()) Then
                        .Parameters.AddWithValue("@Attribute4", passAttribute4)
                        .Parameters.AddWithValue("@Attribute4EntryType", passAttribute4EntryType)
                        .Parameters.AddWithValue("@Attribute4Size", passAttribute4Size)
                        .Parameters.AddWithValue("@Attribute4Default", passAttribute4Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute5.Trim()) Then
                        .Parameters.AddWithValue("@Attribute5", passAttribute5)
                        .Parameters.AddWithValue("@Attribute5EntryType", passAttribute5EntryType)
                        .Parameters.AddWithValue("@Attribute5Size", passAttribute5Size)
                        .Parameters.AddWithValue("@Attribute5Default", passAttribute5Default)
                    End If
                    If Not String.IsNullOrEmpty(passAttribute6.Trim()) Then
                        .Parameters.AddWithValue("@Attribute6", passAttribute6)
                        .Parameters.AddWithValue("@Attribute6EntryType", passAttribute6EntryType)
                        .Parameters.AddWithValue("@Attribute6Size", passAttribute6Size)
                        .Parameters.AddWithValue("@Attribute6Default", passAttribute6Default)
                    End If
                    .Parameters.AddWithValue("@PrimaryOPI", passPrimaryOPI)
                    .Parameters.AddWithValue("@DataCollectionOnline", passDataCollectionOnline)
                    If Not String.IsNullOrEmpty(passResponsibleUser.Trim()) Then .Parameters.AddWithValue("@ResponsibleUser", passResponsibleUser)
                    .Parameters.AddWithValue("@Target", passTarget)
                    .Parameters.AddWithValue("@Historic", passHistoric)
                    .Parameters.AddWithValue("@HistoricStartDate", passStartDate)
                    .Parameters.AddWithValue("@HistoricEndDate", passEndDate)
                    If Not String.IsNullOrEmpty(passProjectedBenefit.Trim()) Then .Parameters.AddWithValue("@ProjectedBenefit", passProjectedBenefit)
                    .Parameters.AddWithValue("@ExpectedBenefit", passExpectedBenefit)
                    .Parameters.AddWithValue("@ExpectedbenefitUOM", passUOM)
                    If passReportingPeriods > 0 Then .Parameters.AddWithValue("@ReportingPeriods", passReportingPeriods)
                    .Parameters.AddWithValue("@ReportingInterval", passReportingInterval)
                    If Not String.IsNullOrEmpty(passReportStartDate.Trim()) Then .Parameters.AddWithValue("@ReportStartDate", passReportStartDate)
                    If Not String.IsNullOrEmpty(passReportEndDate.Trim()) Then .Parameters.AddWithValue("@ReportEndDate", passReportEndDate)
                    .Parameters.AddWithValue("@CustomYAxisValues", passCustomYAxisValues)
                    If Not String.IsNullOrEmpty(passChartYMin.Trim()) Then .Parameters.AddWithValue("@ChartYMin", passChartYMin)
                    If Not String.IsNullOrEmpty(passChartYMax.Trim()) Then .Parameters.AddWithValue("@ChartYMax", passChartYMax)
                    If Not String.IsNullOrEmpty(passChartYLines.Trim()) Then .Parameters.AddWithValue("@ChartYLines", passChartYLines)

                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete TeamOPI"
        Public Shared Sub DeleteTeamOPI(ByVal passTeamID As Integer, ByVal passOPI As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passTeamID, passOPI, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spDelTeamOPI", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@TeamID", passTeamID)
                    .Parameters.AddWithValue("@OPI", passOPI)
                    .ExecuteNonQuery()
                End With
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace
