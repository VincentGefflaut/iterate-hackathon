import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from '@/integrations/supabase/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, AlertTriangle, TrendingUp, Calendar, MapPin, Package, ExternalLink, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

interface ProductAlert {
  alert_id: string;
  event_type: string;
  title: string;
  severity: string;
  urgency: string;
  affected_products: string[];
  affected_areas: string[];
  location: string;
  event_date: string;
  description: string;
  key_facts: string[];
  potential_relevance: string;
  source_url?: string;
  detected_at: string;
  recommended_action: string;
}

interface AlertJSON {
  date: string;
  generated_at: string;
  total_alerts: number;
  severity_threshold: string;
  tracked_locations: string[];
  tracked_products: string[];
  alerts: ProductAlert[];
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const Alerts = () => {
  const [uploading, setUploading] = useState(false);
  const [fetchingFromAPI, setFetchingFromAPI] = useState(false);
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['product-alerts'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('product_alerts')
        .select('*')
        .order('detected_at', { ascending: false });

      if (error) throw error;
      return data;
    },
  });

  // Fetch latest alerts from API on component mount
  useEffect(() => {
    fetchLatestFromAPI();
  }, []);

  const fetchLatestFromAPI = async () => {
    setFetchingFromAPI(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/alerts/latest`);

      if (response.ok) {
        const jsonData: AlertJSON = await response.json();
        await uploadMutation.mutateAsync(jsonData);
        toast.success('Alertes chargées depuis le backend');
      } else if (response.status === 404) {
        console.log('No alerts available from backend yet');
      } else {
        throw new Error('Failed to fetch from API');
      }
    } catch (error) {
      console.error('Error fetching from API:', error);
      // Don't show error toast on initial load if API isn't available
    } finally {
      setFetchingFromAPI(false);
    }
  };

  const uploadMutation = useMutation({
    mutationFn: async (jsonData: AlertJSON) => {
      // Insert metadata
      const { error: metaError } = await supabase
        .from('alert_metadata')
        .insert({
          upload_date: jsonData.date,
          generated_at: jsonData.generated_at,
          total_alerts: jsonData.total_alerts,
          severity_threshold: jsonData.severity_threshold,
          tracked_locations: jsonData.tracked_locations,
          tracked_products: jsonData.tracked_products,
        });

      if (metaError) throw metaError;

      // Insert alerts
      const alertsToInsert = jsonData.alerts.map(alert => ({
        alert_id: alert.alert_id,
        event_type: alert.event_type,
        title: alert.title,
        severity: alert.severity,
        urgency: alert.urgency,
        affected_products: alert.affected_products,
        affected_areas: alert.affected_areas,
        location: alert.location,
        event_date: alert.event_date,
        description: alert.description,
        key_facts: alert.key_facts,
        potential_relevance: alert.potential_relevance,
        source_url: alert.source_url,
        detected_at: alert.detected_at,
        recommended_action: alert.recommended_action,
      }));

      const { error: alertsError } = await supabase
        .from('product_alerts')
        .upsert(alertsToInsert, { onConflict: 'alert_id' });

      if (alertsError) throw alertsError;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-alerts'] });
      toast.success('Alertes importées avec succès');
    },
    onError: (error) => {
      toast.error('Erreur lors de l\'importation: ' + error.message);
    },
  });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const text = await file.text();
      const jsonData: AlertJSON = JSON.parse(text);
      await uploadMutation.mutateAsync(jsonData);
    } catch (error) {
      toast.error('Erreur de lecture du fichier JSON');
    } finally {
      setUploading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
      case 'critical':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'immediate':
        return 'destructive';
      case 'high':
        return 'default';
      default:
        return 'secondary';
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Alertes Produits</h1>
          <p className="text-muted-foreground mt-2">
            Surveillance intelligente du marché et des événements
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={fetchLatestFromAPI}
            disabled={fetchingFromAPI}
            variant="outline"
          >
            <RefreshCw className={`mr-2 h-4 w-4 ${fetchingFromAPI ? 'animate-spin' : ''}`} />
            {fetchingFromAPI ? 'Chargement...' : 'Actualiser'}
          </Button>
          <input
            type="file"
            accept=".json"
            onChange={handleFileUpload}
            className="hidden"
            id="json-upload"
          />
          <label htmlFor="json-upload">
            <Button disabled={uploading} asChild>
              <span className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                {uploading ? 'Importation...' : 'Importer JSON'}
              </span>
            </Button>
          </label>
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Chargement des alertes...</p>
        </div>
      ) : alerts && alerts.length > 0 ? (
        <div className="grid gap-6">
          {alerts.map((alert: any) => (
            <Card key={alert.id} className="overflow-hidden">
              <CardHeader className="bg-gradient-to-r from-background to-accent/10">
                <div className="flex justify-between items-start">
                  <div className="space-y-2 flex-1">
                    <div className="flex gap-2 flex-wrap">
                      <Badge variant={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                      <Badge variant={getUrgencyColor(alert.urgency)}>
                        {alert.urgency}
                      </Badge>
                      <Badge variant="outline">{alert.event_type}</Badge>
                    </div>
                    <CardTitle className="text-xl">{alert.title}</CardTitle>
                  </div>
                  {alert.source_url && (
                    <Button variant="ghost" size="sm" asChild>
                      <a href={alert.source_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent className="pt-6 space-y-4">
                <CardDescription className="text-base">
                  {alert.description}
                </CardDescription>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Location:</span>
                      <span>{alert.location}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">Date événement:</span>
                      <span>{new Date(alert.event_date).toLocaleDateString('fr-FR')}</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-start gap-2 text-sm">
                      <Package className="h-4 w-4 text-muted-foreground mt-0.5" />
                      <div>
                        <span className="font-medium">Produits affectés:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {alert.affected_products.map((product: string, idx: number) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {product}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {alert.key_facts && alert.key_facts.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="font-semibold text-sm flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Faits clés
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                      {alert.key_facts.map((fact: string, idx: number) => (
                        <li key={idx}>{fact}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <Alert>
                  <TrendingUp className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Pertinence:</strong> {alert.potential_relevance}
                  </AlertDescription>
                </Alert>

                <Alert className="bg-primary/5 border-primary/20">
                  <AlertDescription className="font-medium">
                    {alert.recommended_action}
                  </AlertDescription>
                </Alert>

                <div className="text-xs text-muted-foreground pt-2 border-t">
                  Détecté le {new Date(alert.detected_at).toLocaleString('fr-FR')}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Aucune alerte</h3>
            <p className="text-muted-foreground">
              Importez un fichier JSON pour commencer à suivre les alertes produits
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Alerts;
