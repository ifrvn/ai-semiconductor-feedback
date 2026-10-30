"use strict";

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const fmt = (n, digits=2) => Number(n).toFixed(digits);
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const scenarioNames = {
  baseline: "基准",
  no_ai_chip_feedback: "关闭 AI 芯片反馈",
  hbm_capacity_breakthrough: "HBM 产能突破",
  packaging_shortage: "先进封装短缺",
  power_shortage: "电力供应短缺"
};
const metrics = {
  A: "AI 能力指数",
  delivered: "模拟交付量指数",
  market_price: "市场采购价格",
  physical_cost: "生产成本指数"
};
const sectorNames = {wafer:"先进晶圆制造", hbm:"HBM 存储", packaging:"先进封装", power:"电力基础设施"};
const state = {dataset:null,historyMetric:"performance_per_usd",evaluation:"holdout",scenario:"hbm_capacity_breakthrough",metric:"A",year:2032};

function announce(message){
  const toast=$("#toast");
  toast.textContent=message;
  toast.hidden=false;
  window.clearTimeout(announce.timer);
  announce.timer=window.setTimeout(()=>{toast.hidden=true},4400);
}

function svgChart(element, series, labels, options={}){
  const width=1040,height=310;
  const m={left:64,right:16,top:24,bottom:37};
  const w=width-m.left-m.right,h=height-m.top-m.bottom;
  const flat=series.flatMap(s=>s.points.map(p=>p.value)).filter(Number.isFinite);
  if(!flat.length){element.textContent="暂无可展示数据";return}
  let min=Math.min(...flat),max=Math.max(...flat);
  if(Math.abs(max-min)<1e-10){min-=Math.abs(min)*.1+.1;max+=Math.abs(max)*.1+.1}
  else{const span=max-min;min=Math.max(0,min-span*.14);max+=span*.14}
  const x=i=>m.left+(labels.length===1?.5:i/(labels.length-1))*w;
  const y=v=>m.top+(max-v)/(max-min)*h;
  const grid=Array.from({length:5},(_,i)=>{
    const value=min+(max-min)*i/4;
    return `<line class="grid-line" x1="${m.left}" x2="${width-m.right}" y1="${y(value)}" y2="${y(value)}"/><text class="axis-label" x="${m.left-12}" y="${y(value)+4}" text-anchor="end">${fmt(value,value>10?1:2)}</text>`;
  }).join("");
  const ticks=labels.map((label,i)=>{
    const sparse=options.sparse || Math.max(1,Math.ceil(labels.length/7));
    if(i%sparse!==0 && i!==labels.length-1)return "";
    return `<text class="axis-label" x="${x(i)}" y="${height-9}" text-anchor="middle">${label}</text>`;
  }).join("");
  const geometry=series.map((s,index)=>{
    const points=s.points.map(p=>({x:x(p.index),y:y(p.value),value:p.value,index:p.index})).filter(p=>Number.isFinite(p.value));
    const line=points.map((p,i)=>`${i?"L":"M"}${fmt(p.x,2)},${fmt(p.y,2)}`).join(" ");
    const color=index===0?"#70dfdb":"#d6f17d";
    const dots=points.map((p,i)=>options.allDots || i===points.length-1 ?
      `<circle cx="${p.x}" cy="${p.y}" r="4" fill="${color}" stroke="#12222c" stroke-width="2"><title>${s.name} · ${labels[p.index]}: ${fmt(p.value,3)}</title></circle>`:"").join("");
    return `<path class="${index===0?"chart-path":"chart-path chart-path-alt"}" d="${line}" stroke="${color}"/>${dots}`;
  }).join("");
  const marker=`<line class="hover-guide" x1="0" x2="0" y1="${m.top}" y2="${m.top+h}" visibility="hidden" />
    <g class="hover-markers"></g>`;
  element.innerHTML=`<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">${grid}${ticks}${geometry}${marker}</svg>
    <div class="chart-tooltip" role="status" aria-live="off" hidden></div>`;
  const svg=element.querySelector("svg"),guide=element.querySelector(".hover-guide");
  const markers=element.querySelector(".hover-markers"),tooltip=element.querySelector(".chart-tooltip");
  const colors=["#70dfdb","#d6f17d"];
  function show(index){
    const px=x(index),label=labels[index];
    guide.setAttribute("x1",px);guide.setAttribute("x2",px);guide.setAttribute("visibility","visible");
    markers.innerHTML=series.map((s,i)=>{
      const point=s.points.find(p=>p.index===index);
      return point && Number.isFinite(point.value)?
        `<circle cx="${px}" cy="${y(point.value)}" r="7" fill="${colors[i%colors.length]}" stroke="#10232b" stroke-width="3"/>`:"";
    }).join("");
    const values=series.map((s,i)=>{
      const point=s.points.find(p=>p.index===index);
      return point && Number.isFinite(point.value)?
        `<div class="chart-tooltip-row"><span class="chart-tooltip-dot" style="background:${colors[i%colors.length]}"></span><span>${s.name}</span><strong>${fmt(point.value,4)}</strong></div>`:"";
    }).join("");
    tooltip.innerHTML=`<div class="chart-tooltip-title">${label}</div>${values}`;
    tooltip.hidden=false;
    // SVG uses viewBox coordinates while tooltip is an HTML element in CSS pixels.
    // Anchor to the selected data point, then keep the whole tooltip in bounds.
    const rect=svg.getBoundingClientRect();
    const pointYs=series.map(s=>s.points.find(p=>p.index===index))
      .filter(p=>p && Number.isFinite(p.value)).map(p=>y(p.value));
    const anchorY=pointYs.length?Math.min(...pointYs):m.top;
    const anchorX=px/width*rect.width;
    const anchorTop=anchorY/height*rect.height;
    const tipWidth=tooltip.offsetWidth,tipHeight=tooltip.offsetHeight;
    const gap=14,pad=8;
    const left=clamp(anchorX+gap,pad,Math.max(pad,rect.width-tipWidth-pad));
    const above=anchorTop-tipHeight-gap;
    const below=anchorTop+gap;
    const top=above>=pad?above:below+tipHeight<=rect.height-pad?below:
      clamp(above,pad,Math.max(pad,rect.height-tipHeight-pad));
    tooltip.style.left=`${left}px`;
    tooltip.style.top=`${top}px`;
  }
  function fromPointer(event){
    const bounds=svg.getBoundingClientRect();
    if(!bounds.width)return;
    const localX=(event.clientX-bounds.left)/bounds.width*width;
    const index=clamp(Math.round((localX-m.left)/w*(labels.length-1)),0,labels.length-1);
    show(index);
  }
  svg.addEventListener("pointermove",fromPointer);
  svg.addEventListener("pointerdown",fromPointer);
  element.addEventListener("pointerleave",()=>{
    guide.setAttribute("visibility","hidden");
    markers.innerHTML="";
    tooltip.hidden=true;
  });
}

function history(){
  const rows=state.dataset.history.quarterly;
  const isPerf=state.historyMetric==="performance_per_usd";
  svgChart($("#historyChart"),[{name:isPerf?"性能/美元":"推算单位成本",points:rows.map((row,index)=>({index,value:row[state.historyMetric]}))}],
    rows.map(r=>r.quarter.replace("-"," '").replace("Q","Q")),{allDots:true,sparse:2});
  $$("#historyMetric button").forEach(b=>b.classList.toggle("selected",b.dataset.metric===state.historyMetric));
}

function validation(){
  const obj=state.dataset.history[state.evaluation];
  const labels={last_value:"上期值不变",historical_drift:"历史漂移趋势",log_linear:"对数线性模型"};
  const values=Object.entries(labels).map(([key,label])=>({key,label,value:obj.scores[key].log_rmse}));
  const best=Math.min(...values.map(v=>v.value));
  const upper=Math.max(...values.map(v=>v.value))*1.1;
  $("#validationBars").innerHTML=values.map(v=>`<div class="vbar"><div class="vbar-meta"><span>${v.label}${Math.abs(v.value-best)<1e-9?'<span class="vbar-best">● BEST</span>':''}</span><span class="vbar-value">${fmt(v.value,3)}</span></div><div class="vbar-track"><div class="vbar-fill ${Math.abs(v.value-best)<1e-9?"best":""}" style="width:${fmt(100*v.value/upper,2)}%"></div></div></div>`).join("");
  $("#validationCount").textContent=(obj.test_n || obj.origin_count)+" 个历史预测检验点";
}

function selectedSeries(){
  const records=state.dataset.sectors;
  return {
    base:records.filter(r=>r.scenario==="baseline"),
    alternative:records.filter(r=>r.scenario===state.scenario)
  };
}

function scenarios(){
  const {base,alternative}=selectedSeries();
  const labels=base.map(x=>String(Math.round(x.year)));
  $("#scenarioChartTitle").textContent=metrics[state.metric]+"随时间变化";
  $("#scenarioLegend").textContent=scenarioNames[state.scenario];
  const chartSeries=[
    {name:"基准",points:base.map((r,index)=>({index,value:r[state.metric]}))}
  ];
  if(state.scenario!=="baseline"){
    chartSeries.push({name:scenarioNames[state.scenario],points:alternative.map((r,index)=>({index,value:r[state.metric]}))});
  }
  svgChart($("#scenarioChart"),chartSeries,labels,{sparse:2});
  $$("#scenarioChips button").forEach(b=>b.classList.toggle("selected",b.dataset.scenario===state.scenario));
  capacity();
}

function capacity(){
  const row=state.dataset.sectors.find(r=>r.scenario===state.scenario && Math.abs(r.year-state.year)<.01);
  if(!row){$("#capacityBars").textContent="未找到该年度数据";return}
  $("#yearReadout").textContent=state.year;
  $("#capacityBars").innerHTML=Object.entries(sectorNames).map(([key,label])=>{
    const val=row["capacity_"+key],low=row.bottleneck===key;
    return `<div class="cap-card ${low?"bottleneck":""}"><div class="cap-name">${label}</div><div class="cap-num">${fmt(val,2)}</div><div class="cap-track"><div class="cap-fill" style="width:${fmt(clamp(val/1.6*100,0,100),1)}%"></div></div><div class="cap-tag">${low?"● 当前产能瓶颈":"相对产能指数"}</div></div>`;
  }).join("");
  $("#capacityNote").textContent=`${state.year} 年：${sectorNames[row.bottleneck]}构成供给瓶颈。需求 ${fmt(row.requested_demand,2)}，模拟交付指数 ${fmt(row.delivered,2)}，市场价格指数 ${fmt(row.market_price,2)}。仅为模型模拟，不代表实际预测。`;
}

function uncertainty(){
  const data=state.dataset.uncertainty;
  $("#drawCount").textContent=data.samples;
  const fields=[
    ["A","AI 能力指数"],
    ["delivered","模拟交付量指数"],
    ["physical_cost","生产成本指数"],
    ["market_price","市场价格指数"]
  ];
  $("#uncertaintyPlot").innerHTML=fields.map(([field,label])=>{
    const stats=data.baseline[field],low=stats.p05,mid=stats.median,high=stats.p95;
    const scaleMax=Math.max(high*1.15,.01);
    const left=clamp(low/scaleMax*100,0,100),right=clamp(high/scaleMax*100,0,100),median=clamp(mid/scaleMax*100,0,100);
    return `<div class="urow"><div class="urow-top"><span>${label}</span><strong>${fmt(mid,2)} <span style="font:10px var(--mono);color:#8fa8a8">MEDIAN</span></strong></div><div class="u-track"><div class="u-range" style="left:${fmt(left)}%;width:${fmt(right-left)}%"></div><div class="u-med" style="left:${fmt(median)}%"></div></div><div class="u-axis"><span>P05 / ${fmt(low,2)}</span><span>P95 / ${fmt(high,2)}</span></div></div>`;
  }).join("");
}

function wire(){
  $$("#historyMetric button").forEach(b=>b.addEventListener("click",()=>{state.historyMetric=b.dataset.metric;history()}));
  $("#validationSelect").addEventListener("change",e=>{state.evaluation=e.target.value;validation()});
  $("#scenarioMetric").addEventListener("change",e=>{state.metric=e.target.value;scenarios()});
  $("#yearRange").addEventListener("input",e=>{state.year=Number(e.target.value);capacity()});
  $("#scenarioChips").innerHTML=Object.entries(scenarioNames).map(([key,name])=>`<button class="chip ${key===state.scenario?"selected":""}" data-scenario="${key}">${name}</button>`).join("");
  $$("#scenarioChips button").forEach(b=>b.addEventListener("click",()=>{state.scenario=b.dataset.scenario;scenarios()}));
}

async function start(){
  try{
    const response=await fetch("./data.json",{cache:"no-cache"});
    if(!response.ok)throw new Error("HTTP "+response.status);
    const data=await response.json();
    if(data.schema!==1 || !data.history?.quarterly?.length || !data.sectors?.length)throw new Error("Invalid dashboard data");
    state.dataset=data;
    $("#trendValue").textContent=fmt(data.history.trend.growth_pct_per_year,1);
    const values=Object.values(data.history.holdout.scores).map(s=>s.log_rmse);
    $("#holdoutValue").textContent=fmt(Math.min(...values),3);
    wire();history();validation();scenarios();uncertainty();
  }catch(error){
    console.error("Dashboard data unavailable",error);
    announce("数据尚未生成。请运行 python site/build_data.py，或查看 Pages 部署日志。");
    for(const selector of ["#historyChart","#scenarioChart","#validationBars","#capacityBars","#uncertaintyPlot"]){
      const node=$(selector);if(node)node.textContent="数据未加载：请检查部署产物 data.json。";
    }
  }
}

function initThemeToggle(){
  const root=document.documentElement;
  const button=$("#themeToggle");
  const media=window.matchMedia ? window.matchMedia("(prefers-color-scheme: light)") : null;
  function reflect(){
    const light=root.dataset.theme==="light";
    button.setAttribute("aria-pressed",String(light));
    button.setAttribute("aria-label",light?"切换为深色模式":"切换为白天模式");
    button.querySelector(".theme-icon").textContent=light?"☾":"☀";
    button.querySelector(".theme-text").textContent=light?"深色模式":"白天模式";
    const meta=document.querySelector('meta[name="theme-color"]');
    if(meta)meta.setAttribute("content",light?"#f3f7f8":"#0b1119");
  }
  button.addEventListener("click",()=>{
    root.dataset.theme=root.dataset.theme==="light"?"dark":"light";
    try {localStorage.setItem("feedback-theme",root.dataset.theme);} catch (_) {}
    reflect();
  });
  if(media){
    const updateOnSystem=()=>{
      let saved=null;
      try {saved=localStorage.getItem("feedback-theme");} catch (_) {}
      if(saved!=="dark" && saved!=="light"){
        root.dataset.theme=media.matches?"light":"dark";
        reflect();
      }
    };
    if(media.addEventListener)media.addEventListener("change",updateOnSystem);
    else if(media.addListener)media.addListener(updateOnSystem);
  }
  reflect();
}

document.addEventListener("DOMContentLoaded",start);
