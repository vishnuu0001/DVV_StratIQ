<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="DataQuery1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.DataQuery1"
    Title="Data Query" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">

    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>

    <script type="text/javascript" language="javascript">
        $(document).ready(function() {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>

    <table class="Table_Default" id="tblQuery" style="width: 90%">
        <tr>
            <td style="width: 65px; vertical-align: top; text-align: left;">
                <asp:Label ID="label4" runat="server" Text="Select:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandSelect" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSelect" runat="server" Display="None" ControlToValidate="txtExpandSelect"
                    ErrorMessage="Select information is required." CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 65px; vertical-align: top; text-align: left;">
                <asp:Label ID="label3" runat="server" Text="From:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandFrom" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqFrom" runat="server" Display="None" ControlToValidate="txtExpandFrom"
                    ErrorMessage="From information is required" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 65px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label1" runat="server" Text="Where:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandWhere" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 65px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label5" runat="server" Text="Group By:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandGroupBy" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 65px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label2" runat="server" Text="Order By:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandOrderBy" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry"></asp:TextBox>
            </td>
        </tr>
    </table>
    <table id="tbButtons" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" EnableViewState="False"
                    Text="OK"></asp:Button>
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                </asp:Button>
            </td>
            <td style="width: 110px">
                <asp:Button ID="btnClear" runat="server" CssClass="Button_Default" Text="Clear Fields"
                    EnableViewState="False" CausesValidation="False"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnExport" runat="server" CssClass="Button_Default" Text="Export"
                    EnableViewState="False" Visible="False"></asp:Button>
            </td>
        </tr>
    </table>
    <asp:DataGrid ID="gvQueryResults" runat="server" SkinID="DataGrid" AutoGenerateColumns="true">
    </asp:DataGrid>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
