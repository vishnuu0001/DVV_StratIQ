<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="UserSiteMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.UserSiteMaster1"
    Title="User Site Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelUserSiteMaster"
                FormName="User Site Master" NewLinkCaption="User Site Master" ProgramMode="UserSiteMasterMode"
                ProgramName="UserSiteMaster1" RedirectProgramName="UserSiteMaster2" ShowEdit="True"
                ShowExport="True" Translate="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SiteID" HeaderText="SiteID" ShowReturns="False"
                        Visible="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserID" HeaderText="User ID" ShowReturns="False"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="UserName" HeaderText="User" ShowReturns="False"
                        SortExpression="UserName">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" ShowReturns="False" SortExpression="Site">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowTeamView" HeaderText="Team View" ShowReturns="False"
                        SortExpression="AllowTeamView">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowTeamEdit" HeaderText="Team Edit" ShowReturns="False"
                        SortExpression="AllowTeamEdit">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIView" HeaderText="KPI View" ShowReturns="False"
                        SortExpression="AllowKPIView">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AllowKPIEdit" HeaderText="KPI Edit" ShowReturns="False"
                        SortExpression="AllowKPIEdit">
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
