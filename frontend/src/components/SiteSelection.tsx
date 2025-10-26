import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { MapPin, Navigation, Users } from "lucide-react";

const sites = [
  {
    id: 1,
    name: "Massachusetts General Hospital",
    city: "Boston, MA",
    patients: 1247,
    distance: "12 min",
    lat: 42.3636,
    lng: -71.0686,
  },
  {
    id: 2,
    name: "Beth Israel Deaconess Medical Center",
    city: "Boston, MA",
    patients: 923,
    distance: "15 min",
    lat: 42.3389,
    lng: -71.1063,
  },
  {
    id: 3,
    name: "Brigham and Women's Hospital",
    city: "Boston, MA",
    patients: 834,
    distance: "18 min",
    lat: 42.3359,
    lng: -71.1068,
  },
  {
    id: 4,
    name: "Cambridge Health Alliance",
    city: "Cambridge, MA",
    patients: 567,
    distance: "22 min",
    lat: 42.3736,
    lng: -71.1097,
  },
  {
    id: 5,
    name: "Tufts Medical Center",
    city: "Boston, MA",
    patients: 445,
    distance: "14 min",
    lat: 42.3496,
    lng: -71.0634,
  },
];

const heatmapRegions = [
  { name: "Downtown Boston", patients: 2340, intensity: 90 },
  { name: "Cambridge", patients: 1567, intensity: 75 },
  { name: "Brookline", patients: 1234, intensity: 65 },
  { name: "Somerville", patients: 987, intensity: 55 },
  { name: "Newton", patients: 756, intensity: 45 },
];

export default function SiteSelection() {
  const [selectedSite, setSelectedSite] = useState<number | null>(null);

  return (
    <div className="pb-20">
      {/* Top Stats Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Coverage Area</p>
                <p className="text-[#0B5394] mt-1">847 sq mi</p>
              </div>
              <MapPin className="w-8 h-8 text-[#0B5394]" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Patients Within 50 Miles</p>
                <p className="text-[#52C41A] mt-1">8,234</p>
              </div>
              <Users className="w-8 h-8 text-[#52C41A]" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Average Drive Time</p>
                <p className="text-[#6B46C1] mt-1">18 min</p>
              </div>
              <Navigation className="w-8 h-8 text-[#6B46C1]" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Panel - Site List */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recommended Sites</CardTitle>
              <p className="text-gray-500 text-sm">Top 5 by patient density</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {sites.map((site) => (
                <div
                  key={site.id}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-md ${
                    selectedSite === site.id
                      ? "border-[#0B5394] bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setSelectedSite(site.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-sm">{site.name}</h4>
                    <Badge className="bg-[#0B5394] text-white">#{site.id}</Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-3">{site.city}</p>
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-1 text-[#52C41A]">
                      <Users className="w-4 h-4" />
                      <span>{site.patients}</span>
                    </div>
                    <div className="flex items-center gap-1 text-gray-600">
                      <Navigation className="w-4 h-4" />
                      <span>{site.distance}</span>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Main Map Area */}
        <div className="lg:col-span-3">
          <Card>
            <CardContent className="p-0">
              {/* Map Container */}
              <div className="relative h-[600px] bg-gradient-to-br from-blue-50 to-gray-100 rounded-lg overflow-hidden">
                {/* Simulated Map Background */}
                <div className="absolute inset-0 opacity-20">
                  <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDEwIEwgNDAgMTAgTSAxMCAwIEwgMTAgNDAgTSAwIDIwIEwgNDAgMjAgTSAyMCAwIEwgMjAgNDAgTSAwIDMwIEwgNDAgMzAgTSAzMCAwIEwgMzAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzAwMCIgb3BhY2l0eT0iMC4xIiBzdHJva2Utd2lkdGg9IjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')]"></div>
                </div>

                {/* Heatmap Regions */}
                {heatmapRegions.map((region, index) => (
                  <div
                    key={index}
                    className="absolute rounded-full blur-2xl transition-all"
                    style={{
                      left: `${15 + index * 15}%`,
                      top: `${20 + index * 12}%`,
                      width: `${region.intensity * 2}px`,
                      height: `${region.intensity * 2}px`,
                      backgroundColor: `rgba(11, 83, 148, ${region.intensity / 200})`,
                    }}
                  ></div>
                ))}

                {/* Site Markers */}
                {sites.map((site, index) => (
                  <div
                    key={site.id}
                    className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer group"
                    style={{
                      left: `${25 + index * 15}%`,
                      top: `${30 + index * 10}%`,
                    }}
                    onClick={() => setSelectedSite(site.id)}
                  >
                    {/* Marker Pin */}
                    <div
                      className={`relative transition-all ${
                        selectedSite === site.id ? "scale-125" : "scale-100 group-hover:scale-110"
                      }`}
                    >
                      <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center shadow-lg ${
                          selectedSite === site.id
                            ? "bg-[#0B5394] ring-4 ring-[#0B5394]/30"
                            : "bg-white border-2 border-[#0B5394]"
                        }`}
                      >
                        <MapPin
                          className={`w-5 h-5 ${
                            selectedSite === site.id ? "text-white" : "text-[#0B5394]"
                          }`}
                        />
                      </div>

                      {/* Tooltip */}
                      <div
                        className={`absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 p-3 transition-opacity ${
                          selectedSite === site.id ? "opacity-100" : "opacity-0 group-hover:opacity-100"
                        }`}
                      >
                        <p className="text-sm">{site.name}</p>
                        <p className="text-xs text-gray-600 mt-1">{site.city}</p>
                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-200">
                          <div className="flex items-center gap-1 text-[#52C41A]">
                            <Users className="w-3 h-3" />
                            <span className="text-xs">{site.patients}</span>
                          </div>
                          <div className="flex items-center gap-1 text-gray-600">
                            <Navigation className="w-3 h-3" />
                            <span className="text-xs">{site.distance}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Pulse Animation for Selected */}
                    {selectedSite === site.id && (
                      <div className="absolute inset-0 -z-10">
                        <div className="w-10 h-10 rounded-full bg-[#0B5394] animate-ping opacity-20"></div>
                      </div>
                    )}
                  </div>
                ))}

                {/* Legend */}
                <div className="absolute bottom-4 left-4 bg-white rounded-lg shadow-lg p-4">
                  <h4 className="text-sm mb-3">Patient Density</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-[#0B5394] opacity-80"></div>
                      <span className="text-xs">High (1000+)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-[#0B5394] opacity-50"></div>
                      <span className="text-xs">Medium (500-1000)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full bg-[#0B5394] opacity-20"></div>
                      <span className="text-xs">Low (&lt;500)</span>
                    </div>
                  </div>
                </div>

                {/* Controls */}
                <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-2 space-y-2">
                  <button className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded">
                    +
                  </button>
                  <button className="w-8 h-8 flex items-center justify-center hover:bg-gray-100 rounded">
                    -
                  </button>
                </div>

                {/* Selected Site Details */}
                {selectedSite && (
                  <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-4 max-w-xs">
                    <div className="flex items-start justify-between mb-2">
                      <h4>{sites.find((s) => s.id === selectedSite)?.name}</h4>
                      <button
                        onClick={() => setSelectedSite(null)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        ×
                      </button>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      {sites.find((s) => s.id === selectedSite)?.city}
                    </p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Matched Patients:</span>
                        <span className="text-[#52C41A]">
                          {sites.find((s) => s.id === selectedSite)?.patients}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Avg Drive Time:</span>
                        <span className="text-[#6B46C1]">
                          {sites.find((s) => s.id === selectedSite)?.distance}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
