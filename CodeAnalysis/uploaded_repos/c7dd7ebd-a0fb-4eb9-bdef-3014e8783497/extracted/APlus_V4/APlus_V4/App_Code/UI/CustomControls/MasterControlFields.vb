
Namespace WebApp.APlus.UI.CustomControls
    Public Class MasterControlFields
        Inherits CollectionBase

        Default Public ReadOnly Property Item(ByVal nIndex As Integer) As MasterControlField
            Get
                If TypeOf MyBase.List(nIndex) Is MasterControlField Then
                    Return CType(MyBase.List(nIndex), MasterControlField)
                Else
                    Return Nothing
                End If
            End Get
        End Property

        Public Sub Add(ByVal boundcol As DataControlField)
            MyBase.List.Add(boundcol)
        End Sub
        Public Sub Insert(ByVal index As Integer, ByVal boundcol As DataControlField)
            MyBase.List.Insert(0, boundcol)
        End Sub

        Public Function Indexof(ByVal boundcol As MasterControlField) As Integer
            Return MyBase.List.IndexOf(boundcol)
        End Function
    End Class

    Public Class MasterControlField
        Inherits BoundField

        Private _ShowReturns As Boolean = False

        Public Property ShowReturns() As Boolean
            Get
                Return _ShowReturns
            End Get
            Set(ByVal Value As Boolean)
                _ShowReturns = Value
            End Set
        End Property
    End Class
End Namespace
