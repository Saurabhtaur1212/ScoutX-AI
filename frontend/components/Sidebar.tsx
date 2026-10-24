"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BarChart3, Crosshair, Gamepad2, LayoutDashboard, Users, Radar, ShieldCheck, BrainCircuit } from "lucide-react";

const links = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/scouting", label: "Player scouting", icon: Crosshair },
  { href: "/recommendations", label: "AI recommendations", icon: Radar },
  { href: "/rosters", label: "Multi-game rosters", icon: Users },
  { href: "/intelligence", label: "Advanced intelligence", icon: BrainCircuit },
];
export default function Sidebar() {
  const path = usePathname();
  return <aside className="sidebar">
    <Link href="/" className="brand"><span className="brand-mark"><Gamepad2 size={23}/></span><span>SCOUTX<span className="brand-ai"> AI</span><small>ESPORTS INTELLIGENCE</small></span></Link>
    <div className="nav-label">WORKSPACE</div>
    <nav>{links.map(({href,label,icon:Icon}) => <Link key={href} href={href} className={`nav-link ${path===href ? "active" : ""}`}><Icon size={18}/><span>{label}</span>{label==="AI recommendations" && <span className="nav-new">AI</span>}</Link>)}</nav>
    <div className="sidebar-bottom">
      <div className="status-card"><span className="status-dot"/><div><b>Demo environment</b><small>Simulated player data</small></div></div>
      <div className="profile"><div className="avatar">SX</div><div><b>Scout workspace</b><small>Organization admin</small></div><ShieldCheck size={16}/></div>
    </div>
  </aside>;
}
