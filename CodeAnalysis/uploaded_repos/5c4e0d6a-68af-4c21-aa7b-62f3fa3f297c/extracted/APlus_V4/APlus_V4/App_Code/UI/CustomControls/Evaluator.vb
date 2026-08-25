Imports System
Imports System.CodeDom
Imports System.CodeDom.Compiler
Imports Microsoft.VisualBasic
Imports System.Text
Imports System.Reflection

Namespace WebApp.APlus.UI.CustomControls
    Public Class Evaluator

#Region "Private Variables"
        Private Shared ReadOnly staticMethodName As String = "__foo"
        Private _CompiledType As Type = Nothing
        Private _Compiled As Object = Nothing
#End Region

#Region "Constructors"
        Public Sub New(ByVal items As EvaluatorItem())
            ConstructEvaluator(items)
        End Sub
        Public Sub New(ByVal passReturnType As Type, ByVal passExpression As String, ByVal passName As String)
            Dim items As EvaluatorItem() = {New EvaluatorItem(passReturnType, passExpression, passName)}
            ConstructEvaluator(items)
        End Sub
        Public Sub New(ByVal passItem As EvaluatorItem)
            Dim items As EvaluatorItem() = {passItem}
            ConstructEvaluator(items)
        End Sub

        Private Sub ConstructEvaluator(ByVal items As EvaluatorItem())
            Dim comp As CodeDomProvider = CodeDomProvider.CreateProvider("VisualBasic")
            'Dim comp As ICodeCompiler = New VBCodeProvider().CreateCompiler()
            Dim cp As CompilerParameters = New CompilerParameters
            cp.ReferencedAssemblies.Add("system.dll")
            cp.ReferencedAssemblies.Add("system.data.dll")
            cp.ReferencedAssemblies.Add("system.xml.dll")
            cp.GenerateExecutable = False
            cp.GenerateInMemory = True

            Dim code As StringBuilder = New StringBuilder
            code.Append("Imports System" & vbCrLf)
            code.Append("Imports System.Data " & vbCrLf)
            code.Append("Imports System.Data.SqlClient " & vbCrLf)
            code.Append("Imports System.Data.OleDb " & vbCrLf)
            code.Append("Imports System.Xml " & vbCrLf)
            code.Append("namespace APLUS " & vbCrLf)
            code.Append("public class _Evaluator" & vbCrLf)

            For Each item As EvaluatorItem In items
                code.AppendFormat("public Function {1} as {0}", item.ReturnType.Name, item.Name)
                code.Append(vbCrLf)
                code.AppendFormat("return ({0})", item.Expression)
                code.Append(vbCrLf)
                code.Append("End Function" & vbCrLf)
            Next
            code.Append("End Class" & vbCrLf)
            code.Append("End Namespace")

            Dim cr As CompilerResults = comp.CompileAssemblyFromSource(cp, code.ToString())

            If cr.Errors.HasErrors Then
                Dim objError As StringBuilder = New StringBuilder
                objError.Append("Error Compiling Expression: ")

                For Each objErr As CompilerError In cr.Errors
                    objError.AppendFormat("{0}" & vbCrLf, objErr.ErrorText)
                Next

                Throw New Exception("Error Compiling Expression: " + objError.ToString())
            End If

            Dim a As [Assembly] = cr.CompiledAssembly
            _Compiled = a.CreateInstance("APLUS._Evaluator")
        End Sub

#End Region

#Region "Public Methods"
        Public Function Evaluate(ByVal passName As String) As Object
            Dim mi As MethodInfo = _Compiled.GetType().GetMethod(passName)
            Return mi.Invoke(_Compiled, Nothing)
        End Function
        Public Function EvaluateInt(ByVal passName As String) As Integer
            Return CType(Evaluate(passName), Integer)
        End Function
        Public Function EvaluateDouble(ByVal passName As String) As Double
            Return CType(Evaluate(passName), Double)
        End Function
        Public Function EvaluateString(ByVal passName As String) As String
            Return CType(Evaluate(passName), String)
        End Function
        Public Function EvaluateBool(ByVal passName As String) As Boolean
            Return CType(Evaluate(passName), Boolean)
        End Function
#End Region

#Region "Static Method"
        Public Shared Function EvaluateToInteger(ByVal passCode As String) As Integer
            Dim eval As Evaluator = New Evaluator(GetType(Integer), passCode, staticMethodName)
            Return CType(eval.Evaluate(staticMethodName), Integer)
        End Function
        Public Shared Function EvaluateToDouble(ByVal passCode As String) As Double
            Dim eval As Evaluator = New Evaluator(GetType(Double), passCode, staticMethodName)
            Return CType(eval.Evaluate(staticMethodName), Double)
        End Function
        Public Shared Function EvaluateToString(ByVal passCode As String) As String
            Dim eval As Evaluator = New Evaluator(GetType(String), passCode, staticMethodName)
            Return CType(eval.Evaluate(staticMethodName), String)
        End Function
        Public Shared Function EvaluateToBool(ByVal passCode As String) As Boolean
            Dim eval As Evaluator = New Evaluator(GetType(Boolean), passCode, staticMethodName)
            Return CType(eval.Evaluate(staticMethodName), Boolean)
        End Function
        Public Shared Function EvaluateToObject(ByVal passCode As String) As Object
            Dim eval As Evaluator = New Evaluator(GetType(Object), passCode, staticMethodName)
            Return CType(eval.Evaluate(staticMethodName), Object)
        End Function
#End Region

    End Class

    Public Class EvaluatorItem
        Public ReturnType As Type
        Public Name As String
        Public Expression As String

        Public Sub New(ByVal passReturnType As Type, ByVal passExpression As String, ByVal passName As String)
            ReturnType = passReturnType
            Expression = passExpression
            Name = passName
        End Sub

    End Class
End Namespace
