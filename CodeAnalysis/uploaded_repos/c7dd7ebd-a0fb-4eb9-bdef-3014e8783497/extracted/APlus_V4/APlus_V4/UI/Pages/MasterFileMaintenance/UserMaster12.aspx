<%@ Page Language="vb" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="~/UI/Pages/MasterFileMaintenance/UserMaster12.aspx.vb"
    Inherits="WebApp.APlus.UI.Pages.UserMaster12" Title="User Master Attendance Conflicts"
    EnableTheming="true" StylesheetTheme="APlus_Default" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="server">
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
            <table runat="server" id="Table1" class="Table_Default">
                <tr>
                    <td>
                        <asp:GridView ID="gvUsers" runat="server" AutoGenerateColumns="False" SkinID="GridView"
                            Width="100%">
                            <Columns>
                                <asp:BoundField DataField="LastName" HeaderText="Last Name" ReadOnly="True" />
                                <asp:BoundField DataField="FirstName" HeaderText="First Name" ReadOnly="True" />
                                <asp:BoundField DataField="UserID" HeaderText="User ID" ReadOnly="True" />
                                <asp:BoundField DataField="Site" HeaderText="Site" ReadOnly="True" />
                                <asp:BoundField DataField="EmailAddress" HeaderText="Email" />
                                <asp:BoundField DataField="Title" HeaderText="Title" ReadOnly="True" />
                                <asp:BoundField DataField="Active" HeaderText="A+ Active" ReadOnly="True" />
                                <asp:BoundField DataField="AttendanceActive" HeaderText="Attendance Active" ReadOnly="True" />
                                <asp:BoundField DataField="AttendanceConflictInformation" HeaderText="Conflict" HtmlEncode="False" />
                                <asp:ButtonField CommandName="EditRow" Text="Edit" />
                                <asp:TemplateField HeaderText="Copy Title" ItemStyle-HorizontalAlign="Center">
                                    <ItemTemplate>
                                        <asp:CheckBox ID="chkSelected" runat="server" Enabled="true" />
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
            <td style="width: 150px">
                <asp:Button ID="btnProcessSelected" runat="server" CssClass="Button_Variable" Text="Process All Selected"
                    CausesValidation="False"></asp:Button>
            </td>
            <td>
                <asp:Button ID="btnSelectAll" runat="server" CssClass="Button_Default" Text="Select All"
                    CausesValidation="False"></asp:Button>
            </td>
        </tr>
    </table>
</asp:Content>
