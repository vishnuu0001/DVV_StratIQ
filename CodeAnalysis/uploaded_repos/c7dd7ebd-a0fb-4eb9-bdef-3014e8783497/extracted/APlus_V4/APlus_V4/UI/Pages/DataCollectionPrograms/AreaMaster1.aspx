<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AreaMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AreaMaster1"
    Title="Area Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowView="False" ShowAdd="True"
                ShowDelete="True" ShowEdit="True" NewLinkCaption="Area" RedirectProgramName="AreaMaster2"
                FormName="Area Master Maintenance" ProgramName="TrackerTypes1" CommandText="spSelAreaMaster"
                ProgramMode="AreaMaintenanceMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="AreaID" HeaderText="AreaID" />
                    <CC1:MasterControlField DataField="Site" SortExpression="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="Area" SortExpression="Area" HeaderText="Area" />
                    <CC1:MasterControlField DataField="AreaAbbrev" SortExpression="AreaAbbrev" HeaderText="Area Abbrev" />
                    <CC1:MasterControlField DataField="Active" SortExpression="Active" HeaderText="Active" />
                    <CC1:MasterControlField DataField="AreaInAreaGroup" SortExpression="AreaInAreaGroup"
                        HeaderText="Associated with Area Group" />
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
