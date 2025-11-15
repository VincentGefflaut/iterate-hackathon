import { ReactNode, useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { LayoutDashboard, Store, LogOut, Menu, X, Upload, Package, AlertTriangle } from "lucide-react";
import { toast } from "sonner";
import { User } from "@supabase/supabase-js";
import logo from "@/assets/logo-insightflow.png";

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<User | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        navigate("/auth");
      } else {
        setUser(session.user);
      }
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        navigate("/auth");
      } else {
        setUser(session.user);
      }
    });

    return () => subscription.unsubscribe();
  }, [navigate]);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    toast.success("Déconnecté avec succès");
    navigate("/auth");
  };

  const navItems = [
    { path: "/", icon: LayoutDashboard, label: "Tableau de Bord" },
    { path: "/stores", icon: Store, label: "Magasins" },
    { path: "/products", icon: Package, label: "Produits & Stock" },
    { path: "/import", icon: Upload, label: "Importer Données" },
    { path: "/alerts", icon: AlertTriangle, label: "Alertes" },
  ];

  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex w-64 border-r border-border bg-card/30 backdrop-blur-xl flex-col">
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <img src={logo} alt="InsightFlow" className="h-8 w-8 animate-fade-in transition-all duration-300 hover:scale-110 hover:rotate-6 cursor-pointer" />
            <h1 className="text-xl font-bold text-primary hover-glow transition-smooth">
              InsightFlow
            </h1>
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Button
              key={item.path}
              variant={location.pathname === item.path ? "default" : "ghost"}
              className={`w-full justify-start transition-smooth ${
                location.pathname === item.path
                  ? "bg-primary text-primary-foreground shadow-glow"
                  : "hover:bg-secondary hover:translate-x-1"
              }`}
              onClick={() => {
                navigate(item.path);
                setSidebarOpen(false);
              }}
            >
              <item.icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          ))}
        </nav>
        <div className="p-4 border-t border-border space-y-2">
          <div className="px-3 py-2 text-sm text-muted-foreground">
            {user?.email}
          </div>
          <Button
            variant="ghost"
            className="w-full justify-start hover:bg-destructive/10 hover:text-destructive transition-smooth"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
          <aside className="absolute left-0 top-0 h-full w-64 border-r border-border bg-card flex flex-col">
            <div className="p-6 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img src={logo} alt="InsightFlow" className="h-8 w-8 animate-fade-in transition-all duration-300 hover:scale-110 hover:rotate-6 cursor-pointer" />
                <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                  InsightFlow
                </h1>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <nav className="flex-1 p-4 space-y-2">
              {navItems.map((item) => (
                <Button
                  key={item.path}
                  variant={location.pathname === item.path ? "default" : "ghost"}
                  className={`w-full justify-start transition-smooth ${
                    location.pathname === item.path
                      ? "gradient-primary text-primary-foreground"
                      : "hover:bg-secondary"
                  }`}
                  onClick={() => {
                    navigate(item.path);
                    setSidebarOpen(false);
                  }}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.label}
                </Button>
              ))}
            </nav>
            <div className="p-4 border-t border-border space-y-2">
              <div className="px-3 py-2 text-sm text-muted-foreground">
                {user?.email}
              </div>
              <Button
                variant="ghost"
                className="w-full justify-start hover:bg-destructive/10 hover:text-destructive transition-smooth"
                onClick={handleLogout}
              >
                <LogOut className="mr-2 h-4 w-4" />
                Déconnexion
              </Button>
            </div>
          </aside>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="md:hidden p-4 border-b border-border bg-card/50">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>
        </div>
        <div className="p-6 md:p-8">{children}</div>
      </main>
    </div>
  );
};

export default Layout;
