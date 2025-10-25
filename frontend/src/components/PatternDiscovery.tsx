import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Slider } from "./ui/slider";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const scatterData = [
  { x: 45, y: 78, group: 1, patients: 127, pattern: "Diabetes + Hypertension", success: 84 },
  { x: 62, y: 65, group: 2, patients: 89, pattern: "Early Stage Cancer", success: 76 },
  { x: 38, y: 92, group: 3, patients: 234, pattern: "Cardiovascular Risk", success: 91 },
  { x: 71, y: 45, group: 1, patients: 156, pattern: "Metabolic Syndrome", success: 79 },
  { x: 55, y: 88, group: 2, patients: 98, pattern: "Respiratory Disorders", success: 82 },
  { x: 29, y: 71, group: 3, patients: 167, pattern: "Neurological Conditions", success: 88 },
  { x: 82, y: 59, group: 1, patients: 112, pattern: "Autoimmune Diseases", success: 74 },
  { x: 48, y: 82, group: 2, patients: 143, pattern: "Chronic Pain", success: 86 },
  { x: 67, y: 38, group: 3, patients: 91, pattern: "Kidney Disease", success: 71 },
  { x: 41, y: 95, group: 1, patients: 203, pattern: "Heart Failure", success: 93 },
  { x: 76, y: 52, group: 2, patients: 134, pattern: "Liver Dysfunction", success: 77 },
  { x: 33, y: 68, group: 3, patients: 178, pattern: "Depression + Anxiety", success: 85 },
];

const patterns = [
  {
    id: 1,
    number: "P-001",
    name: "Diabetes + Hypertension Cluster",
    patients: 1247,
    details: "Age 55-70, BMI >30, HbA1c >7.5%",
    success: 84,
  },
  {
    id: 2,
    number: "P-002",
    name: "Early Cardiovascular Risk",
    patients: 2134,
    details: "Age 45-60, Cholesterol >200, Family History",
    success: 91,
  },
  {
    id: 3,
    number: "P-003",
    name: "Autoimmune Comorbidity",
    patients: 567,
    details: "Multiple autoimmune markers, Age 30-50",
    success: 74,
  },
  {
    id: 4,
    number: "P-004",
    name: "Respiratory Complex",
    patients: 892,
    details: "COPD + Asthma, Smoking history",
    success: 82,
  },
  {
    id: 5,
    number: "P-005",
    name: "Metabolic Syndrome Profile",
    patients: 1563,
    details: "Insulin resistance, High triglycerides",
    success: 79,
  },
  {
    id: 6,
    number: "P-006",
    name: "Neurological Degeneration",
    patients: 434,
    details: "Age >65, Cognitive decline markers",
    success: 88,
  },
];

const groupColors = ["#0B5394", "#52C41A", "#6B46C1"];

export default function PatternDiscovery() {
  const [successRate, setSuccessRate] = useState([70]);
  const [patientCount, setPatientCount] = useState([100]);
  const [conditions, setConditions] = useState({
    diabetes: true,
    cardiovascular: true,
    autoimmune: false,
    respiratory: false,
  });

  return (
    <div className="pb-20">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content - Left */}
        <div className="lg:col-span-3 space-y-6">
          {/* Scatter Plot */}
          <Card>
            <CardHeader>
              <CardTitle>Patient Pattern Distribution</CardTitle>
              <p className="text-gray-500 text-sm">Hover over dots to see pattern details</p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Age Range"
                    stroke="#6b7280"
                    label={{ value: "Age Factor", position: "insideBottom", offset: -5 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Success"
                    stroke="#6b7280"
                    label={{ value: "Success Score", angle: -90, position: "insideLeft" }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: "3 3" }}
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
                            <p className="text-sm">{data.pattern}</p>
                            <p className="text-sm text-gray-600">Patients: {data.patients}</p>
                            <p className="text-sm text-gray-600">Success: {data.success}%</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Scatter data={scatterData} fill="#8884d8">
                    {scatterData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={groupColors[entry.group - 1]} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Pattern Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {patterns.map((pattern) => (
              <Card key={pattern.id} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-gray-500 text-sm">{pattern.number}</p>
                      <h4 className="mt-1">{pattern.name}</h4>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-4">{pattern.details}</p>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-[#0B5394]">{pattern.patients.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">Patients</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[#52C41A]">{pattern.success}%</p>
                      <p className="text-xs text-gray-500">Success</p>
                    </div>
                  </div>
                  <Button className="w-full bg-[#6B46C1] hover:bg-[#6B46C1]/90">
                    Apply
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Filters Sidebar - Right */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Filters</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Success Rate */}
              <div>
                <Label>Success Rate: ≥{successRate[0]}%</Label>
                <Slider
                  value={successRate}
                  onValueChange={setSuccessRate}
                  min={0}
                  max={100}
                  step={5}
                  className="mt-2"
                />
              </div>

              {/* Patient Count */}
              <div>
                <Label>Min Patients: {patientCount[0]}</Label>
                <Slider
                  value={patientCount}
                  onValueChange={setPatientCount}
                  min={0}
                  max={3000}
                  step={100}
                  className="mt-2"
                />
              </div>

              {/* Conditions */}
              <div>
                <Label className="mb-3 block">Conditions</Label>
                <div className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="diabetes"
                      checked={conditions.diabetes}
                      onCheckedChange={(checked) =>
                        setConditions({ ...conditions, diabetes: checked as boolean })
                      }
                    />
                    <label htmlFor="diabetes" className="text-sm cursor-pointer">
                      Diabetes
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="cardiovascular"
                      checked={conditions.cardiovascular}
                      onCheckedChange={(checked) =>
                        setConditions({ ...conditions, cardiovascular: checked as boolean })
                      }
                    />
                    <label htmlFor="cardiovascular" className="text-sm cursor-pointer">
                      Cardiovascular
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="autoimmune"
                      checked={conditions.autoimmune}
                      onCheckedChange={(checked) =>
                        setConditions({ ...conditions, autoimmune: checked as boolean })
                      }
                    />
                    <label htmlFor="autoimmune" className="text-sm cursor-pointer">
                      Autoimmune
                    </label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="respiratory"
                      checked={conditions.respiratory}
                      onCheckedChange={(checked) =>
                        setConditions({ ...conditions, respiratory: checked as boolean })
                      }
                    />
                    <label htmlFor="respiratory" className="text-sm cursor-pointer">
                      Respiratory
                    </label>
                  </div>
                </div>
              </div>

              {/* Age Range */}
              <div>
                <Label>Age Range: 30-80</Label>
                <Slider defaultValue={[30]} min={0} max={100} step={1} className="mt-2" />
              </div>

              <Button className="w-full">Apply Filters</Button>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Patterns</span>
                <span className="text-[#0B5394]">27</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg Success Rate</span>
                <span className="text-[#52C41A]">83%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Patients</span>
                <span className="text-[#6B46C1]">8,340</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}