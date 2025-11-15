-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  full_name TEXT,
  role TEXT DEFAULT 'user',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

-- Create stores table
CREATE TABLE public.stores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  country TEXT NOT NULL,
  region TEXT NOT NULL,
  city TEXT NOT NULL,
  address TEXT,
  manager_name TEXT,
  phone TEXT,
  status TEXT DEFAULT 'active',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

ALTER TABLE public.stores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view stores"
  ON public.stores FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can insert stores"
  ON public.stores FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Authenticated users can update stores"
  ON public.stores FOR UPDATE
  TO authenticated
  USING (true);

CREATE POLICY "Authenticated users can delete stores"
  ON public.stores FOR DELETE
  TO authenticated
  USING (true);

-- Create market_intelligence table
CREATE TABLE public.market_intelligence (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  region TEXT NOT NULL,
  country TEXT NOT NULL,
  event_name TEXT NOT NULL,
  event_type TEXT NOT NULL,
  description TEXT,
  impact_prediction TEXT NOT NULL,
  impact_percentage INTEGER,
  start_date DATE,
  end_date DATE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

ALTER TABLE public.market_intelligence ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view market intelligence"
  ON public.market_intelligence FOR SELECT
  TO authenticated
  USING (true);

-- Create sales_data table for KPIs
CREATE TABLE public.sales_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  store_id UUID REFERENCES public.stores(id) ON DELETE CASCADE,
  region TEXT NOT NULL,
  country TEXT NOT NULL,
  date DATE NOT NULL,
  revenue DECIMAL(12, 2) NOT NULL,
  margin DECIMAL(12, 2) NOT NULL,
  transactions INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

ALTER TABLE public.sales_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can view sales data"
  ON public.sales_data FOR SELECT
  TO authenticated
  USING (true);

-- Function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = public;

-- Trigger for new user creation
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_profiles_updated_at
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_stores_updated_at
  BEFORE UPDATE ON public.stores
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_market_intelligence_updated_at
  BEFORE UPDATE ON public.market_intelligence
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Insert sample data for market intelligence
INSERT INTO public.market_intelligence (region, country, event_name, event_type, description, impact_prediction, impact_percentage, start_date, end_date) VALUES
('Europe', 'France', 'Soldes d''Été', 'sales', 'Soldes annuels d''été avec réductions importantes', '+35% augmentation de fréquentation', 35, '2025-06-25', '2025-07-29'),
('Europe', 'France', 'Fashion Week Paris', 'fashion', 'Défilés de mode attirant une clientèle haut de gamme', '+22% augmentation CA premium', 22, '2025-09-23', '2025-10-01'),
('North America', 'USA', 'Black Friday', 'sales', 'Plus grand événement shopping de l''année', '+60% augmentation transactions', 60, '2025-11-28', '2025-11-28'),
('Asia', 'Japan', 'Golden Week', 'holiday', 'Série de jours fériés augmentant le shopping', '+28% augmentation fréquentation', 28, '2025-04-29', '2025-05-05'),
('Europe', 'Germany', 'Oktoberfest', 'festival', 'Festival attirant touristes et locaux', '+18% augmentation CA', 18, '2025-09-20', '2025-10-05');

-- Insert sample stores
INSERT INTO public.stores (name, country, region, city, address, manager_name, phone, status) VALUES
('Paris Champs-Élysées', 'France', 'Europe', 'Paris', '78 Avenue des Champs-Élysées', 'Marie Dubois', '+33 1 23 45 67 89', 'active'),
('Lyon Part-Dieu', 'France', 'Europe', 'Lyon', '17 Rue du Docteur Bouchut', 'Pierre Martin', '+33 4 78 62 50 50', 'active'),
('New York Fifth Avenue', 'USA', 'North America', 'New York', '725 Fifth Avenue', 'John Smith', '+1 212 555 0123', 'active'),
('Tokyo Shibuya', 'Japan', 'Asia', 'Tokyo', '21-1 Udagawacho, Shibuya', 'Yuki Tanaka', '+81 3-1234-5678', 'active'),
('Berlin Kurfürstendamm', 'Germany', 'Europe', 'Berlin', 'Kurfürstendamm 231', 'Hans Mueller', '+49 30 12345678', 'active');

-- Insert sample sales data
INSERT INTO public.sales_data (store_id, region, country, date, revenue, margin, transactions)
SELECT 
  s.id,
  s.region,
  s.country,
  CURRENT_DATE - (random() * 30)::integer,
  (random() * 50000 + 10000)::decimal(12,2),
  (random() * 15000 + 3000)::decimal(12,2),
  (random() * 200 + 50)::integer
FROM public.stores s, generate_series(1, 10) g;