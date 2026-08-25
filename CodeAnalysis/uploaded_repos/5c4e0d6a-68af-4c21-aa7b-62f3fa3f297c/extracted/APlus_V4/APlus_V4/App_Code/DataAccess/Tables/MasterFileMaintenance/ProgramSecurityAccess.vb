#Region " Imports"
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
#End Region

Namespace WebApp.APlus.DataAccess.Tables
    Public Class ProgramSecurityAccess

#Region " Select Program Security Access"
        Public Shared Function SelectProgramSecurityAccess(ByVal passProgramName As String, _
                                                           ByVal passUserID As String, _
                                                           Optional ByRef cnMasterConnection As SqlConnection = Nothing) As DataSet
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.DAMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passProgramName, passUserID, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim cnSubConnection As New ApplicationConnection
            Try
                Dim cmSelect As New SqlCommand("spSelProgramSecurityAccess", cnSubConnection.OpenConnection(cnMasterConnection))
                cmSelect.CommandType = CommandType.StoredProcedure
                Dim da As New SqlDataAdapter(cmSelect)
                Dim ds As New DataSet
                cmSelect.Parameters.AddWithValue("@ProgramName", passProgramName)
                cmSelect.Parameters.AddWithValue("@UserID", passUserID)
                da.Fill(ds)
                cmSelect.Dispose()
                Return ds
            Catch Sxc As SqlException
                Throw
            Catch Exc As Exception
                Throw New Exception(Exc.ToString)
            Finally
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " - Update ProgramSecurityAccess"
        '@ -----------------------------------------------------------------------------
        '@ <summary>
        '@ UpdateProgramSecurityAccess
        '@ </summary>
        '@ <param name="ProgramName"></param>
        '@ <param name="UserID"></param>
        '@ <param name="SecurityLevel"></param>
        '@ <param name="cnMasterConnection"></param>
        '@ <returns></returns>
        '@ <remarks>
        '@ </remarks>
        '@ <history>
        '@ 	[cbsmith]	06/14/2004	Created
        '@ </history>
        '@ -----------------------------------------------------------------------------
        Public Shared Function UpdateProgramSecurityAccess(ByVal ProgramName As String, ByVal UserID As String, _
                                        ByVal SecurityLevel As String, _
                                        Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmUpdate As New SqlCommand("spUpdProgramSecurityAccess", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmUpdate
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ProgramName", ProgramName)
                    .Parameters.AddWithValue("@UserID", UserID)
                    .Parameters.AddWithValue("@SecurityLevel", SecurityLevel)
                    myParm = .Parameters.Add("@RETURN_VALUE", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.ReturnValue
                    .ExecuteNonQuery()
                End With
                Return cmUpdate.Parameters("@RETURN_VALUE").Value()
            Finally
                cmUpdate.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " - Delete ProgramSecurityAccess"
        '@ -----------------------------------------------------------------------------
        '@ <summary>
        '@ Delete ProgramSecurityAccess
        '@ </summary>
        '@ <param name="ProgramName"></param>
        '@ <param name="cnMasterConnection"></param>
        '@ <returns>Integer</returns>
        '@ <remarks>
        '@ StoredProcedure = spDelProgramSecurityAccess
        '@ </remarks>
        '@ -----------------------------------------------------------------------------
        Public Shared Function DeleteProgramSecurityAccess(ByVal ProgramName As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing) As Integer
            Dim cnSubConnection As New ApplicationConnection
            Dim myParm As SqlParameter
            Dim cmDelete As New SqlCommand("spDelProgramSecurityAccess", cnSubConnection.OpenConnection(cnMasterConnection))

            Try
                With cmDelete
                    .CommandType = CommandType.StoredProcedure
                    .Parameters.AddWithValue("@ProgramName", ProgramName)
                    myParm = .Parameters.Add("@RETURN_VALUE", SqlDbType.Int)
                    myParm.Direction = ParameterDirection.ReturnValue
                    .ExecuteNonQuery()
                End With
                Return cmDelete.Parameters("@RETURN_VALUE").Value()
            Finally
                cmDelete.Dispose()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Function
#End Region

#Region " Select ProgramSecurityAccessSelectionList and Return Dropdownlist values"
        '@ -----------------------------------------------------------------------------
        '@ <summary>
        '@ Select ProgramSecurityAccess Selection List
        '@ </summary>
        '@ <param name="ddlList"></param>
        '@ <param name="UserID"></param> 
        '@ <param name="cnMasterConnection"></param>
        '@ <remarks>
        '@ StoredProcedure = spSelProgramSecurityAccessSelectionList
        '@ </remarks>
        '@ -----------------------------------------------------------------------------
        Public Shared Sub ProgramSecurityAccessSelectionList(ByRef ddlList As DropDownList, ByVal ProgramName As String, Optional ByRef cnMasterConnection As SqlConnection = Nothing)
            Dim cnSubConnection As New ApplicationConnection
            Dim cmSelect As New SqlCommand("spSelProgramSecurityAccessSelectionList", cnSubConnection.OpenConnection(cnMasterConnection))
            Dim drList As SqlDataReader = Nothing

            Try
                cmSelect.CommandType = CommandType.StoredProcedure
                cmSelect.Parameters.AddWithValue("@ProgramName", ProgramName)
                drList = cmSelect.ExecuteReader(CommandBehavior.CloseConnection)
                While drList.Read()
                    Dim myListItem As ListItem = New ListItem
                    'Loads UserID and UserID Name
                    myListItem.Text = drList.Item(0).ToString.Trim & " - " & drList.Item(1).ToString.Trim
                    'Loads Key value as UserID
                    myListItem.Value = drList.Item(0).ToString.Trim & "|" & drList.Item(1).ToString.Trim
                    ddlList.Items.Add(myListItem)
                End While
            Finally
                cmSelect.Dispose()
                drList.Close()
                cnSubConnection.CloseConnection(cnMasterConnection)
            End Try
        End Sub
#End Region

    End Class
End Namespace

