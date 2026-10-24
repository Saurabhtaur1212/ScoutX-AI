"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowUpRight, Users, Target, Gamepad2, Trophy, TrendingUp, Radar, ChevronRight } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, BarChart, Bar } from "recharts";
import { getJSON, money } from "../lib/api";

const trend = [{month:"May",value:61},{month:"Jun",value:66},{month:"Jul",value:63},{month:"Aug",value:72},{month:"Sep",value:77},{month:"Oct",value:83}];
export default function Dashboard() {
  const [summary,setSummary] = useState<any>(null);
  const [players,setPlayers] = useState<any[]>([]);
  const [teams,setTeams] = useState<any[]>([]);
  const [error,setError] = useState("");
  useEffect(()=>{ Promise.all([getJSON("/api/summary"),getJSON("/api/players?limit=8"),getJSON("/api/teams")]).then(([s,p,t])=>{setSummary(s);setPlayers(p);setTeams(t)}).catch(e=>setError(e.message)); },[]);
  const stats = summary ? [
    {label:"Players scouted",value:summary.total_players,foot:"Across all game ecosystems",icon:Users},
    {label:"Available talent",value:summary.available_players,foot:"Ready for evaluation",icon:Target},
    {label:"Active rosters",value:summary.total_teams,foot:"Across multiple titles",icon:Gamepad2},
    {label:"Avg. win rate",value:`${summary.average_win_rate}%`,foot:"Across demo player pool",icon:Trophy},
  ] : [];
  return <div>
    <header className="topbar"><div><div className="eyebrow">INTELLIGENCE OVERVIEW / 01</div><h1 className="page-title">Command Center</h1><div className="subtitle">Your competitive edge starts with better decisions.</div></div><div className="top-actions"><span className="pill"><span className="live"/> SYSTEM OPERATIONAL</span><Link className="button" href="/recommendations"><Radar size={15}/> Find talent <ArrowUpRight size={14}/></Link></div></header>
    <div className="notice"><strong>DEMO DATA NOTICE</strong> — Player profiles, metrics, rosters, and costs in this environment are simulated for demonstration. Validate all inputs before real recruitment use.</div>
    {error && <div className="error">Cannot connect to API: {error}. Start the backend using the README instructions.</div>}
    <div className="grid stats-grid">{stats.map(s=><div className="card" key={s.label}><div className="stat-head"><span>{s.label}</span><span className="stat-icon"><s.icon size={17}/></span></div><div className="stat-value">{s.value}</div><div className="stat-foot"><strong>●</strong> &nbsp;{s.foot}</div></div>)}</div>
    <div className="grid two-col">
      <section className="card"><div className="section-head"><div><h2>Performance intelligence</h2><p>Illustrative organization-level trajectory</p></div><span className="tag green">+12.4% TREND</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend} margin={{top:10,right:8,left:-20,bottom:0}}><defs><linearGradient id="fillScore" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#b7f36b" stopOpacity={0.22}/><stop offset="95%" stopColor="#b7f36b" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#202c39" strokeDasharray="3 5" vertical={false}/><XAxis dataKey="month" stroke="#687a90" tickLine={false} axisLine={false} fontSize={10}/><YAxis stroke="#687a90" tickLine={false} axisLine={false} fontSize={10}/><Tooltip contentStyle={{background:"#101722",border:"1px solid #2b3948",borderRadius:8,fontSize:11}}/><Area type="monotone" dataKey="value" stroke="#b7f36b" strokeWidth={2.5} fill="url(#fillScore)"/></AreaChart></ResponsiveContainer></div><div className="chart-legend"><span><i className="legend-dot"/> Composite performance index</span><span>Illustrative trend, not live data</span></div></section>
      <section className="card"><div className="section-head"><div><h2>Roster ecosystem</h2><p>Team distribution by game</p></div><Link className="text-link" href="/rosters">MANAGE <ChevronRight size={12} style={{verticalAlign:"middle"}}/></Link></div><div style={{display:"grid",gap:20,marginTop:24}}>{teams.map(t=><div key={t.id}><div className="split"><div><div style={{fontSize:11,fontWeight:800}}>{t.game}</div><div style={{fontSize:9,color:"var(--muted)",marginTop:3}}>{t.name}</div></div><div style={{textAlign:"right"}}><b style={{fontSize:12}}>{t.member_count}/5</b><div style={{fontSize:9,color:"var(--muted)"}}>players</div></div></div><div className="bar-track"><div className="bar-fill" style={{width:`${Math.min(100,t.member_count/5*100)}%`}}/></div></div>)}</div></section>
    </div>
    <section className="card"><div className="section-head"><div><h2>Scouting pool</h2><p>Recently surfaced player profiles from the demo dataset</p></div><Link className="text-link" href="/scouting">VIEW ALL PLAYERS <ChevronRight size={12} style={{verticalAlign:"middle"}}/></Link></div><div className="table-wrap"><table className="table"><thead><tr><th>Player</th><th>Game / role</th><th>Win rate</th><th>K/D</th><th>Cost estimate</th><th>Status</th></tr></thead><tbody>{players.map(p=><tr key={p.id}><td><div className="player-cell"><div className="player-avatar">{p.name.split(" ").map((x:string)=>x[0]).join("")}</div><div><div className="player-name">{p.name}</div><div className="player-handle">@{p.handle}</div></div></div></td><td><div>{p.game}</div><div style={{fontSize:9,color:"var(--muted)",marginTop:4}}>{p.role}</div></td><td>{p.win_rate}%</td><td>{p.kd_ratio}</td><td>{money(p.estimated_cost)}</td><td><span className={`tag ${p.availability==="Available"?"green":"yellow"}`}>{p.availability}</span></td></tr>)}</tbody></table>{!players.length&&!error&&<div className="loading">Loading player pool…</div>}</div></section>
    <div className="footer-note">SCOUTX AI • Role-aware scoring • Explainable recommendations • Multi-game roster intelligence</div>
  </div>;
}
