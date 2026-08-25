Imports System
Imports System.IO
Imports System.Collections
Imports System.Runtime.Serialization

Namespace WebApp.APlus
    <Serializable()> _
    Public Class TeamStackItem
        Public TeamID As Integer = 0
        Public TeamName As String = ""
        Public OPIName As String = ""
        Public ProgramName As String = ""
        Public LastMenu As String = ""
    End Class
End Namespace
