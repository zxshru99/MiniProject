import type { Metadata } from "next";
import "./globals.css";
import { Inter, JetBrains_Mono } from "next/font/google";
import { cn } from "@/lib/utils";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({ 
  subsets: ["latin"], 
  variable: "--font-inter",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({ 
  subsets: ["latin"], 
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AgriAI Predict — Multi-Modal Soil Texture & Crop Yield Intelligence",
  description: "Advanced precision agriculture platform combining deep CNN computer vision for soil texture classification, optical volumetric water content (% VWC) estimation, and XGBoost crop yield forecasting with SHAP explainability.",
  authors: [{ name: "AgriAI Engineering" }],
  keywords: [
    "agri ai",
    "precision agriculture",
    "soil classification cnn",
    "crop yield prediction",
    "soil moisture vwc",
    "grad-cam soil vision",
    "shap agronomic explainability",
    "agrometeorology live weather"
  ],
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html 
      lang="en" 
      className={cn(inter.variable, jetbrainsMono.variable, "dark")}
      style={{ backgroundColor: "#000000" }}
    >
      <body className="font-mono antialiased" style={{ backgroundColor: "#000000" }}>
        <TooltipProvider>
          {children}
        </TooltipProvider>
      </body>
    </html>
  );
}
