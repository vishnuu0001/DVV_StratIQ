#Region " Imports"
Imports System.ComponentModel
Imports System.IO
Imports System.Data
Imports System.Data.SqlClient
Imports System.Web
Imports System.Web.UI
Imports System.Web.UI.WebControls
Imports WebApp.APlus.DataAccess.Tables
Imports WebApp.APlus.DataAccess.Custom
#End Region

Namespace WebApp.APlus.UI.UserControls
    Partial Class TransactionHistory
        Inherits System.Web.UI.UserControl

#Region " Members"
        Private _CommandText As String = String.Empty
        Private _ControlIsExpanded As Boolean = False
        Private _LockControl As Boolean = False
        Private _ShowExpanded As Boolean = False
        Private _StoredProcedureParams As New Hashtable
        Private _Translate As Boolean = False
#End Region

#Region " Properties"
        Public Property CommandText() As String
            Get
                Return _CommandText
            End Get
            Set(ByVal Value As String)
                _CommandText = Value
            End Set
        End Property
        <DefaultValue("False")> _
        Public Property InitialStateExpanded() As Boolean
            Get
                Return _ShowExpanded
            End Get
            Set(ByVal value As Boolean)
                _ShowExpanded = value
            End Set
        End Property
        <DefaultValue("False")> _
        Public Property LockControl() As Boolean
            Get
                Return _LockControl
            End Get
            Set(ByVal value As Boolean)
                _LockControl = value
            End Set
        End Property
        Public Property RecordID() As String
            Get
                Return ViewState.Item("RecordID")
            End Get
            Set(ByVal value As String)
                ViewState.Remove("RecordID")
                ViewState.Add("RecordID", value)
            End Set
        End Property
        Public ReadOnly Property StoredProcedureParams() As Hashtable
            Get
                Return _StoredProcedureParams
            End Get
        End Property
        Public Property TableName() As String
            Get
                Return ViewState.Item("TableName")
            End Get
            Set(ByVal value As String)
                ViewState.Remove("TableName")
                ViewState.Add("TableName", value)
            End Set
        End Property
        Public Property Translate() As Boolean
            Get
                Return _Translate
            End Get
            Set(ByVal value As Boolean)
                _Translate = value
            End Set
        End Property
#End Region

#Region " Event Handlers"
        Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
            If Not Page.IsPostBack Then
                If _Translate Then
                    ibExpandAll.ToolTip = GetTranslationString(ibExpandAll.ToolTip)
                    ibCollapseAll.ToolTip = GetTranslationString(ibCollapseAll.ToolTip)

                    lblText.Text = GetTranslationString(lblText.Text)
                End If

                If _LockControl Then
                    ibCollapseAll.Visible = False
                    ibExpandAll.Visible = False
                    pnlHistory.Visible = True
                    LoadDataGrid()
                    tblExpandCollapse.Rows(0).Cells(0).Visible = False
                Else
                    pnlHistory.Visible = _ShowExpanded
                    _ControlIsExpanded = _ShowExpanded

                    If _ControlIsExpanded Then
                        ibExpandAll.Visible = False
                        ibCollapseAll.Visible = True
                    Else
                        ibExpandAll.Visible = True
                        ibCollapseAll.Visible = False
                    End If
                End If
            End If
        End Sub
        Protected Sub grdHistory_RowDataBound(ByVal sender As Object, ByVal e As System.Web.UI.WebControls.GridViewRowEventArgs) Handles grdHistory.RowDataBound
            If e.Row.RowType = DataControlRowType.DataRow Then
                e.Row.Cells(2).Text = e.Row.Cells(2).Text.Replace(vbCrLf, "<BR />")
            End If
        End Sub
        Protected Sub ibExpandAll_Click(ByVal sender As Object, ByVal e As System.Web.UI.ImageClickEventArgs) Handles ibExpandAll.Click
            ExpandAll()
        End Sub
        Public Sub ExpandAll()
            _ControlIsExpanded = True
            ibExpandAll.Visible = False
            ibCollapseAll.Visible = True
            pnlHistory.Visible = True
            LoadDataGrid()
        End Sub
        Protected Sub ibCollapseAll_Click(ByVal sender As Object, ByVal e As System.Web.UI.ImageClickEventArgs) Handles ibCollapseAll.Click
            CollapseAll()
        End Sub
        Public Sub CollapseAll()
            _ControlIsExpanded = False
            ibExpandAll.Visible = True
            ibCollapseAll.Visible = False
            pnlHistory.Visible = False
            grdHistory.DataSource = Nothing
            grdHistory.DataBind()
        End Sub
        Public Sub RebindGrid()
            LoadDataGrid()
        End Sub
        Public Sub RebindGrid(ByVal passRecordID As String)
            RecordID = passRecordID
            LoadDataGrid()
        End Sub
#End Region

#Region " Custom Methods"
        Private Sub LoadDataGrid()
            Try
                If _Translate Then
                    grdHistory.Columns(0).HeaderText = GetTranslationString(grdHistory.Columns(0).HeaderText)
                    grdHistory.Columns(1).HeaderText = GetTranslationString(grdHistory.Columns(1).HeaderText)
                    grdHistory.Columns(2).HeaderText = GetTranslationString(grdHistory.Columns(2).HeaderText)
                End If

                Dim objDT As DataTable = Nothing

                If Not String.IsNullOrEmpty(_CommandText) Then
                    objDT = GeneralDataAccess.ExecuteDatabaseQuery(_CommandText, _StoredProcedureParams)
                Else
                    objDT = RecordTransactionHistory.SelectRecordTransactionHistory(TableName, RecordID)
                End If

                If objDT IsNot Nothing Then
                    grdHistory.DataSource = objDT
                    grdHistory.DataBind()
                End If
            Catch Exc As Exception

            End Try
        End Sub
#End Region

    End Class
End Namespace