Imports System
Imports System.Web.UI
Imports System.Web.UI.WebControls
Imports System.Data

Namespace WebApp.APlus.UI.CustomControls

    Public Class ApplicationEventCalendar
        Inherits System.Web.UI.WebControls.Calendar
        Implements INamingContainer

#Region " Private Variables / Members"
        Private _dataSource As Object
        Private _dataMember As String
        Private _dayField As String
        Private _itemTemplate As ITemplate
        Private _noEventsTemplate As ITemplate
        Private _dayWithEventsStyle As TableItemStyle
        Private _dtSource As DataTable
        Private _showweeknumbers As Boolean
#End Region

#Region " Properties"
        Public Property ShowWeekNumber() As Boolean
            Get
                Return _showweeknumbers
            End Get
            Set(ByVal Value As Boolean)
                _showweeknumbers = Value
            End Set
        End Property
        Public Property DataSource() As Object
            Get
                Return _dataSource
            End Get
            Set(ByVal Value As Object)
                If TypeOf Value Is DataTable OrElse TypeOf Value Is DataSet Then
                    _dataSource = Value
                Else
                    Throw New Exception("The DataSource property of the DataCalendar control" + " must be a DataTable or DataSet object")
                End If
            End Set
        End Property
        Public Property DataMember() As String
            Get
                Return _dataMember
            End Get
            Set(ByVal Value As String)
                _dataMember = Value
            End Set
        End Property
        Public Property DayField() As String
            Get
                Return _dayField
            End Get
            Set(ByVal Value As String)
                _dayField = Value
            End Set
        End Property
        Public Property DayWithEventsStyle() As TableItemStyle
            Get
                Return _dayWithEventsStyle
            End Get
            Set(ByVal Value As TableItemStyle)
                _dayWithEventsStyle = Value
            End Set
        End Property
        <PersistenceMode(PersistenceMode.InnerProperty), TemplateContainer(GetType(DataCalendarItem))> _
        Public Property ItemTemplate() As ITemplate
            Get
                Return _itemTemplate
            End Get
            Set(ByVal Value As ITemplate)
                _itemTemplate = Value
            End Set
        End Property
        <PersistenceMode(PersistenceMode.InnerProperty), TemplateContainer(GetType(DataCalendarItem))> _
        Public Property NoEventsTemplate() As ITemplate
            Get
                Return _noEventsTemplate
            End Get
            Set(ByVal Value As ITemplate)
                _noEventsTemplate = Value
            End Set
        End Property
#End Region

#Region " Public Events"
        Public Event AfterDayRender(ByVal cell As TableCell, ByVal objdv As DataView)
#End Region

#Region " Override Methods"
        Protected Overrides Sub OnDayRender(ByVal cell As TableCell, ByVal day As CalendarDay)
            Try
                If Not (_dtSource Is Nothing) Then
                    Dim dv As DataView = New DataView(_dtSource)
                    dv.RowFilter = Me.DayField + " >= '" + day.Date.ToString("yyyy/MM/dd") + "' and " + Me.DayField + " < '" + day.Date.AddDays(1).ToString("yyyy/MM/dd") + "'"

                    If _showweeknumbers = True Then
                        'plug in the week number
                        If day.Date.DayOfWeek = DayOfWeek.Monday Then
                            Dim ctlObject As System.Web.UI.HtmlControls.HtmlGenericControl
                            Dim strWeekHolder As String
                            Dim cal As System.Globalization.Calendar = System.Globalization.CultureInfo.CurrentCulture.Calendar
                            strWeekHolder = cal.GetWeekOfYear(day.Date, Globalization.CalendarWeekRule.FirstFourDayWeek, DayOfWeek.Monday).ToString

                            ctlObject = New HtmlGenericControl
                            ctlObject.InnerHtml = " - Week " + strWeekHolder

                            cell.Controls.Add(ctlObject)
                        End If
                    End If

                    If dv.Count > 0 Then
                        If Not (Me.DayWithEventsStyle Is Nothing) Then
                            cell.ApplyStyle(Me.DayWithEventsStyle)
                        End If
                        If Not (Me.ItemTemplate Is Nothing) Then
                            Dim i As Integer = 0
                            While i < dv.Count
                                SetupCalendarItem(cell, dv(i).Row, Me.ItemTemplate)
                                i += 1
                            End While
                        End If

                        RaiseEvent AfterDayRender(cell, dv)
                    Else
                        If Not (Me.NoEventsTemplate Is Nothing) Then
                            SetupCalendarItem(cell, Nothing, Me.NoEventsTemplate)
                        End If
                    End If
                End If
            Catch ex As Exception
                'catch error and return gracefully
            End Try

            MyBase.OnDayRender(cell, day)
        End Sub
        Protected Overrides Sub Render(ByVal html As HtmlTextWriter)
            _dtSource = Nothing
            If Not (Me.DataSource Is Nothing) AndAlso Not (Me.DayField Is Nothing) Then
                If TypeOf Me.DataSource Is DataTable Then
                    _dtSource = DirectCast(Me.DataSource, DataTable)
                End If
                If TypeOf Me.DataSource Is DataSet Then
                    Dim ds As DataSet = DirectCast(Me.DataSource, DataSet)
                    If Me.DataMember Is Nothing OrElse Me.DataMember = "" Then
                        _dtSource = ds.Tables(0)
                    Else
                        _dtSource = ds.Tables(Me.DataMember)
                    End If
                End If
                If _dtSource Is Nothing Then
                    Throw New Exception("Error finding the DataSource.  Please check " + " the DataSource and DataMember properties.")
                End If
            End If
            MyBase.Render(html)
        End Sub
#End Region

#Region " Event Handlers"
        Public Sub New()
            MyBase.New()
            SelectionMode = CalendarSelectionMode.None
            ShowGridLines = True
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub SetupCalendarItem(ByVal cell As TableCell, ByVal r As DataRow, ByVal t As ITemplate)
            Dim dti As DataCalendarItem = New DataCalendarItem(r)
            t.InstantiateIn(dti)
            dti.DataBind()
            cell.Controls.Add(dti)
        End Sub
#End Region

    End Class

    Public Class DataCalendarItem
        Inherits Control
        Implements INamingContainer
        Private _dataItem As DataRow

        Public Sub New(ByVal dr As DataRow)
            _dataItem = dr
        End Sub

        Public Property DataItem() As DataRow
            Get
                Return _dataItem
            End Get
            Set(ByVal Value As DataRow)
                _dataItem = Value
            End Set
        End Property
    End Class
End Namespace

