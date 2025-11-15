import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { TrendingUp, DollarSign, Activity, AlertCircle } from "lucide-react";
import { toast } from "sonner";

interface MarketIntelligence {
  id: string;
  event_name: string;
  event_type: string;
  description: string;
  impact_prediction: string;
  impact_percentage: number;
  start_date: string;
  end_date: string;
  sector_specific: string[];
}

const Dashboard = () => {
  const [selectedRegion, setSelectedRegion] = useState<string>("Europe");
  const [selectedCountry, setSelectedCountry] = useState<string>("all");
  const [marketEvents, setMarketEvents] = useState<MarketIntelligence[]>([]);
  const [salesData, setSalesData] = useState<any[]>([]);
  const [kpis, setKpis] = useState({ revenue: 0, margin: 0, transactions: 0 });
  const [detectedSector, setDetectedSector] = useState<any>(null);

  const regions = ["Europe", "North America", "Asia"];
  const countryByRegion: Record<string, string[]> = {
    "Europe": ["France", "Germany"],
    "North America": ["USA"],
    "Asia": ["Japan"]
  };

  useEffect(() => {
    fetchDetectedSector();
    fetchMarketIntelligence();
    fetchSalesData();
  }, [selectedRegion, selectedCountry]);

  const fetchDetectedSector = async () => {
    try {
      const { data, error } = await supabase
        .from("business_sectors")
        .select("*, stores(*)")
        .order("created_at", { ascending: false })
        .limit(1)
        .maybeSingle();

      if (error) throw error;
      setDetectedSector(data);
    } catch (error) {
      console.error("Error fetching sector:", error);
    }
  };

  const fetchMarketIntelligence = async () => {
    try {
      let query = supabase
        .from("market_intelligence")
        .select("*")
        .eq("region", selectedRegion)
        .eq("is_active", true);

      if (selectedCountry !== "all") {
        query = query.eq("country", selectedCountry);
      }

      // Filter by sector if detected
      if (detectedSector?.sector_type) {
        query = query.contains("sector_specific", [detectedSector.sector_type]);
      }

      const { data, error } = await query.order("impact_percentage", { ascending: false });

      if (error) throw error;
      setMarketEvents(data || []);
    } catch (error) {
      console.error("Error fetching market intelligence:", error);
      toast.error("Erreur lors du chargement des données de marché");
    }
  };

  const fetchSalesData = async () => {
    try {
      let query = supabase
        .from("sales_data")
        .select("*")
        .eq("region", selectedRegion);

      if (selectedCountry !== "all") {
        query = query.eq("country", selectedCountry);
      }

      const { data, error } = await query.order("date", { ascending: true }).limit(30);

      if (error) throw error;

      if (data) {
        // Aggregate data by date
        const aggregated = data.reduce((acc: any, curr: any) => {
          const date = new Date(curr.date).toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
          if (!acc[date]) {
            acc[date] = { date, revenue: 0, margin: 0, transactions: 0 };
          }
          acc[date].revenue += parseFloat(String(curr.revenue));
          acc[date].margin += parseFloat(String(curr.margin));
          acc[date].transactions += curr.transactions;
          return acc;
        }, {});

        const chartData = Object.values(aggregated).slice(-10);
        setSalesData(chartData);

        // Calculate KPIs
        const totalRevenue = data.reduce((sum, item) => sum + parseFloat(String(item.revenue)), 0);
        const totalMargin = data.reduce((sum, item) => sum + parseFloat(String(item.margin)), 0);
        const totalTransactions = data.reduce((sum, item) => sum + item.transactions, 0);

        setKpis({
          revenue: totalRevenue,
          margin: totalMargin,
          transactions: totalTransactions,
        });
      }
    } catch (error) {
      console.error("Error fetching sales data:", error);
      toast.error("Erreur lors du chargement des données de vente");
    }
  };

  const getSectorLabel = (sector: string) => {
    const labels: { [key: string]: string } = {
      retail_fashion: "Retail Habillement",
      retail_food: "Retail Alimentaire",
      retail_electronics: "Retail Électronique",
      retail_home: "Retail Maison",
      retail_beauty: "Retail Beauté",
      retail_sports: "Retail Sport",
      other: "Autre",
    };
    return labels[sector] || sector;
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getEventIcon = (type: string) => {
    switch (type) {
      case "sales":
        return "🎯";
      case "fashion":
        return "👗";
      case "holiday":
        return "🎉";
      case "festival":
        return "🎪";
      default:
        return "📊";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Tableau de Bord
          </h1>
          <p className="text-muted-foreground mt-1">Vue d'ensemble des performances et intelligence de marché</p>
          {detectedSector && (
            <div className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary/10 border border-primary/20">
              <span className="text-sm font-semibold text-primary">
                Secteur: {getSectorLabel(detectedSector.sector_type)}
              </span>
              <span className="text-xs text-muted-foreground">
                ({detectedSector.confidence_score}% confiance)
              </span>
            </div>
          )}
        </div>
        <div className="flex gap-3">
          <Select value={selectedRegion} onValueChange={setSelectedRegion}>
            <SelectTrigger className="w-[180px] bg-secondary/50 border-border">
              <SelectValue placeholder="Région" />
            </SelectTrigger>
            <SelectContent>
              {regions.map((region) => (
                <SelectItem key={region} value={region}>
                  {region}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedCountry} onValueChange={setSelectedCountry}>
            <SelectTrigger className="w-[180px] bg-secondary/50 border-border">
              <SelectValue placeholder="Pays" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les pays</SelectItem>
              {countryByRegion[selectedRegion]?.map((country) => (
                <SelectItem key={country} value={country}>
                  {country}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="gradient-card border-border/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Chiffre d'Affaires</CardTitle>
            <DollarSign className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{formatCurrency(kpis.revenue)}</div>
            <p className="text-xs text-success flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3" />
              +12.5% vs période précédente
            </p>
          </CardContent>
        </Card>
        <Card className="gradient-card border-border/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Marge</CardTitle>
            <TrendingUp className="h-4 w-4 text-success" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{formatCurrency(kpis.margin)}</div>
            <p className="text-xs text-success flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3" />
              +8.3% vs période précédente
            </p>
          </CardContent>
        </Card>
        <Card className="gradient-card border-border/50">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Transactions</CardTitle>
            <Activity className="h-4 w-4 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{kpis.transactions.toLocaleString()}</div>
            <p className="text-xs text-success flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3" />
              +15.7% vs période précédente
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Market Intelligence Section - Alertes d'Impact Local */}
      <Card className="gradient-card border-border/50 shadow-glow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-primary" />
            Alertes d'Impact Local - {selectedCountry !== "all" ? selectedCountry : selectedRegion}
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            {detectedSector 
              ? `Événements pertinents pour le secteur ${getSectorLabel(detectedSector.sector_type)}` 
              : "Événements et tendances actuels impactant vos ventes"}
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {marketEvents.length > 0 ? (
              marketEvents.map((event) => (
                <div
                  key={event.id}
                  className="p-4 rounded-lg bg-secondary/50 border border-border/50 hover:border-primary/50 transition-smooth"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{getEventIcon(event.event_type)}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-foreground">
                          {event.event_name}
                        </h3>
                        <span className="text-xs px-2 py-1 rounded-full bg-primary/10 text-primary">
                          {event.event_type}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
                      <div className="mt-3 p-3 rounded-md bg-primary/5 border border-primary/20">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-primary" />
                            <span className="text-sm font-medium text-foreground">Impact prédit:</span>
                            <span className="text-sm text-foreground">{event.impact_prediction}</span>
                          </div>
                          <span className="text-lg font-bold text-success">+{event.impact_percentage}%</span>
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-muted-foreground">
                        Période: {new Date(event.start_date).toLocaleDateString("fr-FR")}
                        {event.end_date && ` - ${new Date(event.end_date).toLocaleDateString("fr-FR")}`}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                {detectedSector 
                  ? `Aucun événement d'impact détecté pour le secteur ${getSectorLabel(detectedSector.sector_type)} dans cette région`
                  : "Aucun événement de marché actuellement pour cette région. Importez vos données pour activer la détection d'impact sectoriel."}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="gradient-card border-border/50">
          <CardHeader>
            <CardTitle>Évolution du CA</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={{ fill: "hsl(var(--primary))" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card className="gradient-card border-border/50">
          <CardHeader>
            <CardTitle>Transactions par jour</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={salesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="transactions" fill="hsl(var(--accent))" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
