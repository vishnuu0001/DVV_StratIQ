#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web.Security
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports System.Collections.Generic

#End Region

Namespace WebApp.APlus.UI.Pages
    Partial Class TeamOPIValues2
        Inherits ApplicationBase

#Region " Private Variables"
        Private Shared ReadOnly FormName As String = "Team OPI Data Entry"
        Private Shared ReadOnly ProgramName As String = "TeamOPIValues2"
        Private Shared ReadOnly DBTableName As String = "TeamOPIValues"
        Private _TimeRequired As Boolean = False
        Private _OPIType As String = String.Empty
        Private _OPISize As Integer = 0
        Private _NegativeEntryAllowed As Boolean = False
        Private _CalculateValue As Boolean = False
        Private _OPIFormula As String = String.Empty

        'Attribute information
        Private intAttributes As Integer = 0
        Private _A1 As String = String.Empty
        Private _A1Type As String = String.Empty
        Private _A1Size As Integer = 0
        Private _A1Default As Boolean = False
        Private _A2 As String = String.Empty
        Private _A2Type As String = String.Empty
        Private _A2Size As Integer = 0
        Private _A2Default As Boolean = False
        Private _A3 As String = String.Empty
        Private _A3Type As String = String.Empty
        Private _A3Size As Integer = 0
        Private _A3Default As Boolean = False
        Private _A4 As String = String.Empty
        Private _A4Type As String = String.Empty
        Private _A4Size As Integer = 0
        Private _A4Default As Boolean = False
        Private _A5 As String = String.Empty
        Private _A5Type As String = String.Empty
        Private _A5Size As Integer = 0
        Private _A5Default As Boolean = False
        Private _A6 As String = String.Empty
        Private _A6Type As String = String.Empty
        Private _A6Size As Integer = 0
        Private _A6Default As Boolean = False
#End Region

#Region " Load JavaScripts"
        Private Sub LoadCommonJavaScripts()
            Dim StatusArr() As WebControl = {btnOK, btnCancel, btnExit}
            Dim OverMessageArr() As String = {"OK - Enter", "Cancel", "Exit"}
            Dim OutMessageArr() As String = {"", "", ""}
            Dim strDateFormat As String = SessionManager.DateFormat

            ShowStatusBar(StatusArr, OverMessageArr, OutMessageArr)
            txtOPIValueDateTime_CalendarExtender.Format = strDateFormat

            Master.AddBodyAttribute("onkeydown", "javascript:TrapEscKey(document.getElementById('" + btnCancel.UniqueID + "'),window.event,document.getElementById('" + btnExit.UniqueID + "'))")
            Master.AddBodyAttribute("onkeydown", "javascript:TrapEnterKey(document.getElementById('" + btnOK.UniqueID + "'),window.event)")
        End Sub
        Private Sub LoadEditModeJavaScripts()
            Dim myTabArray(2 + intAttributes) As Object
            Dim TabKeyDownArr(2 + intAttributes) As String

            Select Case intAttributes
                Case 0
                    myTabArray(0) = txtOPIValue
                    myTabArray(1) = txtCost
                    myTabArray(2) = txtExpandNotes

                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(0) = Tab(txtCost, txtExpandNotes, "Neg")
                    Else
                        TabKeyDownArr(0) = Tab(txtCost, txtExpandNotes, "Yes")
                    End If
                    TabKeyDownArr(1) = Tab(txtExpandNotes, txtOPIValue, "Yes")
                    TabKeyDownArr(2) = Tab(txtOPIValue, txtCost, "No")
                Case 1
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtOPIValue
                    myTabArray(2) = txtCost
                    myTabArray(3) = txtExpandNotes

                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtOPIValue, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtOPIValue, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtOPIValue, txtExpandNotes, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(1) = Tab(txtCost, txtAttribute1, "Neg")
                    Else
                        TabKeyDownArr(1) = Tab(txtCost, txtAttribute1, "Yes")
                    End If
                    TabKeyDownArr(2) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(3) = Tab(txtAttribute1, txtCost, "No")
                Case 2
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtAttribute2
                    myTabArray(2) = txtOPIValue
                    myTabArray(3) = txtCost
                    myTabArray(4) = txtExpandNotes


                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "No")
                    End Select
                    Select Case _A2Type
                        Case "D"
                            TabKeyDownArr(1) = Tab(txtOPIValue, txtAttribute1, "Neg")
                        Case "N"
                            TabKeyDownArr(1) = Tab(txtOPIValue, txtAttribute1, "NegInt")
                        Case Else
                            TabKeyDownArr(1) = Tab(txtOPIValue, txtAttribute1, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(2) = Tab(txtCost, txtAttribute2, "Neg")
                    Else
                        TabKeyDownArr(2) = Tab(txtCost, txtAttribute2, "Yes")
                    End If
                    TabKeyDownArr(3) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(4) = Tab(txtAttribute1, txtCost, "No")
                Case 3
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtAttribute2
                    myTabArray(2) = txtAttribute3
                    myTabArray(3) = txtOPIValue
                    myTabArray(4) = txtCost
                    myTabArray(5) = txtExpandNotes

                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "No")
                    End Select
                    Select Case _A2Type
                        Case "D"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "Neg")
                        Case "N"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                        Case Else
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "No")
                    End Select
                    Select Case _A3Type
                        Case "D"
                            TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute2, "Neg")
                        Case "N"
                            TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute2, "NegInt")
                        Case Else
                            TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute2, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(3) = Tab(txtCost, txtAttribute3, "Neg")
                    Else
                        TabKeyDownArr(3) = Tab(txtCost, txtAttribute3, "Yes")
                    End If
                    TabKeyDownArr(4) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(5) = Tab(txtAttribute1, txtCost, "No")
                Case 4
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtAttribute2
                    myTabArray(2) = txtAttribute3
                    myTabArray(3) = txtAttribute4
                    myTabArray(4) = txtOPIValue
                    myTabArray(5) = txtCost
                    myTabArray(6) = txtExpandNotes

                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "No")
                    End Select
                    Select Case _A2Type
                        Case "D"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "Neg")
                        Case "N"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                        Case Else
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "No")
                    End Select
                    Select Case _A3Type
                        Case "D"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "Neg")
                        Case "N"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                        Case Else
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "No")
                    End Select
                    Select Case _A4Type
                        Case "D"
                            TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute3, "Neg")
                        Case "N"
                            TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute3, "NegInt")
                        Case Else
                            TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute3, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(4) = Tab(txtCost, txtAttribute4, "Neg")
                    Else
                        TabKeyDownArr(4) = Tab(txtCost, txtAttribute4, "Yes")
                    End If
                    TabKeyDownArr(5) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(6) = Tab(txtAttribute1, txtCost, "No")
                Case 5
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtAttribute2
                    myTabArray(2) = txtAttribute3
                    myTabArray(3) = txtAttribute4
                    myTabArray(4) = txtAttribute5
                    myTabArray(5) = txtOPIValue
                    myTabArray(6) = txtCost
                    myTabArray(7) = txtExpandNotes

                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "No")
                    End Select
                    Select Case _A2Type
                        Case "D"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "Neg")
                        Case "N"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                        Case Else
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "No")
                    End Select
                    Select Case _A3Type
                        Case "D"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "Neg")
                        Case "N"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                        Case Else
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "No")
                    End Select
                    Select Case _A4Type
                        Case "D"
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "Neg")
                        Case "N"
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "NegInt")
                        Case Else
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "No")
                    End Select
                    Select Case _A5Type
                        Case "D"
                            TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute4, "Neg")
                        Case "N"
                            TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute4, "NegInt")
                        Case Else
                            TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute4, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(5) = Tab(txtCost, txtAttribute5, "Neg")
                    Else
                        TabKeyDownArr(5) = Tab(txtCost, txtAttribute5, "Yes")
                    End If
                    TabKeyDownArr(6) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(7) = Tab(txtAttribute1, txtCost, "No")
                Case 6
                    myTabArray(0) = txtAttribute1
                    myTabArray(1) = txtAttribute2
                    myTabArray(2) = txtAttribute3
                    myTabArray(3) = txtAttribute4
                    myTabArray(4) = txtAttribute5
                    myTabArray(5) = txtAttribute6
                    myTabArray(6) = txtOPIValue
                    myTabArray(7) = txtCost
                    myTabArray(8) = txtExpandNotes

                    Select Case _A1Type
                        Case "D"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "Neg")
                        Case "N"
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "NegInt")
                        Case Else
                            TabKeyDownArr(0) = Tab(txtAttribute2, txtExpandNotes, "No")
                    End Select
                    Select Case _A2Type
                        Case "D"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "Neg")
                        Case "N"
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                        Case Else
                            TabKeyDownArr(1) = Tab(txtAttribute3, txtAttribute1, "No")
                    End Select
                    Select Case _A3Type
                        Case "D"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "Neg")
                        Case "N"
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                        Case Else
                            TabKeyDownArr(2) = Tab(txtAttribute4, txtAttribute2, "No")
                    End Select
                    Select Case _A4Type
                        Case "D"
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "Neg")
                        Case "N"
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "NegInt")
                        Case Else
                            TabKeyDownArr(3) = Tab(txtAttribute5, txtAttribute3, "No")
                    End Select
                    Select Case _A5Type
                        Case "D"
                            TabKeyDownArr(4) = Tab(txtAttribute6, txtAttribute4, "Neg")
                        Case "N"
                            TabKeyDownArr(4) = Tab(txtAttribute6, txtAttribute4, "NegInt")
                        Case Else
                            TabKeyDownArr(4) = Tab(txtAttribute6, txtAttribute4, "No")
                    End Select
                    Select Case _A6Type
                        Case "D"
                            TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute5, "Neg")
                        Case "N"
                            TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute5, "NegInt")
                        Case Else
                            TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute5, "No")
                    End Select
                    If _NegativeEntryAllowed Then
                        TabKeyDownArr(6) = Tab(txtCost, txtAttribute6, "Neg")
                    Else
                        TabKeyDownArr(6) = Tab(txtCost, txtAttribute6, "Yes")
                    End If
                    TabKeyDownArr(7) = Tab(txtExpandNotes, txtOPIValue, "No")
                    TabKeyDownArr(8) = Tab(txtAttribute1, txtCost, "No")
            End Select

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)

            'add javascript to tab FROM the OK button
            Dim myTabArray2() As Object = {btnOK}
            Dim TabKeyDownArr2(1) As String
            If intAttributes > 0 Then
                TabKeyDownArr2(0) = Tab(txtAttribute1, txtAttribute1, "No")
            Else
                If _CalculateValue Then
                    TabKeyDownArr2(0) = Tab(txtCost, txtCost, "No")
                Else
                    TabKeyDownArr2(0) = Tab(txtOPIValue, txtOPIValue, "No")
                End If
            End If

            AssociateTabJavascriptEventHandler(myTabArray2, TabKeyDownArr2)
        End Sub
        Private Sub LoadAddModeJavaScripts()
            Dim iControls As Integer = 3

            If _TimeRequired Then
                iControls = 4
            End If

            Dim myTabArray(iControls + intAttributes) As Object
            Dim TabKeyDownArr(iControls + intAttributes) As String

            myTabArray(0) = txtOPIValueDateTime

            myTabArray(iControls + intAttributes - 2) = txtOPIValue
            myTabArray(iControls + intAttributes - 1) = txtCost
            myTabArray(iControls + intAttributes) = txtExpandNotes

            TabKeyDownArr(iControls + intAttributes - 1) = Tab(txtExpandNotes, txtOPIValue, "No")
            TabKeyDownArr(iControls + intAttributes) = Tab(txtOPIValueDateTime, txtCost, "No")

            Select Case intAttributes
                Case 0
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtOPIValue, txtOPIValueDateTime, "No")
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(2) = Tab(txtCost, txtOPIValueTime, "Neg")
                        Else
                            TabKeyDownArr(2) = Tab(txtCost, txtOPIValueTime, "Yes")
                        End If
                    Else
                        TabKeyDownArr(0) = Tab(txtOPIValue, txtExpandNotes, "No")
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(1) = Tab(txtCost, txtOPIValueDateTime, "Neg")
                        Else
                            TabKeyDownArr(1) = Tab(txtCost, txtOPIValueDateTime, "Yes")
                        End If
                    End If
                Case 1
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtOPIValueTime, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(3) = Tab(txtCost, txtAttribute1, "Neg")
                        Else
                            TabKeyDownArr(3) = Tab(txtCost, txtAttribute1, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtOPIValue, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtOPIValue, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtOPIValue, txtOPIValueDateTime, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(2) = Tab(txtCost, txtAttribute1, "Neg")
                        Else
                            TabKeyDownArr(2) = Tab(txtCost, txtAttribute1, "Yes")
                        End If
                    End If
                Case 2
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1
                        myTabArray(3) = txtAttribute2

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute1, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(4) = Tab(txtCost, txtAttribute2, "Neg")
                        Else
                            TabKeyDownArr(4) = Tab(txtCost, txtAttribute2, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1
                        myTabArray(2) = txtAttribute2

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtOPIValue, txtAttribute1, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(3) = Tab(txtCost, txtAttribute2, "Neg")
                        Else
                            TabKeyDownArr(3) = Tab(txtCost, txtAttribute2, "Yes")
                        End If
                    End If
                Case 3
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1
                        myTabArray(3) = txtAttribute2
                        myTabArray(4) = txtAttribute3

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute2, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(5) = Tab(txtCost, txtAttribute3, "Neg")
                        Else
                            TabKeyDownArr(5) = Tab(txtCost, txtAttribute3, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1
                        myTabArray(2) = txtAttribute2
                        myTabArray(3) = txtAttribute3

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtOPIValue, txtAttribute2, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(4) = Tab(txtCost, txtAttribute3, "Neg")
                        Else
                            TabKeyDownArr(4) = Tab(txtCost, txtAttribute3, "Yes")
                        End If
                    End If
                Case 4
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1
                        myTabArray(3) = txtAttribute2
                        myTabArray(4) = txtAttribute3
                        myTabArray(5) = txtAttribute4

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute3, "Neg")
                            Case "N"
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute3, "NegInt")
                            Case Else
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute3, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(6) = Tab(txtCost, txtAttribute4, "Neg")
                        Else
                            TabKeyDownArr(6) = Tab(txtCost, txtAttribute4, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1
                        myTabArray(2) = txtAttribute2
                        myTabArray(3) = txtAttribute3
                        myTabArray(4) = txtAttribute4

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute3, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute3, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtOPIValue, txtAttribute3, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(5) = Tab(txtCost, txtAttribute4, "Neg")
                        Else
                            TabKeyDownArr(5) = Tab(txtCost, txtAttribute4, "Yes")
                        End If
                    End If
                Case 5
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1
                        myTabArray(3) = txtAttribute2
                        myTabArray(4) = txtAttribute3
                        myTabArray(5) = txtAttribute4
                        myTabArray(6) = txtAttribute5

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "Neg")
                            Case "N"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "NegInt")
                            Case Else
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "No")
                        End Select
                        TabKeyDownArr(5) = Tab(txtAttribute5, txtAttribute3, "No")
                        Select Case _A5Type
                            Case "D"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "Neg")
                            Case "N"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "NegInt")
                            Case Else
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute4, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(7) = Tab(txtCost, txtAttribute5, "Neg")
                        Else
                            TabKeyDownArr(7) = Tab(txtCost, txtAttribute5, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1
                        myTabArray(2) = txtAttribute2
                        myTabArray(3) = txtAttribute3
                        myTabArray(4) = txtAttribute4
                        myTabArray(5) = txtAttribute5

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "No")
                        End Select
                        Select Case _A5Type
                            Case "D"
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute4, "Neg")
                            Case "N"
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute4, "NegInt")
                            Case Else
                                TabKeyDownArr(5) = Tab(txtOPIValue, txtAttribute4, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(6) = Tab(txtCost, txtAttribute5, "Neg")
                        Else
                            TabKeyDownArr(6) = Tab(txtCost, txtAttribute5, "Yes")
                        End If
                    End If
                Case 6
                    If _TimeRequired Then
                        myTabArray(1) = txtOPIValueTime
                        myTabArray(2) = txtAttribute1
                        myTabArray(3) = txtAttribute2
                        myTabArray(4) = txtAttribute3
                        myTabArray(5) = txtAttribute4
                        myTabArray(6) = txtAttribute5
                        myTabArray(7) = txtAttribute6

                        TabKeyDownArr(0) = Tab(txtOPIValueTime, txtExpandNotes, "No")
                        TabKeyDownArr(1) = Tab(txtAttribute1, txtOPIValueDateTime, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute2, txtOPIValueTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(5) = Tab(txtAttribute5, txtAttribute3, "Neg")
                            Case "N"
                                TabKeyDownArr(5) = Tab(txtAttribute5, txtAttribute3, "NegInt")
                            Case Else
                                TabKeyDownArr(5) = Tab(txtAttribute5, txtAttribute3, "No")
                        End Select
                        Select Case _A5Type
                            Case "D"
                                TabKeyDownArr(6) = Tab(txtAttribute6, txtAttribute4, "Neg")
                            Case "N"
                                TabKeyDownArr(6) = Tab(txtAttribute6, txtAttribute4, "NegInt")
                            Case Else
                                TabKeyDownArr(6) = Tab(txtAttribute6, txtAttribute4, "No")
                        End Select
                        Select Case _A6Type
                            Case "D"
                                TabKeyDownArr(7) = Tab(txtOPIValue, txtAttribute5, "Neg")
                            Case "N"
                                TabKeyDownArr(7) = Tab(txtOPIValue, txtAttribute5, "NegInt")
                            Case Else
                                TabKeyDownArr(7) = Tab(txtOPIValue, txtAttribute5, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(8) = Tab(txtCost, txtAttribute6, "Neg")
                        Else
                            TabKeyDownArr(8) = Tab(txtCost, txtAttribute6, "Yes")
                        End If
                    Else
                        myTabArray(1) = txtAttribute1
                        myTabArray(2) = txtAttribute2
                        myTabArray(3) = txtAttribute3
                        myTabArray(4) = txtAttribute4
                        myTabArray(5) = txtAttribute5
                        myTabArray(6) = txtAttribute6

                        TabKeyDownArr(0) = Tab(txtAttribute1, txtExpandNotes, "No")
                        Select Case _A1Type
                            Case "D"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "Neg")
                            Case "N"
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "NegInt")
                            Case Else
                                TabKeyDownArr(1) = Tab(txtAttribute2, txtOPIValueDateTime, "No")
                        End Select
                        Select Case _A2Type
                            Case "D"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "Neg")
                            Case "N"
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "NegInt")
                            Case Else
                                TabKeyDownArr(2) = Tab(txtAttribute3, txtAttribute1, "No")
                        End Select
                        Select Case _A3Type
                            Case "D"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "Neg")
                            Case "N"
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "NegInt")
                            Case Else
                                TabKeyDownArr(3) = Tab(txtAttribute4, txtAttribute2, "No")
                        End Select
                        Select Case _A4Type
                            Case "D"
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "Neg")
                            Case "N"
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "NegInt")
                            Case Else
                                TabKeyDownArr(4) = Tab(txtAttribute5, txtAttribute3, "No")
                        End Select
                        Select Case _A5Type
                            Case "D"
                                TabKeyDownArr(5) = Tab(txtAttribute6, txtAttribute4, "Neg")
                            Case "N"
                                TabKeyDownArr(5) = Tab(txtAttribute6, txtAttribute4, "NegInt")
                            Case Else
                                TabKeyDownArr(5) = Tab(txtAttribute6, txtAttribute4, "No")
                        End Select
                        Select Case _A6Type
                            Case "D"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute5, "Neg")
                            Case "N"
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute5, "NegInt")
                            Case Else
                                TabKeyDownArr(6) = Tab(txtOPIValue, txtAttribute5, "No")
                        End Select
                        If _NegativeEntryAllowed Then
                            TabKeyDownArr(7) = Tab(txtCost, txtAttribute6, "Neg")
                        Else
                            TabKeyDownArr(7) = Tab(txtCost, txtAttribute6, "Yes")
                        End If
                    End If
            End Select

            AssociateTabJavascriptEventHandler(myTabArray, TabKeyDownArr)

            'add javascript to tab FROM the OK button
            Dim myTabArray2() As Object = {btnOK}
            Dim TabKeyDownArr2() As String = {Tab(txtOPIValueDateTime, txtOPIValueDateTime, "No")}

            AssociateTabJavascriptEventHandler(myTabArray2, TabKeyDownArr2)
        End Sub
#End Region

#Region " Load Culture Translations"
        Private Sub LoadCultureTranslations()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                lblOPIDescription.Text = GetTranslationString("opidescription", lblOPIDescription.Text.Replace(":", "")) & ":"
                lblDate.Text = GetTranslationString("date", lblDate.Text.Replace(":", "")) & ":"
                lblTime.Text = GetTranslationString("time", lblTime.Text.Replace(":", "")) & ":"
                lblOPIValue.Text = GetTranslationString("opi value", lblOPIValue.Text.Replace(":", "")) & ":"
                lblCost.Text = GetTranslationString("cost", lblCost.Text.Replace(":", "")) & ":"
                lblNotes.Text = GetTranslationString("notes", lblNotes.Text.Replace(":", "")) & ":"
                lblMaintenanceUserID.Text = GetTranslationString("maintuserid", lblMaintenanceUserID.Text.Replace(":", "")) & ":"
                lblMaintenanceDate.Text = GetTranslationString("maintdate", lblMaintenanceDate.Text.Replace(":", "")) & ":"
                btnOK.Text = GetTranslationString("ok", btnOK.Text)
                btnCancel.Text = GetTranslationString("cancel", btnCancel.Text)
                btnExit.Text = GetTranslationString("exit", btnExit.Text)

            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadCultureTranslations", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
#End Region

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, ProgramName, "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If Not Page.IsPostBack Then
                LoadCultureTranslations()
            End If

            Master.HeaderMessage = GetTranslationString(FormName, FormName)
            Master.IconImage = Request.ApplicationPath + "/images/TeamOPI.gif"
            ClientScript.RegisterClientScriptInclude("EditScript", "../../../Scripts/" & SessionManager.CulturePref & "/DataEntry.js")

            LoadCommonJavaScripts()
            LoadPageValidation()

            If Not Page.IsPostBack Then
                Select Case SessionManager.TeamOPIValueMode.ToString
                    Case "ViewRow"
                        pnlExit.Visible = True
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case "DeleteRow"
                        LoadSelectedRecord()
                        UnEnableRecords()
                        btnOK.CausesValidation = False
                        btnOK.Attributes.Add("onclick", "return confirm('Click OK to Delete this OPI Entry.');")
                        TransactionHistory1.LockControl = True
                    Case "AddRow"
                        TransactionHistory1.Visible = False
                        LoadAddModeJavaScripts()
                        imgOPIValueDateTime.Visible = True
                        Dim iOffset As Integer = SiteMaster.GetSiteHourOffset(SessionManager.WorkingSiteID)
                        Dim dtHolder As DateTime = Now.AddHours(iOffset)
                        txtOPIValueDateTime.Text = dtHolder.ToShortDateString
                        If _TimeRequired Then
                            txtOPIValueTime.Text = dtHolder.ToString("HH:mm")
                        End If
                        txtCost.Text = "0"
                        pnlMaint.Visible = False
                        SetAttributeDefaults()
                        If _CalculateValue Then
                            txtOPIValue.CssClass = "Textbox_Display"
                        End If
                        txtOPIValueDateTime.Focus()
                    Case "EditRow"
                        LoadEditModeJavaScripts()
                        LoadSelectedRecord()
                        UnEnableRecords()
                    Case Else
                        Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
                End Select
            End If

            If _CalculateValue Then
                reqOPIValue.Enabled = False
                reqValidOPIValue.Enabled = False
                txtOPIValue.ReadOnly = True
            End If
        End Sub
        Private Sub btnExit_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExit.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPIDate)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute4)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute5)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute6)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIValueMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
        End Sub
        Private Sub btnCancel_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCancel.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If btnCancel.ToolTip = "Confirm" Then
                btnCancel.ToolTip = ""
                btnOK.ToolTip = ""
                btnOK.Text = "OK"

                ProcessConfirm(False)

                If SessionManager.TeamOPIValueMode = "EditRow" Then
                    If intAttributes = 0 Then
                        If _CalculateValue Then
                            txtCost.Focus()
                        Else
                            txtOPIValue.Focus()
                        End If
                    Else
                        txtAttribute1.Focus()
                    End If
                Else
                    txtOPIValueDateTime.Focus()
                End If

                Return
            End If

            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPIDate)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute1)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute2)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute3)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute4)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute5)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute6)
            SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIValueMode)
            Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
        End Sub
        Private Sub btnOK_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOK.Click
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, "", "")
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim blnSuccess As Boolean

            If SessionManager.TeamOPIValueMode = "DeleteRow" Then
                blnSuccess = DeleteTeamOPIValue()
            Else
                If SessionManager.TeamOPIValueMode = "AddRow" Then
                    If Not ValidateDateTime() Then
                        Return
                    End If
                End If

                If _CalculateValue Then
                    If btnOK.ToolTip <> "Confirm" Then
                        btnOK.ToolTip = "Confirm"
                        btnOK.Text = "Confirm"
                        btnCancel.ToolTip = "Confirm"

                        ProcessConfirm(True)

                        If Not CalculateOPI() Then
                            btnCancel_Click(Nothing, Nothing)
                        End If

                        btnOK.Focus()

                        Return
                    End If
                End If

                'if we get here with no OPI Value, then the user is clicking the button too fast
                If txtOPIValue.Text.Trim.Length = 0 Then
                    CalculateOPI()
                    btnOK.Focus()

                    Return
                End If

                If SessionManager.TeamOPIValueMode = "AddRow" Then
                    blnSuccess = InsertTeamOPIValue()
                ElseIf SessionManager.TeamOPIValueMode = "EditRow" Then
                    blnSuccess = UpdateTeamOPIValue()
                End If
            End If

            If blnSuccess Then
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.SelectedOPIDate)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute1)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute2)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute3)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute4)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute5)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.Attribute6)
                SessionManager.RemoveSessionVariable(SessionManager.SessionVariables.TeamOPIValueMode)
                Response.Redirect(Context.Request.ApplicationPath & Path.AltDirectorySeparatorChar & ProgramSecurity.GetProgramURL("TeamOPIValues1"), False)
            End If
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub ProcessConfirm(ByVal bConfirm As Boolean)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, bConfirm)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            If bConfirm Then
                txtOPIValueDateTime.ReadOnly = True
                txtOPIValueDateTime.CssClass = "Textbox_Display"
                imgOPIValueDateTime.Visible = False

                If _TimeRequired Then
                    txtOPIValueTime.ReadOnly = True
                    txtOPIValueTime.CssClass = "Textbox_Display"
                End If

                txtAttribute1.ReadOnly = True
                txtAttribute1.CssClass = "Textbox_Display"
                txtAttribute2.ReadOnly = True
                txtAttribute2.CssClass = "Textbox_Display"
                txtAttribute3.ReadOnly = True
                txtAttribute3.CssClass = "Textbox_Display"
                txtAttribute4.ReadOnly = True
                txtAttribute4.CssClass = "Textbox_Display"
                txtAttribute5.ReadOnly = True
                txtAttribute5.CssClass = "Textbox_Display"
                txtAttribute6.ReadOnly = True
                txtAttribute6.CssClass = "Textbox_Display"
                txtOPIValue.ReadOnly = True
                txtOPIValue.CssClass = "Textbox_Display"
                txtCost.ReadOnly = True
                txtCost.CssClass = "Textbox_Display"
                txtExpandNotes.ReadOnly = True
                txtExpandNotes.CssClass = "Textbox_Display"
            Else
                txtAttribute1.ReadOnly = False
                txtAttribute1.CssClass = "Textbox_Entry"
                txtAttribute2.ReadOnly = False
                txtAttribute2.CssClass = "Textbox_Entry"
                txtAttribute3.ReadOnly = False
                txtAttribute3.CssClass = "Textbox_Entry"
                txtAttribute4.ReadOnly = False
                txtAttribute4.CssClass = "Textbox_Entry"
                txtAttribute5.ReadOnly = False
                txtAttribute5.CssClass = "Textbox_Entry"
                txtAttribute6.ReadOnly = False
                txtAttribute6.CssClass = "Textbox_Entry"
                txtOPIValue.ReadOnly = False
                If _CalculateValue Then
                    txtOPIValue.CssClass = "Textbox_Display"
                Else
                    txtOPIValue.CssClass = "Textbox_Entry"
                End If
                txtCost.ReadOnly = False
                txtCost.CssClass = "Textbox_Entry"
                txtExpandNotes.ReadOnly = False
                txtExpandNotes.CssClass = "Textbox_Entry"

                'only show cal image if add
                If SessionManager.TeamOPIValueMode = "AddRow" Then
                    txtOPIValueDateTime.ReadOnly = False
                    txtOPIValueDateTime.CssClass = "Textbox_Entry"
                    imgOPIValueDateTime.Visible = True
                End If
            End If
        End Sub
        Private Function CalculateOPI() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dValue As Double
                'first, create the OPI calculation
                'sub opi
                If InStr(_OPIFormula, "[Attribute1]") > 0 Then
                    If txtAttribute1.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute1]", RegionalConversion.FormatSQLSingle(txtAttribute1.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If
                If InStr(_OPIFormula, "[Attribute2]") > 0 Then
                    If txtAttribute2.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute2]", RegionalConversion.FormatSQLSingle(txtAttribute2.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If
                If InStr(_OPIFormula, "[Attribute3]") > 0 Then
                    If txtAttribute3.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute3]", RegionalConversion.FormatSQLSingle(txtAttribute3.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If
                If InStr(_OPIFormula, "[Attribute4]") > 0 Then
                    If txtAttribute4.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute4]", RegionalConversion.FormatSQLSingle(txtAttribute4.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If
                If InStr(_OPIFormula, "[Attribute5]") > 0 Then
                    If txtAttribute5.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute5]", RegionalConversion.FormatSQLSingle(txtAttribute5.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If
                If InStr(_OPIFormula, "[Attribute6]") > 0 Then
                    If txtAttribute6.Text.Trim.Length > 0 Then
                        _OPIFormula = _OPIFormula.Replace("[Attribute6]", RegionalConversion.FormatSQLSingle(txtAttribute6.Text))
                    Else
                        txtOPIValue.Text = ""
                        Return False
                    End If
                End If

                dValue = WebApp.APlus.UI.CustomControls.Evaluator.EvaluateToDouble(_OPIFormula)
                Dim strHolder As String

                Select Case _OPIType
                    Case "D"
                        'some cultures use a comma as the decimal seperator
                        'this must be set back to decimal
                        strHolder = String.Format("{0:F" + _OPISize.ToString + "}", dValue)
                        If Not IsNumeric(strHolder) Then
                            Master.DisplayError(GetTranslationString("invalidopiformula", "OPI Formula does not evaluate to a valid numeric value"))
                            Return False
                        End If
                        txtOPIValue.Text = strHolder
                    Case "N"
                        If Not IsNumeric(String.Format("{0:F0}", dValue)) Then
                            Master.DisplayError(GetTranslationString("invalidopiformula", "OPI Formula does not evaluate to a valid numeric value"))
                            Return False
                        End If
                        txtOPIValue.Text = String.Format("{0:F0}", dValue)
                End Select
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - CalculateOPI", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
                Return False
            End Try
        End Function
        Private Sub LoadPageValidation()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim dsHolder As DataTable = TeamOPI.SelectTeamOPI(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)
                Dim dr As DataRow = dsHolder.Rows(0)

                txtOPIUOM.Text = dr("OPIUOM").ToString
                txtExpandOPIDescription.Text = dr("OPIDescription").ToString

                _OPIType = dr("OPIEntryType")
                _OPISize = dr("OPISize")
                _TimeRequired = dr("TimeEntryRequired").ToString
                _NegativeEntryAllowed = dr("NegativeEntryAllowed").ToString
                _CalculateValue = dr("CalculateValue").ToString
                _OPIFormula = dr("OPIFormula").ToString

                If _TimeRequired Then
                    pnlTime.Visible = True
                    reqValueTime.Enabled = True
                Else
                    pnlTime.Visible = False
                End If

                If (IsDBNull(dr("Attribute1"))) = False Then
                    _A1 = dr("Attribute1")
                    _A1Type = dr("Attribute1EntryType")
                    _A1Size = dr("Attribute1Size")
                    If Not (dr("Attribute1Default") Is DBNull.Value) Then
                        _A1Default = dr("Attribute1Default")
                    End If
                End If
                If (IsDBNull(dr("Attribute2"))) = False Then
                    _A2 = dr("Attribute2")
                    _A2Type = dr("Attribute2EntryType")
                    _A2Size = dr("Attribute2Size")
                    If Not (dr("Attribute2Default") Is DBNull.Value) Then
                        _A2Default = dr("Attribute2Default")
                    End If
                End If
                If (IsDBNull(dr("Attribute3"))) = False Then
                    _A3 = dr("Attribute3")
                    _A3Type = dr("Attribute3EntryType")
                    _A3Size = dr("Attribute3Size")
                    If Not (dr("Attribute3Default") Is DBNull.Value) Then
                        _A3Default = dr("Attribute3Default")
                    End If
                End If
                If (IsDBNull(dr("Attribute4"))) = False Then
                    _A4 = dr("Attribute4")
                    _A4Type = dr("Attribute4EntryType")
                    _A4Size = dr("Attribute4Size")
                    If Not (dr("Attribute4Default") Is DBNull.Value) Then
                        _A4Default = dr("Attribute4Default")
                    End If
                End If
                If (IsDBNull(dr("Attribute5"))) = False Then
                    _A5 = dr("Attribute5")
                    _A5Type = dr("Attribute5EntryType")
                    _A5Size = dr("Attribute5Size")
                    If Not (dr("Attribute5Default") Is DBNull.Value) Then
                        _A5Default = dr("Attribute5Default")
                    End If
                End If
                If (IsDBNull(dr("Attribute6"))) = False Then
                    _A6 = dr("Attribute6")
                    _A6Type = dr("Attribute6EntryType")
                    _A6Size = dr("Attribute6Size")
                    If Not (dr("Attribute6Default") Is DBNull.Value) Then
                        _A6Default = dr("Attribute6Default")
                    End If
                End If

                'now we have to update the regEx validators
                'do the OPI Value first
                Select Case _OPIType.ToUpper
                    Case "N"
                        txtOPIValue.Width = New Unit(_OPISize * 12)
                        If _NegativeEntryAllowed Then
                            txtOPIValue.MaxLength = 1 + _OPISize
                            reqValidOPIValue.ValidationExpression = "-?\d{1," + _OPISize.ToString + "}"
                        Else
                            txtOPIValue.MaxLength = _OPISize
                            reqValidOPIValue.ValidationExpression = "\d{1," + _OPISize.ToString + "}"
                        End If

                        reqValidOPIValue.ErrorMessage = "OPI Value must be a numeric value with no more than " + _OPISize.ToString + " digits"
                    Case "D"
                        txtOPIValue.Width = New Unit((8 + _OPISize) * 12)
                        If _NegativeEntryAllowed Then
                            txtOPIValue.MaxLength = 9 + _OPISize
                            reqValidOPIValue.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _OPISize.ToString + "})|(-?\d{0,7})"
                        Else
                            txtOPIValue.MaxLength = 8 + _OPISize
                            reqValidOPIValue.ValidationExpression = "(\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _OPISize.ToString + "})|(\d{0,7})"
                        End If

                        reqValidOPIValue.ErrorMessage = "OPI Value must be decimal value with no more than " + _OPISize.ToString + " decimal places"
                End Select

                SetupAttributes()
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadPageValidation", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub SetupAttributes()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                'attribute 1
                If _A1.Length > 0 Then
                    intAttributes += 1
                    lblAttribute1.Text = GetTranslationString(_A1, _A1) & ":"
                    reqA1.Enabled = True
                    reqA1.ErrorMessage = "Enter " + _A1

                    txtAttribute1.Width = New Unit(_A1Size * 12)
                    txtAttribute1.MaxLength = _A1Size

                    Select Case _A1Type.ToUpper
                        Case "N"
                            reqValidA1.ValidationExpression = "-?\d{1," + _A1Size.ToString + "}"
                            reqValidA1.ErrorMessage = _A1 + " Value must be a numeric value with no more than " + _A1Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute1.MaxLength += 1
                        Case "D"
                            reqValidA1.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A1Size.ToString + "})|(-?\d{0,7})"
                            reqValidA1.ErrorMessage = _A1 + " Value must be decimal value with no more than " + _A1Size.ToString + " decimal places"

                            txtAttribute1.Width = New Unit((8 + _A1Size) * 12)
                            txtAttribute1.MaxLength = 8 + _A1Size

                            'Allow for negative
                            txtAttribute1.MaxLength += 1
                        Case "C"
                            reqValidA1.ValidationExpression = ".{1," + _A1Size.ToString + "}"
                            reqValidA1.ErrorMessage = _A1 + " Value must contain " + (_A1Size).ToString + " or less characters"
                        Case "R"
                            reqValidA1.ValidationExpression = ".{" + _A1Size.ToString + "}"
                            reqValidA1.ErrorMessage = _A1 + " Value must contain " + _A1Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute1.Visible = False
                End If

                'attribute 2
                If _A2.Length > 0 Then
                    intAttributes += 1
                    lblAttribute2.Text = GetTranslationString(_A2, _A2) & ":"
                    reqA2.Enabled = True
                    reqA2.ErrorMessage = "Enter " + _A2

                    txtAttribute2.Width = New Unit(_A2Size * 12)
                    txtAttribute2.MaxLength = _A2Size

                    Select Case _A2Type.ToUpper
                        Case "N"
                            reqValidA2.ValidationExpression = "-?\d{1," + _A2Size.ToString + "}"
                            reqValidA2.ErrorMessage = _A2 + " Value must be a numeric value with no more than " + _A2Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute2.MaxLength += 1
                        Case "D"
                            reqValidA2.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A2Size.ToString + "})|(-?\d{0,7})"
                            reqValidA2.ErrorMessage = _A2 + " Value must be decimal value with no more than " + _A2Size.ToString + " decimal places"

                            txtAttribute2.Width = New Unit((8 + _A2Size) * 12)
                            txtAttribute2.MaxLength = 8 + _A2Size

                            'Allow for negative
                            txtAttribute2.MaxLength += 1
                        Case "C"
                            reqValidA2.ValidationExpression = ".{1," + _A2Size.ToString + "}"
                            reqValidA2.ErrorMessage = _A2 + " Value must contain " + (_A2Size).ToString + " or less characters"
                        Case "R"
                            reqValidA2.ValidationExpression = ".{" + _A2Size.ToString + "}"
                            reqValidA2.ErrorMessage = _A2 + " Value must contain " + _A2Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute2.Visible = False
                End If

                'attribute 3
                If _A3.Length > 0 Then
                    intAttributes += 1
                    lblAttribute3.Text = GetTranslationString(_A3, _A3) & ":"
                    reqA3.Enabled = True
                    reqA3.ErrorMessage = "Enter " + _A3

                    txtAttribute3.Width = New Unit(_A3Size * 12)
                    txtAttribute3.MaxLength = _A3Size

                    Select Case _A3Type.ToUpper
                        Case "N"
                            reqValidA3.ValidationExpression = "-?\d{1," + _A3Size.ToString + "}"
                            reqValidA3.ErrorMessage = _A3 + " Value must be a numeric value with no more than " + _A3Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute3.MaxLength += 1
                        Case "D"
                            reqValidA3.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A3Size.ToString + "})|(-?\d{0,7})"
                            reqValidA3.ErrorMessage = _A3 + " Value must be decimal value with no more than " + _A3Size.ToString + " decimal places"

                            txtAttribute3.Width = New Unit((8 + _A3Size) * 12)
                            txtAttribute3.MaxLength = 8 + _A3Size

                            'Allow for negative
                            txtAttribute3.MaxLength += 1
                        Case "C"
                            reqValidA3.ValidationExpression = ".{1," + _A3Size.ToString + "}"
                            reqValidA3.ErrorMessage = _A3 + " Value must contain " + (_A3Size).ToString + " or less characters"
                        Case "R"
                            reqValidA3.ValidationExpression = ".{" + _A3Size.ToString + "}"
                            reqValidA3.ErrorMessage = _A3 + " Value must contain " + _A3Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute3.Visible = False
                End If

                'attribute 4
                If _A4.Length > 0 Then
                    intAttributes += 1
                    lblAttribute4.Text = GetTranslationString(_A4, _A4) & ":"
                    reqA4.Enabled = True
                    reqA4.ErrorMessage = "Enter " + _A4

                    txtAttribute4.Width = New Unit(_A4Size * 12)
                    txtAttribute4.MaxLength = _A4Size

                    Select Case _A4Type.ToUpper
                        Case "N"
                            reqValidA4.ValidationExpression = "-?\d{1," + _A4Size.ToString + "}"
                            reqValidA4.ErrorMessage = _A4 + " Value must be a numeric value with no more than " + _A4Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute4.MaxLength += 1
                        Case "D"
                            reqValidA4.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A4Size.ToString + "})|(-?\d{0,7})"
                            reqValidA4.ErrorMessage = _A4 + " Value must be decimal value with no more than " + _A4Size.ToString + " decimal places"

                            txtAttribute4.Width = New Unit((8 + _A4Size) * 12)
                            txtAttribute4.MaxLength = 8 + _A4Size

                            'Allow for negative
                            txtAttribute4.MaxLength += 1
                        Case "C"
                            reqValidA4.ValidationExpression = ".{1," + _A4Size.ToString + "}"
                            reqValidA4.ErrorMessage = _A4 + " Value must contain " + (_A4Size).ToString + " or less characters"
                        Case "R"
                            reqValidA4.ValidationExpression = ".{" + _A4Size.ToString + "}"
                            reqValidA4.ErrorMessage = _A4 + " Value must contain " + _A4Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute4.Visible = False
                End If

                'attribute 5
                If _A5.Length > 0 Then
                    intAttributes += 1
                    lblAttribute5.Text = GetTranslationString(_A5, _A5) & ":"
                    reqA5.Enabled = True
                    reqA5.ErrorMessage = "Enter " + _A5

                    txtAttribute5.Width = New Unit(_A5Size * 12)
                    txtAttribute5.MaxLength = _A5Size

                    Select Case _A5Type.ToUpper
                        Case "N"
                            reqValidA5.ValidationExpression = "-?\d{1," + _A5Size.ToString + "}"
                            reqValidA5.ErrorMessage = _A5 + " Value must be a numeric value with no more than " + _A5Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute5.MaxLength += 1
                        Case "D"
                            reqValidA5.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A5Size.ToString + "})|(-?\d{0,7})"
                            reqValidA5.ErrorMessage = _A5 + " Value must be decimal value with no more than " + _A5Size.ToString + " decimal places"

                            txtAttribute5.Width = New Unit((8 + _A5Size) * 12)
                            txtAttribute5.MaxLength = 8 + _A5Size

                            'Allow for negative
                            txtAttribute5.MaxLength += 1
                        Case "C"
                            reqValidA5.ValidationExpression = ".{1," + _A5Size.ToString + "}"
                            reqValidA5.ErrorMessage = _A5 + " Value must contain " + (_A5Size).ToString + " or less characters"
                        Case "R"
                            reqValidA5.ValidationExpression = ".{" + _A5Size.ToString + "}"
                            reqValidA5.ErrorMessage = _A5 + " Value must contain " + _A5Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute5.Visible = False
                End If

                'attribute 6
                If _A6.Length > 0 Then
                    intAttributes += 1
                    lblAttribute6.Text = GetTranslationString(_A6, _A6) & ":"
                    reqA6.Enabled = True
                    reqA6.ErrorMessage = "Enter " + _A6

                    txtAttribute6.Width = New Unit(_A6Size * 12)
                    txtAttribute6.MaxLength = _A6Size

                    Select Case _A6Type.ToUpper
                        Case "N"
                            reqValidA6.ValidationExpression = "-?\d{1," + _A6Size.ToString + "}"
                            reqValidA6.ErrorMessage = _A6 + " Value must be a numeric value with no more than " + _A6Size.ToString + " digits"

                            'Allow for negative
                            txtAttribute6.MaxLength += 1
                        Case "D"
                            reqValidA6.ValidationExpression = "(-?\d{0,7}\" & System.Threading.Thread.CurrentThread.CurrentCulture.NumberFormat.NumberDecimalSeparator & "{1}\d{0," + _A6Size.ToString + "})|(-?\d{0,7})"
                            reqValidA6.ErrorMessage = _A6 + " Value must be decimal value with no more than " + _A6Size.ToString + " decimal places"

                            txtAttribute6.Width = New Unit((8 + _A6Size) * 12)
                            txtAttribute6.MaxLength = 8 + _A6Size

                            'Allow for negative
                            txtAttribute6.MaxLength += 1
                        Case "C"
                            reqValidA6.ValidationExpression = ".{1," + _A6Size.ToString + "}"
                            reqValidA6.ErrorMessage = _A6 + " Value must contain " + (_A6Size).ToString + " or less characters"
                        Case "R"
                            reqValidA6.ValidationExpression = ".{" + _A6Size.ToString + "}"
                            reqValidA6.ErrorMessage = _A6 + " Value must contain " + _A6Size.ToString + " characters"
                    End Select
                Else
                    pnlAttribute6.Visible = False
                End If
            Catch Exc As Exception
                Throw
            End Try
        End Sub
        Private Sub LoadSelectedRecord()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim strHolder As String = RegionalConversion.FormatSQLDate(SessionManager.SelectedOPIDate, True)
                Dim ds As DataTable = TeamOPIValues.SelectTeamOPIValue(SessionManager.TeamOPIValueID)
                If ds IsNot Nothing AndAlso ds.Rows.Count > 0 Then
                    Dim dr As DataRow = ds.Rows(0)

                    If IsDate(dr("OPIValueDateTime")) Then
                        If _TimeRequired = True Then
                            txtOPIValueDateTime.Text = Convert.ToDateTime("" + dr("OPIValueDateTime")).ToShortDateString
                            txtOPIValueTime.Text = Convert.ToDateTime("" + dr("OPIValueDateTime")).ToLongTimeString
                        Else
                            txtOPIValueDateTime.Text = Convert.ToDateTime("" + dr("OPIValueDateTime")).ToShortDateString
                        End If
                    Else
                        txtOPIValueDateTime.Text = String.Empty
                    End If

                    If dr("OPIValue") = 0 Then
                        txtOPIValue.Text = "0"
                    Else
                        txtOPIValue.Text = RegionalConversion.FormatLocalSingle(dr("OPIValue"), "F2")
                    End If
                    txtCost.Text = dr("Cost").ToString
                    txtExpandNotes.Text = dr("Notes").ToString

                    txtMaintenanceUserID.Text = dr("MaintenanceUserID").ToString
                    txtMaintenanceDate.Text = Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToShortDateString + " " + Convert.ToDateTime("" + dr.Item("MaintenanceDate")).ToString("HH:mm:ss")

                    If (IsDBNull(dr("Attribute1Value")) = False) Then
                        If dr("Attribute1EntryType").ToString = "D" Then
                            txtAttribute1.Text = RegionalConversion.FormatLocalSingle(dr("Attribute1Value").ToString.Trim)
                        Else
                            txtAttribute1.Text = dr("Attribute1Value").ToString.Trim
                        End If
                        lblOldA1.Text = dr("Attribute1Value").ToString.Trim
                    Else
                        lblOldA1.Text = String.Empty
                    End If
                    If (IsDBNull(dr("Attribute2Value")) = False) Then
                        If dr("Attribute2EntryType").ToString = "D" Then
                            txtAttribute2.Text = RegionalConversion.FormatLocalSingle(dr("Attribute2Value").ToString.Trim)
                        Else
                            txtAttribute2.Text = dr("Attribute2Value").ToString.Trim
                        End If
                        lblOldA2.Text = dr("Attribute2Value").ToString.Trim
                    Else
                        lblOldA2.Text = String.Empty
                    End If
                    If (IsDBNull(dr("Attribute3Value")) = False) Then
                        If dr("Attribute3EntryType").ToString = "D" Then
                            txtAttribute3.Text = RegionalConversion.FormatLocalSingle(dr("Attribute3Value").ToString.Trim)
                        Else
                            txtAttribute3.Text = dr("Attribute3Value").ToString.Trim
                        End If
                        lblOldA3.Text = dr("Attribute3Value").ToString.Trim
                    Else
                        lblOldA3.Text = String.Empty
                    End If
                    If (IsDBNull(dr("Attribute4Value")) = False) Then
                        If dr("Attribute4EntryType").ToString = "D" Then
                            txtAttribute4.Text = RegionalConversion.FormatLocalSingle(dr("Attribute4Value").ToString.Trim)
                        Else
                            txtAttribute4.Text = dr("Attribute4Value").ToString.Trim
                        End If
                        lblOldA4.Text = dr("Attribute4Value").ToString.Trim
                    Else
                        lblOldA4.Text = String.Empty
                    End If
                    If (IsDBNull(dr("Attribute5Value")) = False) Then
                        If dr("Attribute5EntryType").ToString = "D" Then
                            txtAttribute5.Text = RegionalConversion.FormatLocalSingle(dr("Attribute5Value").ToString.Trim)
                        Else
                            txtAttribute5.Text = dr("Attribute5Value").ToString.Trim
                        End If
                        lblOldA5.Text = dr("Attribute5Value").ToString.Trim
                    Else
                        lblOldA5.Text = String.Empty
                    End If
                    If (IsDBNull(dr("Attribute6Value")) = False) Then
                        If dr("Attribute6EntryType").ToString = "D" Then
                            txtAttribute6.Text = RegionalConversion.FormatLocalSingle(dr("Attribute6Value").ToString.Trim)
                        Else
                            txtAttribute6.Text = dr("Attribute6Value").ToString.Trim
                        End If
                        lblOldA6.Text = dr("Attribute6Value").ToString.Trim
                    Else
                        lblOldA6.Text = String.Empty
                    End If

                    TransactionHistory1.TableName = DBTableName
                    TransactionHistory1.RecordID = SessionManager.TeamOPIValueID

                    Dim objDic As New Dictionary(Of String, String)
                    objDic.Add("Team", SessionManager.SelectedTeam)
                    objDic.Add("OPI", SessionManager.SelectedOPI)
                    If _TimeRequired = True Then
                        objDic.Add("OPIValueDateTime", txtOPIValueDateTime.Text.Trim() & " " & txtOPIValueTime.Text.Trim())
                    Else
                        objDic.Add("OPIValueDateTime", txtOPIValueDateTime.Text.Trim())
                    End If
                    objDic.Add("Attribute1Value", txtAttribute1.Text.Trim())
                    objDic.Add("Attribute2Value", txtAttribute2.Text.Trim())
                    objDic.Add("Attribute3Value", txtAttribute3.Text.Trim())
                    objDic.Add("Attribute4Value", txtAttribute4.Text.Trim())
                    objDic.Add("Attribute5Value", txtAttribute5.Text.Trim())
                    objDic.Add("Attribute6Value", txtAttribute6.Text.Trim())
                    objDic.Add("OPIValue", txtOPIValue.Text.Trim())
                    objDic.Add("Cost", txtCost.Text.Trim())
                    objDic.Add("Notes", txtExpandNotes.Text.Trim())
                    SessionManager.RecordTransactionCurrentValues = objDic
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - LoadSelectedRecord", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.CustomError)
            End Try
        End Sub
        Private Sub UnEnableRecords()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Select Case SessionManager.TeamOPIValueMode.ToString
                Case "EditRow"
                    txtOPIValueDateTime.ReadOnly = True
                    txtOPIValueDateTime.CssClass = "Textbox_Display"
                    imgOPIValueDateTime.Visible = False
                    txtOPIValueDateTime_CalendarExtender.Enabled = False
                    txtOPIValueTime.ReadOnly = True
                    txtOPIValueTime.CssClass = "Textbox_Display"
                    txtOPIValueTime.ReadOnly = True
                    txtOPIValueTime.CssClass = "Textbox_Display"
                    Select Case intAttributes
                        Case 0
                            txtOPIValue.Focus()
                        Case Else
                            txtAttribute1.Focus()
                    End Select

                    If _CalculateValue Then
                        txtOPIValue.CssClass = "Textbox_Display"
                    End If

                Case Else
                    If SessionManager.TeamOPIValueMode = "ViewRow" Then
                        pnlOKCancel.Visible = False
                    End If
                    txtOPIValueDateTime.ReadOnly = True
                    txtOPIValueDateTime.CssClass = "Textbox_Display"
                    imgOPIValueDateTime.Visible = False
                    txtOPIValueDateTime_CalendarExtender.Enabled = False
                    txtOPIValueTime.ReadOnly = True
                    txtOPIValueTime.CssClass = "Textbox_Display"
                    txtOPIValueTime.ReadOnly = True
                    txtOPIValueTime.CssClass = "Textbox_Display"
                    txtOPIValue.ReadOnly = True
                    txtOPIValue.CssClass = "Textbox_Display"
                    txtCost.ReadOnly = True
                    txtCost.CssClass = "Textbox_Display"
                    txtExpandNotes.ReadOnly = True
                    txtExpandNotes.CssClass = "Textbox_Display"
                    txtAttribute1.ReadOnly = True
                    txtAttribute1.CssClass = "Textbox_Display"
                    txtAttribute2.ReadOnly = True
                    txtAttribute2.CssClass = "Textbox_Display"
                    txtAttribute3.ReadOnly = True
                    txtAttribute3.CssClass = "Textbox_Display"
                    txtAttribute4.ReadOnly = True
                    txtAttribute4.CssClass = "Textbox_Display"
                    txtAttribute5.ReadOnly = True
                    txtAttribute5.CssClass = "Textbox_Display"
                    txtAttribute6.ReadOnly = True
                    txtAttribute6.CssClass = "Textbox_Display"
            End Select
        End Sub
        Private Function FormatAttributeValue(ByVal passAttributeNumber As Integer) As String
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo, passAttributeNumber)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strAType As String = String.Empty
            Dim iASize As Integer
            Dim txtHolder As TextBox = Nothing
            Dim strHolder As String = String.Empty

            Select Case passAttributeNumber
                Case 1
                    strAType = _A1Type
                    iASize = _A1Size
                    txtHolder = txtAttribute1
                Case 2
                    strAType = _A2Type
                    iASize = _A2Size
                    txtHolder = txtAttribute2
                Case 3
                    strAType = _A3Type
                    iASize = _A3Size
                    txtHolder = txtAttribute3
                Case 4
                    strAType = _A4Type
                    iASize = _A4Size
                    txtHolder = txtAttribute4
                Case 5
                    strAType = _A5Type
                    iASize = _A5Size
                    txtHolder = txtAttribute5
                Case 6
                    strAType = _A6Type
                    iASize = _A6Size
                    txtHolder = txtAttribute6
            End Select

            'now that we have our validation information
            Select Case strAType
                Case "D"
                    'calculate the spaces to the left of the decimal place
                    'If txtHolder.Text.StartsWith("-") Then
                    '    txtHolder.Text = "-0" + txtHolder.Text.Replace("-", "")
                    'Else
                    '    txtHolder.Text = "0" + txtHolder.Text
                    'End If
                    strHolder = RegionalConversion.FormatSQLSingle(txtHolder.Text, Replace("0." & Space(iASize), " ", "0"))
                Case "N"
                    strHolder = txtHolder.Text
                Case "C", "R"
                    'we don't have to do anything with these as they are stored 'as is' in the DB
                    strHolder = txtHolder.Text
            End Select

            Return strHolder
        End Function
        Private Function ValidateDateTime() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strDateHolder As String = String.Empty
            Dim strTimeHolder As String = String.Empty

            Try
                'first, validate the date
                strDateHolder = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text)
                If Not IsDate(strDateHolder) Then
                    Throw New Exception("Invalid Date")
                    Return False
                End If

                If _TimeRequired Then
                    strTimeHolder = RegionalConversion.FormatSQLTime(txtOPIValueTime.Text)

                    'verify that the time is greater than "00:00:00"
                    If strTimeHolder = DateTime.Parse("00:00").TimeOfDay.ToString Then
                        Throw New Exception("Invalid Time")
                        Return False
                    End If

                    If Not IsDate(strTimeHolder) Then
                        Throw New Exception("Invalid Time")
                        Return False
                    End If
                End If
            Catch Exc As Exception
                Dim strMessage As String

                If _TimeRequired = True Then
                    strMessage = GetTranslationString("invaliddatetime", "Invalid Date / Time Entered")
                Else
                    strMessage = GetTranslationString("invaliddate", "Invalid Date Entered")
                End If
                Master.DisplayError(strMessage)
                Return False
            End Try

            Return True
        End Function
        Private Function InsertTeamOPIValue() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim strTimeHolder As String = String.Empty

            Dim strDateHolder As String = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text)
            If _TimeRequired Then
                strTimeHolder = RegionalConversion.FormatSQLTime(txtOPIValueTime.Text)
            End If

            Try
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.GetDictionaryValues(objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                Dim passOPIValueDateTime As String = (strDateHolder + " " + strTimeHolder).Trim
                Dim strOPIValue As String = RegionalConversion.FormatSQLSingle(txtOPIValue.Text)
                Dim intReslut As Integer = TeamOPIValues.InsertTeamOPIValue(SessionManager.SelectedTeamID, SessionManager.SelectedOPI, passOPIValueDateTime, strOPIValue, txtCost.Text, txtExpandNotes.Text.Trim, FormatAttributeValue(1), FormatAttributeValue(2), FormatAttributeValue(3), FormatAttributeValue(4), FormatAttributeValue(5), FormatAttributeValue(6), SessionManager.UserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, intReslut, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - InsertTeamOPIValue", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.InsertError)
                Return False
            End Try
        End Function
        Private Function UpdateTeamOPIValue() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                'get the values that we're going to send into the update function
                Dim passTeam As String = SessionManager.SelectedTeam
                Dim passOPI As String = SessionManager.SelectedOPI
                Dim passOPIValueDateTime As String = txtOPIValueDateTime.Text
                If _TimeRequired Then
                    passOPIValueDateTime = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text & " " & txtOPIValueTime.Text, True)
                Else
                    passOPIValueDateTime = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text)
                End If

                Dim passOPIValue As String = RegionalConversion.FormatSQLSingle(txtOPIValue.Text)
                Dim passCost As String = RegionalConversion.FormatSQLSingle(txtCost.Text)
                Dim passNotes As String = txtExpandNotes.Text.Trim
                Dim passA1 As String = FormatAttributeValue(1)
                Dim passA2 As String = FormatAttributeValue(2)
                Dim passA3 As String = FormatAttributeValue(3)
                Dim passA4 As String = FormatAttributeValue(4)
                Dim passA5 As String = FormatAttributeValue(5)
                Dim passA6 As String = FormatAttributeValue(6)

                'OLD Attributes
                Dim passOldA1 As String = lblOldA1.Text
                Dim passOldA2 As String = lblOldA2.Text
                Dim passOldA3 As String = lblOldA3.Text
                Dim passOldA4 As String = lblOldA4.Text
                Dim passOldA5 As String = lblOldA5.Text
                Dim passOldA6 As String = lblOldA6.Text

                Dim passUserID As String = SessionManager.UserID
                Dim objDic As Dictionary(Of String, String) = GetUpdatedValues()
                Dim strChangeLog As String = TransactionProcessing.CompareDictionaryValues(SessionManager.RecordTransactionCurrentValues, objDic)

                If strChangeLog.Trim.Length = 0 Then
                    Return True
                End If

                TeamOPIValues.UpdateTeamOPIValue(SessionManager.TeamOPIValueID, passOPIValue, passCost, passNotes, passA1, passA2, passA3, passA4, passA5, passA6, passOldA1, passOldA2, passOldA3, passOldA4, passOldA5, passOldA6, passUserID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamOPIValueID, strChangeLog, SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - UpdateTeamOPIValue", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.UpdateError)
                Return False
            End Try
        End Function
        Private Function DeleteTeamOPIValue() As Boolean
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                Dim passOPIValueDateTime As String = txtOPIValueDateTime.Text
                If _TimeRequired Then
                    passOPIValueDateTime = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text & " " & txtOPIValueTime.Text, True)
                Else
                    passOPIValueDateTime = RegionalConversion.FormatSQLDate(txtOPIValueDateTime.Text)
                End If
                TeamOPIValues.DeleteTeamOPIValue(SessionManager.TeamOPIValueID)
                RecordTransactionHistory.InsertRecordTransactionHistory(DBTableName, SessionManager.TeamOPIValueID, "Team OPI Value Deleted", SessionManager.UserID)
                Return True
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - DeleteTeamOPIValue", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
                Return False
            End Try
        End Function
        Private Sub SetAttributeDefaults()
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Try
                'if ANY of the attribute values should be defaulted then get the info from the database
                If _A1Default = True Or _A2Default = True Or _A3Default = True Or _A4Default = True Or _A5Default = True Or _A6Default = True Then
                    'OK, get the defaults from the database and then plug them in
                    Dim dsHolder As DataTable = TeamOPIValues.SelectTeamOPIAttributeDefaults(SessionManager.SelectedTeamID, SessionManager.SelectedOPI)

                    'verify that we indeed have data
                    If dsHolder IsNot Nothing AndAlso dsHolder.Rows.Count > 0 Then
                        Dim dtRow As DataRow = dsHolder.Rows(0)

                        If _A1Default = True Then
                            txtAttribute1.Text = dtRow("Attribute1Value").ToString
                        End If
                        If _A2Default = True Then
                            txtAttribute2.Text = dtRow("Attribute2Value").ToString
                        End If
                        If _A3Default = True Then
                            txtAttribute3.Text = dtRow("Attribute3Value").ToString
                        End If
                        If _A4Default = True Then
                            txtAttribute4.Text = dtRow("Attribute4Value").ToString
                        End If
                        If _A5Default = True Then
                            txtAttribute5.Text = dtRow("Attribute5Value").ToString
                        End If
                        If _A6Default = True Then
                            txtAttribute6.Text = dtRow("Attribute6Value").ToString
                        End If
                    End If
                End If
            Catch Exc As Exception
                Master.DisplayErrors(ProgramName & " - SetAttributeDefaults", Exc, SessionManager.UserID, CustomControls.ApplicationErrorControl.ApplicationErrorMessages.DeleteError)
            End Try
        End Sub
        Private Function GetUpdatedValues() As Dictionary(Of String, String)
            Try
                If SessionManager.CheckEventTrackerLevel(SessionManager.EventTrackerLevels.UITeams) Then
                    Dim functionInfo As System.Reflection.MethodBase = System.Reflection.MethodBase.GetCurrentMethod()
                    Dim strEventInfo As String = EventTracker.GetFunctionInformation(functionInfo)
                    EventTracker.AddNoEmail(functionInfo.DeclaringType.FullName & "." & functionInfo.DeclaringType.Name, strEventInfo.Trim(), SessionManager.UserID)
                End If
            Catch Exc As Exception
                'Nothing
            End Try

            Dim objDic As New Dictionary(Of String, String)
            objDic.Add("Team", SessionManager.SelectedTeam)
            objDic.Add("OPI", SessionManager.SelectedOPI)
            If _TimeRequired = True Then
                objDic.Add("OPIValueDateTime", txtOPIValueDateTime.Text.Trim() & " " & txtOPIValueTime.Text.Trim())
            Else
                objDic.Add("OPIValueDateTime", txtOPIValueDateTime.Text.Trim())
            End If
            objDic.Add("Attribute1Value", txtAttribute1.Text.Trim())
            objDic.Add("Attribute2Value", txtAttribute2.Text.Trim())
            objDic.Add("Attribute3Value", txtAttribute3.Text.Trim())
            objDic.Add("Attribute4Value", txtAttribute4.Text.Trim())
            objDic.Add("Attribute5Value", txtAttribute5.Text.Trim())
            objDic.Add("Attribute6Value", txtAttribute6.Text.Trim())
            objDic.Add("OPIValue", txtOPIValue.Text.Trim())
            objDic.Add("Cost", txtCost.Text.Trim())
            objDic.Add("Notes", txtExpandNotes.Text.Trim())
            Return objDic
        End Function
#End Region

    End Class
End Namespace
