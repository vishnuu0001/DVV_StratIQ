#Region "Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus.DataAccess.Custom
    Public Class UserMasterHR

#Region " Add User Master HR"
        Public Shared Sub AddUserMasterHR(ByVal passSite As String, _
                                               ByVal passLastName As String, _
                                               ByVal passFirstname As String, _
                                               ByVal passMiddleName As String, _
                                               ByVal passDeptNumber As String, _
                                               ByVal passTitle As String, _
                                               ByVal passStatus As String, _
                                               Optional ByRef cnMasterConnection As SqlConnection = Nothing, _
                                               Optional ByRef trans As SqlTransaction = Nothing)

            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, _
                                                                                     passSite, _
                                                                                     passLastName, _
                                                                                     passFirstname, _
                                                                                     passMiddleName, _
                                                                                     passDeptNumber, _
                                                                                     passTitle, _
                                                                                     passStatus, _
                                                                                     "", _
                                                                                     "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmAdd As New SqlCommand("spInsUserMasterHR", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                If Not trans Is Nothing Then
                    cmAdd.Transaction = trans
                End If

                With cmAdd
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Site", passSite)
                    .Parameters.AddWithValue("@LastName", passLastName)
                    .Parameters.AddWithValue("@Firstname", passFirstname)
                    .Parameters.AddWithValue("@MiddleName", passMiddleName)
                    .Parameters.AddWithValue("@DeptNumber", passDeptNumber)
                    .Parameters.AddWithValue("@Title", passTitle)
                    .Parameters.AddWithValue("@Status", passStatus)
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

#Region " Insert User Master HR Import"
        Public Shared Sub InsertUserMasterHRImport(ByVal passSite As String, _
                                                   ByRef passDataTable As DataTable)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSite, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnMasterConnection As SqlConnection = ApplicationConnection.OpenMasterConnection
            Dim trans As SqlTransaction = cnMasterConnection.BeginTransaction(IsolationLevel.ReadUncommitted)

            Try
                For Each row As DataRow In passDataTable.Rows
                    AddUserMasterHR(passSite, row("LastName"), row("FirstName"), row("MiddleName"), row("DeptNumber"), row("Title"), row("Status"), cnMasterConnection, trans)
                Next
                trans.Commit()
            Catch Exc As Exception
                trans.Rollback()
                Throw
            Finally
                ApplicationConnection.CloseMasterConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

#Region " Delete User Master HR"
        Public Shared Sub DeleteUserMasterHRBySite(ByVal passSite As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passSite, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Dim cmDelete As New SqlCommand("spDelUserMasterHR", cnSubConnection.OpenConnection(cnMasterConnection))
            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@Site", passSite)
                    .ExecuteNonQuery()
                End With
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
