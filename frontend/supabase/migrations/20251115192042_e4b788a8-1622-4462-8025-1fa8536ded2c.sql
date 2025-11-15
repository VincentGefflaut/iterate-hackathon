-- Create table for product alerts
CREATE TABLE public.product_alerts (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  alert_id TEXT NOT NULL UNIQUE,
  event_type TEXT NOT NULL,
  title TEXT NOT NULL,
  severity TEXT NOT NULL,
  urgency TEXT NOT NULL,
  affected_products TEXT[] NOT NULL,
  affected_areas TEXT[] NOT NULL,
  location TEXT NOT NULL,
  event_date DATE NOT NULL,
  description TEXT NOT NULL,
  key_facts TEXT[] NOT NULL,
  potential_relevance TEXT NOT NULL,
  source_url TEXT,
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
  recommended_action TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create table for alert metadata
CREATE TABLE public.alert_metadata (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  upload_date DATE NOT NULL,
  generated_at TIMESTAMP WITH TIME ZONE NOT NULL,
  total_alerts INTEGER NOT NULL,
  severity_threshold TEXT NOT NULL,
  tracked_locations TEXT[] NOT NULL,
  tracked_products TEXT[] NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.product_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alert_metadata ENABLE ROW LEVEL SECURITY;

-- Create policies for product_alerts
CREATE POLICY "Anyone can view product alerts"
ON public.product_alerts
FOR SELECT
USING (true);

CREATE POLICY "Anyone can insert product alerts"
ON public.product_alerts
FOR INSERT
WITH CHECK (true);

CREATE POLICY "Anyone can update product alerts"
ON public.product_alerts
FOR UPDATE
USING (true);

CREATE POLICY "Anyone can delete product alerts"
ON public.product_alerts
FOR DELETE
USING (true);

-- Create policies for alert_metadata
CREATE POLICY "Anyone can view alert metadata"
ON public.alert_metadata
FOR SELECT
USING (true);

CREATE POLICY "Anyone can insert alert metadata"
ON public.alert_metadata
FOR INSERT
WITH CHECK (true);

-- Create trigger for updated_at
CREATE TRIGGER update_product_alerts_updated_at
BEFORE UPDATE ON public.product_alerts
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Create index for better query performance
CREATE INDEX idx_product_alerts_severity ON public.product_alerts(severity);
CREATE INDEX idx_product_alerts_event_date ON public.product_alerts(event_date);
CREATE INDEX idx_product_alerts_location ON public.product_alerts(location);