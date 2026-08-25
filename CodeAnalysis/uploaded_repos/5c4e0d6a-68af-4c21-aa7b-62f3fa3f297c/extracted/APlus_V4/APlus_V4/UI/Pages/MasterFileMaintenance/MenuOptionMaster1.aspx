<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="MenuOptionMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.MenuOptionMaster1"
    Title="Menu Option Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelMenuOptionMaster"
                FormName="Menu Option Master Maintenance" NewLinkCaption="Menu Option" ProgramMode="MenuOptionMode"
                ProgramName="MenuOptionMaster1" RedirectProgramName="MenuOptionMaster2" ShowExport="True"
                Translate="True" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="Menu" HeaderText="Menu" ShowReturns="False" SortExpression="Menu">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="OptionValue" HeaderText="Option" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="OptionDescription" HeaderText="Description" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Program" HeaderText="Program" ShowReturns="False"
                        SortExpression="Program">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="LinkURL" HeaderText="URL" ShowReturns="False">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ProgramGroup" HeaderText="Program Group" ShowReturns="False"
                        SortExpression="ProgramGroup">
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
