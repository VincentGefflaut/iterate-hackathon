export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      alert_metadata: {
        Row: {
          created_at: string
          generated_at: string
          id: string
          severity_threshold: string
          total_alerts: number
          tracked_locations: string[]
          tracked_products: string[]
          upload_date: string
        }
        Insert: {
          created_at?: string
          generated_at: string
          id?: string
          severity_threshold: string
          total_alerts: number
          tracked_locations: string[]
          tracked_products: string[]
          upload_date: string
        }
        Update: {
          created_at?: string
          generated_at?: string
          id?: string
          severity_threshold?: string
          total_alerts?: number
          tracked_locations?: string[]
          tracked_products?: string[]
          upload_date?: string
        }
        Relationships: []
      }
      business_sectors: {
        Row: {
          confidence_score: number | null
          created_at: string | null
          detected_keywords: string[] | null
          id: string
          sector_type: string
          store_id: string | null
          updated_at: string | null
        }
        Insert: {
          confidence_score?: number | null
          created_at?: string | null
          detected_keywords?: string[] | null
          id?: string
          sector_type: string
          store_id?: string | null
          updated_at?: string | null
        }
        Update: {
          confidence_score?: number | null
          created_at?: string | null
          detected_keywords?: string[] | null
          id?: string
          sector_type?: string
          store_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "business_sectors_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: true
            referencedRelation: "stores"
            referencedColumns: ["id"]
          },
        ]
      }
      inventory: {
        Row: {
          created_at: string | null
          id: string
          last_restock_date: string | null
          max_stock_level: number | null
          min_stock_level: number | null
          product_id: string | null
          quantity_in_stock: number
          store_id: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          last_restock_date?: string | null
          max_stock_level?: number | null
          min_stock_level?: number | null
          product_id?: string | null
          quantity_in_stock?: number
          store_id?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          last_restock_date?: string | null
          max_stock_level?: number | null
          min_stock_level?: number | null
          product_id?: string | null
          quantity_in_stock?: number
          store_id?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "inventory_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "products"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "inventory_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: false
            referencedRelation: "stores"
            referencedColumns: ["id"]
          },
        ]
      }
      market_intelligence: {
        Row: {
          country: string
          created_at: string | null
          description: string | null
          end_date: string | null
          event_name: string
          event_type: string
          id: string
          impact_percentage: number | null
          impact_prediction: string
          is_active: boolean | null
          region: string
          sector_specific: string[] | null
          start_date: string | null
          updated_at: string | null
        }
        Insert: {
          country: string
          created_at?: string | null
          description?: string | null
          end_date?: string | null
          event_name: string
          event_type: string
          id?: string
          impact_percentage?: number | null
          impact_prediction: string
          is_active?: boolean | null
          region: string
          sector_specific?: string[] | null
          start_date?: string | null
          updated_at?: string | null
        }
        Update: {
          country?: string
          created_at?: string | null
          description?: string | null
          end_date?: string | null
          event_name?: string
          event_type?: string
          id?: string
          impact_percentage?: number | null
          impact_prediction?: string
          is_active?: boolean | null
          region?: string
          sector_specific?: string[] | null
          start_date?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      orders: {
        Row: {
          created_at: string | null
          customer_id: string | null
          id: string
          order_date: string
          order_number: string
          product_id: string | null
          quantity: number
          store_id: string | null
          total_amount: number
          unit_price: number
        }
        Insert: {
          created_at?: string | null
          customer_id?: string | null
          id?: string
          order_date: string
          order_number: string
          product_id?: string | null
          quantity?: number
          store_id?: string | null
          total_amount: number
          unit_price: number
        }
        Update: {
          created_at?: string | null
          customer_id?: string | null
          id?: string
          order_date?: string
          order_number?: string
          product_id?: string | null
          quantity?: number
          store_id?: string | null
          total_amount?: number
          unit_price?: number
        }
        Relationships: [
          {
            foreignKeyName: "orders_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "products"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "orders_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: false
            referencedRelation: "stores"
            referencedColumns: ["id"]
          },
        ]
      }
      product_alerts: {
        Row: {
          affected_areas: string[]
          affected_products: string[]
          alert_id: string
          created_at: string
          description: string
          detected_at: string
          event_date: string
          event_type: string
          id: string
          key_facts: string[]
          location: string
          potential_relevance: string
          recommended_action: string
          severity: string
          source_url: string | null
          title: string
          updated_at: string
          urgency: string
        }
        Insert: {
          affected_areas: string[]
          affected_products: string[]
          alert_id: string
          created_at?: string
          description: string
          detected_at: string
          event_date: string
          event_type: string
          id?: string
          key_facts: string[]
          location: string
          potential_relevance: string
          recommended_action: string
          severity: string
          source_url?: string | null
          title: string
          updated_at?: string
          urgency: string
        }
        Update: {
          affected_areas?: string[]
          affected_products?: string[]
          alert_id?: string
          created_at?: string
          description?: string
          detected_at?: string
          event_date?: string
          event_type?: string
          id?: string
          key_facts?: string[]
          location?: string
          potential_relevance?: string
          recommended_action?: string
          severity?: string
          source_url?: string | null
          title?: string
          updated_at?: string
          urgency?: string
        }
        Relationships: []
      }
      products: {
        Row: {
          category: string | null
          cost: number | null
          created_at: string | null
          id: string
          price: number
          product_code: string
          product_name: string
          store_id: string | null
          subcategory: string | null
          updated_at: string | null
        }
        Insert: {
          category?: string | null
          cost?: number | null
          created_at?: string | null
          id?: string
          price: number
          product_code: string
          product_name: string
          store_id?: string | null
          subcategory?: string | null
          updated_at?: string | null
        }
        Update: {
          category?: string | null
          cost?: number | null
          created_at?: string | null
          id?: string
          price?: number
          product_code?: string
          product_name?: string
          store_id?: string | null
          subcategory?: string | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "products_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: false
            referencedRelation: "stores"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string | null
          email: string
          full_name: string | null
          id: string
          role: string | null
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email: string
          full_name?: string | null
          id: string
          role?: string | null
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string
          full_name?: string | null
          id?: string
          role?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
      sales_data: {
        Row: {
          country: string
          created_at: string | null
          date: string
          id: string
          margin: number
          region: string
          revenue: number
          store_id: string | null
          transactions: number | null
        }
        Insert: {
          country: string
          created_at?: string | null
          date: string
          id?: string
          margin: number
          region: string
          revenue: number
          store_id?: string | null
          transactions?: number | null
        }
        Update: {
          country?: string
          created_at?: string | null
          date?: string
          id?: string
          margin?: number
          region?: string
          revenue?: number
          store_id?: string | null
          transactions?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "sales_data_store_id_fkey"
            columns: ["store_id"]
            isOneToOne: false
            referencedRelation: "stores"
            referencedColumns: ["id"]
          },
        ]
      }
      stores: {
        Row: {
          address: string | null
          city: string
          country: string
          created_at: string | null
          id: string
          manager_name: string | null
          name: string
          phone: string | null
          region: string
          status: string | null
          updated_at: string | null
        }
        Insert: {
          address?: string | null
          city: string
          country: string
          created_at?: string | null
          id?: string
          manager_name?: string | null
          name: string
          phone?: string | null
          region: string
          status?: string | null
          updated_at?: string | null
        }
        Update: {
          address?: string | null
          city?: string
          country?: string
          created_at?: string | null
          id?: string
          manager_name?: string | null
          name?: string
          phone?: string | null
          region?: string
          status?: string | null
          updated_at?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
