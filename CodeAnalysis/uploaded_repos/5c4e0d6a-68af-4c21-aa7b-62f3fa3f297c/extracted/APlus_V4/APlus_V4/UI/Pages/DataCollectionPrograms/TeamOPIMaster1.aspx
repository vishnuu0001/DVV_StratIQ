<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="TeamOPIMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.TeamOPIMaster1"
    Title="Team OPI Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="[spSelTeamOPIMaster]"
                ProgramName="TeamOPIMaintenance" FormName="Team OPI Maintenance" RedirectProgramName="TeamOPIMaintenance2"
                ShowView="True" ShowEdit="True" ShowDelete="True" ShowAdd="True" NewLinkCaption="Team OPI"
                AlternatingRows="True" ProgramMode="OPIMode" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false" />
                    <CC1:MasterControlField DataField="Team" SortExpression="Team" HeaderText="Team" />
                    <CC1:MasterControlField DataField="OPI" SortExpression="OPI" HeaderText="OPI" />
                    <CC1:MasterControlField DataField="PrimaryOPI" SortExpression="PrimaryOPI" HeaderText="Primary OPI" />
                    <CC1:MasterControlField DataField="Target" SortExpression="Target" HeaderText="Target" />
                    <CC1:MasterControlField DataField="Historic" SortExpression="Historic" HeaderText="Historic" />
                    <CC1:MasterControlField DataField="HistoricStartDate" SortExpression="HistoricStartDate"
                        HeaderText="Historic Start Date" />
                    <CC1:MasterControlField DataField="HistoricEndDate" SortExpression="HistoricEndDate"
                        HeaderText="Historic End Date" />
                    <CC1:MasterControlField DataField="ExpectedBenefit" SortExpression="ExpectedBenefit"
                        HeaderText="Expected Benefit" />
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
