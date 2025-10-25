import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Download, Filter, ArrowUpDown, Eye, Mail } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Progress } from "./ui/progress";

const patients = [
  {
    id: "PT-10847",
    matchScore: 94,
    age: 62,
    gender: "F",
    conditions: "Type 2 Diabetes, Hypertension",
    location: "Boston, MA",
    likelihood: "Very High",
  },
  {
    id: "PT-10923",
    matchScore: 89,
    age: 58,
    gender: "M",
    conditions: "Type 2 Diabetes, High Cholesterol",
    location: "Cambridge, MA",
    likelihood: "High",
  },
  {
    id: "PT-11205",
    matchScore: 87,
    age: 65,
    gender: "F",
    conditions: "Type 2 Diabetes, Obesity",
    location: "Worcester, MA",
    likelihood: "High",
  },
  {
    id: "PT-11384",
    matchScore: 82,
    age: 54,
    gender: "M",
    conditions: "Type 2 Diabetes",
    location: "Springfield, MA",
    likelihood: "Moderate",
  },
  {
    id: "PT-11502",
    matchScore: 79,
    age: 67,
    gender: "F",
    conditions: "Type 2 Diabetes, Kidney Disease",
    location: "Lowell, MA",
    likelihood: "Moderate",
  },
  {
    id: "PT-11678",
    matchScore: 76,
    age: 59,
    gender: "M",
    conditions: "Type 2 Diabetes, Neuropathy",
    location: "New Bedford, MA",
    likelihood: "Moderate",
  },
  {
    id: "PT-11834",
    matchScore: 73,
    age: 61,
    gender: "F",
    conditions: "Type 2 Diabetes, Retinopathy",
    location: "Quincy, MA",
    likelihood: "Moderate",
  },
  {
    id: "PT-11956",
    matchScore: 68,
    age: 55,
    gender: "M",
    conditions: "Type 2 Diabetes, COPD",
    location: "Lynn, MA",
    likelihood: "Low",
  },
];

const scoreDistribution = [
  { name: "90-100", value: 127, color: "#52C41A" },
  { name: "80-89", value: 234, color: "#0B5394" },
  { name: "70-79", value: 312, color: "#6B46C1" },
  { name: "60-69", value: 174, color: "#9CA3AF" },
];

const getLikelihoodColor = (likelihood: string) => {
  switch (likelihood) {
    case "Very High":
      return "bg-[#52C41A] text-white";
    case "High":
      return "bg-[#0B5394] text-white";
    case "Moderate":
      return "bg-[#6B46C1] text-white";
    case "Low":
      return "bg-gray-400 text-white";
    default:
      return "bg-gray-400 text-white";
  }
};

export default function PatientMatches() {
  const [sortField, setSortField] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 8;

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  return (
    <div className="pb-20">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3 space-y-6">
          {/* Header */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2>Type 2 Diabetes Glucose Control Study</h2>
                  <p className="text-gray-500 mt-1">NCT2024001 • 847 Matched Patients</p>
                </div>
                <div className="flex gap-3">
                  <Button variant="outline">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                  <Button className="bg-[#0B5394] hover:bg-[#0B5394]/90">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Table */}
          <Card>
            <CardHeader>
              <CardTitle>Patient Matches</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>
                      <button
                        onClick={() => handleSort("id")}
                        className="flex items-center gap-1 hover:text-[#0B5394]"
                      >
                        Patient ID
                        <ArrowUpDown className="w-4 h-4" />
                      </button>
                    </TableHead>
                    <TableHead>
                      <button
                        onClick={() => handleSort("matchScore")}
                        className="flex items-center gap-1 hover:text-[#0B5394]"
                      >
                        Match Score
                        <ArrowUpDown className="w-4 h-4" />
                      </button>
                    </TableHead>
                    <TableHead>Age/Gender</TableHead>
                    <TableHead>Conditions</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Likelihood</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {patients.slice(0, itemsPerPage).map((patient) => (
                    <TableRow key={patient.id} className="hover:bg-gray-50">
                      <TableCell className="text-[#0B5394]">{patient.id}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Progress value={patient.matchScore} className="w-20" />
                          <span>{patient.matchScore}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {patient.age} / {patient.gender}
                      </TableCell>
                      <TableCell className="max-w-xs truncate">{patient.conditions}</TableCell>
                      <TableCell>{patient.location}</TableCell>
                      <TableCell>
                        <Badge className={getLikelihoodColor(patient.likelihood)}>
                          {patient.likelihood}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Mail className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-600">
                  Showing {(currentPage - 1) * itemsPerPage + 1} to{" "}
                  {Math.min(currentPage * itemsPerPage, patients.length)} of {patients.length} results
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(currentPage + 1)}
                    disabled={currentPage * itemsPerPage >= patients.length}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Score Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Score Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={scoreDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    dataKey="value"
                  >
                    {scoreDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-4 space-y-2">
                {scoreDistribution.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: item.color }}
                      ></div>
                      <span>{item.name}</span>
                    </div>
                    <span className="text-gray-600">{item.value}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Statistics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Average Score</span>
                <span className="text-[#0B5394]">82.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Top Score</span>
                <span className="text-[#52C41A]">98%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Matches</span>
                <span className="text-[#6B46C1]">847</span>
              </div>
            </CardContent>
          </Card>

          {/* Location Filter */}
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-gray-600 mb-2 block">Min Match Score</label>
                <Select defaultValue="70">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="90">90%+</SelectItem>
                    <SelectItem value="80">80%+</SelectItem>
                    <SelectItem value="70">70%+</SelectItem>
                    <SelectItem value="60">60%+</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-gray-600 mb-2 block">Location</label>
                <Select defaultValue="all">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Locations</SelectItem>
                    <SelectItem value="boston">Boston, MA</SelectItem>
                    <SelectItem value="cambridge">Cambridge, MA</SelectItem>
                    <SelectItem value="worcester">Worcester, MA</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm text-gray-600 mb-2 block">Likelihood</label>
                <Select defaultValue="all">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All</SelectItem>
                    <SelectItem value="very-high">Very High</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="moderate">Moderate</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button className="w-full">Apply Filters</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}