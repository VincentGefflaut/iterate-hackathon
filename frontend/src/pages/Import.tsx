import { useState, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const Import = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [csvData, setCsvData] = useState<any>(null);
  const [selectedStore, setSelectedStore] = useState<string>("");
  const [stores, setStores] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { toast } = useToast();
  const navigate = useNavigate();

  // Fetch stores on mount
  useEffect(() => {
    const fetchStores = async () => {
      const { data } = await supabase.from("stores").select("*");
      if (data) setStores(data);
    };
    fetchStores();
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "text/csv") {
      setFile(droppedFile);
      processFile(droppedFile);
    } else {
      toast({
        title: "Format invalide",
        description: "Veuillez déposer un fichier CSV",
        variant: "destructive",
      });
    }
  }, []);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      processFile(selectedFile);
    }
  }, []);

  const processFile = async (file: File) => {
    if (!selectedStore) {
      toast({
        title: "Boutique non sélectionnée",
        description: "Veuillez sélectionner une boutique avant d'importer",
        variant: "destructive",
      });
      return;
    }

    setIsAnalyzing(true);
    setUploadProgress(20);

    const reader = new FileReader();
    reader.onload = async (e) => {
      const csvText = e.target?.result as string;
      setUploadProgress(40);

      try {
        const { data, error } = await supabase.functions.invoke("analyze-csv", {
          body: { csvText, storeId: selectedStore },
        });

        setUploadProgress(80);

        if (error) throw error;

        setCsvData(data);
        setUploadProgress(100);
        
        toast({
          title: "Analyse terminée",
          description: `Secteur détecté: ${getSectorLabel(data.sector.sector)} (${data.sector.confidence}% de confiance)`,
        });
      } catch (error: any) {
        console.error("Error analyzing CSV:", error);
        toast({
          title: "Erreur d'analyse",
          description: error.message || "Impossible d'analyser le fichier",
          variant: "destructive",
        });
      } finally {
        setIsAnalyzing(false);
      }
    };

    reader.readAsText(file);
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

  const getSectorIcon = (confidence: number) => {
    if (confidence >= 70) return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (confidence >= 40) return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    return <AlertCircle className="h-5 w-5 text-red-500" />;
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Importation de Données
          </h1>
          <p className="text-muted-foreground">
            Importez vos données de commandes, produits et inventaire depuis un fichier CSV
          </p>
        </div>

        {/* Store Selection */}
        <Card className="p-6 bg-card border-border/50">
          <label className="text-sm font-medium text-foreground mb-2 block">
            Sélectionner une boutique
          </label>
          <Select value={selectedStore} onValueChange={setSelectedStore}>
            <SelectTrigger className="w-full bg-background border-border">
              <SelectValue placeholder="Choisir une boutique..." />
            </SelectTrigger>
            <SelectContent>
              {stores.map((store) => (
                <SelectItem key={store.id} value={store.id}>
                  {store.name} - {store.city}, {store.country}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Card>

        {/* Drop Zone */}
        <Card
          className={`relative p-12 border-2 border-dashed transition-all ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-border/50 bg-card hover:border-primary/50"
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="p-4 rounded-full bg-primary/10">
              <Upload className="h-12 w-12 text-primary" />
            </div>
            <div className="text-center">
              <p className="text-lg font-medium text-foreground mb-1">
                Glissez-déposez votre fichier CSV ici
              </p>
              <p className="text-sm text-muted-foreground">
                ou cliquez pour sélectionner un fichier
              </p>
            </div>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileInput}
              className="hidden"
              id="file-input"
              disabled={!selectedStore}
            />
            <Button
              onClick={() => document.getElementById("file-input")?.click()}
              variant="outline"
              disabled={!selectedStore}
            >
              <FileText className="mr-2 h-4 w-4" />
              Parcourir les fichiers
            </Button>
          </div>
        </Card>

        {isAnalyzing && (
          <Card className="p-6 bg-card border-border/50">
            <div className="space-y-2">
              <p className="text-sm font-medium text-foreground">
                Analyse en cours...
              </p>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          </Card>
        )}

        {csvData && (
          <>
            {/* Sector Detection Result */}
            <Card className="p-6 bg-card border-border/50">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-foreground mb-1">
                    Secteur d'Activité Détecté
                  </h3>
                  <p className="text-2xl font-bold text-primary mb-2">
                    {getSectorLabel(csvData.sector.sector)}
                  </p>
                  <p className="text-sm text-muted-foreground mb-3">
                    Mots-clés détectés: {csvData.sector.keywords.join(", ")}
                  </p>
                  <div className="flex items-center gap-2">
                    {getSectorIcon(csvData.sector.confidence)}
                    <span className="text-sm font-medium">
                      Confiance: {csvData.sector.confidence}%
                    </span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Data Preview */}
            <Card className="p-6 bg-card border-border/50">
              <h3 className="text-lg font-semibold text-foreground mb-4">
                Aperçu des Données ({csvData.totalRows} lignes)
              </h3>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-border/50">
                      {csvData.headers.map((header: string, i: number) => (
                        <TableHead key={i} className="text-foreground font-semibold">
                          {header}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {csvData.preview.map((row: any, i: number) => (
                      <TableRow key={i} className="border-border/50">
                        {csvData.headers.map((header: string, j: number) => (
                          <TableCell key={j} className="text-muted-foreground">
                            {row[header]}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </Card>

            <div className="flex gap-4">
              <Button
                onClick={() => navigate("/dashboard")}
                className="flex-1"
              >
                Voir le Tableau de Bord
              </Button>
              <Button
                onClick={() => {
                  setFile(null);
                  setCsvData(null);
                  setUploadProgress(0);
                }}
                variant="outline"
              >
                Nouveau fichier
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Import;