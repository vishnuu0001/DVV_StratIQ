#Region "Imports"
Imports System.IO
Imports WebApp.APlus.DataAccess.Tables
Imports System.Configuration
Imports System.Data
#End Region


Namespace WebApp.APlus.UI.UserControls
    Partial Class TeamOPIGraph
        Inherits System.Web.UI.UserControl

#Region " Properties"
        Public Property ChartType() As String
            Get
                Return SessionManager.ChartType
            End Get
            Set(ByVal Value As String)
                SessionManager.ChartType = Value
            End Set
        End Property
        Public Property OPIUOM() As String
            Get
                Return SessionManager.OPIUOM
            End Get
            Set(ByVal Value As String)
                SessionManager.OPIUOM = Value
            End Set
        End Property
        Public Property ChartWidth() As Integer
            Get
                Return SessionManager.ChartWidth
            End Get
            Set(ByVal Value As Integer)
                SessionManager.ChartWidth = Value
            End Set
        End Property
        Public Property ChartHeight() As Integer
            Get
                Return SessionManager.ChartHeight
            End Get
            Set(ByVal Value As Integer)
                SessionManager.ChartHeight = Value
            End Set
        End Property
        Public Property ChartTeamID() As Integer
            Get
                Return SessionManager.ChartTeamID
            End Get
            Set(ByVal Value As Integer)
                SessionManager.ChartTeamID = Value
            End Set
        End Property
        Public Property ChartOPI() As String
            Get
                Return SessionManager.ChartOPI
            End Get
            Set(ByVal Value As String)
                SessionManager.ChartOPI = Value
            End Set
        End Property
        Public Property ChartTitle() As String
            Get
                Return SessionManager.ChartTitle
            End Get
            Set(ByVal Value As String)
                SessionManager.ChartTitle = Value
            End Set
        End Property
        Public Property WhiteChart() As Boolean
            Get
                Return SessionManager.WhiteChart
            End Get
            Set(ByVal Value As Boolean)
                SessionManager.WhiteChart = Value
            End Set
        End Property
        Public Property DetailChart() As Boolean
            Get
                Return SessionManager.DetailChart
            End Get
            Set(ByVal Value As Boolean)
                SessionManager.DetailChart = Value
            End Set
        End Property
#End Region

    End Class
End Namespace
