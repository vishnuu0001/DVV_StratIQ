<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="CultureMaster1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CultureMaster1"
    Title="Culture Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelCultureMaster"
                FormName="Culture Master Maintenance" NewLinkCaption="Culture" ProgramMode="CultureMasterMode"
                ProgramName="CultureMaster1" RedirectProgramName="CultureMaster2" ShowEdit="True"
                ShowExit="True" ShowExport="True" AlternatingRows="True" ShowView="False">
                <GridColumns>
                    <CC1:MasterControlField DataField="CultureID" HeaderText="CultureID" ShowReturns="False"
                        SortExpression="CultureID">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CultureCode" HeaderText="Culture" ShowReturns="False"
                        SortExpression="CultureCode">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CultureDescription" HeaderText="Description" ShowReturns="False"
                        SortExpression="CultureDescription">
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
