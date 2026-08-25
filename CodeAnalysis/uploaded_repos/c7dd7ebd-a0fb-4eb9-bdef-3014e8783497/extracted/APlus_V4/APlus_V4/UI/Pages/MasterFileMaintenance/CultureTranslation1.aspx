<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="CultureTranslation1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.CultureTranslation1"
    Title="Culture Translation Maintenance" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelResourceValues"
                FormName="Culture Translation Master Maintenance" NewLinkCaption="Culture Translation"
                ProgramMode="CultureTranslationMode" ProgramName="CultureTranslationMaster1"
                RedirectProgramName="CultureTranslation2" ShowView="False" Translate="True" AlternatingRows="True"
                ShowFunctionButtonOne="True" ShowExport="true" FunctionButtonOneLabel="Clear Application Cache">
                <GridColumns>
                    <CC1:MasterControlField DataField="CultureCode" HeaderText="Culture" ShowReturns="False"
                        SortExpression="CultureCode">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ResourceKey" HeaderText="Key" ShowReturns="False"
                        SortExpression="ResourceKey">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="DefaultValue" HeaderText="Default" ShowReturns="False"
                        SortExpression="DefaultValue">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ResourceValue" HeaderText="Translation" ShowReturns="False"
                        SortExpression="ResourceValue">
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
