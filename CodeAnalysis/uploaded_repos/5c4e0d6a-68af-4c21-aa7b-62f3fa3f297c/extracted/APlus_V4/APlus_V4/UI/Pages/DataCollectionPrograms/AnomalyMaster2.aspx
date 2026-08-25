<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="AnomalyMaster2.aspx.vb" EnableEventValidation="false"
    Inherits="WebApp.APlus.UI.Pages.AnomalyMaster2" Title="Anomaly Maintenance" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<%@ Register Src="../../UserControls/TransactionHistory.ascx" TagName="TransactionHistory"
    TagPrefix="uc1" %>
<%@ Register Assembly="AjaxControlToolkit" Namespace="AjaxControlToolkit" TagPrefix="CC1" %>
<%@ Register Namespace="WebApp.APlus.UI.CustomControls" TagPrefix="CC2" %>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentHeader" runat="Server">
    <link type="text/css" href="../../../Styles/CalanderStyle.css" rel="stylesheet" />
    <style type="text/css">
        .style1
        {
            width: 150px;
        }
        .style2
        {
            width: 200px;
        }
    </style>
</asp:Content>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <script type="text/javascript" language="javascript" src="../../../Scripts/jquery.functions.js"></script>
    <script type="text/javascript" language="javascript">
        $(document).ready(function () {
            $("textarea[name*='txtExpand']").TextAreaExpander();
        });
    </script>
    <table class="Table_Default" id="Table1">
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAnomalyID" runat="server" Text="Anomaly ID:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomalyID" runat="server" CssClass="Textbox_Display" MaxLength="3"
                    Width="31px" ReadOnly="True"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblSite" runat="server" Text="Site:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlSite" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtSite" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqSite" runat="server" ErrorMessage="Select Site"
                    ControlToValidate="ddlSite" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAnomalyType" runat="server" Text="Anomaly Type:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlAnomalyType" runat="server" Width="325px" CssClass="DropdownList_Entry">
                </asp:DropDownList>
                <asp:TextBox ID="txtAnomalyType" runat="server" Width="325px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAnomalyType" runat="server" ErrorMessage="Select Anomaly Type"
                    ControlToValidate="ddlAnomalyType" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblArea" runat="server" Text="Area:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlArea" runat="server" CssClass="DropdownList_Entry" Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtArea" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqArea" runat="server" ErrorMessage="Select Area"
                    ControlToValidate="ddlArea" Display="None"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblKPI" runat="server" Text="KPI:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlKPIID" runat="server" Width="325px" CssClass="DropdownList_Entry"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:TextBox ID="txtKPIID" runat="server" Width="325px" MaxLength="15" CssClass="Textbox_Display"
                    Visible="False" Height="16px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblAnomaly" runat="server" Text="Anomaly:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtAnomaly" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                    Width="450px"></asp:TextBox>
                <asp:RequiredFieldValidator ID="reqAnomaly" runat="server" ErrorMessage="Enter Anomaly"
                    ControlToValidate="txtAnomaly" Display="None" CssClass="Label_Left_8PT"></asp:RequiredFieldValidator>
            </td>
        </tr>
        <tr>
            <td style="width: 120px" valign="top">
                <asp:Label ID="lblDescription" runat="server" Text="Description:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtExpandSubject" runat="server" CssClass="Textbox_Entry" Width="400px"
                    MaxLength="600" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td colspan="2">
                &nbsp;
            </td>
        </tr>
        <div runat="server" id="pnlSGI" visible="false">
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblSGI" runat="server" Text="SGI:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:RadioButtonList ID="rblSGI" runat="server" RepeatDirection="Horizontal" Width="200px"
                        Height="16px">
                        <asp:ListItem Value="1">Yes</asp:ListItem>
                        <asp:ListItem Value="0">No</asp:ListItem>
                    </asp:RadioButtonList>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblChangeFEMEA" runat="server" Text="Change FEMEA:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:RadioButtonList ID="rblFEMEA" runat="server" RepeatDirection="Horizontal" Width="200px"
                        Height="16px">
                        <asp:ListItem Value="1">Yes</asp:ListItem>
                        <asp:ListItem Value="0">No</asp:ListItem>
                    </asp:RadioButtonList>
                </td>
            </tr>
            <tr>
                <td style="width: 120px">
                    <asp:Label ID="lblFEMEADescription" runat="server" Text="What:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtFEMEADescription" runat="server" CssClass="Textbox_Entry" MaxLength="100"
                        Width="450px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblFEMEAJustification" runat="server" Text="Justification:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandFEMEAJustification" runat="server" CssClass="Textbox_Entry"
                        Width="400px" MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblRiskAnalysis" runat="server" Text="Risk Analysis:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:RadioButtonList ID="rblRiskAnalysis" runat="server" RepeatDirection="Horizontal"
                        Width="200px">
                        <asp:ListItem Value="1">Applicable</asp:ListItem>
                        <asp:ListItem Value="0">Not Applicable</asp:ListItem>
                    </asp:RadioButtonList>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblRiskJustification" runat="server" Text="Justification:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandRiskJustification" runat="server" CssClass="Textbox_Entry"
                        Width="400px" MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblRiskResult" runat="server" Text="Risk Analysis Result:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:CheckBox ID="ckRiskResult1" runat="server" Text="Proposed Actions Reduce the Risk" /><br />
                    <asp:CheckBox ID="ckRiskResult2" runat="server" Text="Proposed Actions Keep the Current Risk" /><br />
                    <asp:CheckBox ID="ckRiskResult3" runat="server" Text="Proposed Actions Increase the Risk" />
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblRiskResultJustification" runat="server" Text="Justification:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandRiskResultJustification" runat="server" CssClass="Textbox_Entry"
                        Width="400px" MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblSystemAgainstError" runat="server" Text="System Against Error:"
                        CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandSystemAgainstError" runat="server" CssClass="Textbox_Entry"
                        Width="400px" MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td colspan="2">
                    &nbsp;
                </td>
            </tr>
        </div>
        <tr>
            <td>
                <asp:Label ID="lblResponsibleUser" runat="server" Text="Responsible User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:DropDownList ID="ddlResponsibleUser" runat="server" CssClass="DropdownList_Entry"
                    Width="194px">
                </asp:DropDownList>
                <asp:TextBox ID="txtResponsibleUser" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                    Width="184px" Visible="False"></asp:TextBox>
                &nbsp;
                <asp:DropDownList ID="ddlUserSite" runat="server" CssClass="DropdownList_Entry" Width="194px"
                    AutoPostBack="True">
                </asp:DropDownList>
                <asp:RequiredFieldValidator ID="reqResponsibleUser" runat="server" ErrorMessage="Select Responsible User"
                    ControlToValidate="ddlResponsibleUser" Display="None"></asp:RequiredFieldValidator>
                <CC1:ListSearchExtender ID="ddlResponsibleUser_ListSearchExtender" runat="server"
                    Enabled="True" TargetControlID="ddlResponsibleUser">
                </CC1:ListSearchExtender>
            </td>
        </tr>
        <div runat="server" id="pnlOrigins">
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblOrigin" runat="server" Text="Origin:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:DropDownList ID="ddlOrigins1" runat="server" CssClass="DropdownList_Entry" Width="194px"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOrigins1" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                        Width="184px" Visible="False"></asp:TextBox>
                    &nbsp;
                    <asp:DropDownList ID="ddlOrigins2" runat="server" CssClass="DropdownList_Entry" Width="194px"
                        AutoPostBack="True">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOrigins2" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                        Width="184px" Visible="False"></asp:TextBox>
                    &nbsp;
                    <asp:DropDownList ID="ddlOrigins3" runat="server" CssClass="DropdownList_Entry" Width="194px">
                    </asp:DropDownList>
                    <asp:TextBox ID="txtOrigins3" runat="server" CssClass="Textbox_Display" ReadOnly="True"
                        Width="184px" Visible="False"></asp:TextBox>
                </td>
            </tr>
        </div>
        <div runat="server" id="pnlClose">
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblObservations" runat="server" Text="Observations:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandObservations" runat="server" CssClass="Textbox_Entry" Width="400px"
                        MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblClosedDate" runat="server" Text="Closed Date:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtClosedDate" runat="server" Width="81" CssClass="Textbox_Display"
                        MaxLength="10" ReadOnly="True"></asp:TextBox>
                    <asp:CheckBox ID="ckClose" runat="server" Visible="False" />
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    &nbsp;
                </td>
                <td>
                    <asp:RadioButtonList ID="rblCancelled" runat="server" RepeatDirection="Horizontal"
                        Width="200px">
                        <asp:ListItem Value="0">Completed</asp:ListItem>
                        <asp:ListItem Value="1">Cancelled</asp:ListItem>
                    </asp:RadioButtonList>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    <asp:Label ID="lblEvaluation" runat="server" Text="Evaluation:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtExpandEvaluation" runat="server" CssClass="Textbox_Entry" Width="400px"
                        MaxLength="250" TextMode="MultiLine" Rows="2" Height="28px"></asp:TextBox>
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="middle">
                    <asp:Label ID="lblEvaluatedDate" runat="server" Text="Evaluated Date:" CssClass="Label_Left_8PT"></asp:Label>
                </td>
                <td>
                    <asp:TextBox ID="txtEvaluatedDate" runat="server" Width="81" CssClass="Textbox_Display"
                        MaxLength="10" ReadOnly="True"></asp:TextBox>
                    <asp:CheckBox ID="ckEvaluate" runat="server" Visible="False" />
                </td>
            </tr>
            <tr>
                <td style="width: 120px" valign="top">
                    &nbsp;
                </td>
                <td>
                    <asp:RadioButtonList ID="rblEffective" runat="server" RepeatDirection="Horizontal"
                        Width="204px">
                        <asp:ListItem Value="0">Effective</asp:ListItem>
                        <asp:ListItem Value="1">Ineffective</asp:ListItem>
                    </asp:RadioButtonList>
                </td>
            </tr>
        </div>
        <tr>
            <td style="width: 120px" valign="middle">
                <asp:Label ID="lblAutoGenerated" runat="server" Text="Auto Generated:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:CheckBox ID="ckAutoGenerated" runat="server" Enabled="False" />
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblCreatedDate" runat="server" Text="Created Date:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCreatedDate" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>
            </td>
        </tr>
        <tr>
            <td style="width: 120px">
                <asp:Label ID="lblCreatedUser" runat="server" Text="Created User:" CssClass="Label_Left_8PT"></asp:Label>
            </td>
            <td>
                <asp:TextBox ID="txtCreatedUser" runat="server" CssClass="Textbox_Display" MaxLength="50"
                    ReadOnly="True" Width="178px"></asp:TextBox>
            </td>
        </tr>
    </table>
    <asp:GridView ID="gvAttachments" runat="server" AutoGenerateColumns="False" EmptyDataText="No Attachments"
        Width="480px" CellPadding="3" CellSpacing="1" DataKeyNames="AttachmentID,FileName">
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
                    <asp:LinkButton ID="btnLink" runat="server" CausesValidation="false" CommandName="ViewAttachment"
                        Text="LinkButton"></asp:LinkButton>
                </ItemTemplate>
            </asp:TemplateField>
            <asp:TemplateField HeaderText="Delete" Visible="False">
                <HeaderStyle HorizontalAlign="right" />
                <ItemStyle HorizontalAlign="right" />
                <ItemTemplate>
                    <asp:ImageButton runat="server" CommandName="DeleteAttachment" ToolTip="Delete Attachment"
                        ID="btnDelete" ImageUrl="../../../images/delete.gif" CausesValidation="False" />
                </ItemTemplate>
            </asp:TemplateField>
            <asp:BoundField DataField="AttachmentID" Visible="false" />
            <asp:BoundField DataField="FileName" Visible="false" />
        </Columns>
    </asp:GridView>
    <asp:Panel ID="pnlAddAttachment" runat="server" Visible="False">
        <table id="tbButtons1" style="width: 480px" cellspacing="5" width="480" border="0">
            <tr>
                <td align="center">
                    <input id="fil" style="font-size: 8pt; width: 386px; font-family: Verdana; height: 24px"
                        type="file" size="45" name="fil" runat="server" />
                </td>
                <td align="center">
                    <asp:Button ID="btnAttach" runat="server" Width="74px" Font-Size="8pt" Text="Attach"
                        EnableViewState="False" CausesValidation="False" Height="24px" Font-Names="Microsoft Sans Serif">
                    </asp:Button>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel runat="server" ID="pnlGrids">
        <table width="100%">
            <tr>
                <td>
                    <br />
                    <asp:Label ID="lblAnomalyCauses" runat="server" Width="150px" Text="Anomaly Causes:"
                        CssClass="Label_Left_8PT"></asp:Label>
                </td>
            </tr>
            <tr>
                <td align="left">
                    <CC2:MasterControl ID="mcCauses" runat="server" AlternatingRows="True" CommandText="spSelAnomalyCauses"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="AnomalyMaster2"
                        RedirectProgramName="AnomalyMaster2" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="true" Width="100%">
                        <GridColumns>
                            <CC2:MasterControlField DataField="AnomalyCause" HeaderText="Cause" ShowReturns="False">
                            </CC2:MasterControlField>
                            <CC2:MasterControlField DataField="AnomalyCauseAnalysis" HeaderText="Analysis" ShowReturns="False">
                            </CC2:MasterControlField>
                            <CC2:MasterControlField DataField="AnomalyActions" HeaderText="Actions" ShowReturns="False">
                            </CC2:MasterControlField>
                        </GridColumns>
                    </CC2:MasterControl>
                </td>
            </tr>
            <tr>
                <td>
                    <br />
                    <asp:Label ID="lblAnomalyActions" runat="server" Width="150px" Text="Anomaly Actions:"
                        CssClass="Label_Left_8PT"></asp:Label>
                </td>
            </tr>
            <tr>
                <td align="left">
                    <CC2:MasterControl ID="mcActions" runat="server" AlternatingRows="True" CommandText="spSelAnomalyActions"
                        DeleteLabel="" EditLabel="" PrimaryControl="False" ProgramName="AnomalyMaster2"
                        RedirectProgramName="AnomalyMaster2" ShowAdd="False" ShowDelete="False" ShowEdit="False"
                        ShowExit="False" ShowExport="False" ShowView="False" Translate="true" Width="100%">
                        <GridColumns>
                            <CC2:MasterControlField DataField="AnomalyCause" HeaderText="Cause" ShowReturns="False" />
                            <CC2:MasterControlField DataField="ActionWhat" HeaderText="What" ShowReturns="False" />
                            <CC2:MasterControlField DataField="ActionWhere" HeaderText="Where" ShowReturns="False" />
                            <CC2:MasterControlField DataField="ActionWhy" HeaderText="Why" ShowReturns="False" />
                            <CC2:MasterControlField DataField="ActionHow" HeaderText="How" ShowReturns="False" />
                            <CC2:MasterControlField DataField="TargetDate" HeaderText="Target Date" ShowReturns="False"
                                HtmlEncode="false" />
                            <CC2:MasterControlField DataField="ResponsibleUser" HeaderText="Responsible User"
                                ShowReturns="False" />
                            <CC2:MasterControlField DataField="Actions" HeaderText="Actions" ShowReturns="True" />
                            <CC2:MasterControlField DataField="ClosedDate" HeaderText="Closed Date" ShowReturns="False"
                                HtmlEncode="false" />
                        </GridColumns>
                    </CC2:MasterControl>
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlOKCancel" runat="server">
        <table id="tbButtons">
            <tr>
                <td style="width: 110px">
                    <asp:Button ID="btnOK" runat="server" CssClass="Button_Default" Text="OK" EnableViewState="False">
                    </asp:Button>
                </td>
                <td align="left" class="style1">
                    <asp:Button ID="btnCancel" runat="server" CssClass="Button_Default" Text="Cancel"
                        CausesValidation="False"></asp:Button>
                </td>
                <td align="left" class="style1">
                    <asp:Button ID="btnAnomalyActions" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Anomaly Actions" />
                </td>
                <td align="left">
                    <asp:Button ID="btnReOpenAnomaly" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="ReOpen Anomaly" Visible="False" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <asp:Panel ID="pnlExit" runat="server" Visible="False">
        <table id="Table3" class="Table_Default">
            <tr>
                <td class="style1">
                    <asp:Button ID="btnExit" runat="server" CssClass="Button_Default" Text="Exit" CausesValidation="False">
                    </asp:Button>
                </td>
                <td class="style2">
                    <asp:Button ID="btnAnomalyActions1" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="Anomaly Actions" />
                </td>
                <td>
                    <asp:Button ID="btnReOpenAnomaly1" runat="server" CausesValidation="False" CssClass="Button_Default"
                        Text="ReOpen Anomaly" Visible="False" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <uc1:TransactionHistory ID="TransactionHistory1" runat="server" InitialStateExpanded="False" />
    <asp:ValidationSummary ID="valErrors" runat="server" CssClass="Label_Left_8PT" DisplayMode="List"
        ShowMessageBox="True" ShowSummary="False"></asp:ValidationSummary>
    <asp:Panel ID="pnlPopupAddAttachments" runat="server" CssClass="modalPopup" Style="display: none"
        Width="250px">
        <table width="100%">
            <tr>
                <td align="center" colspan="3" valign="middle">
                    <asp:Label ID="lblAddAttachmentsHeader" runat="server" BackColor="RoyalBlue" Font-Bold="True"
                        Font-Names="Tahoma" Font-Size="10pt" ForeColor="White" Height="20px" Text="Add Attachments"
                        Width="100%"></asp:Label>
                </td>
            </tr>
            <tr>
                <td colspan="1" style="width: 23px" valign="top">
                    <asp:Image ID="Image7" runat="server" ImageUrl="~/images/QuestionMessage.gif" />
                </td>
                <td colspan="2" style="height: 50px" valign="top">
                    &nbsp;<div id="TextBox6" runat="server" bordercolor="Transparent" borderstyle="None"
                        cssclass="Textbox_Display" height="95%" width="95%">
                        Do you want to Attach any Documents to this Anomaly?</div>
                </td>
            </tr>
            <tr>
                <td style="width: 23px">
                </td>
                <td>
                    <asp:Button ID="btnAddAttachmentsOK" runat="server" CssClass="Button_Default" Text="Yes"
                        CausesValidation="false" UseSubmitBehavior="false" />
                </td>
                <td>
                    <asp:Button ID="btnAddAttachementsCancel" runat="server" CssClass="Button_Default"
                        Text="No" CausesValidation="false" UseSubmitBehavior="false" />
                </td>
            </tr>
        </table>
    </asp:Panel>
    <CC1:ModalPopupExtender ID="mpAddAttachments" runat="server" BackgroundCssClass="modalBackground"
        TargetControlID="pnlPopupAddAttachments" DropShadow="True" PopupControlID="pnlPopupAddAttachments">
    </CC1:ModalPopupExtender>
</asp:Content>
