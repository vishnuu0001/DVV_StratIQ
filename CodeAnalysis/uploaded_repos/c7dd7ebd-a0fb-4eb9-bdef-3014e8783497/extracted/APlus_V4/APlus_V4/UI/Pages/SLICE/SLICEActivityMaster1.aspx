<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityMaster1"
    Title="SLICE Activity Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register TagPrefix="CC1" Namespace="WebApp.APlus.UI.CustomControls" %>
<%@ Register Src="../../UserControls/WorkcenterSubHeader.ascx" TagName="WorkcenterSubHeader"
    TagPrefix="uc1" %>
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
            <uc1:WorkcenterSubHeader ID="WorkcenterSubHeader1" runat="server"></uc1:WorkcenterSubHeader>
            <br />
            <asp:Label ID="lblSLICEActivityGroup" runat="server" Text="SLICE Activity Group:"
                CssClass="Label_Left_8PT"></asp:Label><asp:HyperLink ID="hlnkShowSLICEActivityGroup"
                    runat="server" Font-Bold="True" Target="_blank" Text="HyperLink" CssClass="Link_Default"></asp:HyperLink>
            <br />
            <br />
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSLICEActivityMasterByActivityGroupMasterID"
                FormName="SLICE Activity Maintenance" NewLinkCaption="SLICE Activity" ProgramMode="SLICEActivityMasterMode"
                ProgramName="SLICEActivityMaster1" RedirectProgramName="SLICEActivityMaster2"
                ShowExport="False" AlternatingRows="True" RaiseExitEvent="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SLICEActivityID" SortExpression="SLICEActivityID"
                        HeaderText="Activity ID" Visible="False" />
                    <CC1:MasterControlField DataField="SAPEntity" SortExpression="SAPEntity" HeaderText="Entity#" />
                    <CC1:MasterControlField DataField="Entity" SortExpression="Entity" Visible="True"
                        HeaderText="Component" />
                    <CC1:MasterControlField DataField="Location" SortExpression="Location" HeaderText="Location" />
                    <CC1:MasterControlField DataField="PresentationSequence" SortExpression="PresentationSequence"
                        HeaderText="Seq" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Position" SortExpression="Position"
                        HeaderText="Position" />
                    <CC1:MasterControlField ShowReturns="True" DataField="SLICEType" SortExpression="SLICEType"
                        HeaderText="Type" />
                    <CC1:MasterControlField ShowReturns="True" DataField="SLICEActivityGroup" SortExpression="SLICEActivityGroup"
                        HeaderText="SLICE Acivity Group" />
                    <CC1:MasterControlField ShowReturns="False" DataField="SLICEFrequency" Visible="true"
                        SortExpression="Frequency" HeaderText="Target Deviation" />
                    <CC1:MasterControlField ShowReturns="False" DataField="LinkURL" Visible="true" SortExpression="LinkURL"
                        HeaderText="Link URL" />
                    <CC1:MasterControlField ShowReturns="False" DataField="DesiredCondition" Visible="true"
                        SortExpression="DesiredCondition" HeaderText="Desired Condition" />
                    <CC1:MasterControlField ShowReturns="False" DataField="Results" Visible="true" SortExpression="Results"
                        HeaderText="Results" />
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
