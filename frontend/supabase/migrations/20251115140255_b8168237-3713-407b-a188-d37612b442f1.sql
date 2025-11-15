-- Create business_sectors table to track detected sectors per store
CREATE TABLE public.business_sectors (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  store_id uuid REFERENCES public.stores(id) ON DELETE CASCADE,
  sector_type text NOT NULL CHECK (sector_type IN ('retail_fashion', 'retail_food', 'retail_electronics', 'retail_home', 'retail_beauty', 'retail_sports', 'other')),
  confidence_score numeric CHECK (confidence_score >= 0 AND confidence_score <= 100),
  detected_keywords text[],
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(store_id)
);

-- Create products table
CREATE TABLE public.products (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  store_id uuid REFERENCES public.stores(id) ON DELETE CASCADE,
  product_code text NOT NULL,
  product_name text NOT NULL,
  category text,
  subcategory text,
  price numeric NOT NULL,
  cost numeric,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(store_id, product_code)
);

-- Create orders table
CREATE TABLE public.orders (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  store_id uuid REFERENCES public.stores(id) ON DELETE CASCADE,
  order_number text NOT NULL,
  order_date timestamp with time zone NOT NULL,
  product_id uuid REFERENCES public.products(id) ON DELETE SET NULL,
  quantity integer NOT NULL DEFAULT 1,
  unit_price numeric NOT NULL,
  total_amount numeric NOT NULL,
  customer_id text,
  created_at timestamp with time zone DEFAULT now(),
  UNIQUE(store_id, order_number, product_id)
);

-- Create inventory table
CREATE TABLE public.inventory (
  id uuid NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  store_id uuid REFERENCES public.stores(id) ON DELETE CASCADE,
  product_id uuid REFERENCES public.products(id) ON DELETE CASCADE,
  quantity_in_stock integer NOT NULL DEFAULT 0,
  min_stock_level integer DEFAULT 0,
  max_stock_level integer,
  last_restock_date timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(store_id, product_id)
);

-- Add triggers for updated_at
CREATE TRIGGER update_business_sectors_updated_at
  BEFORE UPDATE ON public.business_sectors
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_products_updated_at
  BEFORE UPDATE ON public.products
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_inventory_updated_at
  BEFORE UPDATE ON public.inventory
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Enable RLS
ALTER TABLE public.business_sectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inventory ENABLE ROW LEVEL SECURITY;

-- RLS Policies for business_sectors
CREATE POLICY "Authenticated users can view business sectors"
  ON public.business_sectors FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert business sectors"
  ON public.business_sectors FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update business sectors"
  ON public.business_sectors FOR UPDATE
  TO authenticated
  USING (true);

-- RLS Policies for products
CREATE POLICY "Authenticated users can view products"
  ON public.products FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert products"
  ON public.products FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update products"
  ON public.products FOR UPDATE
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can delete products"
  ON public.products FOR DELETE
  TO authenticated
  USING (true);

-- RLS Policies for orders
CREATE POLICY "Authenticated users can view orders"
  ON public.orders FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert orders"
  ON public.orders FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update orders"
  ON public.orders FOR UPDATE
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can delete orders"
  ON public.orders FOR DELETE
  TO authenticated
  USING (true);

-- RLS Policies for inventory
CREATE POLICY "Authenticated users can view inventory"
  ON public.inventory FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert inventory"
  ON public.inventory FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update inventory"
  ON public.inventory FOR UPDATE
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can delete inventory"
  ON public.inventory FOR DELETE
  TO authenticated
  USING (true);

-- Update market_intelligence table to add sector_specific field
ALTER TABLE public.market_intelligence 
ADD COLUMN IF NOT EXISTS sector_specific text[] DEFAULT '{}';

-- Add some sector-specific market intelligence data
INSERT INTO public.market_intelligence (event_name, event_type, region, country, impact_prediction, impact_percentage, description, start_date, end_date, sector_specific) VALUES
('Météo Pluvieuse', 'weather', 'Europe', 'France', 'Hausse des ventes imperméables', 15, 'Période de fortes pluies prévue', CURRENT_DATE, CURRENT_DATE + INTERVAL '7 days', ARRAY['retail_fashion']::text[]),
('Black Friday', 'commercial', 'Europe', 'France', 'Forte augmentation trafic', 40, 'Black Friday annuel', '2024-11-29', '2024-11-29', ARRAY['retail_fashion', 'retail_electronics', 'retail_home']::text[]),
('Canicule Été', 'weather', 'Europe', 'France', 'Hausse ventes boissons fraîches', 25, 'Températures élevées prévues', '2024-07-01', '2024-08-31', ARRAY['retail_food']::text[]),
('Rentrée Scolaire', 'seasonal', 'Europe', 'France', 'Pic fournitures scolaires', 30, 'Période de rentrée des classes', '2024-08-20', '2024-09-10', ARRAY['retail_electronics', 'retail_fashion']::text[])
ON CONFLICT DO NOTHING;