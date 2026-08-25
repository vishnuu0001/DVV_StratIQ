#Region " Imports"
Imports System
Imports System.Collections
Imports System.Collections.Generic
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.DataAccess.Connections
Imports WebApp.APlus.DataAccess.Tables
#End Region

Namespace WebApp.APlus
    Public Class TransactionProcessing

#Region " Compare and Validate Methods"
        Public Shared Function GetDictionaryValues(ByVal passNewValues As Dictionary(Of String, String)) As String
            Dim sb As New StringBuilder
            If passNewValues.Count > 0 Then
                For Each kvp As KeyValuePair(Of String, String) In passNewValues
                    If sb.Length > 0 Then sb.Append(vbCrLf)
                    sb.Append(kvp.Key & ": " & kvp.Value)
                Next
            End If
            If sb.Length > 0 Then
                Return sb.ToString.Trim
            Else
                Return String.Empty
            End If
        End Function

        Public Shared Function CompareDictionaryValues(ByVal passOriginalValues As Dictionary(Of String, String), ByVal passNewValues As Dictionary(Of String, String)) As String
            Dim sb As New StringBuilder
            If passNewValues.Count > 0 Then
                For Each kvp As KeyValuePair(Of String, String) In passNewValues
                    If passOriginalValues.ContainsKey(kvp.Key) Then
                        If passOriginalValues.Item(kvp.Key).ToString.Trim <> kvp.Value.ToString.Trim Then
                            If sb.Length > 0 Then sb.Append(vbCrLf)
                            sb.Append(kvp.Key.ToString() & ": " & kvp.Value.ToString.Trim())
                        End If
                    ElseIf kvp.Value.ToString.Trim.Length > 0 Then
                        If sb.Length > 0 Then sb.Append(vbCrLf)
                        sb.Append(kvp.Key.ToString() & ": " & kvp.Value.ToString.Trim())
                    End If
                Next
            End If

            If sb.Length > 0 Then
                Return sb.ToString.Trim
            Else
                Return String.Empty
            End If
        End Function
#End Region

    End Class
End Namespace