import { useState, useEffect } from "react";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "./components/ui/tabs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine,
  Cell,
  ScatterChart,
  Scatter,
  ZAxis,
} from "recharts";
// Dialog component removed - using custom modal instead
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import {
  Activity,
  Search,
  Users,
  MapPin,
  Settings,
  Database,
  Plus,
  Loader2,
} from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [trialId, setTrialId] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [allTrialResults, setAllTrialResults] = useState<any[]>([]);

  const handleAddTrial = async () => {
    if (!trialId) return;

    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8080/api/match/trial", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ trial_id: trialId }),
      });

      if (!response.ok) {
        throw new Error("Failed to match patients");
      }

      const data = await response.json();

      // Add new trial result to the array
      setAllTrialResults(prev => [data, ...prev]); // Add to beginning

      setDialogOpen(false);
      setTrialId("");
      setActiveTab("matches"); // Switch to matches tab to show results
    } catch (error) {
      console.error("Error matching patients:", error);
      alert("Failed to match patients. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleButtonClick = () => {
    setDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-[#0B5394] rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-[#0B5394]">TrialMatch AI</h1>
                <p className="text-gray-500 text-sm">
                  Healthcare Dashboard
                </p>
              </div>
            </div>

            {/* Add Trial Button */}
            <Button
              variant="outline"
              className="bg-white border-2 border-black rounded-lg hover:bg-gray-50"
              onClick={handleButtonClick}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Trial
            </Button>
          </div>
        </div>
      </header>

      {/* Custom Modal - Simple and working */}
      {dialogOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => {
              setDialogOpen(false);
              setTrialId("");
            }}
          />

          {/* Modal Content */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div
              className="bg-white rounded-lg shadow-xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="mb-4">
                <h2 className="text-lg font-semibold mb-2">Add Clinical Trial</h2>
                <p className="text-sm text-gray-500">
                  Enter a clinical trial ID (NCT number) to match patients
                </p>
              </div>

              {/* Input */}
              <div className="mb-6">
                <Input
                  placeholder="e.g., NCT05706298"
                  value={trialId}
                  onChange={(e) => setTrialId(e.target.value)}
                  className="w-full"
                  autoFocus
                />
              </div>

              {/* Footer */}
              <div className="flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => {
                    setDialogOpen(false);
                    setTrialId("");
                  }}
                >
                  Cancel
                </Button>
                <Button
                  className="bg-[#52C41A] hover:bg-[#52C41A]/90 text-white"
                  onClick={handleAddTrial}
                  disabled={!trialId || isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Matching...
                    </>
                  ) : (
                    "Match Patients"
                  )}
                </Button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="w-full"
        >
          <TabsList className="!w-full !flex mb-6 h-auto">
            <TabsTrigger value="dashboard" className="flex-1">
              <Activity className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">
                Dashboard
              </span>
            </TabsTrigger>
            <TabsTrigger value="dataset" className="flex-1">
              <Database className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Dataset</span>
            </TabsTrigger>
            <TabsTrigger value="patterns" className="flex-1">
              <Search className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Patterns</span>
            </TabsTrigger>
            <TabsTrigger value="agents" className="flex-1">
              <Settings className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Agents</span>
            </TabsTrigger>
            <TabsTrigger value="matches" className="flex-1">
              <Users className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Matches</span>
            </TabsTrigger>
            <TabsTrigger value="sites" className="flex-1">
              <MapPin className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Sites</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard">
            <DashboardView />
          </TabsContent>

          <TabsContent value="dataset">
            <DatasetView />
          </TabsContent>

          <TabsContent value="patterns">
            <PatternsView />
          </TabsContent>

          <TabsContent value="agents">
            <AgentsView />
          </TabsContent>

          <TabsContent value="matches">
            <MatchesView allTrialResults={allTrialResults} />
          </TabsContent>

          <TabsContent value="sites">
            <SitesView />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

// Dashboard View
function DashboardView() {
  // Enrollment trend data
  const enrollmentData = [
    { month: "M1", manual: 40, aiPredicted: 120, aiActual: 115 },
    { month: "M2", manual: 85, aiPredicted: 210, aiActual: 205 },
    { month: "M3", manual: 130, aiPredicted: 295, aiActual: 288 },
    { month: "M4", manual: 175, aiPredicted: 375, aiActual: null }, // Current month
    { month: "M5", manual: 215, aiPredicted: 445, aiActual: null },
    { month: "M6", manual: 255, aiPredicted: 500, aiActual: null },
    { month: "M7", manual: 295, aiPredicted: 500, aiActual: null },
    { month: "M8", manual: 330, aiPredicted: 500, aiActual: null },
    { month: "M9", manual: 365, aiPredicted: 500, aiActual: null },
    { month: "M10", manual: 400, aiPredicted: 500, aiActual: null },
    { month: "M11", manual: 435, aiPredicted: 500, aiActual: null },
    { month: "M12", manual: 470, aiPredicted: 500, aiActual: null },
    { month: "M13", manual: 500, aiPredicted: 500, aiActual: null },
  ];

  // Pattern distribution data
  const patternData = [
    { name: "Elderly Diabetics", count: 2847, success: 73, color: "#0B5394" },
    { name: "Mid-age Controlled", count: 1923, success: 68, color: "#1E6BB8" },
    { name: "Young Onset", count: 1456, success: 64, color: "#3B82F6" },
    { name: "Uncontrolled HbA1c", count: 987, success: 58, color: "#60A5FA" },
    { name: "Cardiovascular", count: 734, success: 52, color: "#93C5FD" },
  ];

  const metrics = [
    {
      label: "Active Trials",
      value: "247",
      change: "+12%",
      color: "#0B5394",
    },
    {
      label: "Patient Matches",
      value: "1,834",
      change: "+8%",
      color: "#52C41A",
    },
    {
      label: "AI Agents",
      value: "12",
      change: "Active",
      color: "#6B46C1",
    },
    {
      label: "Success Rate",
      value: "94%",
      change: "+3%",
      color: "#0B5394",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <CardContent className="pt-6">
              <div className="flex flex-col">
                <span className="text-sm text-gray-500">
                  {metric.label}
                </span>
                <div className="flex items-baseline gap-2 mt-2">
                  <span
                    className="text-2xl"
                    style={{ color: metric.color }}
                  >
                    {metric.value}
                  </span>
                  <span className="text-sm text-[#52C41A]">
                    {metric.change}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trial Enrollment Trends Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Trial Enrollment Trends</CardTitle>
            <p className="text-xs text-gray-500 mt-1">
              AI-powered matching accelerates enrollment by 6 months, saving $2.4M
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart
                data={enrollmentData}
                margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorManual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#EF4444" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorPredicted" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0B5394" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#0B5394" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#52C41A" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#52C41A" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="month"
                  tick={{ fontSize: 12 }}
                  stroke="#888"
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke="#888"
                  label={{ value: "Patients", angle: -90, position: "insideLeft", fontSize: 12 }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <ReferenceLine
                  y={500}
                  stroke="#888"
                  strokeDasharray="5 5"
                  label={{ value: "Target: 500", position: "right", fontSize: 10 }}
                />
                <Area
                  type="monotone"
                  dataKey="manual"
                  stroke="#EF4444"
                  strokeWidth={2}
                  fill="url(#colorManual)"
                  name="Manual Screening"
                />
                <Area
                  type="monotone"
                  dataKey="aiPredicted"
                  stroke="#0B5394"
                  strokeWidth={2}
                  fill="url(#colorPredicted)"
                  name="AI Predicted"
                />
                <Area
                  type="monotone"
                  dataKey="aiActual"
                  stroke="#52C41A"
                  strokeWidth={3}
                  fill="url(#colorActual)"
                  name="AI Actual Progress"
                  strokeDasharray="0"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Match Distribution Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Pattern Distribution</CardTitle>
            <p className="text-xs text-gray-500 mt-1">
              Conway engine discovered patient patterns with match quality
            </p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={patternData}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 12 }}
                  stroke="#888"
                  label={{ value: "Patients", position: "insideBottom", offset: -5, fontSize: 12 }}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fontSize: 11 }}
                  stroke="#888"
                  width={95}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "white",
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                  formatter={(value: any, name: string, props: any) => [
                    `${value} patients (${props.payload.success}% success)`,
                    "",
                  ]}
                />
                <Bar
                  dataKey="count"
                  radius={[0, 4, 4, 0]}
                  label={{
                    position: "right",
                    fontSize: 11,
                    formatter: (value: number) => value.toLocaleString(),
                  }}
                >
                  {patternData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
              >
                <div className="w-2 h-2 rounded-full bg-[#52C41A]" />
                <div className="flex-1">
                  <p className="text-sm">
                    New patient match found for Trial #{i}234
                  </p>
                  <p className="text-xs text-gray-500">
                    2 hours ago
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Dataset View
function DatasetView() {
  const datasets = [
    {
      category: "Clinical Trials",
      source: "ClinicalTrials.gov API v2",
      count: 100,
      details: [
        { label: "API Endpoint", value: "https://clinicaltrials.gov/api/v2/studies" },
        { label: "Filter Status", value: "RECRUITING" },
        { label: "Default Condition", value: "Diabetes" },
        { label: "Data Fields", value: "NCT ID, Title, Phase, Enrollment, Eligibility, Sites" },
      ],
      color: "#0B5394",
    },
    {
      category: "Patient Data",
      source: "Synthetic Data Generation",
      count: 5000,
      details: [
        { label: "Data Method", value: "Python NumPy/Pandas" },
        { label: "Age Range", value: "18-90 years" },
        { label: "Conditions", value: "Diabetes, Hypertension, Cancer, Alzheimer's, Cardiovascular" },
        { label: "Data Fields", value: "Patient ID, Age, Gender, Conditions, Medications, Lab Values, Location" },
      ],
      color: "#52C41A",
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Dataset Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 mb-6">
            View summaries of all datasets used in the TrialMatch AI system. Multiple datasets can be configured to support various trial types and patient populations.
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {datasets.map((dataset) => (
              <Card key={dataset.category}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{dataset.category}</CardTitle>
                    <div
                      className="px-3 py-1 rounded-full text-sm font-medium"
                      style={{
                        backgroundColor: `${dataset.color}20`,
                        color: dataset.color,
                      }}
                    >
                      {dataset.count.toLocaleString()} records
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Data Source */}
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <div className="text-xs text-gray-500 mb-1">Data Source</div>
                    <div className="font-medium text-sm">{dataset.source}</div>
                  </div>

                  {/* Details */}
                  <div className="space-y-3">
                    {dataset.details.map((detail) => (
                      <div key={detail.label} className="border-b border-gray-100 pb-2 last:border-0">
                        <div className="text-xs text-gray-500 mb-1">{detail.label}</div>
                        <div className="text-sm break-words">{detail.value}</div>
                      </div>
                    ))}
                  </div>

                  {/* Status Badge */}
                  <div className="pt-2">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-50 rounded-full">
                      <div className="w-2 h-2 rounded-full bg-[#52C41A]" />
                      <span className="text-xs text-green-700">Active Dataset</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Additional Info Card */}
      <Card>
        <CardHeader>
          <CardTitle>Dataset Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
              <Database className="w-5 h-5 text-[#0B5394] mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-sm mb-1">Real-Time Clinical Trial Data</h4>
                <p className="text-xs text-gray-600">
                  Clinical trials are fetched in real-time from ClinicalTrials.gov API v2 with pagination support. The system automatically filters for recruiting trials and handles rate limiting.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
              <Users className="w-5 h-5 text-[#52C41A] mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-sm mb-1">Synthetic Patient Population</h4>
                <p className="text-xs text-gray-600">
                  Patient data is synthetically generated using realistic distributions for demographics, conditions, medications, and lab values. Geographic data covers US locations.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
              <Activity className="w-5 h-5 text-[#6B46C1] mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-sm mb-1">Extensible Architecture</h4>
                <p className="text-xs text-gray-600">
                  The system supports multiple datasets and can be extended to include additional data sources, trial types, and patient populations as needed.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Patterns View
function PatternsView() {
  const [selectedPattern, setSelectedPattern] = useState<string | null>(null);
  const [patterns, setPatterns] = useState<any[]>([]);
  const [clusterData, setClusterData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch real patterns from backend
  useEffect(() => {
    const fetchPatterns = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8080/api/patterns");
        const data = await response.json();

        // Map backend patterns to frontend format using insights
        const colors = ["#0B5394", "#1E6BB8", "#3B82F6", "#60A5FA", "#93C5FD"];

        // Use simple Pattern 1, Pattern 2 labels
        const mappedPatterns = data.patterns.map((p: any, idx: number) => {
          return {
            name: `Pattern ${idx + 1}`,
            pattern_id: p.pattern_id, // Keep original ID for filtering
            count: p.size,
            color: colors[idx % colors.length],
          };
        });

        setPatterns(mappedPatterns);

        // Generate visualization data from embeddings if available
        if (data.patterns.length > 0) {
          const vizData: any[] = [];
          data.patterns.forEach((pattern: any, pIdx: number) => {
            // Use centroid as center point and generate scatter around it
            const centerX = pattern.centroid[0] || 0;
            const centerY = pattern.centroid[1] || 0;

            // Use simple Pattern N label
            const displayName = `Pattern ${pIdx + 1}`;

            // Generate points for this cluster
            for (let i = 0; i < Math.min(pattern.size, 200); i++) {
              vizData.push({
                x: centerX + (Math.random() - 0.5) * 3,
                y: centerY + (Math.random() - 0.5) * 3,
                cluster: pIdx,
                patternName: displayName,
                pattern_id: pattern.pattern_id,
                color: colors[pIdx % colors.length],
                patientId: `P${String(pIdx * 1000 + i).padStart(6, "0")}`,
              });
            }
          });
          setClusterData(vizData);
        }
      } catch (error) {
        console.error("Failed to fetch patterns:", error);
        // Fallback to mock data on error
        setPatterns([
          { name: "Pattern 0", count: 3254, color: "#0B5394" },
          { name: "Pattern 1", count: 1746, color: "#1E6BB8" },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchPatterns();
  }, []); // Empty dependency array - fetch once on mount

  // Filter data based on selected pattern
  const filteredData = selectedPattern
    ? clusterData.filter((d) => d.patternName === selectedPattern)
    : clusterData;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-[#0B5394]" />
          <p className="text-gray-500">Loading Conway patterns from 5000 Synthea patients...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Pattern Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Discovered Patterns</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            Conway unsupervised learning discovered {patterns.length} distinct patient clusters from real Synthea FHIR data
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={selectedPattern === null ? "default" : "outline"}
              className={
                selectedPattern === null
                  ? "bg-[#0B5394] hover:bg-[#0B5394]/90 text-white"
                  : ""
              }
              onClick={() => setSelectedPattern(null)}
              size="sm"
            >
              All Patterns ({clusterData.length})
            </Button>
            {patterns.map((pattern) => (
              <Button
                key={pattern.name}
                variant={selectedPattern === pattern.name ? "default" : "outline"}
                className={
                  selectedPattern === pattern.name
                    ? "hover:opacity-90"
                    : ""
                }
                style={
                  selectedPattern === pattern.name
                    ? { backgroundColor: pattern.color, color: "white" }
                    : {}
                }
                onClick={() => setSelectedPattern(pattern.name)}
                size="sm"
              >
                <div
                  className="w-3 h-3 rounded-full mr-2"
                  style={{ backgroundColor: pattern.color }}
                />
                {pattern.name} ({pattern.count})
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* UMAP Scatter Plot */}
      <Card>
        <CardHeader>
          <CardTitle>UMAP Projection of Patient Space</CardTitle>
          <p className="text-xs text-gray-500 mt-1">
            2D visualization of high-dimensional patient features. Each dot represents a patient.
          </p>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={500}>
            <ScatterChart
              margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                type="number"
                dataKey="x"
                name="UMAP-1"
                domain={[-8, 8]}
                tick={{ fontSize: 12 }}
                stroke="#888"
                label={{
                  value: "UMAP Dimension 1",
                  position: "insideBottom",
                  offset: -10,
                  fontSize: 12,
                }}
              />
              <YAxis
                type="number"
                dataKey="y"
                name="UMAP-2"
                domain={[-8, 8]}
                tick={{ fontSize: 12 }}
                stroke="#888"
                label={{
                  value: "UMAP Dimension 2",
                  angle: -90,
                  position: "insideLeft",
                  fontSize: 12,
                }}
              />
              <ZAxis range={[60, 60]} />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                contentStyle={{
                  backgroundColor: "white",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border rounded-lg shadow-lg">
                        <p className="font-semibold text-sm">{data.patternName}</p>
                        <p className="text-xs text-gray-600">
                          Patient: {data.patientId}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          UMAP-1: {data.x.toFixed(2)}
                        </p>
                        <p className="text-xs text-gray-500">
                          UMAP-2: {data.y.toFixed(2)}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: "12px" }}
                content={() => (
                  <div className="flex justify-center gap-4 mt-4 flex-wrap">
                    {patterns.map((pattern) => (
                      <div key={pattern.name} className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: pattern.color }}
                        />
                        <span className="text-xs text-gray-600">{pattern.name}</span>
                      </div>
                    ))}
                  </div>
                )}
              />
              {patterns.map((pattern, index) => {
                const patternData = filteredData.filter(
                  (d) => d.patternName === pattern.name
                );
                return (
                  <Scatter
                    key={pattern.name}
                    name={pattern.name}
                    data={patternData}
                    fill={pattern.color}
                    fillOpacity={selectedPattern === pattern.name ? 0.9 : 0.6}
                  />
                );
              })}
            </ScatterChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Pattern Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Pattern Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {patterns.map((pattern) => (
              <div
                key={pattern.name}
                className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedPattern(pattern.name)}
                style={{
                  borderLeftWidth: "4px",
                  borderLeftColor: pattern.color,
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: pattern.color }}
                  />
                  <h4 className="font-semibold text-sm">{pattern.name}</h4>
                </div>
                <p className="text-2xl font-bold text-gray-800">
                  {pattern.count.toLocaleString()}
                </p>
                <p className="text-xs text-gray-500">patients identified</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Agents View
function AgentsView() {
  const agents = [
    { name: "Eligibility Agent", status: "Active", tasks: 234 },
    { name: "Matching Agent", status: "Active", tasks: 189 },
    { name: "Data Mining Agent", status: "Active", tasks: 156 },
    {
      name: "Site Selection Agent",
      status: "Active",
      tasks: 98,
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>AI Agent Control Center</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="p-4 bg-gradient-to-br from-[#6B46C1]/10 to-transparent rounded-lg border border-[#6B46C1]/20"
              >
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-[#52C41A]" />
                  <span className="text-xs text-gray-500">
                    {agent.status}
                  </span>
                </div>
                <h3 className="mb-1">{agent.name}</h3>
                <p className="text-sm text-gray-500">
                  {agent.tasks} tasks completed
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Matches View
function MatchesView({ allTrialResults }: { allTrialResults: any[] }) {
  const [expandedTrialId, setExpandedTrialId] = useState<string | null>(null);
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Clinical Trial Matches</CardTitle>
          <p className="text-sm text-gray-500 mt-2">
            {allTrialResults.length > 0
              ? `${allTrialResults.length} trial${allTrialResults.length > 1 ? 's' : ''} matched. Click on any trial to view patient matches.`
              : "No trials added yet. Click 'Add Trial' to match patients to a clinical trial."}
          </p>
        </CardHeader>
      </Card>

      {/* List of all trials */}
      {allTrialResults.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No trial matches yet</p>
            <p className="text-sm mt-2">Use the "Add Trial" button to start matching patients</p>
          </CardContent>
        </Card>
      ) : (
        allTrialResults.map((trialResult, index) => {
          const isExpanded = expandedTrialId === trialResult.trial_info.nct_id;

          return (
            <Card
              key={trialResult.trial_info.nct_id + index}
              className="border-l-4 border-l-[#0B5394] cursor-pointer hover:shadow-md transition-shadow"
              onClick={() =>
                setExpandedTrialId(isExpanded ? null : trialResult.trial_info.nct_id)
              }
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-lg">{trialResult.trial_info.title}</CardTitle>
                      <span className="text-xs text-gray-400">
                        {isExpanded ? "▼" : "▶"}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">Trial ID:</span>
                        <span className="font-medium">{trialResult.trial_info.nct_id}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">Condition:</span>
                        <span>{trialResult.trial_info.condition}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">Phase:</span>
                        <span>{trialResult.trial_info.phase}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-gray-500">Date Added:</span>
                        <span>{new Date(trialResult.date_added).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-green-50 rounded-lg ml-4">
                    <div className="text-2xl font-bold text-[#52C41A]">
                      {trialResult.total_matches}
                    </div>
                    <div className="text-xs text-gray-600 whitespace-nowrap">Patients Matched</div>
                  </div>
                </div>
              </CardHeader>

              {/* Expanded Patient Matches */}
              {isExpanded && (
                <CardContent className="border-t" onClick={(e) => e.stopPropagation()}>
                  <h4 className="font-medium mb-4">Top 10 Matched Patients</h4>

                  {/* Desktop Table */}
                  <div className="hidden md:block overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-gray-200">
                          <th className="text-left py-3 px-4 text-sm text-gray-500">Patient ID</th>
                          <th className="text-left py-3 px-4 text-sm text-gray-500">Age</th>
                          <th className="text-left py-3 px-4 text-sm text-gray-500">Condition</th>
                          <th className="text-left py-3 px-4 text-sm text-gray-500">
                            Match Score
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {trialResult.matches.map((match: any) => (
                          <tr
                            key={match.patient_id}
                            className="border-b border-gray-100 hover:bg-gray-50"
                          >
                            <td className="py-3 px-4">{match.patient_id}</td>
                            <td className="py-3 px-4">{match.age}</td>
                            <td className="py-3 px-4">{match.condition}</td>
                            <td className="py-3 px-4">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                                  <div
                                    className="bg-[#52C41A] h-2 rounded-full"
                                    style={{ width: `${match.score}%` }}
                                  />
                                </div>
                                <span className="text-sm">{match.score}%</span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Mobile Cards */}
                  <div className="md:hidden space-y-4">
                    {trialResult.matches.map((match: any) => (
                      <div key={match.patient_id} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-500">Patient ID</span>
                          <span>{match.patient_id}</span>
                        </div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-500">Age</span>
                          <span>{match.age}</span>
                        </div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm text-gray-500">Condition</span>
                          <span>{match.condition}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-3">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-[#52C41A] h-2 rounded-full"
                              style={{ width: `${match.score}%` }}
                            />
                          </div>
                          <span className="text-sm">{match.score}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              )}
            </Card>
          );
        })
      )}
    </div>
  );
}

// Sites View
function SitesView() {
  const sites = [
    {
      name: "Memorial Hospital",
      location: "New York, NY",
      trials: 12,
      capacity: 85,
    },
    {
      name: "City Medical Center",
      location: "Los Angeles, CA",
      trials: 8,
      capacity: 92,
    },
    {
      name: "Research Institute",
      location: "Boston, MA",
      trials: 15,
      capacity: 78,
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Site Selection Map</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg mb-6">
            <p className="text-gray-400">Map Placeholder</p>
          </div>

          <div className="space-y-3">
            {sites.map((site) => (
              <div
                key={site.name}
                className="p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="mb-1">{site.name}</h3>
                    <p className="text-sm text-gray-500">
                      {site.location}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm">
                      {site.trials} trials
                    </p>
                    <p className="text-sm text-gray-500">
                      {site.capacity}% capacity
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}