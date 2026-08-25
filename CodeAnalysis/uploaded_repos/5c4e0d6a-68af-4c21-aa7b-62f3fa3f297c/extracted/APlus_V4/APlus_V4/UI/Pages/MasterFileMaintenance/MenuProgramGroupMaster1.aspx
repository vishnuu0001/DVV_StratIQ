<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MenuProgramGroupMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MenuProgramGroupMaster1"
    Title="Menu Program Group Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelMenuProgramGroupMaster"
                FormName="Menu Program Group Master Maintenance" NewLinkCaption="Menu Program Group"
                ProgramMode="MenuProgramGroupMode" ProgramName="MenuProgramGroupMaster1" RedirectProgramName="MenuProgramGroupMaster2"
                ShowExport="True" Translate="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Menu" HeaderText="Menu" ShowReturns="False" SortExpression="Menu">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ProgramGroup" HeaderText="Program Group" ShowReturns="False"
                        SortExpression="ProgramGroup">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="MenuColumn" HeaderText="Column" ShowReturns="False"
                        SortExpression="MenuColumn">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="SortOrder" HeaderText="Sort Order" ShowReturns="False"
                        SortExpression="SortOrder">
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
