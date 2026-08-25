#Region " Imports"
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports WebApp.APlus.Helper
Imports WebApp.APlus.UI
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
Imports WebApp.APlus.UI.UserControls
Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Drawing.Imaging
#End Region

Namespace WebApp.APlus.UI.UserControls
    Partial Class TeamOPIReportGraph
        Inherits System.Web.UI.Page

#Region " Event Handlers"
        Private Sub Page_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
            Dim iWidth As Integer = 400
            Dim iHeight As Integer = 300
            Dim bDetailChart As Boolean = False
            Dim strChartType As String = "OPI"
            Dim strChartTitle As String = ""
            Dim OPIUOM As String = "OPI Value"
            Dim PageBrush As Brush = New SolidBrush(Color.WhiteSmoke)

            If Not IsNothing(SessionManager.ChartType) Then
                If SessionManager.ChartType.ToString.Trim.Length > 0 Then
                    strChartType = SessionManager.ChartType
                End If
            End If
            If Not IsNothing(SessionManager.ChartTitle) Then
                If SessionManager.ChartTitle.ToString.Trim.Length > 0 Then
                    strChartTitle = SessionManager.ChartTitle
                End If
            End If
            If Not IsNothing(SessionManager.DetailChart) Then
                If SessionManager.DetailChart = "True" Then
                    bDetailChart = True
                End If
            End If
            If Not IsNothing(SessionManager.WhiteChart) Then
                If SessionManager.WhiteChart = "True" Then
                    PageBrush = New SolidBrush(Color.White)
                End If
            End If
            If Not IsNothing(SessionManager.ChartWidth) Then
                iWidth = CInt(SessionManager.ChartWidth)
            End If
            If Not IsNothing(SessionManager.ChartHeight) Then
                iHeight = CInt(SessionManager.ChartHeight)
            End If
            If Not IsNothing(SessionManager.OPIUOM) Then
                OPIUOM = SessionManager.OPIUOM
            End If
            Dim objDT As DataTable
            Dim objDTHistory As DataTable

            Dim c As LineChart = New LineChart(iWidth, iHeight, Page)
            Dim iCounter As Integer = 0
            Dim iItemCounter As Integer = 0
            Dim sMaxValueHolder As Single = 0
            Dim sMinValueHolder As Single = 0
            Dim objHistoric As Object = Nothing
            Dim objTarget As Object = Nothing
            Dim bAutoChart As Boolean = False

            c.Title = strChartTitle
            c.OPIUOM = OPIUOM
            c.Xorigin = 0
            c.Yorigin = 0

            c.ShowMarkers = False
            c.BackColor = PageBrush
            c.DetailChart = bDetailChart

            'set up values for historic and target
            Select Case strChartType.ToUpper
                Case "COSTBENEFIT"
                    bAutoChart = True
                    objDT = TeamOPIValues.SelectTeamOPIValuesReportSummary(SessionManager.ChartTeamID, SessionManager.ChartOPI, True)
                    iItemCounter = objDT.Rows.Count - 1

                    Dim dBenefit As Double = 0
                    Dim dValueHolder As Object = DBNull.Value
                    c.MaximumXValue = iItemCounter + 1
                    c.Xdivs = iItemCounter + 1
                    c.ShowControlLimits = False
                    c.ShowEventLines = False

                    For iCounter = 0 To objDT.Rows.Count - 1
                        If Not (objDT.Rows(iCounter)("BenefitPercentage") Is DBNull.Value) Then
                            dBenefit += CType(objDT.Rows(iCounter)("BenefitPercentage"), Double)
                            dValueHolder = dBenefit

                            'Maximum values
                            If dBenefit > sMaxValueHolder Then
                                sMaxValueHolder = dBenefit
                            End If
                        Else
                            dValueHolder = DBNull.Value
                        End If

                        'Minimum Values
                        If dBenefit < sMinValueHolder Then
                            sMinValueHolder = dBenefit
                        End If

                        c.AddXLabels(iCounter, objDT.Rows(iCounter)("ReportPeriod").ToShortDateString)
                        c.AddValue(iCounter, dValueHolder, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value)

                        iItemCounter -= 1
                    Next
                Case "ALLDETAILS"
                    objDT = TeamOPIValues.SelectTeamOPIReportAllDetail(SessionManager.ChartTeamID, SessionManager.ChartOPI)
                    iItemCounter = objDT.Rows.Count - 1

                    Dim dValueHolder As Object = DBNull.Value
                    Dim strHolder As String = ""
                    c.MaximumXValue = iItemCounter + 1
                    c.Xdivs = iItemCounter + 1
                    c.ShowControlLimits = False
                    c.ShowEventLines = True
                    c.ChartYInset = 200

                    For iCounter = 0 To objDT.Rows.Count - 1
                        'Maximum values
                        If Not (objDT.Rows(iCounter)("OPIValue") Is DBNull.Value) Then
                            dValueHolder = CType(objDT.Rows(iCounter)("OPIValue"), Double)

                            If dValueHolder > sMaxValueHolder Then
                                sMaxValueHolder = dValueHolder
                            End If
                        Else
                            dValueHolder = DBNull.Value
                        End If

                        'Minimum Values
                        If dValueHolder < sMinValueHolder Then
                            sMinValueHolder = dValueHolder
                        End If

                        strHolder = CType(objDT.Rows(iCounter)("OPIDate"), DateTime).ToString("MM/dd/yy")
                        If Not (objDT.Rows(iCounter)("Attribute1Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute1Value").ToString
                        End If
                        If Not (objDT.Rows(iCounter)("Attribute2Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute2Value").ToString
                        End If
                        If Not (objDT.Rows(iCounter)("Attribute3Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute3Value").ToString
                        End If
                        If Not (objDT.Rows(iCounter)("Attribute4Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute4Value").ToString
                        End If
                        If Not (objDT.Rows(iCounter)("Attribute5Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute5Value").ToString
                        End If
                        If Not (objDT.Rows(iCounter)("Attribute6Value") Is DBNull.Value) Then
                            strHolder += " " & objDT.Rows(iCounter)("Attribute6Value").ToString
                        End If

                        c.AddXLabels(iCounter, strHolder)
                        c.AddValue(iCounter, dValueHolder, DBNull.Value, DBNull.Value, objDT.Rows(iCounter)("EventDescription"), objDT.Rows(iCounter)("EventWidth"), objDT.Rows(iCounter)("EventStyle"), objDT.Rows(iCounter)("EventColor"))

                        iItemCounter -= 1
                    Next
                Case Else
                    objDT = TeamOPIValues.SelectTeamOPIValuesReportSummary(SessionManager.ChartTeamID, SessionManager.ChartOPI, True)
                    iItemCounter = objDT.Rows.Count - 1
                    objDTHistory = TeamOPIValues.SelectTeamOPIHistoryAndBenefit(SessionManager.ChartTeamID, SessionManager.ChartOPI)

                    If objDTHistory.Rows.Count > 0 Then
                        If Not objDTHistory.Rows(0)("Historic") Is DBNull.Value Then
                            sMaxValueHolder = objDTHistory.Rows(0)("Historic")
                            sMinValueHolder = objDTHistory.Rows(0)("Historic")

                            objHistoric = objDTHistory.Rows(0)("Historic")
                            iItemCounter += 1
                        End If
                        If Not objDTHistory.Rows(0)("Target") Is DBNull.Value Then
                            If objDTHistory.Rows(0)("Target") > sMaxValueHolder Then
                                sMaxValueHolder = objDTHistory.Rows(0)("Target")
                            End If
                            If objDTHistory.Rows(0)("Target") < sMinValueHolder Then
                                sMinValueHolder = objDTHistory.Rows(0)("Target")
                            End If

                            objTarget = objDTHistory.Rows(0)("Target")
                            iItemCounter += 1
                        End If
                    End If

                    c.MaximumXValue = iItemCounter + 1
                    c.Xdivs = iItemCounter + 1
                    c.ShowControlLimits = True
                    c.ShowEventLines = True

                    If Not IsNothing(objTarget) Then
                        c.AddXLabels(iItemCounter, "Target")
                        c.AddValue(iItemCounter, objTarget, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, True)

                        iItemCounter -= 1
                    End If

                    For iCounter = objDT.Rows.Count - 1 To 0 Step -1
                        'Maximum values
                        If Not (objDT.Rows(iCounter)("OPIValue") Is DBNull.Value) Then
                            If Convert.ToSingle("0" + objDT.Rows(iCounter)("OPIValue")) > sMaxValueHolder Then
                                sMaxValueHolder = objDT.Rows(iCounter)("OPIValue")
                            End If
                        End If
                        If Not (objDT.Rows(iCounter)("UpperValue") Is DBNull.Value) Then
                            If Convert.ToSingle("0" + objDT.Rows(iCounter)("UpperValue")) > sMaxValueHolder Then
                                sMaxValueHolder = objDT.Rows(iCounter)("UpperValue")
                            End If
                        End If

                        'Minimum Values
                        If Not (objDT.Rows(iCounter)("OPIValue") Is DBNull.Value) Then
                            If Convert.ToSingle("0" + objDT.Rows(iCounter)("OPIValue")) < sMinValueHolder Then
                                sMinValueHolder = objDT.Rows(iCounter)("OPIValue")
                            End If
                        End If
                        If Not (objDT.Rows(iCounter)("LowerValue") Is DBNull.Value) Then
                            If Convert.ToSingle("0" + objDT.Rows(iCounter)("LowerValue")) < sMinValueHolder Then
                                sMinValueHolder = objDT.Rows(iCounter)("LowerValue")
                            End If
                        End If

                        c.AddXLabels(iItemCounter, objDT.Rows(iCounter)("ReportPeriod").ToShortDateString)
                        c.AddValue(iItemCounter, objDT.Rows(iCounter)("OPIValue"), objDT.Rows(iCounter)("UpperValue"), objDT.Rows(iCounter)("LowerValue"), objDT.Rows(iCounter)("EventDescription"), objDT.Rows(iCounter)("EventWidth"), objDT.Rows(iCounter)("EventStyle"), objDT.Rows(iCounter)("EventColor"))

                        iItemCounter -= 1
                    Next

                    If Not IsNothing(objHistoric) Then
                        c.AddXLabels(0, "Historic")
                        c.AddValue(0, objHistoric, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, DBNull.Value, True)
                    End If
            End Select

            If Not bAutoChart Then
                objDT = TeamOPI.SelectTeamOPI(SessionManager.ChartTeamID, SessionManager.ChartOPI)
                If Not objDT Is Nothing AndAlso objDT.Rows.Count > 0 Then
                    Dim dtRow As DataRow = objDT.Rows(0)

                    If Not dtRow("CustomYAxisValues") Is DBNull.Value AndAlso dtRow("CustomYAxisValues") = True Then
                        If (dtRow("ChartYMin") Is DBNull.Value) OrElse (dtRow("ChartYMax") Is DBNull.Value) OrElse (dtRow("ChartYLines") Is DBNull.Value) Then
                            bAutoChart = True
                        Else
                            bAutoChart = False

                            c.MinimumYValue = dtRow("ChartYMin")
                            c.MaximumYValue = dtRow("ChartYMax")
                            c.Ydivs = dtRow("ChartYLines")
                        End If
                    Else
                        bAutoChart = True
                    End If
                Else
                    bAutoChart = True
                End If
            End If

            If bAutoChart Then
                If bDetailChart Then
                    c.Ydivs = 10
                Else
                    c.Ydivs = 5
                End If

                c.MaximumYValue = CInt(sMaxValueHolder + (sMaxValueHolder / 10))
                c.MinimumYValue = CInt(sMinValueHolder - (Math.Abs(sMinValueHolder) / 10))

                'if the min value is less then 20% of the max and it's not (-) then just make it 0
                If c.MinimumYValue < (c.MaximumYValue / 5) Then
                    If c.MinimumYValue > 0 Then
                        c.MinimumYValue = 0
                    End If
                End If

                RoundMinMax(c.MinimumYValue, c.MaximumYValue, bDetailChart)
            End If

            c.Draw()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub RoundMinMax(ByRef lValue As Double, ByRef uValue As Double, ByVal bDetail As Boolean)
            Dim strChar As String

            If Math.Abs(lValue) > 50 Or Math.Abs(uValue) > 50 Then
                'assume 100 for both
                'Max
                'strChar = Right((uValue.ToString), 2)
                'If strChar <> "00" Then
                '    uValue += (100 - Convert.ToInt16(strChar))
                'End If
                If (uValue Mod 5) <> (uValue \ 5) Then
                    uValue = ((uValue \ 5) + 1) * 5
                End If

                'Min
                strChar = Right((Math.Abs(lValue).ToString), 2)
                If lValue < 0 Then
                    lValue -= (100 - Convert.ToInt16(strChar))
                Else
                    lValue -= (Convert.ToInt16(strChar))
                End If
            ElseIf Math.Abs(lValue) <= 1 And Math.Abs(uValue) <= 1 Then
                'assume 5 for the breaks
                strChar = Right((uValue.ToString), 1)
                If strChar <> "0" Then
                    'If bDetail Then
                    '    uValue += (10 - Convert.ToInt16(strChar))
                    'Else
                    uValue += (1 - Convert.ToInt16(strChar))
                    'End If
                End If

                'Min
                strChar = Right((Math.Abs(lValue).ToString), 1)
                If lValue < 0 Then
                    lValue -= (5 - Convert.ToInt16(strChar))
                Else
                    lValue -= (Convert.ToInt16(strChar))
                End If

            ElseIf Math.Abs(lValue) <= 2 And Math.Abs(uValue) <= 2 Then
                'assume 5 for the breaks
                strChar = Right((uValue.ToString), 1)
                If strChar <> "0" Then
                    'If bDetail Then
                    '    uValue += (10 - Convert.ToInt16(strChar))
                    'Else
                    uValue += (2 - Convert.ToInt16(strChar))
                    'End If
                End If

                'Min
                strChar = Right((Math.Abs(lValue).ToString), 1)
                If lValue < 0 Then
                    lValue -= (5 - Convert.ToInt16(strChar))
                Else
                    lValue -= (Convert.ToInt16(strChar))
                End If
            ElseIf Math.Abs(lValue) <= 5 And Math.Abs(uValue) <= 5 Then
                'assume 5 for the breaks
                strChar = Right((uValue.ToString), 1)
                If strChar <> "0" Then
                    'If bDetail Then
                    '    uValue += (10 - Convert.ToInt16(strChar))
                    'Else
                    uValue += (5 - Convert.ToInt16(strChar))
                    'End If
                End If

                'Min
                strChar = Right((Math.Abs(lValue).ToString), 1)
                If lValue < 0 Then
                    lValue -= (5 - Convert.ToInt16(strChar))
                Else
                    lValue -= (Convert.ToInt16(strChar))
                End If
            Else
                'assume 10 for the breaks
                'strChar = Right((uValue.ToString), 1)
                'If strChar <> "0" Then
                '    uValue += (10 - Convert.ToInt16(strChar))
                'End If

                If (uValue Mod 5) <> (uValue \ 5) Then
                    uValue = ((uValue \ 5) + 1) * 5
                End If

                'Min
                strChar = Right((Math.Abs(lValue).ToString), 1)
                If lValue < 0 Then
                    lValue -= (10 - Convert.ToInt16(strChar))
                Else
                    lValue -= (Convert.ToInt16(strChar))
                End If
            End If
        End Sub
#End Region

    End Class

    Public Class LineChart

#Region " Variables"
        Public bmpChart As Bitmap
        Public Title As String = "Default Title"
        Public BackColor As Brush = New SolidBrush(Color.WhiteSmoke)
        Public chartValues As ArrayList = New ArrayList
        Public chartXLabels As ArrayList = New ArrayList
        Public Xorigin As Integer = 0, Yorigin As Integer = 0
        Public MaximumXValue As Single
        Public MaximumYValue As Single, MinimumYValue As Single
        Public Xdivs As Long, Ydivs As Long
        Public StartTime As DateTime
        Public ShowMarkers As Boolean = False
        Private Width As Integer, Height As Integer
        Public grpChart As Graphics
        Public pgChart As Page
        Public ShowControlLimits As Boolean
        Public ShowEventLines As Boolean
        Public DetailChart As Boolean
        Public OPIUOM As String
        Public ChartXInset As Integer = 55
        Public ChartYInset As Integer = 80
#End Region

#Region " Structs"
        Structure datapoint
            Public x As Single
            Public y As Object
            Public UpperLimit As Object
            Public LowerLimit As Object
            Public NoDataPoint As Boolean
            Public valid As Boolean
            Public EventDescription As Object
            Public EventWidth As Object
            Public EventStyle As Object
            Public EventColor As Object
        End Structure
        Structure dataXLabel
            Public x As Single
            Public Label As String
        End Structure

#End Region

#Region " Event Handlers"
        Public Sub New(ByVal myWidth As Integer, ByVal myHeight As Integer, ByVal myPage As Page)
            Width = myWidth
            Height = myHeight
            MaximumXValue = myWidth
            MaximumYValue = myHeight
            bmpChart = New Bitmap(myWidth, myHeight)
            grpChart = Graphics.FromImage(bmpChart)
            pgChart = myPage
        End Sub
        Protected Overrides Sub Finalize()
            grpChart.Dispose()
            bmpChart.Dispose()
            MyBase.Finalize()
        End Sub
#End Region

#Region " Custom Methods"
        Public Sub AddValue(ByVal x As Single, ByVal y As Object, ByVal UpperLimit As Object, ByVal LowerLimit As Object, ByVal EventDescription As Object, ByVal EventWidth As Object, ByVal EventStyle As Object, ByVal EventColor As Object)
            AddValue(x, y, UpperLimit, LowerLimit, EventDescription, EventWidth, EventStyle, EventColor, False)
        End Sub
        Public Sub AddValue(ByVal x As Single, ByVal y As Object, ByVal UpperLimit As Object, ByVal LowerLimit As Object, ByVal EventDescription As Object, ByVal EventWidth As Object, ByVal EventStyle As Object, ByVal EventColor As Object, ByVal NoDataPoint As Boolean)
            Dim myPoint As datapoint
            myPoint.x = x
            myPoint.y = y
            myPoint.UpperLimit = UpperLimit
            myPoint.LowerLimit = LowerLimit
            myPoint.EventDescription = EventDescription
            myPoint.EventWidth = EventWidth
            myPoint.EventStyle = EventStyle
            myPoint.EventColor = EventColor
            myPoint.NoDataPoint = NoDataPoint
            myPoint.valid = True
            chartValues.Add(myPoint)
        End Sub
        Public Sub AddXLabels(ByVal x As Integer, ByVal strLabel As String)
            Dim xLabel As dataXLabel
            xLabel.x = x
            xLabel.Label = strLabel
            chartXLabels.Add(xLabel)
        End Sub
        Public Sub Draw()
            Dim i As Integer
            Dim x As Single, y As Single, x0 As Single, y0 As Single
            Dim myLabel As String
            Dim blackPen As Pen = New Pen(Color.Black, 2)
            Dim blackBrush As Brush = New SolidBrush(Color.Black)
            Dim darkredBrush As Brush = New SolidBrush(Color.DarkRed)
            Dim axisFont As Font = New Font("Tahoma", 8)
            Dim XaxisFont As Font = New Font("Tahoma", 7)

            Dim ChartWidth As Integer = Width - (2 * ChartXInset)
            Dim ChartHeight As Integer = Height - (ChartXInset + ChartYInset)
            Dim blnShowXLabel As Boolean = True
            Dim tickPen As New Pen(Color.Black, 2)

            Dim prevPoint As datapoint = New datapoint
            Dim myPoint As datapoint
            Dim xlabel As dataXLabel
            Dim redPen As New Pen(Color.Red, 1)
            Dim redPenWide As New Pen(Color.Red, 2)
            Dim graypen As New Pen(Color.Gray, 1)

            blackPen.DashStyle = DashStyle.Solid
            blackPen.LineJoin = LineJoin.Round
            blackPen.DashCap = DashCap.Round
            grpChart.SmoothingMode = SmoothingMode.HighQuality

            'first, validate the MaximumYValue
            If MaximumYValue = 0 Then
                MaximumYValue = 1
            End If

            'first establish working area
            pgChart.Response.ContentType = "image/jpeg"
            grpChart.FillRectangle(BackColor, 0, 0, Width, Height)
            grpChart.DrawRectangle(New Pen(Color.Black, 1), ChartXInset - 2, ChartXInset, ChartWidth + 2, ChartHeight)

            'must draw all text items before doing the rotate below
            grpChart.DrawString(Title, New Font("Tahoma", 12), blackBrush, Width / 3, 10)
            grpChart.DrawString(OPIUOM, New Font("Tahoma", 8), blackBrush, 0, 10)

            Dim objStringFormat As New System.Drawing.StringFormat
            objStringFormat.FormatFlags = StringFormatFlags.DirectionVertical

            'draw X axis labels
            For Each xlabel In chartXLabels
                If Xdivs = 1 Then
                    x = ChartXInset + ChartWidth / 2
                Else
                    x = ChartXInset + xlabel.x * ChartWidth / (Xdivs - 1)
                End If
                y = ChartHeight + ChartXInset

                myLabel = xlabel.Label

                grpChart.DrawString(myLabel, XaxisFont, blackBrush, x - 12 + 5, y + 10, objStringFormat)

                grpChart.DrawLine(tickPen, x, y + 2, x, y - 2)
            Next

            'draw Y axis labels
            For i = 0 To Ydivs
                If i = 0 Then
                    x = ChartXInset
                    y = ChartHeight + ChartXInset - (i * ChartHeight / Ydivs)
                    myLabel = MinimumYValue.ToString
                    grpChart.DrawString(myLabel, axisFont, blackBrush, 5, y - 6)
                    grpChart.DrawLine(graypen, (Width - ChartXInset), y, x - 3, y)
                ElseIf i = Ydivs Then
                    x = ChartXInset
                    y = ChartHeight + ChartXInset - (i * ChartHeight / Ydivs)
                    myLabel = ((MaximumYValue) * i / Ydivs).ToString()
                    grpChart.DrawString(myLabel, axisFont, blackBrush, 5, y - 6)
                    grpChart.DrawLine(graypen, (Width - ChartXInset), y, x - 3, y)
                Else
                    x = ChartXInset
                    y = ChartHeight + ChartXInset - (i * ChartHeight / Ydivs)
                    myLabel = (((MaximumYValue - MinimumYValue) * i / Ydivs) + MinimumYValue).ToString()
                    grpChart.DrawString(myLabel, axisFont, blackBrush, 5, y - 6)
                    grpChart.DrawLine(graypen, (Width - ChartXInset), y, x - 3, y)
                End If
            Next

            'add event descriptions - if applicable
            If ShowEventLines Then
                For Each myPoint In chartValues
                    If Not myPoint.EventDescription Is DBNull.Value Then
                        'now, put the event short description in
                        'if we have more than 15 chars then
                        'split the text into two lines
                        x = ChartXInset + myPoint.x * ChartWidth / (Xdivs - 1) - 15

                        If myPoint.EventDescription.ToString.Length > 15 Then
                            'split at the first space after 12 and make two lines
                            Dim strHolder As String = myPoint.EventDescription.ToString
                            Dim iLocation As Integer = strHolder.IndexOf(" ", 12)

                            If iLocation = -1 Then
                                grpChart.DrawString(myPoint.EventDescription, XaxisFont, blackBrush, x, ChartXInset * 0.8)
                            Else
                                grpChart.DrawString(strHolder.Substring(0, iLocation).Trim, XaxisFont, blackBrush, x, (ChartXInset * 0.8) - 10)

                                grpChart.DrawString(strHolder.Substring(iLocation).Trim, XaxisFont, blackBrush, x, ChartXInset * 0.8)
                            End If
                        Else
                            grpChart.DrawString(myPoint.EventDescription, XaxisFont, blackBrush, x, ChartXInset * 0.8)
                        End If
                    End If
                Next
            End If

            'transform drawing coords to lower-left (0,0)
            grpChart.RotateTransform(180)
            grpChart.TranslateTransform(0, -Height)
            grpChart.TranslateTransform(-ChartXInset, ChartYInset)
            grpChart.ScaleTransform(-1, 1)

            'de-initialize previous coordinate variables
            Dim bPreviousDataPoint As Boolean = False
            Dim brLimitBrush As System.Drawing.Brush = blackBrush
            Dim BarWidth As Short = ChartWidth / MaximumXValue / 5

            'draw chart data
            For Each myPoint In chartValues
                'if we have a valid data point
                If Not myPoint.y Is DBNull.Value And myPoint.NoDataPoint = False Then
                    If MaximumXValue = 1 Then
                        x = ChartWidth / 2
                    Else
                        x = ChartWidth * (myPoint.x - Xorigin) / (MaximumXValue - 1)
                    End If
                    y = ChartHeight * ((myPoint.y - MinimumYValue) / (MaximumYValue - MinimumYValue))

                    'grpChart.DrawLine(blackPen, x, 0, x, y)

                    If bPreviousDataPoint = True Then
                        grpChart.DrawLine(blackPen, x0, y0, x, y)
                    End If

                    'this shows a red circle around the datapoint
                    'if the user specifically requests to see the markers
                    brLimitBrush = blackBrush
                    If Not (myPoint.UpperLimit Is DBNull.Value) Then
                        If myPoint.y > myPoint.UpperLimit Then
                            brLimitBrush = darkredBrush
                        End If
                    End If
                    If Not (myPoint.LowerLimit Is DBNull.Value) Then
                        If myPoint.y < myPoint.LowerLimit Then
                            brLimitBrush = darkredBrush
                        End If
                    End If

                    grpChart.FillEllipse(brLimitBrush, x - 2, y - 2, 4, 4)

                    bPreviousDataPoint = True
                    x0 = x
                    y0 = y
                ElseIf myPoint.NoDataPoint And Not myPoint.y Is DBNull.Value Then
                    'historic or Target
                    x = ChartWidth * (myPoint.x - Xorigin) / (MaximumXValue - 1)
                    y = ChartHeight * ((myPoint.y - MinimumYValue) / (MaximumYValue - MinimumYValue))
                    If myPoint.x = 0 Then
                        grpChart.FillRectangle(New SolidBrush(Color.Red), New Rectangle(x - 1, 0, BarWidth, y))
                    Else
                        grpChart.FillRectangle(New SolidBrush(Color.LawnGreen), New Rectangle(x - BarWidth - 1, 0, BarWidth, y))
                    End If
                End If
            Next

            'show control limits if applicable
            If ShowControlLimits Then
                Dim objRedBrush As SolidBrush
                objRedBrush = New SolidBrush(Color.FromArgb(75, 255, 0, 0))

                bPreviousDataPoint = False
                For Each myPoint In chartValues
                    If myPoint.NoDataPoint = False Then
                        x = ChartWidth * (myPoint.x - Xorigin) / (MaximumXValue - 1)

                        'Upper limit
                        If Not (myPoint.UpperLimit Is DBNull.Value) Then
                            y = ChartHeight * ((myPoint.UpperLimit - MinimumYValue) / (MaximumYValue - MinimumYValue))

                            If bPreviousDataPoint = True Then
                                grpChart.DrawLine(redPenWide, x0, y, x, y)
                            End If

                            '*****
                            'Fills the invalid area with red
                            'Looks nice but the seams between the boxes are noticeable
                            'grpChart.FillRectangle(objRedBrush, New Rectangle(x - 1, y, x0 - x, ChartHeight - y))
                        End If

                        'Lower limit
                        If Not (myPoint.LowerLimit Is DBNull.Value) Then
                            y = ChartHeight * ((myPoint.LowerLimit - MinimumYValue) / (MaximumYValue - MinimumYValue))

                            If bPreviousDataPoint = True Then
                                grpChart.DrawLine(redPenWide, x0, y, x, y)
                            End If

                            '*****
                            'Fills the invalid area with red
                            'Looks nice but the seams between the boxes are noticeable
                            'grpChart.FillRectangle(objRedBrush, New Rectangle(x - 1, 0, x0 - x, y))
                        End If

                        x0 = x
                        bPreviousDataPoint = True
                    End If
                Next
            End If

            'Show Event Lines if applicable
            If ShowEventLines Then
                'Event Lines
                Dim EventPen As Pen

                For Each myPoint In chartValues
                    If Not myPoint.EventDescription Is DBNull.Value Then
                        EventPen = New Pen(Color.FromName(myPoint.EventColor), myPoint.EventWidth)
                        EventPen.DashStyle = myPoint.EventStyle

                        x = ChartWidth * (myPoint.x - Xorigin) / (MaximumXValue - 1)
                        grpChart.DrawLine(EventPen, x, 0, x, ChartHeight)
                    End If
                Next
            End If

            'finally send graphics to browser
            bmpChart.Save(pgChart.Response.OutputStream, ImageFormat.Jpeg)
        End Sub
#End Region

    End Class
End Namespace
