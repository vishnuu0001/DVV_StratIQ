<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyActions1.aspx.vb" Inherits="WebApp.APlus.UI.Pages.AnomalyActions1"
    Title="Anomaly Actions" %>

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
            <CC1:MasterControl ID="mcAnomaly" runat="server" ShowAdd="false" ShowDelete="false"
                Translate="true" ShowView="false" ShowEdit="false" 
                NewLinkCaption="Anomaly" RedirectProgramName="AnomalyMaster2"
                FormName="Anomaly Maintenance" ProgramName="AnomalyMaster1" CommandText="spSelAnomalyMasterByID"
                ProgramMode="AnomalyMode" AlternatingRows="True" PrimaryControl="false">
                <GridColumns>
                    <CC1:MasterControlField DataField="AnomalyID" HeaderText="ID" />
                    <CC1:MasterControlField DataField="Site" HeaderText="Site" />
                    <CC1:MasterControlField DataField="AnomalyType" HeaderText="Type" />
                    <CC1:MasterControlField DataField="Anomaly" HeaderText="Anomaly" />
                    <CC1:MasterControlField DataField="Subject" HeaderText="Description" />
                    <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User" />
                    <CC1:MasterControlField DataField="Observations" HeaderText="Observations" ShowReturns="true" />
                    <CC1:MasterControlField DataField="ClosedDateTime" HeaderText="Closed" />
                    <CC1:MasterControlField DataField="CreatedUser" HeaderText="Created By" />
                    <CC1:MasterControlField DataField="CreatedDateTime" HeaderText="Created" />
                    <CC1:MasterControlField DataField="ResponsibleUserID" HeaderText="ResponsibleUserID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CreatedUserID" HeaderText="CreatedUserID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="EditAnomaly" HeaderText="EditAnomaly" Visible="false">
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <asp:Label ID="lblAnomalyActions" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomaly Actions</asp:Label>
            <CC1:MasterControl ID="mcActions" runat="server" ShowAdd="True" ShowDelete="True"
                Translate="true" ShowEdit="True" NewLinkCaption="Anomaly Action" RedirectProgramName="AnomalyActions2"
                FormName="Anomaly Actions" ProgramName="AnomalyActions1" CommandText="spSelAnomalyActions"
                ShowExport="false" ProgramMode="AnomalyActionMode" AlternatingRows="True" ShowFunctionButtonOne="true"
                FunctionButtonOneLabel="New Anomaly Cause">
                <GridColumns>
                    <CC1:MasterControlField DataField="AnomalyActionID" HeaderText="AnomalyActionID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyCause" HeaderText="Cause" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ActionWhat" HeaderText="What" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ActionWhere" HeaderText="Where">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ActionWhy" HeaderText="Why" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ActionHow" HeaderText="How" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="TargetDate" HeaderText="Target Date" HtmlEncode="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="Actions" HeaderText="Actions" HtmlEncode="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ClosedDate" HeaderText="Closed Date" HtmlEncode="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ResponsibleUserID" HeaderText="ResponsibleUserID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyResponsibleUserID" HeaderText="AnomalyResponsibleUserID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CreatedUserID" HeaderText="CreatedUserID" Visible="false">
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <asp:Label ID="lblAnomalyCauses" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomaly Causes</asp:Label>
            <CC1:MasterControl ID="mcCauses" runat="server" ShowDelete="true" ShowView="false"
                Translate="true" ShowEdit="true" ShowAdd="false" ShowExport="false" PrimaryControl="false"
                NewLinkCaption="Anomaly Type" RedirectProgramName="AnomalyActions1" FormName="Anomaly Actions"
                ProgramName="AnomalyActions1" CommandText="spSelAnomalyCauses" ProgramMode="Mode"
                AlternatingRows="True" ShowExit="False">
                <GridColumns>
                    <CC1:MasterControlField DataField="AnomalyCauseID" HeaderText="AnomalyCauseID" Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyCause" HeaderText="Cause" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyCauseAnalysis" HeaderText="Analysis" ShowReturns="true">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="AnomalyActions" HeaderText="Actions">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="ResponsibleUserID" HeaderText="ResponsibleUserID"
                        Visible="false">
                    </CC1:MasterControlField>
                    <CC1:MasterControlField DataField="CreatedUserID" HeaderText="CreatedUserID" Visible="false">
                    </CC1:MasterControlField>
                </GridColumns>
            </CC1:MasterControl>
            <br />
            <br />
            <asp:Label ID="lblAnomalyAttachments" runat="server" CssClass="HeaderTitleText" Font-Bold="True">Anomaly Attachments</asp:Label>
            <asp:GridView ID="gvAttachments" runat="server" AutoGenerateColumns="False" EmptyDataText="No Attachments"
                Width="480px" CellPadding="3" CellSpacing="1">
                <HeaderStyle HorizontalAlign="left" BackColor="#41519a" ForeColor="#ffffff" Font-Size="8pt"
                    Font-Bold="true" VerticalAlign="Top" />
                <RowStyle BackColor="#f5f5f5" Font-Size="8pt" ForeColor="000000" VerticalAlign="Top"
                    HorizontalAlign="Left" />
                <AlternatingRowStyle BackColor="#e7e7e7" Font-Size="8pt" ForeColor="000000" VerticalAlign="Top"
                    HorizontalAlign="Left" />
                <EmptyDataRowStyle BackColor="#DEDFDE" Font-Bold="true" ForeColor="Red" Font-Size="10pt"
                    HorizontalAlign="Left" VerticalAlign="Top" />
                <Columns>
                    <asp:TemplateField HeaderText="Attachment">
                        <HeaderStyle HorizontalAlign="left" />
                        <ItemStyle HorizontalAlign="left" />
                        <ItemTemplate>
                            <asp:Image runat="server" ImageUrl="~/images/small_mail_attachment.gif" ID="imgAttach" />
                            <asp:LinkButton ID="LinkButton1" runat="server" CausesValidation="false" CommandName="ViewAttachment"
                                Text='<%# DataBinder.Eval(Container.DataItem, "FileName") %>' CommandArgument='<%# DataBinder.Eval(Container.DataItem, "AttachmentID") %>'></asp:LinkButton>
                        </ItemTemplate>
                    </asp:TemplateField>
                </Columns>
            </asp:GridView>
            <asp:Panel ID="pnlAddAttachment" runat="server" Visible="False">
                <table id="tbButtons1" style="width: 480px" cellspacing="5" width="480" border="0">
                    <tr>
                        <td>
                            <asp:Button ID="btnAttach" runat="server" Text="Add Attachment" 
                                CssClass="Button_Variable">
                            </asp:Button>
                        </td>
                    </tr>
                </table>
            </asp:Panel>
            <asp:Timer ID="Timer1" runat="server" Interval="50">
            </asp:Timer>
        </ContentTemplate>
        <Triggers>
            <asp:AsyncPostBackTrigger ControlID="Timer1" EventName="Tick" />
        </Triggers>
    </asp:UpdatePanel>
</asp:Content>
