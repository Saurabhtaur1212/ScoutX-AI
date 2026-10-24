import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "../components/Sidebar";

export const metadata: Metadata = {
  title: "ScoutX AI | Esports Intelligence",
  description: "AI-powered esports scouting and multi-roster intelligence",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><div className="shell"><Sidebar /><main className="main">{children}<footer className="site-credit">Designed and Developed by TEAM 404</footer></main></div></body></html>;
}
