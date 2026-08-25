<%@ Page Language="VB" MasterPageFile="~/UI/Pages/MasterPages/ApplicationMaster.master"
    AutoEventWireup="false" CodeFile="ChangeLog.aspx.vb" Inherits="WebApp.APlus.UI.Pages.ChangeLog"
    Title="Change Log" %>

<%@ MasterType TypeName="WebApp.APlus.UI.Pages.ApplicationMaster" %>
<asp:Content ID="Content1" ContentPlaceHolderID="ContentPlaceHolder1" runat="Server">
    <h5>
        Version 3.1.5</h5>
    <ul>
        <li>2013.12.23</li>
        <li>Add Anomaly Attachments now available on Anomaly Actions page</li>
    </ul>
    <h5>
        Version 3.1.4</h5>
    <ul>
        <li>2013.12.22</li>
        <li>Anomaly Origin Maintenance now available</li>
        <li>Filter by Anomaly Description added to Site Anomalies</li>
    </ul>
    <h5>
        Version 3.1.3</h5>
    <ul>
        <li>2013.12.17</li>
        <li>[User Master IT Request Compaure] is now [User Master Attendance Record Compare]</li>
    </ul>
    <h5>
        Version 3.1.2</h5>
    <ul>
        <li>2013.12.11</li>
        <li>Business Area & Business Unit Maintenance added</li>
        <li>Ability to bulk change Business Area & Business Unit for KPIs and Teams added</li>
    </ul>
    <h5>
        Version 3.1.1.4</h5>
    <ul>
        <li>2013.06.23</li>
        <li>Minor bug fixes</li>
    </ul>
    <h5>
        Version 3.1.1.3</h5>
    <ul>
        <li>Minor bug fixes on Query Parameters page.</li>
    </ul>
    <h5>
        Version 3.1.1.2</h5>
    <ul>
        <li>2013.02.16</li>
        <li>Minor bug fixes:
            <ul>
                <li style="list-style: square;">Several session variable properties did not match the
                    assigned enum.</li>
            </ul>
        </li>
    </ul>
    <h5>
        Version 3.1.1.1</h5>
    <ul>
        <li>Fixed some minor translation issues on the Anomaly pages</li>
    </ul>
    <h5>
        Version 3.1.1.0</h5>
    <ul>
        <li>Daily KPI Interface now supports the CalendarDays element for MTD values</li>
    </ul>
    <h5>
        Version 3.1.0.0</h5>
    <ul>
        <li>Implemented Versioning</li>
        <li>Adding Changelog</li>
    </ul>
    <asp:Button ID="btnExit" runat="server" Text="Exit" CssClass="Button_Default" />
</asp:Content>
