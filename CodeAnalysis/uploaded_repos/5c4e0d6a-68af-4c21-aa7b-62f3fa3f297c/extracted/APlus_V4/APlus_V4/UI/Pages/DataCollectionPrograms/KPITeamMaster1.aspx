<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="KPITeamMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.KPITeamMaster1"
    Title="KPI Team Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelKPITeamMasterByKPI"
                FormName="KPI Team Maintenance" NewLinkCaption="KPI Team" ProgramMode="KPITeamMasterMode"
                ProgramName="KPITeamMaster1" RedirectProgramName="KPITeamMaster2" AlternatingRows="True"
                ShowExport="True" ShowView="false" Translate="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="KPIID" HeaderText="KPIID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TeamID" HeaderText="TeamID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="KPI" HeaderText="KPI" ShowReturns="False" SortExpression="KPI|Team">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Team" HeaderText="Team" ShowReturns="False" SortExpression="Team|KPI">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Description" HeaderText="Team Status" ShowReturns="False" SortExpression="Description|Team">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIView" HeaderText="Allow View" ShowReturns="False"
                        SortExpression="AllowKPIView|KPI">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="Allow Edit" ShowReturns="False"
                        SortExpression="AllowKPIEdit|KPI">
                    </CC1:MasterControlField>
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
