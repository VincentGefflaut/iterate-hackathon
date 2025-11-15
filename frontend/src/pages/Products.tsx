import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Package, Search, Filter, AlertTriangle, TrendingDown, Package2 } from "lucide-react";
import { toast } from "sonner";

interface Product {
  id: string;
  product_code: string;
  product_name: string;
  category: string;
  subcategory: string;
  price: number;
  cost: number;
  store_id: string;
  stores?: {
    name: string;
    city: string;
  };
  inventory?: {
    quantity_in_stock: number;
    min_stock_level: number;
    max_stock_level: number;
  }[];
}

const Products = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [selectedStore, setSelectedStore] = useState<string>("all");
  const [priceFilter, setPriceFilter] = useState<string>("all");
  const [stockFilter, setStockFilter] = useState<string>("all");
  const [categories, setCategories] = useState<string[]>([]);
  const [stores, setStores] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [products, searchTerm, selectedCategory, selectedStore, priceFilter, stockFilter]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch products with inventory and store info
      const { data: productsData, error: productsError } = await supabase
        .from("products")
        .select(`
          *,
          stores (name, city),
          inventory (quantity_in_stock, min_stock_level, max_stock_level)
        `)
        .order("product_name", { ascending: true });

      if (productsError) throw productsError;

      // Fetch stores
      const { data: storesData, error: storesError } = await supabase
        .from("stores")
        .select("*")
        .order("name", { ascending: true });

      if (storesError) throw storesError;

      if (productsData) {
        setProducts(productsData);
        
        // Extract unique categories
        const uniqueCategories = [...new Set(productsData.map(p => p.category).filter(Boolean))];
        setCategories(uniqueCategories as string[]);
      }

      if (storesData) {
        setStores(storesData);
      }

    } catch (error: any) {
      console.error("Error fetching products:", error);
      toast.error("Erreur lors du chargement des produits");
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...products];

    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        p =>
          p.product_name.toLowerCase().includes(term) ||
          p.product_code.toLowerCase().includes(term) ||
          p.category?.toLowerCase().includes(term) ||
          p.subcategory?.toLowerCase().includes(term)
      );
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter(p => p.category === selectedCategory);
    }

    // Store filter
    if (selectedStore !== "all") {
      filtered = filtered.filter(p => p.store_id === selectedStore);
    }

    // Price filter
    if (priceFilter !== "all") {
      filtered = filtered.sort((a, b) => {
        if (priceFilter === "low-high") return a.price - b.price;
        if (priceFilter === "high-low") return b.price - a.price;
        return 0;
      });
    }

    // Stock filter
    if (stockFilter === "low") {
      filtered = filtered.filter(p => {
        const inv = p.inventory?.[0];
        return inv && inv.quantity_in_stock <= inv.min_stock_level;
      });
    } else if (stockFilter === "out") {
      filtered = filtered.filter(p => {
        const inv = p.inventory?.[0];
        return inv && inv.quantity_in_stock === 0;
      });
    }

    setFilteredProducts(filtered);
  };

  const getStockStatus = (product: Product) => {
    const inv = product.inventory?.[0];
    if (!inv) return { label: "Non suivi", color: "secondary" };
    
    if (inv.quantity_in_stock === 0) {
      return { label: "Rupture", color: "destructive" };
    } else if (inv.quantity_in_stock <= inv.min_stock_level) {
      return { label: "Stock faible", color: "warning" };
    } else if (inv.max_stock_level && inv.quantity_in_stock >= inv.max_stock_level * 0.8) {
      return { label: "Stock élevé", color: "success" };
    }
    return { label: "Normal", color: "default" };
  };

  const getMarginPercentage = (product: Product) => {
    if (!product.cost || product.cost === 0) return null;
    return ((product.price - product.cost) / product.price * 100).toFixed(1);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      minimumFractionDigits: 2,
    }).format(value);
  };

  // Calculate stats
  const totalProducts = products.length;
  const lowStockCount = products.filter(p => {
    const inv = p.inventory?.[0];
    return inv && inv.quantity_in_stock <= inv.min_stock_level;
  }).length;
  const outOfStockCount = products.filter(p => {
    const inv = p.inventory?.[0];
    return inv && inv.quantity_in_stock === 0;
  }).length;
  const totalValue = products.reduce((sum, p) => {
    const inv = p.inventory?.[0];
    return sum + (inv?.quantity_in_stock || 0) * p.price;
  }, 0);

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-foreground mb-2">
            Produits & Inventaire
          </h1>
          <p className="text-muted-foreground">
            Gestion complète de vos produits et niveaux de stock
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="p-4 bg-card border-border/50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Package className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Produits</p>
                <p className="text-2xl font-bold text-foreground">{totalProducts}</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-4 bg-card border-border/50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-yellow-500/10">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Stock Faible</p>
                <p className="text-2xl font-bold text-foreground">{lowStockCount}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border/50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-destructive/10">
                <TrendingDown className="h-5 w-5 text-destructive" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Rupture</p>
                <p className="text-2xl font-bold text-foreground">{outOfStockCount}</p>
              </div>
            </div>
          </Card>

          <Card className="p-4 bg-card border-border/50">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-success/10">
                <Package2 className="h-5 w-5 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Valeur Stock</p>
                <p className="text-2xl font-bold text-foreground">{formatCurrency(totalValue)}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card className="p-6 bg-card border-border/50">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="h-5 w-5 text-primary" />
            <h3 className="text-lg font-semibold text-foreground">Filtres</h3>
          </div>
          
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 bg-background border-border"
              />
            </div>

            {/* Category Filter */}
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Catégorie" />
              </SelectTrigger>
              <SelectContent className="bg-popover border-border z-50">
                <SelectItem value="all">Toutes catégories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Store Filter */}
            <Select value={selectedStore} onValueChange={setSelectedStore}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Boutique" />
              </SelectTrigger>
              <SelectContent className="bg-popover border-border z-50">
                <SelectItem value="all">Toutes boutiques</SelectItem>
                {stores.map((store) => (
                  <SelectItem key={store.id} value={store.id}>
                    {store.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Price Filter */}
            <Select value={priceFilter} onValueChange={setPriceFilter}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Prix" />
              </SelectTrigger>
              <SelectContent className="bg-popover border-border z-50">
                <SelectItem value="all">Tous les prix</SelectItem>
                <SelectItem value="low-high">Prix croissant</SelectItem>
                <SelectItem value="high-low">Prix décroissant</SelectItem>
              </SelectContent>
            </Select>

            {/* Stock Filter */}
            <Select value={stockFilter} onValueChange={setStockFilter}>
              <SelectTrigger className="bg-background border-border">
                <SelectValue placeholder="Stock" />
              </SelectTrigger>
              <SelectContent className="bg-popover border-border z-50">
                <SelectItem value="all">Tous les stocks</SelectItem>
                <SelectItem value="low">Stock faible</SelectItem>
                <SelectItem value="out">Rupture</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {(searchTerm || selectedCategory !== "all" || selectedStore !== "all" || 
            priceFilter !== "all" || stockFilter !== "all") && (
            <div className="mt-4 flex justify-between items-center">
              <p className="text-sm text-muted-foreground">
                {filteredProducts.length} produit(s) trouvé(s)
              </p>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm("");
                  setSelectedCategory("all");
                  setSelectedStore("all");
                  setPriceFilter("all");
                  setStockFilter("all");
                }}
              >
                Réinitialiser les filtres
              </Button>
            </div>
          )}
        </Card>

        {/* Products Table */}
        <Card className="bg-card border-border/50">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="border-border/50 hover:bg-transparent">
                  <TableHead className="text-foreground font-semibold">Code</TableHead>
                  <TableHead className="text-foreground font-semibold">Produit</TableHead>
                  <TableHead className="text-foreground font-semibold">Catégorie</TableHead>
                  <TableHead className="text-foreground font-semibold">Boutique</TableHead>
                  <TableHead className="text-foreground font-semibold text-right">Prix</TableHead>
                  <TableHead className="text-foreground font-semibold text-right">Coût</TableHead>
                  <TableHead className="text-foreground font-semibold text-right">Marge</TableHead>
                  <TableHead className="text-foreground font-semibold text-center">Stock</TableHead>
                  <TableHead className="text-foreground font-semibold text-center">Statut</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      Chargement des produits...
                    </TableCell>
                  </TableRow>
                ) : filteredProducts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                      Aucun produit trouvé
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredProducts.map((product) => {
                    const stockStatus = getStockStatus(product);
                    const margin = getMarginPercentage(product);
                    const inv = product.inventory?.[0];

                    return (
                      <TableRow key={product.id} className="border-border/50 hover:bg-secondary/50">
                        <TableCell className="font-mono text-sm text-muted-foreground">
                          {product.product_code}
                        </TableCell>
                        <TableCell className="font-medium text-foreground">
                          <div>
                            <p>{product.product_name}</p>
                            {product.subcategory && (
                              <p className="text-xs text-muted-foreground">{product.subcategory}</p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="border-border">
                            {product.category || "Non catégorisé"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {product.stores ? (
                            <div>
                              <p>{product.stores.name}</p>
                              <p className="text-xs">{product.stores.city}</p>
                            </div>
                          ) : (
                            "N/A"
                          )}
                        </TableCell>
                        <TableCell className="text-right font-semibold text-foreground">
                          {formatCurrency(product.price)}
                        </TableCell>
                        <TableCell className="text-right text-muted-foreground">
                          {product.cost ? formatCurrency(product.cost) : "N/A"}
                        </TableCell>
                        <TableCell className="text-right">
                          {margin ? (
                            <span className={`font-medium ${parseFloat(margin) > 30 ? 'text-success' : 'text-foreground'}`}>
                              {margin}%
                            </span>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          {inv ? (
                            <div className="flex flex-col items-center">
                              <span className="font-semibold text-foreground">{inv.quantity_in_stock}</span>
                              <span className="text-xs text-muted-foreground">
                                Min: {inv.min_stock_level}
                              </span>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell className="text-center">
                          <Badge
                            variant={
                              stockStatus.color === "destructive"
                                ? "destructive"
                                : stockStatus.color === "warning"
                                ? "outline"
                                : "secondary"
                            }
                            className={
                              stockStatus.color === "warning"
                                ? "border-yellow-500 text-yellow-500"
                                : stockStatus.color === "success"
                                ? "bg-success/10 text-success border-success/20"
                                : ""
                            }
                          >
                            {stockStatus.label}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Products;