#Region " Imports "

Imports System.Drawing

#End Region

Namespace WebApp.APlus.UI.UserControls
    Partial Class APlusTimeControl
        Inherits System.Web.UI.UserControl

#Region " Properties"
        Public Property Time() As String
            Get
                Return ddlHours.SelectedValue & ":" & ddlMinutes.SelectedValue
            End Get
            Set(ByVal Value As String)
                SelectedHour = Value.Trim.Substring(0, 2)
                SelectedMinute = Value.Trim.Substring(3, 2)
            End Set
        End Property
        Public Property SelectedHour() As String
            Get
                Return ddlHours.SelectedValue
            End Get
            Set(ByVal Value As String)
                ddlHours.Items.FindByValue(Value.Trim()).Selected = True
            End Set
        End Property

        Public Property SelectedMinute() As String
            Get
                Return ddlMinutes.SelectedValue
            End Get
            Set(ByVal Value As String)
                ddlMinutes.Items.FindByValue(Value.Trim()).Selected = True
            End Set
        End Property
        Public ReadOnly Property HoursDropdown() As DropDownList
            Get
                Return ddlHours
            End Get
        End Property

        Public ReadOnly Property MinutesDropdown() As DropDownList
            Get
                Return ddlMinutes
            End Get
        End Property
        Public Property HoursDropdownEnabled() As Boolean
            Get
                Return ddlHours.Enabled
            End Get
            Set(ByVal Value As Boolean)
                ddlHours.Enabled = Value
            End Set
        End Property
        Public Property MinuteDropdownEnabled() As Boolean
            Get
                Return ddlMinutes.Enabled
            End Get
            Set(ByVal Value As Boolean)
                ddlMinutes.Enabled = Value
            End Set
        End Property
        Public Property HoursDropdownBackColor() As Color
            Get
                Return ddlHours.BackColor
            End Get
            Set(ByVal Value As Color)
                ddlHours.BackColor = Value
            End Set
        End Property

        Public Property MinuteDropdownBackColor() As Color
            Get
                Return ddlMinutes.BackColor
            End Get
            Set(ByVal Value As Color)
                ddlMinutes.BackColor = Value
            End Set
        End Property

        Public Property Enabled() As Boolean
            Get
                Return ddlHours.Enabled
            End Get
            Set(ByVal Value As Boolean)
                ddlHours.Enabled = Value
                ddlMinutes.Enabled = Value
            End Set
        End Property

        Public Property [ReadOnly]() As Boolean
            Get
                Return Not ddlHours.Enabled
            End Get
            Set(ByVal Value As Boolean)
                ddlHours.Enabled = Not Value
                ddlMinutes.Enabled = Not Value
            End Set
        End Property

        Public Property CssClass() As String
            Get
                Return ddlHours.CssClass
            End Get
            Set(ByVal Value As String)
                ddlHours.CssClass = Value
                ddlMinutes.CssClass = Value
            End Set
        End Property
#End Region

#Region " Event Handlers"
        Private Sub ddlMinutes_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlMinutes.SelectedIndexChanged
            SelectedMinute = ddlMinutes.SelectedValue.ToString.Trim()
        End Sub
        Private Sub ddlHours_SelectedIndexChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles ddlHours.SelectedIndexChanged
            SelectedHour = ddlHours.SelectedValue.ToString.Trim()
        End Sub
#End Region

    End Class
End Namespace

