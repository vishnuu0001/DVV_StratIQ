<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="QueryMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.QueryMaster2"
    Title="Query Master" ValidateRequest="false" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table id="tblQuery" width="100%">
        <tr>
            <td style="width: 56px">
            </td>
            <td>
                <asp:Label ID="lblQueryID" runat="server" Visible="False" CssClass="Label_Left_8PT"></asp:Label>
                <asp:Label ID="lblSiteID" runat="server" Visible="False" CssClass="Label_Left_8PT"></asp:Label>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label7" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" MaxLength="50" Width="184px" CssClass="Textbox_Display"
                    ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label6" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtQueryDescription" runat="server" CssClass="Textbox_Entry" Width="100%"
                    MaxLength="250" Rows="1"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqQueryDescription" runat="server" ErrorMessage="Query Description is required."
                    ControlToValidate="txtQueryDescription" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="label4" runat="server" Text="Select:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandSelect" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry" Height="28px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSelect" runat="server" Display="None" ControlToValidate="txtExpandSelect"
                    ErrorMessage="Select information is required."></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="label3" runat="server" Text="From:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandFrom" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry" Height="28px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqFrom" runat="server" Display="None" ControlToValidate="txtExpandFrom"
                    ErrorMessage="From information is required"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label1" runat="server" Text="Where:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandWhere" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label5" runat="server" Text="Group By:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandGroupBy" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 56px; vertical-align: top; text-align: left;">
                <asp:Label ID="Label2" runat="server" CssClass="Label_Left_8PT" Text="Order By:"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandOrderBy" runat="server" TextMode="MultiLine" MaxLength="250"
                    Width="100%" CssClass="Textbox_Entry" Height="28px"></asp:TextBox>
            </td>
        </tr>
    </table>
    <br />
    <table id="tblParameters" width="90%" class="Table_Default">
        <tr>
            <td>
                <asp:Button ID="btnParameters" runat="server" CssClass="Button_Default" Text="Parameters"
                    CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
    <br />
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK"></asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" CausesValidation="False"
                        Text="Cancel"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" CausesValidation="False"
                        Text="Exit"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" ShowSummary="False"
        ShowMessageBox="True" DisplayMode="List"></asp:ValidationSummary>
</asp:Content>
