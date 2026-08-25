<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="InternetLinks1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.InternetLinks1"
    Title="Internet Links" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/AttachmentStyle.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <br />
    <div class="grid">
        <div class="rounded">
            <div class="top-outer">
                <div class="top-inner">
                    <div class="top">
                        <h2>
                            <asp:Label ID="lblInfo" runat="server" Text="Label"></asp:Label></h2>
                    </div>
                </div>
            </div>
            <div class="mid-outer">
                <div class="mid-inner">
                    <div class="mid">
                        <asp:GridView ID="gvInternetLinks" runat="server" AutoGenerateColumns="False" CssClass="datatable"
                            CellPadding="0" BorderWidth="0px" GridLines="None" ShowHeader="False">
                            <RowStyle CssClass="row" />
                            <Columns>
                                <asp:TemplateField HeaderText="" ShowHeader="False">
                                    <ItemTemplate>
                                        <asp:LinkButton ID="LinkButton1" runat="server" CausesValidation="false" CommandName=""
                                            Text='<%# Eval("Description") %>' OnClientClick='<%# Eval("LinkUrl") %>' ToolTip='<%# Eval("Url") %>'></asp:LinkButton>
                                    </ItemTemplate>
                                    <HeaderStyle CssClass="first" />
                                    <ItemStyle CssClass="first" />
                                </asp:TemplateField>
                            </Columns>
                        </asp:GridView>
                    </div>
                </div>
            </div>
            <div class="bottom-outer">
                <div class="bottom-inner">
                    <div class="bottom">
                    </div>
                </div>
            </div>
        </div>
    </div>
    <br />
    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" CausesValidation="False"
        Text="Exit"></asp:Button>
</asp:Content>
