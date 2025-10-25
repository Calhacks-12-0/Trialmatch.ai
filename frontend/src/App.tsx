import { useState } from "react";
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
  Activity,
  Search,
  Users,
  MapPin,
  Settings,
} from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");

  return (
    <div className="min-h-screen bg-[#F5F7FA]">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
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
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="w-full"
        >
          <TabsList className="grid w-full grid-cols-5 mb-6">
            <TabsTrigger value="dashboard">
              <Activity className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">
                Dashboard
              </span>
            </TabsTrigger>
            <TabsTrigger value="patterns">
              <Search className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Patterns</span>
            </TabsTrigger>
            <TabsTrigger value="agents">
              <Settings className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Agents</span>
            </TabsTrigger>
            <TabsTrigger value="matches">
              <Users className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Matches</span>
            </TabsTrigger>
            <TabsTrigger value="sites">
              <MapPin className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Sites</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="dashboard">
            <DashboardView />
          </TabsContent>

          <TabsContent value="patterns">
            <PatternsView />
          </TabsContent>

          <TabsContent value="agents">
            <AgentsView />
          </TabsContent>

          <TabsContent value="matches">
            <MatchesView />
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
        <Card>
          <CardHeader>
            <CardTitle>Trial Enrollment Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <p className="text-gray-400">Chart Placeholder</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Match Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
              <p className="text-gray-400">Chart Placeholder</p>
            </div>
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

// Patterns View
function PatternsView() {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Pattern Discovery</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-gray-400">
              Scatter Plot & Filters Placeholder
            </p>
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
function MatchesView() {
  const matches = [
    {
      id: "P001",
      name: "Patient A",
      trial: "NCT001234",
      score: 95,
    },
    {
      id: "P002",
      name: "Patient B",
      trial: "NCT001235",
      score: 92,
    },
    {
      id: "P003",
      name: "Patient C",
      trial: "NCT001236",
      score: 88,
    },
    {
      id: "P004",
      name: "Patient D",
      trial: "NCT001237",
      score: 85,
    },
  ];

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Patient Matches</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Desktop Table */}
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm text-gray-500">
                    Patient ID
                  </th>
                  <th className="text-left py-3 px-4 text-sm text-gray-500">
                    Name
                  </th>
                  <th className="text-left py-3 px-4 text-sm text-gray-500">
                    Trial
                  </th>
                  <th className="text-left py-3 px-4 text-sm text-gray-500">
                    Match Score
                  </th>
                </tr>
              </thead>
              <tbody>
                {matches.map((match) => (
                  <tr
                    key={match.id}
                    className="border-b border-gray-100 hover:bg-gray-50"
                  >
                    <td className="py-3 px-4">{match.id}</td>
                    <td className="py-3 px-4">{match.name}</td>
                    <td className="py-3 px-4">{match.trial}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 max-w-[100px]">
                          <div
                            className="bg-[#52C41A] h-2 rounded-full"
                            style={{ width: `${match.score}%` }}
                          />
                        </div>
                        <span className="text-sm">
                          {match.score}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile Cards */}
          <div className="md:hidden space-y-4">
            {matches.map((match) => (
              <div
                key={match.id}
                className="p-4 bg-gray-50 rounded-lg"
              >
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    Patient ID
                  </span>
                  <span>{match.id}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    Name
                  </span>
                  <span>{match.name}</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">
                    Trial
                  </span>
                  <span>{match.trial}</span>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-[#52C41A] h-2 rounded-full"
                      style={{ width: `${match.score}%` }}
                    />
                  </div>
                  <span className="text-sm">
                    {match.score}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
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