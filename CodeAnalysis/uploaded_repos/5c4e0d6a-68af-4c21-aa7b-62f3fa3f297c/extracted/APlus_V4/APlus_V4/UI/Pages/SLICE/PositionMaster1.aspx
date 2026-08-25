<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="PositionMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.PositionMaster1"
    Title="Position Master" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelPositionMaster"
                FormName="Position Master" NewLinkCaption="Position Master" ProgramMode="PositionMasterMode"
                ProgramName="PositionMaster1" RedirectProgramName="PositionMaster2" ShowExport="False"
                AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField ShowReturns="False" DataField="PositionID" SortExpression="PositionID"
                        HeaderText="Position ID" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Workcenter" SortExpression="Workcenter"
                        HeaderText="Entity" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Position" SortExpression="Position"
                        HeaderText="Location" />
                    <CC1:MasterControlField ShowReturns="False" DataField="WorkcenterID" Visible="False"
                        HeaderText="WorkcenterID" />
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
