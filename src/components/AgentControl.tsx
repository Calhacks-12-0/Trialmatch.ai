import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ScrollArea } from "./ui/scroll-area";
import { Pause, Play } from "lucide-react";

const agents = [
  { id: 1, name: "Screening Agent", status: "Processing", x: 50, y: 20 },
  { id: 2, name: "Matching Agent", status: "Complete", x: 20, y: 50 },
  { id: 3, name: "Analytics Agent", status: "Idle", x: 80, y: 50 },
  { id: 4, name: "Reporting Agent", status: "Processing", x: 35, y: 80 },
  { id: 5, name: "Compliance Agent", status: "Complete", x: 65, y: 80 },
  { id: 6, name: "Coordinator", status: "Processing", x: 50, y: 50, isCenter: true },
];

const recentQueries = [
  { query: "Find patients for diabetes trial", time: "2 min ago", status: "Complete" },
  { query: "Analyze cardiovascular risk patterns", time: "15 min ago", status: "Complete" },
  { query: "Match patients to oncology studies", time: "1 hour ago", status: "Complete" },
  { query: "Generate compliance report for Q4", time: "2 hours ago", status: "Complete" },
  { query: "Screen patients with BMI > 30", time: "3 hours ago", status: "Complete" },
];

const activityMessages = [
  { agent: "Coordinator", message: "Initiating patient screening workflow", color: "#0B5394" },
  { agent: "Screening Agent", message: "Processing 1,247 patient records", color: "#52C41A" },
  { agent: "Matching Agent", message: "Found 89 potential matches for NCT2024001", color: "#6B46C1" },
  { agent: "Analytics Agent", message: "Calculating success probability scores", color: "#0B5394" },
  { agent: "Compliance Agent", message: "Verifying eligibility criteria compliance", color: "#52C41A" },
  { agent: "Reporting Agent", message: "Generating match summary report", color: "#6B46C1" },
  { agent: "Coordinator", message: "Workflow completed successfully", color: "#0B5394" },
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
                    agent.isCenter ? "w-32 h-32" : "w-24 h-24"
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
                      <p className={`text-xs ${agent.isCenter ? "" : "text-xs"}`}>
                        {agent.name.replace(" Agent", "")}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{agent.status}</p>
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
