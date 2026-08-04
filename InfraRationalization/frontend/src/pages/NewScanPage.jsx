// ---------------------------------------------------------------------------
// Author: Vishnuu A
// Scope: InfraRationalization — frontend/src/pages (NewScanPage.jsx)
// Date: 2026-05-30
// ---------------------------------------------------------------------------
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Cloud, Network, Database, Wifi } from 'lucide-react'
import toast from 'react-hot-toast'
import {
  Field as FluentField,
  Input,
  Textarea,
  Checkbox,
  Button,
  TabList,
  Tab,
  Text,
  tokens,
} from '@fluentui/react-components'
import { startScan, getScanTargetCandidates } from '../api/client.js'
import AppHeader from '../components/AppHeader.jsx'

const TABS = [
  { id: 'onprem', label: 'On-Premises', icon: Network },
  { id: 'aws',    label: 'AWS',         icon: Cloud },
  { id: 'azure',  label: 'Azure',       icon: Cloud },
  { id: 'gcp',    label: 'GCP',         icon: Cloud },
  { id: 'multi',  label: 'Multi-Cloud', icon: Database },
]

// Function: FormField
const FormField = ({ label, type = 'text', value, onChange, placeholder = '', hint = '' }) => (
  <FluentField label={label} hint={hint}>
    <Input
      type={type}
      value={value}
      onChange={(_, data) => onChange(data.value)}
      placeholder={placeholder}
    />
  </FluentField>
)

// Function: Section
const Section = ({ title, children }) => (
  <div className="space-y-4">
    <Text
      block
      style={{
        fontSize: '11px',
        fontWeight: 600,
        color: tokens.colorBrandForeground1,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
        paddingBottom: '8px',
      }}
    >
      {title}
    </Text>
    {children}
  </div>
)

// Function: NewScanPage
export default function NewScanPage() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('onprem')
  const [reportName, setReportName] = useState('')
  const [loading, setLoading] = useState(false)

  // OnPrem
  const [networkRange, setNetworkRange] = useState('')
  const [reachableCandidates, setReachableCandidates] = useState([])
  const [candidatesLoading, setCandidatesLoading] = useState(true)
  const [sshUser, setSshUser] = useState('')
  const [sshPass, setSshPass] = useState('')
  const [sshKey, setSshKey] = useState('')
  const [winrmUser, setWinrmUser] = useState('')
  const [winrmPass, setWinrmPass] = useState('')

  // AWS
  const [awsKey, setAwsKey] = useState('')
  const [awsSecret, setAwsSecret] = useState('')
  const [awsRegions, setAwsRegions] = useState('us-east-1,eu-west-1')

  // Azure
  const [azTenant, setAzTenant] = useState('')
  const [azClient, setAzClient] = useState('')
  const [azSecret, setAzSecret] = useState('')
  const [azSub, setAzSub] = useState('')

  // GCP
  const [gcpProject, setGcpProject] = useState('')
  const [gcpSaJson, setGcpSaJson] = useState('')
  const [gcpRegions, setGcpRegions] = useState('us-central1')

  // Options
  const [deepScan, setDeepScan] = useState(true)
  const [portScan, setPortScan] = useState(true)
  const [timeout, setTimeout_] = useState('30')

  useEffect(() => {
    let active = true
    getScanTargetCandidates()
      .then(data => { if (active) setReachableCandidates(data.candidates || []) })
      .catch(() => { if (active) setReachableCandidates([]) })
      .finally(() => { if (active) setCandidatesLoading(false) })
    return () => { active = false }
  }, [])

  // Function: handleSubmit
  const handleSubmit = async () => {
    if ((tab === 'onprem' || tab === 'multi') && !networkRange.trim()) {
      toast.error('Enter a CIDR range that is reachable from this server (see the confirmed-reachable options above).')
      return
    }
    const name = reportName.trim() || `Scan ${new Date().toLocaleString()}`
    const base = {
      provider: tab,
      report_name: name,
      deep_scan: deepScan,
      port_scan: portScan,
      timeout_seconds: parseInt(timeout) || 30,
    }

    let payload = { ...base }

    if (tab === 'onprem' || tab === 'multi') {
      payload = {
        ...payload,
        network_range: networkRange.trim(),
        ssh_username: sshUser.trim(),
        ssh_password: sshPass,
        ssh_key_path: sshKey.trim(),
        winrm_username: winrmUser.trim(),
        winrm_password: winrmPass,
      }
    }
    if (tab === 'aws' || tab === 'multi') {
      payload = {
        ...payload,
        aws_access_key_id: awsKey.trim(),
        aws_secret_access_key: awsSecret,
        aws_regions: awsRegions.split(',').map(r => r.trim()).filter(Boolean),
      }
    }
    if (tab === 'azure' || tab === 'multi') {
      payload = {
        ...payload,
        azure_tenant_id: azTenant.trim(),
        azure_client_id: azClient.trim(),
        azure_client_secret: azSecret,
        azure_subscription_id: azSub.trim(),
      }
    }
    if (tab === 'gcp' || tab === 'multi') {
      payload = {
        ...payload,
        gcp_project_id: gcpProject.trim(),
        gcp_service_account_json: gcpSaJson.trim(),
        gcp_regions: gcpRegions.split(',').map(r => r.trim()).filter(Boolean),
      }
    }

    setLoading(true)
    try {
      const { scan_id } = await startScan(payload)
      toast.success('Scan started!')
      navigate(`/scans/progress/${scan_id}`)
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to start scan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-surface">
      <AppHeader title="New Infrastructure Scan" subtitle="Configure your scan target and credentials" backTo="/" />

      <main className="max-w-4xl mx-auto px-5 py-8 space-y-6">
        {/* Report name */}
        <div className="glass p-6">
          <FormField
            label="Report Name"
            value={reportName}
            onChange={setReportName}
            placeholder={`Infrastructure Scan — ${new Date().toLocaleDateString()}`}
          />
        </div>

        {/* Provider tabs */}
        <div className="glass p-6 space-y-6">
          <TabList selectedValue={tab} onTabSelect={(_, data) => setTab(data.value)}>
            {TABS.map(({ id, label, icon: Icon }) => (
              <Tab key={id} value={id} icon={<Icon size={14} />}>{label}</Tab>
            ))}
          </TabList>

          {/* OnPrem fields */}
          {(tab === 'onprem' || tab === 'multi') && (
            <Section title="On-Premises Network">
              <FormField
                label="CIDR Range"
                value={networkRange}
                onChange={setNetworkRange}
                placeholder="e.g. 10.0.0.0/24 — must be reachable from this server"
                hint="Discovery is network-level: this only finds hosts on a range this backend server can actually route to — not your own laptop's network, and not a customer network unless it's already connected (VPN/peering, or a scanning appliance deployed inside it)."
              />
              {!candidatesLoading && reachableCandidates.length > 0 && (
                <div
                  style={{
                    borderRadius: tokens.borderRadiusMedium,
                    border: `1px solid ${tokens.colorPaletteGreenBorder2}`,
                    background: tokens.colorPaletteGreenBackground1,
                    padding: '12px',
                  }}
                >
                  <Text
                    block
                    style={{
                      fontSize: '12px',
                      fontWeight: 500,
                      color: tokens.colorPaletteGreenForeground1,
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                      marginBottom: '8px',
                    }}
                  >
                    <Wifi size={12} /> Confirmed reachable from this server right now
                  </Text>
                  <div className="flex flex-wrap gap-2">
                    {reachableCandidates.map(c => (
                      <Button
                        key={c.cidr}
                        size="small"
                        appearance={networkRange === c.cidr ? 'primary' : 'outline'}
                        onClick={() => setNetworkRange(c.cidr)}
                        title={`Interface: ${c.interface} (${c.local_ip})`}
                        style={{ fontFamily: tokens.fontFamilyMonospace }}
                      >
                        {c.cidr}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
              <div className="grid sm:grid-cols-2 gap-4">
                <FormField label="SSH Username" value={sshUser} onChange={setSshUser} placeholder="root" />
                <FormField label="SSH Password" type="password" value={sshPass} onChange={setSshPass} placeholder="••••••••" />
              </div>
              <FormField
                label="SSH Private Key Path (optional)"
                value={sshKey}
                onChange={setSshKey}
                placeholder="/home/user/.ssh/id_rsa"
              />
              <div className="grid sm:grid-cols-2 gap-4">
                <FormField label="WinRM Username (Windows)" value={winrmUser} onChange={setWinrmUser} placeholder="Administrator" />
                <FormField label="WinRM Password" type="password" value={winrmPass} onChange={setWinrmPass} placeholder="••••••••" />
              </div>
            </Section>
          )}

          {/* AWS fields */}
          {(tab === 'aws' || tab === 'multi') && (
            <Section title="AWS Credentials">
              <div className="grid sm:grid-cols-2 gap-4">
                <FormField label="Access Key ID" value={awsKey} onChange={setAwsKey} placeholder="AKIA..." />
                <FormField label="Secret Access Key" type="password" value={awsSecret} onChange={setAwsSecret} placeholder="••••••••" />
              </div>
              <FormField
                label="Regions (comma separated)"
                value={awsRegions}
                onChange={setAwsRegions}
                placeholder="us-east-1,eu-west-1,ap-south-1"
              />
            </Section>
          )}

          {/* Azure fields */}
          {(tab === 'azure' || tab === 'multi') && (
            <Section title="Azure Credentials">
              <div className="grid sm:grid-cols-2 gap-4">
                <FormField label="Tenant ID" value={azTenant} onChange={setAzTenant} placeholder="xxxxxxxx-xxxx-..." />
                <FormField label="Client ID (App Registration)" value={azClient} onChange={setAzClient} placeholder="xxxxxxxx-xxxx-..." />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <FormField label="Client Secret" type="password" value={azSecret} onChange={setAzSecret} placeholder="••••••••" />
                <FormField label="Subscription ID" value={azSub} onChange={setAzSub} placeholder="xxxxxxxx-xxxx-..." />
              </div>
            </Section>
          )}

          {/* GCP fields */}
          {(tab === 'gcp' || tab === 'multi') && (
            <Section title="GCP Credentials">
              <FormField
                label="Project ID"
                value={gcpProject}
                onChange={setGcpProject}
                placeholder="my-gcp-project-123"
              />
              <FluentField label="Service Account JSON">
                <Textarea
                  value={gcpSaJson}
                  onChange={(_, data) => setGcpSaJson(data.value)}
                  rows={4}
                  placeholder='{ "type": "service_account", ... }'
                  style={{ fontFamily: tokens.fontFamilyMonospace }}
                />
              </FluentField>
              <FormField
                label="Regions (comma separated)"
                value={gcpRegions}
                onChange={setGcpRegions}
                placeholder="us-central1,europe-west1"
              />
            </Section>
          )}
        </div>

        {/* Scan options */}
        <div className="glass p-6">
          <Text
            block
            style={{
              fontSize: '11px',
              fontWeight: 600,
              color: tokens.colorBrandForeground1,
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
              paddingBottom: '8px',
              marginBottom: '16px',
            }}
          >
            Scan Options
          </Text>
          <div className="grid sm:grid-cols-3 gap-4">
            <Checkbox
              checked={deepScan}
              onChange={(_, data) => setDeepScan(!!data.checked)}
              label={
                <div>
                  <Text block weight="medium" size={300}>Deep Scan</Text>
                  <Text block size={200} style={{ color: tokens.colorNeutralForeground3 }}>SSH/WinRM enrichment</Text>
                </div>
              }
            />
            <Checkbox
              checked={portScan}
              onChange={(_, data) => setPortScan(!!data.checked)}
              label={
                <div>
                  <Text block weight="medium" size={300}>Port Scan</Text>
                  <Text block size={200} style={{ color: tokens.colorNeutralForeground3 }}>nmap service detection</Text>
                </div>
              }
            />
            <FormField
              label="Timeout (seconds)"
              type="number"
              value={timeout}
              onChange={setTimeout_}
              placeholder="30"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end">
          <Button appearance="secondary" onClick={() => navigate('/')}>
            Cancel
          </Button>
          <Button
            appearance="primary"
            onClick={handleSubmit}
            disabled={loading}
            icon={<Play size={15} />}
          >
            {loading ? 'Starting…' : 'Start Scan'}
          </Button>
        </div>
      </main>
    </div>
  )
}
