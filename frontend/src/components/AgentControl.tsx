import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { Pause, Play, MessageCircle, ArrowRight, Search, Sparkles, Users, Activity, CheckCircle, MapPin, TrendingUp } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./ui/dialog";
import AgentChat from "./AgentChat";

const agents = [
  { id: 1, name: "Eligibility Agent", key: "eligibility", status: "Processing", x: 15, y: 20, port: 8001 },
  { id: 2, name: "Pattern Agent", key: "pattern", status: "Complete", x: 80, y: 20, port: 8002 },
  { id: 3, name: "Discovery Agent", key: "discovery", status: "Processing", x: 50, y: 20, port: 8003 },
  { id: 4, name: "Matching Agent", key: "matching", status: "Complete", x: 20, y: 50, port: 8004 },
  { id: 5, name: "Site Agent", key: "site", status: "Processing", x: 35, y: 80, port: 8005 },
  { id: 6, name: "Prediction Agent", key: "prediction", status: "Complete", x: 65, y: 80, port: 8006 },
  { id: 7, name: "Validation Agent", key: "validation", status: "Complete", x: 80, y: 50, port: 8007 },
  { id: 8, name: "Coordinator", key: "coordinator", status: "Processing", x: 50, y: 50, isCenter: true, port: 8000 },
];

// Workflow pipeline agents in sequential order
const workflowAgents = [
  { name: "Eligibility Agent", key: "eligibility", description: "Criteria Extraction", icon: Search, color: "#0B5394" },
  { name: "Pattern Agent", key: "pattern", description: "Pattern Matching", icon: Sparkles, color: "#6B46C1" },
  { name: "Discovery Agent", key: "discovery", description: "Patient Discovery", icon: Users, color: "#52C41A" },
  { name: "Matching Agent", key: "matching", description: "Patient Scoring", icon: Activity, color: "#0B5394" },
  { name: "Validation Agent", key: "validation", description: "Exclusion Check", icon: CheckCircle, color: "#6B46C1" },
  { name: "Site Agent", key: "site", description: "Site Selection", icon: MapPin, color: "#52C41A" },
  { name: "Prediction Agent", key: "prediction", description: "Timeline Prediction", icon: TrendingUp, color: "#0B5394" },
];

const recentQueries = [
  { query: "Find patients for diabetes trial", time: "2 min ago", status: "Complete" },
  { query: "Analyze cardiovascular risk patterns", time: "15 min ago", status: "Complete" },
  { query: "Match patients to oncology studies", time: "1 hour ago", status: "Complete" },
  { query: "Generate compliance report for Q4", time: "2 hours ago", status: "Complete" },
  { query: "Screen patients with BMI > 30", time: "3 hours ago", status: "Complete" },
];

const activityMessages = [
  { agent: "Coordinator", message: "Initiating patient matching workflow for NCT04567890", color: "#0B5394" },
  { agent: "Eligibility Agent", message: "Extracting trial criteria from ClinicalTrials.gov", color: "#0B5394" },
  { agent: "Pattern Agent", message: "Matching patterns to trial criteria using UMAP", color: "#6B46C1" },
  { agent: "Discovery Agent", message: "Searching 1,000 FHIR patient records", color: "#52C41A" },
  { agent: "Discovery Agent", message: "Found 87 candidate patients in Pattern #42", color: "#52C41A" },
  { agent: "Matching Agent", message: "Scoring 87 patients using similarity metrics", color: "#0B5394" },
  { agent: "Validation Agent", message: "Validating patients against exclusion criteria", color: "#6B46C1" },
  { agent: "Validation Agent", message: "86 patients validated, 1 excluded (kidney disease)", color: "#6B46C1" },
  { agent: "Site Agent", message: "Analyzing feasibility for 10 trial sites", color: "#52C41A" },
  { agent: "Site Agent", message: "Top sites: UCLA (87%), Stanford (81%), UCSF (79%)", color: "#52C41A" },
  { agent: "Prediction Agent", message: "Forecasting enrollment timeline", color: "#0B5394" },
  { agent: "Prediction Agent", message: "Predicted completion: March 15, 2025", color: "#0B5394" },
  { agent: "Coordinator", message: "Workflow completed: 86 matches, 3 sites, 2.3s", color: "#0B5394" },
];

export default function AgentControl() {
  const [query, setQuery] = useState("");
  const [isPaused, setIsPaused] = useState(false);
  const [displayedMessages, setDisplayedMessages] = useState(activityMessages);

  useEffect(() => {
    if (!isPaused) {
      const interval = setInterval(() => {
        setDisplayedMessages((prev) => {
          const newMessage = activityMessages[Math.floor(Math.random() * activityMessages.length)];
          return [...prev.slice(-10), { ...newMessage, time: new Date().toISOString() }];
        });
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [isPaused]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Processing":
        return "#0B5394";
      case "Complete":
        return "#52C41A";
      case "Idle":
        return "#9CA3AF";
      default:
        return "#9CA3AF";
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Agent Workflow Pipeline */}
      <Card>
        <CardHeader>
          <CardTitle>Agent Workflow Pipeline</CardTitle>
          <p className="text-gray-500 text-sm">How the agent network processes clinical trial matching requests</p>
        </CardHeader>
        <CardContent>
          <div className="relative overflow-x-auto">
            {/* Trial Query Start */}
            <div className="flex items-center gap-3 mb-8 min-w-max">
              <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 text-white flex items-center justify-center shadow-lg">
                <div className="text-center">
                  <Search className="w-6 h-6 mx-auto mb-1" />
                  <p className="text-[10px] font-semibold">Trial Query</p>
                </div>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />

              {/* Workflow Agents in Horizontal Layout */}
              <div className="flex items-center gap-2 flex-1 min-w-0">
                {workflowAgents.map((agent, index) => {
                  const Icon = agent.icon;
                  return (
                    <React.Fragment key={agent.key}>
                      <div className="flex-shrink-0">
                        <div
                          className="w-20 h-20 rounded-lg shadow-md hover:shadow-lg transition-all cursor-pointer flex flex-col items-center justify-center text-white relative overflow-hidden group"
                          style={{ backgroundColor: agent.color }}
                        >
                          <div className="absolute inset-0 bg-black opacity-0 group-hover:opacity-10 transition-opacity"></div>
                          <Icon className="w-5 h-5 mb-1" />
                          <p className="text-[10px] font-semibold text-center px-1 leading-tight">{agent.name.replace(" Agent", "")}</p>
                          <div className="absolute top-1 right-1">
                            <div className="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></div>
                          </div>
                        </div>
                      </div>
                      {index < workflowAgents.length - 1 && (
                        <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      )}
                    </React.Fragment>
                  );
                })}
              </div>

              <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />

              {/* Patient Matches Result */}
              <div className="flex-shrink-0 w-20 h-20 rounded-lg bg-gradient-to-br from-green-500 to-green-600 text-white flex items-center justify-center shadow-lg">
                <div className="text-center">
                  <Users className="w-6 h-6 mx-auto mb-1" />
                  <p className="text-[10px] font-semibold">Matches</p>
                </div>
              </div>
            </div>

            {/* Sequential Agent Execution */}
            <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 rounded-lg p-4">
              <h4 className="text-sm font-semibold mb-3 text-gray-700">Sequential Agent Execution:</h4>
              <div className="space-y-2">
                {workflowAgents.map((agent, index) => (
                  <div key={agent.key} className="flex items-center gap-3 text-sm">
                    <div className="flex items-center justify-center w-6 h-6 rounded-full bg-white border-2" style={{ borderColor: agent.color }}>
                      <span className="text-xs font-bold" style={{ color: agent.color }}>{index + 1}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {React.createElement(agent.icon, { className: "w-4 h-4", style: { color: agent.color } })}
                      <span className="font-medium" style={{ color: agent.color }}>{agent.name}</span>
                    </div>
                    <span className="text-gray-600 text-xs">{agent.description}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hexagon Flow Diagram */}
      <Card>
        <CardHeader>
          <CardTitle>AI Agent Network</CardTitle>
          <p className="text-gray-500 text-sm">Real-time agent orchestration and status</p>
        </CardHeader>
        <CardContent>
          <div className="relative h-[500px] bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-8">
            {/* Connection Lines */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {agents
                .filter((agent) => !agent.isCenter)
                .map((agent) => {
                  const centerAgent = agents.find((a) => a.isCenter);
                  if (!centerAgent) return null;
                  return (
                    <line
                      key={agent.id}
                      x1={`${agent.x}%`}
                      y1={`${agent.y}%`}
                      x2={`${centerAgent.x}%`}
                      y2={`${centerAgent.y}%`}
                      stroke="#0B5394"
                      strokeWidth="2"
                      strokeDasharray="5,5"
                      className="animate-pulse"
                      opacity="0.3"
                    />
                  );
                })}
            </svg>

            {/* Agent Hexagons */}
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 transition-all hover:scale-110"
                style={{ left: `${agent.x}%`, top: `${agent.y}%` }}
              >
                <div
                  className={`${
                    agent.isCenter ? "w-40 h-40" : "w-28 h-28"
                  } relative flex items-center justify-center`}
                >
                  {/* Hexagon */}
                  <div
                    className="absolute inset-0 rounded-lg shadow-lg flex items-center justify-center"
                    style={{
                      backgroundColor: "white",
                      border: `3px solid ${getStatusColor(agent.status)}`,
                    }}
                  >
                    <div className="text-center p-2">
                      <div
                        className="w-3 h-3 rounded-full mx-auto mb-2"
                        style={{
                          backgroundColor: getStatusColor(agent.status),
                          animation: agent.status === "Processing" ? "pulse 2s infinite" : "none",
                        }}
                      ></div>
                      <p className={`text-xs ${agent.isCenter ? "font-semibold" : ""}`}>
                        {agent.name.replace(" Agent", "")}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{agent.status}</p>

                      {/* Chat Button */}
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            size="sm"
                            variant="outline"
                            className="mt-2 h-7 px-2 text-xs"
                            onClick={(e: React.MouseEvent) => e.stopPropagation()}
                          >
                            <MessageCircle className="w-3 h-3 mr-1" />
                            Chat
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>Chat with {agent.name}</DialogTitle>
                          </DialogHeader>
                          <AgentChat
                            agentName={agent.key}
                            agentDisplayName={agent.name}
                          />
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Query Interface - Left */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Natural Language Control</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-3">
                <Input
                  placeholder="E.g., Find patients for diabetes trial..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="flex-1"
                />
                <Button className="bg-[#0B5394] hover:bg-[#0B5394]/90">Execute</Button>
              </div>
              <p className="text-sm text-gray-500">
                Try: "Find patients for diabetes trial" or "Analyze cardiovascular patterns"
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Recent Queries</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentQueries.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div>
                      <p className="text-sm">{item.query}</p>
                      <p className="text-xs text-gray-500 mt-1">{item.time}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#52C41A]"></div>
                      <span className="text-xs text-gray-600">{item.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activity Log - Right */}
        <div>
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Activity Log</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsPaused(!isPaused)}
                >
                  {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[500px]">
                <div className="space-y-3">
                  {displayedMessages.map((msg, index) => (
                    <div
                      key={index}
                      className="p-3 rounded-lg border-l-4 bg-gray-50"
                      style={{ borderLeftColor: msg.color }}
                    >
                      <p className="text-xs" style={{ color: msg.color }}>
                        {msg.agent}
                      </p>
                      <p className="text-sm mt-1">{msg.message}</p>
                      <p className="text-xs text-gray-500 mt-1">Just now</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
