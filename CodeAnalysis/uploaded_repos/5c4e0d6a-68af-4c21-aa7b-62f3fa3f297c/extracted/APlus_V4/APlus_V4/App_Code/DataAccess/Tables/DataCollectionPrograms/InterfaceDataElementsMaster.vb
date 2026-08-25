#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class InterfaceDataElements

#Region " Select Methods"
        Public Shared Function SelectInterfaceDataElement(ByVal passDataElement As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelInterfaceDataElement", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@DataElement", passDataElement)

                da.Fill(dt)
                Return dt
            Catch Exc As Exception
                Throw
            Finally
                da.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
        Public Shared Function SelectValidateDataElements(ByVal passDataElements As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataTable
            Dim cnSubConnection As New ApplicationConnection
            Dim da As New SqlDataAdapter(New SqlCommand("spSelValidateDataElements", cnSubConnection.OpenConnection(cnMasterConnection)))
            Dim dt As New DataTable
            Try
                da.SelectCommand.CommandType = CommandType.StoredProcedure
                da.SelectCommand.Parameters.AddWithValue("@DataElements", passDataElements)

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
        Public Shared Sub InsertDataElement(ByVal passDataElement As String, ByVal passSiteID As Integer, ByVal passSource As String, ByVal passAppSource As String, _
        ByVal passAppKPIKey As String, ByVal passAppMill As String, ByVal passAppIdentKey As String, ByVal passAppIdent As String, ByVal passUOM As String, _
        ByVal passActive As Boolean, ByVal passDailyValue As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsInterfaceDataElementsMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmAdd.CommandType = CommandType.StoredProcedure

                cmAdd.Parameters.AddWithValue("@DataElement", passDataElement)
                cmAdd.Parameters.AddWithValue("@SiteID", passSiteID)
                cmAdd.Parameters.AddWithValue("@Source", passSource)
                cmAdd.Parameters.AddWithValue("@APP_SOURCE", passAppSource)
                cmAdd.Parameters.AddWithValue("@APP_KPIKEY", passAppKPIKey)
                cmAdd.Parameters.AddWithValue("@APP_MILL", passAppMill)
                cmAdd.Parameters.AddWithValue("@APP_IDENTKEY", passAppIdentKey)
                cmAdd.Parameters.AddWithValue("@APP_IDENT", passAppIdent)
                cmAdd.Parameters.AddWithValue("@UOM", passUOM)
                cmAdd.Parameters.AddWithValue("@Active", passActive)
                cmAdd.Parameters.AddWithValue("@DailyValue", passDailyValue)

                cmAdd.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmAdd.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub UpdateDataElement(ByVal passDataElement As String, ByVal passSiteID As Integer, ByVal passSource As String, ByVal passAppSource As String, _
        ByVal passAppKPIKey As String, ByVal passAppMill As String, ByVal passAppIdentKey As String, ByVal passAppIdent As String, ByVal passUOM As String, _
        ByVal passActive As Boolean, ByVal passDailyValue As Boolean, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmUpdate As New SqlCommand("spUpdInterfaceDataElementsMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmUpdate.CommandType = CommandType.StoredProcedure

                cmUpdate.Parameters.AddWithValue("@DataElement", passDataElement)
                cmUpdate.Parameters.AddWithValue("@SiteID", passSiteID)
                cmUpdate.Parameters.AddWithValue("@Source", passSource)
                cmUpdate.Parameters.AddWithValue("@APP_SOURCE", passAppSource)
                cmUpdate.Parameters.AddWithValue("@APP_KPIKEY", passAppKPIKey)
                cmUpdate.Parameters.AddWithValue("@APP_MILL", passAppMill)
                cmUpdate.Parameters.AddWithValue("@APP_IDENTKEY", passAppIdentKey)
                cmUpdate.Parameters.AddWithValue("@APP_IDENT", passAppIdent)
                cmUpdate.Parameters.AddWithValue("@UOM", passUOM)
                cmUpdate.Parameters.AddWithValue("@Active", passActive)
                cmUpdate.Parameters.AddWithValue("@DailyValue", passDailyValue)

                cmUpdate.ExecuteNonQuery()
            Catch Exc As Exception
                Throw
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
        Public Shared Sub DeleteDataElement(ByVal passDataElement As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DATeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelInterfaceDataElementsMaster", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                cmDelete.CommandType = CommandType.StoredProcedure
                cmDelete.Parameters.AddWithValue("@DataElement", passDataElement)
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

