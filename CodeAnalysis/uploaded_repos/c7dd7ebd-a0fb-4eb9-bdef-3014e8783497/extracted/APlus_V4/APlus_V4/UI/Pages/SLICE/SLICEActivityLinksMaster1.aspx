<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="SLICEActivityLinksMaster1.aspx.vb" Inherits="WebApp.APlus.UI.SLICE.SLICEActivityLinksMaster1"
    Title="SLICE Activity Links Master" %>

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
            <CC1:MasterControl ID="MasterControl1" runat="server" CommandText="spSelSLICEActivityLinkByLinkID"
                FormName="SLICE Activity Link Maintenance" NewLinkCaption="SLICE Activity Link"
                ProgramMode="SLICEActivityLinkMasterMode" ProgramName="SLICEActivityLinksMaster1"
                RedirectProgramName="SLICEActivityLinksMaster2" ShowExport="False" AlternatingRows="True">
                <GridColumns>
                    <CC1:MasterControlField DataField="SLICEActivityLinkID" SortExpression="SLICEActivityLinkID"
                        HeaderText="SLICE Activity Link ID" Visible="False" />
                    <CC1:MasterControlField DataField="SLICEActivityGroup" SortExpression="SLICEActivityGroup"
                        HeaderText="Checksheet Template" />
                    <CC1:MasterControlField DataField="Entity" SortExpression="Entity" Visible="True"
                        HeaderText="Entity" />
                    <CC1:MasterControlField DataField="SLICEType" SortExpression="SLICEType" HeaderText="SLICE Type"
                        ShowReturns="true" />
                    <CC1:MasterControlField ShowReturns="False" DataField="SLICEActivityLinkType" SortExpression="SLICEActivityLinkType"
                        HeaderText="SLICE Activity Link Type" />
                    <CC1:MasterControlField ShowReturns="True" DataField="LinkDescription" SortExpression="LinkDescription"
                        HeaderText="Link Description" />
                    <CC1:MasterControlField ShowReturns="False" DataField="LinkURL" Visible="true" SortExpression="LinkURL"
                        HeaderText="Link URL" />
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
