<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserMaster7.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserMaster7"
    Title="User Maintenance" EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/ApplicationSpecialStyles.css" rel="stylesheet" />
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <asp:UpdateProgress ID="UpdateProgress1" runat="server" DisplayAfter="50">
        <ProgressTemplate>
            <div style="position: absolute; z-index: 1;">
                <asp:Image runat="server" ID="imgWait" Height="48" Width="48" ImageUrl="~/images/barcircle.gif" />
                <asp:AlwaysVisibleControlExtender ID="imgWait_AlwaysVisibleControlExtender" runat="server"
                    Enabled="True" TargetControlID="imgWait" VerticalSide="Middle" HorizontalSide="Center">
                </asp:AlwaysVisibleControlExtender>
            </div>
        </ProgressTemplate>
    </asp:UpdateProgress>
    <asp:UpdatePanel ID="UpdatePanel1" runat="server">
        <ContentTemplate>
            <table width="100%" class="rowCount_table">
                <tr>
                    <td class="rowCount_row">
                        <asp:Label ID="lblRecords" runat="server" Visible="True"></asp:Label>
                    </td>
                </tr>
            </table>
            <table style="width: 100%">
                <tr>
                    <td>
                        <asp:GridView runat="server" ID="grdUsers" Width="100%" AutoGenerateColumns="False"
                            SkinID="GridView">
                            <Columns>
                                <asp:BoundField DataField="LastName" HeaderText="Last Name"></asp:BoundField>
                                <asp:BoundField DataField="FirstName" HeaderText="First Name"></asp:BoundField>
                                <asp:BoundField DataField="MiddleInitial" HeaderText="Middle"></asp:BoundField>
                                <asp:BoundField DataField="UserID" HeaderText="User ID"></asp:BoundField>
                                <asp:BoundField DataField="Site" HeaderText="Site"></asp:BoundField>
                                <asp:BoundField DataField="EmailAddress" HeaderText="Email"></asp:BoundField>
                                <asp:ButtonField Text="Add to User Master" CommandName="AddRow">
                                    <ItemStyle ForeColor="Blue"></ItemStyle>
                                </asp:ButtonField>
                                <asp:TemplateField>
                                    <ItemTemplate>
                                        <asp:CheckBox ID="chkSelected" runat="server" />
                                    </ItemTemplate>
                                </asp:TemplateField>
                            </Columns>
                        </asp:GridView>
                    </td>
                </tr>
            </table>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
    <table id="Table3" class="Table_Default">
        <tr>
            <td style="width: 110px">
                <asp:Button ID="btnExit" runat="server" CausesValidation="False" Text="Exit" CssClass="Button_Default">
                </asp:Button>
            </td>
            <td>
                <asp:Button ID="btnProcessSelected" runat="server" CausesValidation="False" CssClass="Button_Variable"
                    Text="Process All Selected" />
            </td>
        </tr>
    </table>
</asp:Content>
