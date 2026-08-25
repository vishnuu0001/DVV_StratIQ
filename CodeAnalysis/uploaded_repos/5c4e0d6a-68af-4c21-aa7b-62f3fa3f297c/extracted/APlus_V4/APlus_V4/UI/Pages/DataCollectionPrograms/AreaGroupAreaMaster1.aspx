<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AreaGroupAreaMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AreaGroupAreaMaster1"
    Title="Area Group Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" ShowAdd="True" ShowDelete="True"
                ShowView="false" ShowEdit="False" NewLinkCaption="Area Group Area" RedirectProgramName="AreaGroupAreaMaster2"
                FormName="Area Group Maintenance" ProgramName="AreaGroupAreaMaster1" CommandText="spSelAreaGroupAreaMaster"
                ProgramMode="AreaGroupAreaMasterMode" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField Visible="False" DataField="AreaGroupID" HeaderText="AreaGroup" />
                    <CC1:MasterControlField Visible="False" DataField="AreaID" HeaderText="Area" />
                    <CC1:MasterControlField DataField="AreaGroup" SortExpression="AreaGroup" HeaderText="Area Group" />
                    <CC1:MasterControlField DataField="Area" SortExpression="Area" HeaderText="Area" />
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
