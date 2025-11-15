import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Pencil, Trash2, Store as StoreIcon } from "lucide-react";
import { toast } from "sonner";

interface Store {
  id: string;
  name: string;
  country: string;
  region: string;
  city: string;
  address: string | null;
  manager_name: string | null;
  phone: string | null;
  status: string;
}

const Stores = () => {
  const [stores, setStores] = useState<Store[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingStore, setEditingStore] = useState<Store | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    country: "",
    region: "",
    city: "",
    address: "",
    manager_name: "",
    phone: "",
    status: "active",
  });

  const regions = ["Europe", "North America", "Asia"];
  const countryByRegion: Record<string, string[]> = {
    "Europe": ["France", "Germany", "Spain", "Italy", "UK"],
    "North America": ["USA", "Canada", "Mexico"],
    "Asia": ["Japan", "China", "South Korea", "Singapore"]
  };

  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async () => {
    try {
      const { data, error } = await supabase
        .from("stores")
        .select("*")
        .order("created_at", { ascending: false });

      if (error) throw error;
      setStores(data || []);
    } catch (error) {
      console.error("Error fetching stores:", error);
      toast.error("Erreur lors du chargement des magasins");
    }
  };

  const handleOpenDialog = (store?: Store) => {
    if (store) {
      setEditingStore(store);
      setFormData({
        name: store.name,
        country: store.country,
        region: store.region,
        city: store.city,
        address: store.address || "",
        manager_name: store.manager_name || "",
        phone: store.phone || "",
        status: store.status,
      });
    } else {
      setEditingStore(null);
      setFormData({
        name: "",
        country: "",
        region: "",
        city: "",
        address: "",
        manager_name: "",
        phone: "",
        status: "active",
      });
    }
    setIsDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingStore) {
        const { error } = await supabase
          .from("stores")
          .update(formData)
          .eq("id", editingStore.id);

        if (error) throw error;
        toast.success("Magasin mis à jour avec succès");
      } else {
        const { error } = await supabase.from("stores").insert([formData]);

        if (error) throw error;
        toast.success("Magasin créé avec succès");
      }

      setIsDialogOpen(false);
      fetchStores();
    } catch (error: any) {
      console.error("Error saving store:", error);
      toast.error(error.message || "Erreur lors de l'enregistrement");
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Êtes-vous sûr de vouloir supprimer ce magasin ?")) return;

    try {
      const { error } = await supabase.from("stores").delete().eq("id", id);

      if (error) throw error;
      toast.success("Magasin supprimé avec succès");
      fetchStores();
    } catch (error: any) {
      console.error("Error deleting store:", error);
      toast.error(error.message || "Erreur lors de la suppression");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
            Gestion des Magasins
          </h1>
          <p className="text-muted-foreground mt-1">Gérez votre réseau de boutiques physiques</p>
        </div>
        <Button onClick={() => handleOpenDialog()} className="gradient-primary hover:opacity-90 transition-smooth">
          <Plus className="mr-2 h-4 w-4" />
          Ajouter un magasin
        </Button>
      </div>

      <Card className="gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <StoreIcon className="h-5 w-5 text-primary" />
            Liste des magasins ({stores.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border border-border">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-secondary/50">
                  <TableHead>Nom</TableHead>
                  <TableHead>Région</TableHead>
                  <TableHead>Pays</TableHead>
                  <TableHead>Ville</TableHead>
                  <TableHead>Responsable</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {stores.length > 0 ? (
                  stores.map((store) => (
                    <TableRow key={store.id} className="hover:bg-secondary/50">
                      <TableCell className="font-medium">{store.name}</TableCell>
                      <TableCell>{store.region}</TableCell>
                      <TableCell>{store.country}</TableCell>
                      <TableCell>{store.city}</TableCell>
                      <TableCell>{store.manager_name || "-"}</TableCell>
                      <TableCell>
                        <Badge
                          variant={store.status === "active" ? "default" : "secondary"}
                          className={store.status === "active" ? "bg-success" : ""}
                        >
                          {store.status === "active" ? "Actif" : "Inactif"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleOpenDialog(store)}
                            className="hover:bg-primary/10 hover:text-primary transition-smooth"
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(store.id)}
                            className="hover:bg-destructive/10 hover:text-destructive transition-smooth"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      Aucun magasin enregistré
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="bg-card border-border max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editingStore ? "Modifier le magasin" : "Ajouter un nouveau magasin"}
            </DialogTitle>
            <DialogDescription>
              Remplissez les informations du magasin ci-dessous
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Nom du magasin *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="bg-secondary/50 border-border"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="region">Région *</Label>
                  <Select
                    value={formData.region}
                    onValueChange={(value) => setFormData({ ...formData, region: value, country: "" })}
                  >
                    <SelectTrigger className="bg-secondary/50 border-border">
                      <SelectValue placeholder="Sélectionnez" />
                    </SelectTrigger>
                    <SelectContent>
                      {regions.map((region) => (
                        <SelectItem key={region} value={region}>
                          {region}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="country">Pays *</Label>
                  <Select
                    value={formData.country}
                    onValueChange={(value) => setFormData({ ...formData, country: value })}
                    disabled={!formData.region}
                  >
                    <SelectTrigger className="bg-secondary/50 border-border">
                      <SelectValue placeholder="Sélectionnez" />
                    </SelectTrigger>
                    <SelectContent>
                      {formData.region &&
                        countryByRegion[formData.region]?.map((country) => (
                          <SelectItem key={country} value={country}>
                            {country}
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="city">Ville *</Label>
                <Input
                  id="city"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  required
                  className="bg-secondary/50 border-border"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="address">Adresse</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="bg-secondary/50 border-border"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="manager">Responsable</Label>
                  <Input
                    id="manager"
                    value={formData.manager_name}
                    onChange={(e) => setFormData({ ...formData, manager_name: e.target.value })}
                    className="bg-secondary/50 border-border"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="phone">Téléphone</Label>
                  <Input
                    id="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="bg-secondary/50 border-border"
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="status">Statut</Label>
                <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
                  <SelectTrigger className="bg-secondary/50 border-border">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Actif</SelectItem>
                    <SelectItem value="inactive">Inactif</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="ghost" onClick={() => setIsDialogOpen(false)}>
                Annuler
              </Button>
              <Button type="submit" className="gradient-primary hover:opacity-90 transition-smooth">
                {editingStore ? "Mettre à jour" : "Créer"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Stores;
