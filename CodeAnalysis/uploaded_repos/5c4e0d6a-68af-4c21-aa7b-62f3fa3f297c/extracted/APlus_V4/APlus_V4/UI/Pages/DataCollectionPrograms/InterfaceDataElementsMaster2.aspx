<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="InterfaceDataElementsMaster2.aspx.vb" Inherits="WebApp.APlus.UI.Pages.InterfaceDataElementsMaster2"
    Title="Data Element Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblDataElement" runat="server" Text="Data Element:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtDataElement" runat="server" CssClass="Textbox_Entry" MaxLength="50"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqDataElement" runat="server" ErrorMessage="Enter Data Element"
                    ControlToValidate="txtDataElement" Display="None" 
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="150px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSource" runat="server" Text="Source:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtSource" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSource" runat="server" ErrorMessage="Enter Source"
                    ControlToValidate="txtSource" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAppSource" runat="server" Text="App Source:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAppSource" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAppSource" runat="server" ErrorMessage="Enter App Source"
                    ControlToValidate="txtAppSource" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAppKPIKey" runat="server" Text="App KPI Key:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAppKPIKey" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAppKPIKey" runat="server" ErrorMessage="Enter App KPI Key"
                    ControlToValidate="txtAppKPIKey" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAppMill" runat="server" Text="App Mill:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAppMill" runat="server" CssClass="Textbox_Entry" MaxLength="10"
                    Width="100px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAppMill" runat="server" ErrorMessage="Enter App Mill"
                    ControlToValidate="txtAppMill" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAppIdentKey" runat="server" Text="App Ident Key:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAppIdentKey" runat="server" CssClass="Textbox_Entry" MaxLength="1"
                    Width="25px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAppIdentKey" runat="server" ErrorMessage="Enter App Ident Key"
                    ControlToValidate="txtAppIdentKey" Display="None" 
                    CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAppIdent" runat="server" Text="App Ident:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAppIdent" runat="server" CssClass="Textbox_Entry" MaxLength="25"
                    Width="259px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAppIdent" runat="server" ErrorMessage="Enter App Ident"
                    ControlToValidate="txtAppIdent" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblUOM" runat="server" Text="UOM:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtUOM" runat="server" CssClass="Textbox_Entry" MaxLength="15"
                    Width="150px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqUOM" runat="server" ErrorMessage="Enter UOM"
                    ControlToValidate="txtUOM" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblActive" runat="server" Text="Active:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckActive" runat="server" />
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblDailyValue" runat="server" Text="Daily Value:" 
                    CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckDailyValue" runat="server" />
            </td>
        </tr>
    </table>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons" class="Table_Default">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td>
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
</asp:Content>
