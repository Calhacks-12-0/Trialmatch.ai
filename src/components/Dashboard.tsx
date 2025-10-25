import { Activity, Users, Target, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { Tabs, TabsList, TabsTrigger } from "./ui/tabs";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { useState } from "react";

const metrics = [
  { title: "Patients Analyzed", value: "50,847", icon: Users, color: "#0B5394" },
  { title: "Patterns Discovered", value: "27", icon: Target, color: "#6B46C1" },
  { title: "Active Trials", value: "12", icon: Activity, color: "#52C41A" },
  { title: "Average Match Time", value: "2.3s", icon: Clock, color: "#0B5394" },
];

const recentTrials = [
  { id: "NCT2024001", name: "Type 2 Diabetes Glucose Control Study", matched: 847, status: "Active" },
  { id: "NCT2024002", name: "Alzheimer's Prevention Trial Phase III", matched: 234, status: "Recruiting" },
  { id: "NCT2024003", name: "Breast Cancer Immunotherapy Study", matched: 156, status: "Active" },
  { id: "NCT2024004", name: "Hypertension Management Trial", matched: 923, status: "Enrolling" },
  { id: "NCT2024005", name: "COPD Treatment Efficacy Study", matched: 445, status: "Active" },
];

const enrollmentData3Month = [
  { month: "Oct", predicted: 120, actual: 115 },
  { month: "Nov", predicted: 145, actual: 152 },
  { month: "Dec", predicted: 170, actual: 168 },
];

const enrollmentData6Month = [
  { month: "Jul", predicted: 50, actual: 45 },
  { month: "Aug", predicted: 75, actual: 78 },
  { month: "Sep", predicted: 95, actual: 92 },
  { month: "Oct", predicted: 120, actual: 115 },
  { month: "Nov", predicted: 145, actual: 152 },
  { month: "Dec", predicted: 170, actual: 168 },
];

const enrollmentData12Month = [
  { month: "Jan", predicted: 10, actual: 8 },
  { month: "Feb", predicted: 20, actual: 22 },
  { month: "Mar", predicted: 35, actual: 32 },
  { month: "Apr", predicted: 45, actual: 48 },
  { month: "May", predicted: 60, actual: 58 },
  { month: "Jun", predicted: 80, actual: 75 },
  { month: "Jul", predicted: 95, actual: 92 },
  { month: "Aug", predicted: 110, actual: 115 },
  { month: "Sep", predicted: 130, actual: 128 },
  { month: "Oct", predicted: 145, actual: 148 },
  { month: "Nov", predicted: 160, actual: 165 },
  { month: "Dec", predicted: 180, actual: 175 },
];

const agents = [
  { name: "Screening", status: "Processing" },
  { name: "Matching", status: "Complete" },
  { name: "Analytics", status: "Idle" },
  { name: "Reporting", status: "Processing" },
  { name: "Compliance", status: "Complete" },
  { name: "Coordinator", status: "Processing" },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "Active":
    case "Complete":
      return "bg-[#52C41A] text-white";
    case "Recruiting":
    case "Processing":
      return "bg-[#0B5394] text-white";
    case "Enrolling":
      return "bg-[#6B46C1] text-white";
    case "Idle":
      return "bg-gray-400 text-white";
    default:
      return "bg-gray-400 text-white";
  }
};

export default function Dashboard() {
  const [enrollmentPeriod, setEnrollmentPeriod] = useState("6");

  const getEnrollmentData = () => {
    switch (enrollmentPeriod) {
      case "3":
        return enrollmentData3Month;
      case "6":
        return enrollmentData6Month;
      case "12":
        return enrollmentData12Month;
      default:
        return enrollmentData6Month;
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">{metric.title}</p>
                  <h3 className="mt-2" style={{ color: metric.color }}>{metric.value}</h3>
                </div>
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: `${metric.color}20` }}
                >
                  <metric.icon className="w-6 h-6" style={{ color: metric.color }} />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Section - Wider */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent Trials */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Trials</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentTrials.map((trial) => (
                  <div
                    key={trial.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <span className="text-gray-500 text-sm">{trial.id}</span>
                        <Badge className={getStatusColor(trial.status)}>{trial.status}</Badge>
                      </div>
                      <p className="mt-1">{trial.name}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[#0B5394]">{trial.matched}</p>
                      <p className="text-gray-500 text-sm">matched</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Enrollment Chart */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Enrollment Trends</CardTitle>
                <Tabs value={enrollmentPeriod} onValueChange={setEnrollmentPeriod}>
                  <TabsList className="bg-gray-100">
                    <TabsTrigger value="3">3M</TabsTrigger>
                    <TabsTrigger value="6">6M</TabsTrigger>
                    <TabsTrigger value="12">12M</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={getEnrollmentData()}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="month" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="predicted"
                    stroke="#0B5394"
                    strokeWidth={2}
                    name="Predicted"
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#52C41A"
                    strokeWidth={2}
                    name="Actual"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Right Section - Narrower */}
        <div className="space-y-6">
          {/* AI Agents Status */}
          <Card>
            <CardHeader>
              <CardTitle>AI Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {agents.map((agent, index) => (
                  <div
                    key={index}
                    className="p-4 rounded-lg border-2 border-gray-200 hover:border-[#0B5394] transition-colors"
                  >
                    <div className="flex flex-col items-center text-center">
                      <div
                        className={`w-3 h-3 rounded-full mb-2 ${
                          agent.status === "Processing"
                            ? "bg-[#0B5394] animate-pulse"
                            : agent.status === "Complete"
                            ? "bg-[#52C41A]"
                            : "bg-gray-400"
                        }`}
                      ></div>
                      <p className="text-sm">{agent.name}</p>
                      <p className="text-xs text-gray-500 mt-1">{agent.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full bg-[#0B5394] hover:bg-[#0B5394]/90">
                New Trial Search
              </Button>
              <Button className="w-full bg-[#6B46C1] hover:bg-[#6B46C1]/90">
                Upload Patient Cohort
              </Button>
              <Button className="w-full bg-[#52C41A] hover:bg-[#52C41A]/90">
                Generate Report
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
