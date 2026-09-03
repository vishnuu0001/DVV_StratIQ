using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json.Serialization;
using System.Windows;
using System.Windows.Threading;
using Microsoft.Web.WebView2.Core;

namespace LabRobot.WindowsApp;

public partial class MainWindow : Window
{
    private static readonly Uri ClaudeUri = new("https://claude.ai/");
    private static readonly Uri VeoUri = new("https://labs.google/fx/tools/flow");
    private static readonly Uri CopilotUri = new("https://copilot.microsoft.com/");

    private readonly Uri _labRobotUri;
    private readonly Uri _portalBaseUri;
    private readonly Uri? _pendingProtocolUri;
    private readonly DispatcherTimer _sessionTimer;
    private bool _webViewReady;
    private bool _hasPortalSession;
    private bool _checkingPortalSession;
    private string? _portalToken;

    public MainWindow()
    {
        InitializeComponent();

        var configuredPortalUrl = Environment.GetEnvironmentVariable("PORTAL_BASE_URL");
        _portalBaseUri = Uri.TryCreate(configuredPortalUrl, UriKind.Absolute, out var portalUri)
            ? portalUri
            : new Uri("https://strat-iq.azurewebsites.net/");

        var configuredLabUrl = Environment.GetEnvironmentVariable("LAB_ROBOT_URL");
        _labRobotUri = Uri.TryCreate(configuredLabUrl, UriKind.Absolute, out var configuredUri)
            ? configuredUri
            : new Uri(_portalBaseUri, "/lab/");

        _pendingProtocolUri = Environment.GetCommandLineArgs()
            .Skip(1)
            .Select(value => Uri.TryCreate(value, UriKind.Absolute, out var uri) ? uri : null)
            .FirstOrDefault(uri => uri?.Scheme.Equals("labrobot", StringComparison.OrdinalIgnoreCase) == true);

        _sessionTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(15) };
        _sessionTimer.Tick += SessionTimer_Tick;

        Loaded += MainWindow_Loaded;
        Closed += (_, _) => _sessionTimer.Stop();
    }

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        try
        {
            var userDataFolder = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "StratAqorynth",
                "LabRobot",
                "WebView2");

            var environment = await CoreWebView2Environment.CreateAsync(userDataFolder: userDataFolder);
            await Browser.EnsureCoreWebView2Async(environment);

            Browser.CoreWebView2.Settings.AreDefaultContextMenusEnabled = true;
            Browser.CoreWebView2.Settings.AreDevToolsEnabled = true;
            Browser.CoreWebView2.Settings.IsStatusBarEnabled = false;
            Browser.CoreWebView2.Settings.IsZoomControlEnabled = true;
            Browser.CoreWebView2.NewWindowRequested += CoreWebView2_NewWindowRequested;
            Browser.CoreWebView2.NavigationStarting += CoreWebView2_NavigationStarting;
            Browser.CoreWebView2.NavigationCompleted += CoreWebView2_NavigationCompleted;
            Browser.CoreWebView2.HistoryChanged += CoreWebView2_HistoryChanged;
            Browser.CoreWebView2.DocumentTitleChanged += CoreWebView2_DocumentTitleChanged;

            _webViewReady = true;
            _sessionTimer.Start();

            if (_pendingProtocolUri is not null)
            {
                await HandleProtocolLaunchAsync(_pendingProtocolUri);
            }
        }
        catch (Exception exception)
        {
            MessageBox.Show(
                $"WebView2 could not be initialized. Install or repair the Microsoft Edge WebView2 Runtime.\n\n{exception.Message}",
                "Lab Robot Windows App",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
        }
    }

    private async Task NavigateAsync(Uri destination)
    {
        if (!_webViewReady)
        {
            await Browser.EnsureCoreWebView2Async();
            _webViewReady = true;
        }

        HomePanel.Visibility = Visibility.Collapsed;
        BrowserPanel.Visibility = Visibility.Visible;
        LoadingPanel.Visibility = Visibility.Visible;
        AddressText.Text = DisplayAddress(destination);
        ExternalButton.IsEnabled = true;
        RefreshButton.IsEnabled = true;
        Browser.CoreWebView2.Navigate(destination.AbsoluteUri);
    }

    private void ShowHome()
    {
        BrowserPanel.Visibility = Visibility.Collapsed;
        HomePanel.Visibility = Visibility.Visible;
        LoadingPanel.Visibility = Visibility.Collapsed;
        AddressText.Text = "App home";
        ExternalButton.IsEnabled = false;
        RefreshButton.IsEnabled = false;
        BackButton.IsEnabled = false;
        ForwardButton.IsEnabled = false;
    }

    private async void LabRobotButton_Click(object sender, RoutedEventArgs e)
    {
        if (_hasPortalSession)
        {
            await NavigateAsync(_labRobotUri);
            return;
        }

        await NavigateAsync(new Uri(_portalBaseUri, "/login?desktop=labrobot"));
    }
    private async void ClaudeButton_Click(object sender, RoutedEventArgs e) => await NavigateProtectedAsync(ClaudeUri);
    private async void VeoButton_Click(object sender, RoutedEventArgs e) => await NavigateProtectedAsync(VeoUri);
    private async void CopilotButton_Click(object sender, RoutedEventArgs e) => await NavigateProtectedAsync(CopilotUri);
    private void HomeButton_Click(object sender, RoutedEventArgs e) => ShowHome();

    private void BackButton_Click(object sender, RoutedEventArgs e)
    {
        if (Browser.CanGoBack) Browser.GoBack();
    }

    private void ForwardButton_Click(object sender, RoutedEventArgs e)
    {
        if (Browser.CanGoForward) Browser.GoForward();
    }

    private void RefreshButton_Click(object sender, RoutedEventArgs e)
    {
        if (_webViewReady) Browser.Reload();
    }

    private void ExternalButton_Click(object sender, RoutedEventArgs e)
    {
        if (Browser.Source is null) return;
        Process.Start(new ProcessStartInfo(Browser.Source.AbsoluteUri) { UseShellExecute = true });
    }

    private void CoreWebView2_NewWindowRequested(object? sender, CoreWebView2NewWindowRequestedEventArgs e)
    {
        if (!IsAllowedWebUri(e.Uri))
        {
            e.Handled = true;
            return;
        }

        // OAuth and provider links stay inside the native shell.
        e.Handled = true;
        Browser.CoreWebView2.Navigate(e.Uri);
    }

    private void CoreWebView2_NavigationStarting(object? sender, CoreWebView2NavigationStartingEventArgs e)
    {
        if (Uri.TryCreate(e.Uri, UriKind.Absolute, out var requestedUri)
            && requestedUri.Scheme.Equals("labrobot", StringComparison.OrdinalIgnoreCase))
        {
            e.Cancel = true;
            _ = HandleProtocolLaunchAsync(requestedUri);
            return;
        }

        if (!IsAllowedWebUri(e.Uri))
        {
            e.Cancel = true;
            MessageBox.Show("Only HTTPS pages and the configured local Lab Robot address can open in this workspace.",
                "Navigation blocked", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        LoadingPanel.Visibility = Visibility.Visible;
        AddressText.Text = Uri.TryCreate(e.Uri, UriKind.Absolute, out var addressUri)
            ? DisplayAddress(addressUri)
            : e.Uri;

        if (requestedUri is not null
            && requestedUri.Host.Equals(_portalBaseUri.Host, StringComparison.OrdinalIgnoreCase)
            && requestedUri.AbsolutePath.Equals("/login", StringComparison.OrdinalIgnoreCase))
        {
            _hasPortalSession = false;
            _portalToken = null;
        }
    }

    private void CoreWebView2_NavigationCompleted(object? sender, CoreWebView2NavigationCompletedEventArgs e)
    {
        LoadingPanel.Visibility = Visibility.Collapsed;
        if (!e.IsSuccess)
        {
            AddressText.Text = $"Unable to load page ({e.WebErrorStatus})";
        }
    }

    private void CoreWebView2_HistoryChanged(object? sender, object e)
    {
        BackButton.IsEnabled = Browser.CanGoBack;
        ForwardButton.IsEnabled = Browser.CanGoForward;
    }

    private void CoreWebView2_DocumentTitleChanged(object? sender, object e)
    {
        var title = Browser.CoreWebView2.DocumentTitle;
        Title = string.IsNullOrWhiteSpace(title) ? "Lab Robot Windows App" : $"{title} - Lab Robot Windows App";
    }

    private bool IsAllowedWebUri(string? value)
    {
        if (!Uri.TryCreate(value, UriKind.Absolute, out var uri)) return false;
        if (uri.Scheme.Equals(Uri.UriSchemeHttps, StringComparison.OrdinalIgnoreCase)) return true;

        return uri.Scheme.Equals(Uri.UriSchemeHttp, StringComparison.OrdinalIgnoreCase)
            && (uri.IsLoopback || uri.Host.Equals(_labRobotUri.Host, StringComparison.OrdinalIgnoreCase));
    }

    private async Task HandleProtocolLaunchAsync(Uri protocolUri)
    {
        var parameters = ParseQuery(protocolUri.Query);
        if (!parameters.TryGetValue("ticket", out var ticket) || string.IsNullOrWhiteSpace(ticket))
        {
            await NavigateAsync(new Uri(_portalBaseUri, "/login?reason=desktop-ticket-missing"));
            return;
        }

        try
        {
            LoadingPanel.Visibility = Visibility.Visible;
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            var exchangeUri = new Uri(_portalBaseUri, "/api/auth/desktop/exchange");
            using var response = await client.PostAsJsonAsync(exchangeUri, new { ticket });
            var handoff = await response.Content.ReadFromJsonAsync<DesktopHandoff>();
            if (!response.IsSuccessStatusCode || string.IsNullOrWhiteSpace(handoff?.Token))
            {
                throw new InvalidOperationException(handoff?.Error ?? "The desktop launch ticket was rejected.");
            }

            _hasPortalSession = true;
            _portalToken = handoff.Token;
            var labUri = Uri.TryCreate(handoff.LabRobotUrl, UriKind.Absolute, out var issuedLabUri)
                && issuedLabUri.Host.Equals(_labRobotUri.Host, StringComparison.OrdinalIgnoreCase)
                ? issuedLabUri
                : _labRobotUri;
            var destination = new UriBuilder(labUri)
            {
                Fragment = $"authToken={Uri.EscapeDataString(handoff.Token)}",
            }.Uri;
            await NavigateAsync(destination);
        }
        catch (Exception exception)
        {
            _hasPortalSession = false;
            _portalToken = null;
            MessageBox.Show(
                $"The portal session could not be transferred to Lab Robot.\n\n{exception.Message}",
                "Sign-in required",
                MessageBoxButton.OK,
                MessageBoxImage.Warning);
            await NavigateAsync(new Uri(_portalBaseUri, "/login?reason=desktop-handoff-failed"));
        }
    }

    private static Dictionary<string, string> ParseQuery(string query)
    {
        return query.TrimStart('?')
            .Split('&', StringSplitOptions.RemoveEmptyEntries)
            .Select(part => part.Split('=', 2))
            .Where(parts => parts.Length == 2)
            .ToDictionary(
                parts => Uri.UnescapeDataString(parts[0]),
                parts => Uri.UnescapeDataString(parts[1]),
                StringComparer.OrdinalIgnoreCase);
    }

    private static string DisplayAddress(Uri uri)
    {
        var safe = new UriBuilder(uri) { Fragment = string.Empty };
        return safe.Uri.AbsoluteUri;
    }

    private async Task NavigateProtectedAsync(Uri destination)
    {
        if (!_hasPortalSession || string.IsNullOrWhiteSpace(_portalToken))
        {
            await NavigateAsync(new Uri(_portalBaseUri, "/login?desktop=labrobot"));
            return;
        }

        await NavigateAsync(destination);
    }

    private async void SessionTimer_Tick(object? sender, EventArgs e)
    {
        if (_checkingPortalSession || string.IsNullOrWhiteSpace(_portalToken)) return;
        _checkingPortalSession = true;
        try
        {
            using var client = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
            client.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", _portalToken);
            using var response = await client.GetAsync(new Uri(_portalBaseUri, "/api/auth/session"));
            if (!response.IsSuccessStatusCode)
            {
                await ForcePortalLoginAsync("session-closed");
                return;
            }

            var session = await response.Content.ReadFromJsonAsync<PortalSession>();
            var hasLabAccess = session?.User?.Role?.Equals("admin", StringComparison.OrdinalIgnoreCase) == true
                || session?.User?.Apps?.Contains("LAB_ROBOT", StringComparer.OrdinalIgnoreCase) == true;
            if (!hasLabAccess)
            {
                await ForcePortalLoginAsync("lab-access-removed");
            }
        }
        catch (HttpRequestException)
        {
            // Fail closed when the authority cannot validate the session.
            await ForcePortalLoginAsync("session-validation-unavailable");
        }
        catch (TaskCanceledException)
        {
            await ForcePortalLoginAsync("session-validation-timeout");
        }
        finally
        {
            _checkingPortalSession = false;
        }
    }

    private async Task ForcePortalLoginAsync(string reason)
    {
        _hasPortalSession = false;
        _portalToken = null;
        await NavigateAsync(new Uri(_portalBaseUri, $"/login?reason={Uri.EscapeDataString(reason)}"));
    }

    private sealed class DesktopHandoff
    {
        [JsonPropertyName("token")]
        public string? Token { get; init; }

        [JsonPropertyName("lab_robot_url")]
        public string? LabRobotUrl { get; init; }

        [JsonPropertyName("error")]
        public string? Error { get; init; }
    }

    private sealed class PortalSession
    {
        [JsonPropertyName("user")]
        public PortalUser? User { get; init; }
    }

    private sealed class PortalUser
    {
        [JsonPropertyName("role")]
        public string? Role { get; init; }

        [JsonPropertyName("apps")]
        public string[]? Apps { get; init; }
    }
}
