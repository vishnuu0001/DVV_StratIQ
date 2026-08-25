<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIValues1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIValues1"
    Title="OPI Data Entry" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="asp" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
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
            <table id="Table1" class="Table_Default">
                <tr>
                    <td align="left">
                        <asp:RadioButtonList ID="rblOPI" runat="server" RepeatDirection="Horizontal" Width="480px"
                            AutoPostBack="True">
                            <asp:ListItem Value="100" Text="Show Top 100 Records" Selected="True"></asp:ListItem>
                            <asp:ListItem Value="500" Text="Show Top 500 Records"></asp:ListItem>
                            <asp:ListItem Value="All" Text="Show All Records"></asp:ListItem>
                        </asp:RadioButtonList>
                    </td>
                </tr>
            </table>
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelTeamOPIValues"
                FormName="Team OPI Values" NewLinkCaption="Team OPI Value" ProgramName="TeamOPIValues1"
                RedirectProgramName="TeamOPIValues2" AlternatingRows="True" ShowRowCount="True"
                InitialSort="OPIValueDateTime" InitialSortOrder="desc" ProgramMode="TeamOPIValueMode"
                FunctionButtonOneLabel="Import from Excel" ShowFunctionButtonOne="True" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamOPIValueID" HeaderText="TeamOPIValueID" Visible="false" />
                    <CC1:MasterControlField DataField="OPIValueDateTime" HeaderText="Date / Time" SortExpression="OPIValueDateTime"
                        ShowReturns="False" HtmlEncode="False" />
                </GridColumns>
            </CC1:MasterControl>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
