import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.81.1';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface CSVRow {
  [key: string]: string;
}

interface SectorDetectionResult {
  sector: string;
  confidence: number;
  keywords: string[];
}

const sectorKeywords = {
  retail_fashion: ['vêtement', 'textile', 'chaussure', 'mode', 'accessoire', 'robe', 'pantalon', 'chemise', 't-shirt', 'jean', 'fashion', 'clothing', 'apparel'],
  retail_food: ['alimentaire', 'nourriture', 'boisson', 'épicerie', 'fruit', 'légume', 'viande', 'pain', 'fromage', 'food', 'grocery', 'beverage'],
  retail_electronics: ['électronique', 'ordinateur', 'téléphone', 'tablette', 'tv', 'console', 'casque', 'électroménager', 'electronics', 'computer', 'phone'],
  retail_home: ['maison', 'décoration', 'meuble', 'literie', 'cuisine', 'salle de bain', 'home', 'furniture', 'decor'],
  retail_beauty: ['beauté', 'cosmétique', 'parfum', 'maquillage', 'soin', 'beauty', 'cosmetic', 'makeup', 'skincare'],
  retail_sports: ['sport', 'fitness', 'équipement sportif', 'vélo', 'running', 'sports', 'athletic', 'gym']
};

function detectSector(csvData: CSVRow[]): SectorDetectionResult {
  const sectorScores: { [key: string]: { score: number; keywords: Set<string> } } = {};
  
  // Initialize scores
  Object.keys(sectorKeywords).forEach(sector => {
    sectorScores[sector] = { score: 0, keywords: new Set() };
  });
  
  // Analyze all text content in CSV
  csvData.forEach(row => {
    const textContent = Object.values(row).join(' ').toLowerCase();
    
    Object.entries(sectorKeywords).forEach(([sector, keywords]) => {
      keywords.forEach(keyword => {
        if (textContent.includes(keyword.toLowerCase())) {
          sectorScores[sector].score += 1;
          sectorScores[sector].keywords.add(keyword);
        }
      });
    });
  });
  
  // Find sector with highest score
  let maxScore = 0;
  let detectedSector = 'other';
  let detectedKeywords: string[] = [];
  
  Object.entries(sectorScores).forEach(([sector, data]) => {
    if (data.score > maxScore) {
      maxScore = data.score;
      detectedSector = sector;
      detectedKeywords = Array.from(data.keywords);
    }
  });
  
  const totalWords = csvData.length * Object.keys(csvData[0] || {}).length;
  const confidence = Math.min((maxScore / Math.max(totalWords * 0.1, 1)) * 100, 100);
  
  return {
    sector: detectedSector,
    confidence: Math.round(confidence),
    keywords: detectedKeywords
  };
}

function parseCSV(csvText: string): CSVRow[] {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) return [];
  
  const headers = lines[0].split(/[,;]/).map(h => h.trim().replace(/^"|"$/g, ''));
  const rows: CSVRow[] = [];
  
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(/[,;]/).map(v => v.trim().replace(/^"|"$/g, ''));
    if (values.length === headers.length) {
      const row: CSVRow = {};
      headers.forEach((header, index) => {
        row[header] = values[index];
      });
      rows.push(row);
    }
  }
  
  return rows;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { csvText, storeId } = await req.json();
    
    if (!csvText || !storeId) {
      return new Response(
        JSON.stringify({ error: 'CSV text and store ID are required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Parse CSV
    const parsedData = parseCSV(csvText);
    
    if (parsedData.length === 0) {
      return new Response(
        JSON.stringify({ error: 'Could not parse CSV data' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Detect sector
    const sectorDetection = detectSector(parsedData);

    // Store sector detection in database
    const { error: sectorError } = await supabase
      .from('business_sectors')
      .upsert({
        store_id: storeId,
        sector_type: sectorDetection.sector,
        confidence_score: sectorDetection.confidence,
        detected_keywords: sectorDetection.keywords
      }, {
        onConflict: 'store_id'
      });

    if (sectorError) {
      console.error('Error storing sector:', sectorError);
      return new Response(
        JSON.stringify({ error: 'Failed to store sector detection' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Process and store data based on detected structure
    const headers = Object.keys(parsedData[0]);
    const hasProducts = headers.some(h => 
      ['product', 'produit', 'article', 'item'].some(keyword => 
        h.toLowerCase().includes(keyword)
      )
    );
    
    const hasOrders = headers.some(h => 
      ['order', 'commande', 'transaction'].some(keyword => 
        h.toLowerCase().includes(keyword)
      )
    );

    const result: any = {
      sector: sectorDetection,
      preview: parsedData.slice(0, 5),
      totalRows: parsedData.length,
      headers,
      dataTypes: {
        hasProducts,
        hasOrders,
        hasInventory: headers.some(h => 
          ['stock', 'inventory', 'inventaire', 'quantity'].some(keyword => 
            h.toLowerCase().includes(keyword)
          )
        )
      }
    };

    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in analyze-csv function:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});