#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class SessionInfo
        Inherits System.Web.UI.Page

        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UIMasterFile) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "SessionInfo", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            BindSessionVariables()
        End Sub

        Private Sub BindSessionVariables()
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
                Dim objRow As TableRow
                Dim objCell As TableCell

                Dim objKey As String

                'First, add application variables
                For Each objKey In Application.Keys
                    objRow = New TableRow

                    objCell = New TableCell
                    objCell.Text = objKey
                    objRow.Cells.Add(objCell)

                    objCell = New TableCell
                    If Not IsNothing(Application.Contents.Item(objKey)) Then
                        objCell.Text = Application.Item(objKey).ToString
                    End If
                    objRow.Cells.Add(objCell)

                    tblSession.Rows.Add(objRow)
                Next

                For Each objKey In SessionManager.GetAllSessionVariables.Keys
                    If objKey <> "__ViewState" Then
                        objRow = New TableRow

                        objCell = New TableCell
                        objCell.Text = objKey
                        objRow.Cells.Add(objCell)

                        objCell = New TableCell
                        If Not IsNothing(Session.Contents.Item(objKey)) Then
                            objCell.Text = Session.Contents.Item(objKey).ToString
                            objRow.Cells.Add(objCell)
                            tblSession.Rows.Add(objRow)

                            Select Case Session.Contents.Item(objKey).GetType.Name
                                Case "Hashtable"
                                    Dim objHashtable As Hashtable = CType(Session.Contents.Item(objKey), Hashtable)
                                    Dim myEnumerator As IDictionaryEnumerator = objHashtable.GetEnumerator()

                                    While myEnumerator.MoveNext
                                        objRow = New TableRow

                                        objCell = New TableCell
                                        objCell.Text = myEnumerator.Key.ToString
                                        objRow.Cells.Add(objCell)

                                        objCell = New TableCell
                                        objCell.Text = myEnumerator.Value
                                        objRow.Cells.Add(objCell)

                                        tblSession.Rows.Add(objRow)
                                    End While
                                Case Else
                                    'don't do anything here
                            End Select
                        Else
                            objRow.Cells.Add(objCell)
                            tblSession.Rows.Add(objRow)
                        End If
                    End If
                Next
            Catch Exc As Exception
                EventTracker.Add("SessionInfo - BindSessionVariables", Exc.ToString(), SessionManager.UserID)
            End Try
        End Sub
    End Class
End Namespace

