"use client";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Activity, BrainCircuit, CheckCircle2, CircleAlert, FileText, GitCompareArrows, Search, ShieldAlert, Sparkles, Video, Wallet } from "lucide-react";
import { getJSON, postJSON, money } from "../../lib/api";

type Player = { id:number; name:string; handle:string; game:string; role:string; region?:string; availability:string; estimated_cost:number; matches_played:number; win_rate:number; confidence:number; metrics:Record<string,number>; data_source?:string };
type Team = { id:number; name:string; game:string; budget:number; member_ids:number[]; members?:Player[]; member_count?:number };
type Feature = { id:string; name:string; status:string; description:string };
const fmt = (v:any) => typeof v === "number" ? (Number.isInteger(v) ? v.toLocaleString("en-IN") : v.toFixed(1)) : String(v ?? "—");

export default function IntelligencePage() {
  const [players,setPlayers] = useState<Player[]>([]);
  const [teams,setTeams] = useState<Team[]>([]);
  const [overview,setOverview] = useState<any>(null);
  const [quality,setQuality] = useState<any>(null);
  const [playerId,setPlayerId] = useState("");
  const [teamId,setTeamId] = useState("");
  const [budget,setBudget] = useState("600000");
  const [tab,setTab] = useState("style-match");
  const [result,setResult] = useState<any>(null);
  const [videoItems,setVideoItems] = useState<any[]>([]);
  const [feedbackItems,setFeedbackItems] = useState<any[]>([]);
  const [videoForm,setVideoForm] = useState({title:"",video_url:"",timestamp_seconds:"0",observation:"",tag:"Scouting note"});
  const [feedbackForm,setFeedbackForm] = useState({useful:"true",reason:"",reviewer:"Demo scout"});
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState("");
  const [message,setMessage] = useState("");
  const [search,setSearch] = useState("");

  const selectedPlayer = useMemo(()=>players.find(p=>String(p.id)===playerId),[players,playerId]);
  const selectedTeam = useMemo(()=>teams.find(t=>String(t.id)===teamId),[teams,teamId]);
  const visiblePlayers = useMemo(()=>players.filter(p=>!search || `${p.name} ${p.handle} ${p.game} ${p.role}`.toLowerCase().includes(search.toLowerCase())),[players,search]);

  async function refresh() {
    const [p,t,o,q,v,f] = await Promise.all([
      getJSON<Player[]>("/api/players?limit=1000"), getJSON<Team[]>("/api/teams"),
      getJSON("/api/intelligence/overview"), getJSON("/api/intelligence/data-quality"),
      getJSON("/api/intelligence/video-evidence"), getJSON("/api/intelligence/feedback")
    ]);
    setPlayers(p); setTeams(t); setOverview(o); setQuality(q); setVideoItems(v.items || []); setFeedbackItems(f.items || []);
    if (!playerId && p.length) setPlayerId(String(p[0].id));
    if (!teamId && t.length) setTeamId(String(t[0].id));
  }
  useEffect(()=>{refresh().catch(e=>setError(e.message));},[]);

  async function runAction(path:string, method:"GET"|"POST"="GET", body?:any) {
    setBusy(true); setError(""); setMessage(""); setResult(null);
    try {
      const data = method === "GET" ? await getJSON(path) : await postJSON(path,body,method);
      setResult(data); setMessage("Analysis completed.");
      if (tab === "data-quality") setQuality(data);
      return data;
    } catch(e:any) { setError(e.message || "Request failed"); return null; }
    finally { setBusy(false); }
  }

  async function saveVideo(e:FormEvent) {
    e.preventDefault(); if(!playerId) return;
    const data = await runAction("/api/intelligence/video-evidence","POST",{player_id:Number(playerId),...videoForm,timestamp_seconds:Number(videoForm.timestamp_seconds)});
    if(data) { setVideoForm({title:"",video_url:"",timestamp_seconds:"0",observation:"",tag:"Scouting note"}); await refresh(); }
  }
  async function saveFeedback(e:FormEvent) {
    e.preventDefault(); if(!playerId) return;
    const data = await runAction("/api/intelligence/feedback","POST",{player_id:Number(playerId),useful:feedbackForm.useful==="true",reason:feedbackForm.reason,reviewer:feedbackForm.reviewer});
    if(data) { setFeedbackForm({...feedbackForm,reason:""}); await refresh(); }
  }
  const tabs = [
    ["style-match","Style matching"],["meta","Meta adaptability"],["value","Recruitment value"],
    ["roster","Roster scenarios"],["video","Video evidence"],["feedback","Scout feedback"],
    ["quality","Data quality"],["report","Scouting report"]
  ];
  const selectClass = "select"; const inputClass = "input";
  const actionButton = (label:string,onClick:()=>void) => <button className="button" onClick={onClick} disabled={busy || !playerId}>{busy?"Working…":label}</button>;
  const chosenEvidence = videoItems.filter(v=>!playerId || v.player_id===Number(playerId));

  return <div>
    <header className="topbar"><div><div className="eyebrow">SCOUTING WORKBENCH / 05</div><h1 className="page-title">Advanced Intelligence</h1><div className="subtitle">Evidence-linked scouting, player similarity, roster scenarios and quality controls.</div></div><div className="pill"><span className="live"/> {overview?.counts?.players ?? players.length} players indexed</div></header>
    <div className="notice"><strong>PROTOTYPE NOTICE</strong> — Current records are simulated demo data. Similarity, adaptability and value are transparent heuristics, not validated predictions. Video evidence is manually linked; no automated video recognition is enabled.</div>
    {error && <div className="error">{error}</div>}{message && !error && <div className="notice"><strong>SUCCESS</strong> — {message}</div>}
    <section className="stats-grid grid" style={{marginBottom:18}}>
      <div className="card"><div className="stat-head">Player profiles <span className="stat-icon"><BrainCircuit size={16}/></span></div><div className="stat-value">{overview?.counts?.players ?? players.length}</div><div className="stat-foot">Available for analysis</div></div>
      <div className="card"><div className="stat-head">Video evidence <span className="stat-icon"><Video size={16}/></span></div><div className="stat-value">{overview?.counts?.video_evidence ?? videoItems.length}</div><div className="stat-foot">Timestamped observations</div></div>
      <div className="card"><div className="stat-head">Scout feedback <span className="stat-icon"><Activity size={16}/></span></div><div className="stat-value">{overview?.counts?.scout_feedback ?? feedbackItems.length}</div><div className="stat-foot">Stored for offline evaluation</div></div>
      <div className="card"><div className="stat-head">Records flagged <span className="stat-icon"><ShieldAlert size={16}/></span></div><div className="stat-value">{quality?.flagged_players ?? "—"}</div><div className="stat-foot">Need data review</div></div>
    </section>
    <section className="card" style={{marginBottom:16}}>
      <div className="section-head"><div><h2>Analysis context</h2><p>Select the player and roster to use across tools.</p></div><span className="tag green">8 MODULES</span></div>
      <div className="filters"><input className={inputClass} placeholder="Search player pool…" value={search} onChange={e=>setSearch(e.target.value)} style={{flex:"1 1 200px"}}/><select className={selectClass} value={playerId} onChange={e=>{setPlayerId(e.target.value);setResult(null)}} style={{flex:"2 1 260px"}}><option value="">Select player</option>{visiblePlayers.map(p=><option key={p.id} value={p.id}>{p.name} · {p.game} · {p.role}</option>)}</select><select className={selectClass} value={teamId} onChange={e=>{setTeamId(e.target.value);setResult(null)}} style={{flex:"1 1 220px"}}><option value="">Select roster</option>{teams.map(t=><option key={t.id} value={t.id}>{t.name} · {t.game}</option>)}</select><input className={inputClass} type="number" min="0" value={budget} onChange={e=>setBudget(e.target.value)} aria-label="Recruitment budget" style={{width:160}}/></div>
      {selectedPlayer && <div className="split" style={{flexWrap:"wrap",fontSize:11,color:"var(--muted)"}}><span><b style={{color:"var(--text)"}}>{selectedPlayer.name}</b> · {selectedPlayer.game} / {selectedPlayer.role} · {selectedPlayer.matches_played} matches</span><span>Est. cost: <b style={{color:"var(--green)"}}>{money(selectedPlayer.estimated_cost)}</b></span></div>}
    </section>
    <div style={{display:"flex",gap:7,flexWrap:"wrap",marginBottom:16}}>{tabs.map(([id,label])=><button key={id} className={`button ${tab===id?"":"secondary"}`} style={{padding:"9px 11px"}} onClick={()=>{setTab(id);setResult(null);setError("");setMessage("")}}>{label}</button>)}</div>

    {tab==="style-match" && <section className="card"><div className="section-head"><div><h2><GitCompareArrows size={16} style={{verticalAlign:"middle",marginRight:7}}/>Player Style Matching</h2><p>Find same-game players with similar metric profiles.</p></div>{actionButton("Find similar players",()=>runAction(`/api/intelligence/style-match/${playerId}?limit=10`))}</div>{result?.matches && <><div className="table-wrap"><table className="table"><thead><tr><th>Player</th><th>Role</th><th>Similarity</th><th>Shared metrics</th><th>Availability</th></tr></thead><tbody>{result.matches.map((m:any)=><tr key={m.player.id}><td>{m.player.name} <small style={{color:"var(--muted)"}}>@{m.player.handle}</small></td><td>{m.player.role}</td><td><span className="score">{m.similarity}%</span></td><td>{m.shared_metrics}</td><td>{m.player.availability}</td></tr>)}</tbody></table></div><p className="footer-note">{result.method}. {result.warning}</p></>}</section>}

    {tab==="meta" && <section className="card"><div className="section-head"><div><h2><Activity size={16} style={{verticalAlign:"middle",marginRight:7}}/>Meta Adaptability Tracker</h2><p>Current proxy based on adaptability and available trend values.</p></div>{actionButton("Analyze adaptability",()=>runAction(`/api/intelligence/meta-adaptability/${playerId}`))}</div>{result?.meta_adaptability_proxy!==undefined && <div className="stats-grid grid"><div className="mini-metric"><small>Adaptability proxy</small><b className="score">{result.meta_adaptability_proxy}/100</b></div><div className="mini-metric"><small>Trend stability proxy</small><b>{result.trend_stability_proxy}/100</b></div><div className="mini-metric"><small>Trend average</small><b>{result.trend_average}/100</b></div><div className="mini-metric"><small>Patch history</small><b>{result.patch_history_available?"Available":"Not available"}</b></div><p className="footer-note" style={{gridColumn:"1/-1"}}>{result.warning}</p></div>}</section>}

    {tab==="value" && <section className="card"><div className="section-head"><div><h2><Wallet size={16} style={{verticalAlign:"middle",marginRight:7}}/>Recruitment Value Estimator</h2><p>Compare a performance proxy against the configured budget.</p></div>{actionButton("Estimate value",()=>runAction(`/api/intelligence/recruitment-value/${playerId}?budget=${encodeURIComponent(budget||"0")}`))}</div>{result?.value_per_100k_cost!==undefined && <><div className="stats-grid grid"><div className="mini-metric"><small>Performance proxy</small><b>{result.role_performance_proxy}/100</b></div><div className="mini-metric"><small>Value per ₹100k cost</small><b className="score">{result.value_per_100k_cost}</b></div><div className="mini-metric"><small>Budget coverage</small><b>{result.budget_coverage_score}%</b></div><div className="mini-metric"><small>Budget status</small><b>{result.within_budget?"Within budget":"Over budget"}</b></div></div><p className="footer-note">{result.warning}</p></>}</section>}

    {tab==="roster" && <section className="card"><div className="section-head"><div><h2><GitCompareArrows size={16} style={{verticalAlign:"middle",marginRight:7}}/>Counterfactual Roster Analysis</h2><p>Compare a candidate's metric contribution to the selected roster.</p></div>{actionButton("Simulate candidate",()=>teamId&&runAction(`/api/intelligence/counterfactual?team_id=${teamId}&candidate_id=${playerId}`,"POST",{}))}</div>{!selectedTeam&&<p className="footer-note">Select a roster in the analysis context first.</p>}{result?.deltas && <><div className="table-wrap"><table className="table"><thead><tr><th>Metric</th><th>Before</th><th>After</th><th>Change</th></tr></thead><tbody>{Object.keys(result.deltas).map(k=><tr key={k}><td>{k.replaceAll("_"," ")}</td><td>{result.before[k]}</td><td>{result.after[k]}</td><td className={result.deltas[k]>=0?"score":""}>{result.deltas[k]>0?"+":""}{result.deltas[k]}</td></tr>)}</tbody></table></div><p className="footer-note">{result.interpretation} {result.warning}</p></>}</section>}

    {tab==="video" && <div className="grid two-col"><section className="card"><div className="section-head"><div><h2><Video size={16} style={{verticalAlign:"middle",marginRight:7}}/>Link video evidence</h2><p>Attach a clip timestamp to a scouting observation.</p></div></div><form onSubmit={saveVideo} style={{display:"grid",gap:10}}><input className={inputClass} required minLength={2} placeholder="Video title / match name" value={videoForm.title} onChange={e=>setVideoForm({...videoForm,title:e.target.value})}/><input className={inputClass} required type="url" placeholder="https:// video URL" value={videoForm.video_url} onChange={e=>setVideoForm({...videoForm,video_url:e.target.value})}/><input className={inputClass} required type="number" min="0" max="86400" placeholder="Timestamp in seconds" value={videoForm.timestamp_seconds} onChange={e=>setVideoForm({...videoForm,timestamp_seconds:e.target.value})}/><input className={inputClass} placeholder="Tag (e.g. clutch, utility, positioning)" value={videoForm.tag} onChange={e=>setVideoForm({...videoForm,tag:e.target.value})}/><textarea className={inputClass} required minLength={3} rows={4} placeholder="What should the scout review at this moment?" value={videoForm.observation} onChange={e=>setVideoForm({...videoForm,observation:e.target.value})}/><button className="button" disabled={busy||!playerId} type="submit">Save evidence for selected player</button></form></section><section className="card"><div className="section-head"><div><h2>Linked evidence</h2><p>{chosenEvidence.length} clip notes for current selection</p></div><button className="button secondary" onClick={()=>getJSON(`/api/intelligence/video-evidence${playerId?`?player_id=${playerId}`:""}`).then(d=>setVideoItems(d.items||[])).catch(e=>setError(e.message))}>Refresh</button></div>{chosenEvidence.length===0?<div className="empty">No evidence linked yet. Add a timestamped clip note.</div>:chosenEvidence.map(v=><div key={v.id} style={{borderBottom:"1px solid var(--line)",padding:"12px 0"}}><div className="split"><b>{v.title}</b><span className="tag">{v.tag}</span></div><p style={{fontSize:11,color:"var(--muted)",lineHeight:1.6}}>{v.observation}</p><a className="text-link" href={`${v.video_url}${v.video_url.includes("#")?"":"#t="+v.timestamp_seconds}`} target="_blank" rel="noreferrer">Open clip at {Math.floor(v.timestamp_seconds/60)}:{String(v.timestamp_seconds%60).padStart(2,"0")} ↗</a></div>)}</section></div>}

    {tab==="feedback" && <div className="grid two-col"><section className="card"><div className="section-head"><div><h2><Sparkles size={16} style={{verticalAlign:"middle",marginRight:7}}/>Scout Feedback Loop</h2><p>Store reviewer feedback for offline evaluation.</p></div></div><form onSubmit={saveFeedback} style={{display:"grid",gap:10}}><select className={selectClass} value={feedbackForm.useful} onChange={e=>setFeedbackForm({...feedbackForm,useful:e.target.value})}><option value="true">Recommendation was useful</option><option value="false">Recommendation was not useful</option></select><input className={inputClass} placeholder="Reviewer name" value={feedbackForm.reviewer} onChange={e=>setFeedbackForm({...feedbackForm,reviewer:e.target.value})}/><textarea className={inputClass} required minLength={3} rows={4} placeholder="Why was it useful or not useful?" value={feedbackForm.reason} onChange={e=>setFeedbackForm({...feedbackForm,reason:e.target.value})}/><button className="button" disabled={busy||!playerId} type="submit">Save scout feedback</button></form><p className="footer-note">Feedback is saved for review. This prototype does not automatically retrain a model.</p></section><section className="card"><div className="section-head"><div><h2>Recent feedback</h2><p>{feedbackItems.length} recorded reviews</p></div></div>{feedbackItems.length===0?<div className="empty">No feedback recorded yet.</div>:feedbackItems.slice().reverse().slice(0,8).map(f=><div key={f.id} style={{padding:"11px 0",borderBottom:"1px solid var(--line)"}}><div className="split"><b>{f.player_name}</b><span className={`tag ${f.useful?"green":"yellow"}`}>{f.useful?"Useful":"Not useful"}</span></div><p style={{fontSize:11,color:"var(--muted)"}}>{f.reason}</p><small style={{color:"var(--muted)"}}>{f.reviewer} · {String(f.created_at||"").slice(0,10)}</small></div>)}</section></div>}

    {tab==="quality" && <section className="card"><div className="section-head"><div><h2><ShieldAlert size={16} style={{verticalAlign:"middle",marginRight:7}}/>Data Quality Monitor</h2><p>Identify records that need validation before scouting decisions.</p></div><button className="button" disabled={busy} onClick={()=>runAction("/api/intelligence/data-quality")}>Run quality checks</button></div>{(result?.records||quality?.records) && <><div className="stats-grid grid"><div className="mini-metric"><small>Total records</small><b>{(result||quality).total_players}</b></div><div className="mini-metric"><small>Flagged records</small><b>{(result||quality).flagged_players}</b></div><div className="mini-metric"><small>Complete rate</small><b>{(result||quality).quality_rate}%</b></div></div><div className="table-wrap"><table className="table"><thead><tr><th>Player</th><th>Quality</th><th>Confidence</th><th>Issues</th></tr></thead><tbody>{(result||quality).records.filter((r:any)=>r.issues.length).slice(0,80).map((r:any)=><tr key={r.player_id}><td>{r.name}<div style={{fontSize:9,color:"var(--muted)"}}>{r.game}</div></td><td><span className="tag yellow">{r.quality}</span></td><td>{r.confidence??"—"}</td><td>{r.issues.join("; ")}</td></tr>)}</tbody></table></div><p className="footer-note">Quality flags do not prove that a player is weak; they indicate that the evidence needs review.</p></>}</section>}

    {tab==="report" && <section className="card"><div className="section-head"><div><h2><FileText size={16} style={{verticalAlign:"middle",marginRight:7}}/>Evidence-Based Scouting Report</h2><p>Structured summary with strengths, development areas, linked evidence and limitations.</p></div>{actionButton("Generate report",()=>runAction(`/api/intelligence/reports/${playerId}`))}</div>{result?.report_id && <><div className="split" style={{flexWrap:"wrap",marginBottom:14}}><span className="tag green">{result.report_id}</span><button className="button secondary" onClick={()=>{const blob=new Blob([JSON.stringify(result,null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`${result.report_id}.json`;a.click();URL.revokeObjectURL(url)}}>Export report JSON</button></div><h2 style={{fontSize:18}}>{result.player.name} · {result.player.game}</h2><p style={{fontSize:12,color:"var(--muted)",lineHeight:1.7}}>{result.summary}</p><div className="grid two-col"><div><h3 style={{fontSize:12}}>Top strengths</h3>{result.strengths.map((x:any)=><div className="metric-row" key={x.metric}><div className="metric-row-head"><span>{x.metric.replaceAll("_"," ")}</span><b>{fmt(x.score)}</b></div><div className="bar-track"><div className="bar-fill" style={{width:`${Math.max(0,Math.min(100,Number(x.score)||0))}%`}}/></div></div>)}</div><div><h3 style={{fontSize:12}}>Development areas</h3>{result.development_areas.map((x:any)=><div className="metric-row" key={x.metric}><div className="metric-row-head"><span>{x.metric.replaceAll("_"," ")}</span><b>{fmt(x.score)}</b></div><div className="bar-track"><div className="bar-fill" style={{width:`${Math.max(0,Math.min(100,Number(x.score)||0))}%`}}/></div></div>)}</div></div><h3 style={{fontSize:12}}>Evidence linked</h3>{result.evidence.length?result.evidence.map((v:any)=><p key={v.id} style={{fontSize:11}}><a className="text-link" href={`${v.video_url}#t=${v.timestamp_seconds}`} target="_blank" rel="noreferrer">{v.title} · {v.timestamp_seconds}s ↗</a> — {v.observation}</p>):<p className="footer-note">No video evidence is linked to this player yet.</p>}<h3 style={{fontSize:12,marginTop:18}}>Limitations</h3><ul className="reason-list">{result.limitations.map((x:string)=><li key={x}>{x}</li>)}</ul><p className="footer-note">Generated at {result.generated_at}. Review the source data and clips before making a recruitment decision.</p></>}</section>}
    <div className="footer-note">ScoutX AI Advanced Intelligence uses transparent demo heuristics. Patch history, verified video analysis, true market pricing and learned recommendation models require appropriate data sources and validation.</div>
  </div>;
}
