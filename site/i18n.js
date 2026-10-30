/* Local-first, dependency-free zh-CN / en localization. */
(function(){
  "use strict";
  const translations={
  "实证数据": "Evidence",
  "模型检验": "Validation",
  "情景模拟": "Scenarios",
  "不确定性": "Uncertainty",
  "白天模式": "Light mode",
  "深色模式": "Dark mode",
  "当人工智能": "When artificial intelligence",
  "遇见": "meets ",
  "半导体工业": "the semiconductor industry",
  "AI 的进步能否加速芯片研发、压低算力成本，并再次推动 AI 自身？从真实历史数据出发，探索这场产业反馈循环的边界与可能性。": "Can AI accelerate chip R&D, lower compute costs, and drive further AI progress? Explore the limits of this feedback loop through historical evidence and illustrative models.",
  "探索研究数据 ": "Explore the evidence ",
  "了解研究方法 ": "Explore methodology ",
  "研究范围说明": "Research scope",
  "历史数据和模型模拟严格分开。只有硬件性能/价格代理指标进行了样本外检验；未来情景、资本建设延迟及 AI→芯片的因果反馈系数均未通过真实数据校准，不代表预测。": "Historical observations and model simulations are separate. Only the hardware performance-per-dollar proxy has undergone out-of-time validation. Future scenarios, construction delays, and causal AI-to-chip feedback coefficients remain uncalibrated; these are not forecasts.",
  "样本内性能/价格年化增长率": "In-sample annual growth in performance per dollar",
  "2023–2025 · Epoch AI 分组数据": "2023–2025 · Epoch AI grouped data",
  "2025 留出集最佳基准误差": "Best baseline error on 2025 holdout",
  "基于过去数据进行预测": "Forecast using past observations only",
  "独立建模的产业产能部门": "Individually modeled supply sectors",
  "晶圆 · HBM · 封装 · 电力": "Wafers · HBM · Packaging · Power",
  "AI→芯片产业的因果系数": "Causal AI-to-chip industry coefficient",
  "尚缺匹配的因果识别数据": "Not identified with available evidence",
  "历史数据 ": "Historical data ",
  "不是预测": "Not forecasts",
  "从已公开的季度加速器价格性能数据，观察硬件经济性的实际变化。": "Observed changes in accelerator economics from published quarterly data.",
  "AI 加速器性能与单位成本": "AI accelerator performance and implied cost",
  "销售金额加权的理论性能/美元指标；不包含使用率、网络和电力。": "Spend-weighted theoretical performance per dollar; excludes utilization, networking, and power.",
  "性能 / 美元": "Performance / USD",
  "单位成本": "Implied unit cost",
  " 2025 H100 参考单位": " 2025 H100 reference unit",
  "历史观测 · 12 季度": "Observations · 12 quarters",
  "数据来源 Epoch AI ↗": "Source: Epoch AI ↗",
  "让预测接受": "Putting forecasts to the ",
  "检验": "test",
  "简单基准对照；评估过去数据能否预测未参与拟合的未来季度。": "Compare simple baselines on future quarters excluded from training.",
  "样本外预测误差": "Out-of-sample forecast errors",
  "对数 RMSE 越低越好；基于历史代理指标。": "Lower log RMSE is better; measured on a historical proxy.",
  "评估窗口": "Evaluation window",
  "2025 年留出集": "2025 holdout",
  "滚动 · 下一季度": "Rolling · next quarter",
  "滚动 · 四季度后": "Rolling · four quarters ahead",
  "误差单位 / LOG RMSE": "Error metric / LOG RMSE",
  "拟合得更好": "A better fit",
  "不等于预测得更好。": "does not mean a better forecast.",
  "即使历史数据呈上升趋势，对数线性拟合也不一定在留出季度中优于更简单的基准。": "Even with an upward historical trend, log-linear regression may underperform simpler baselines on unseen quarters.",
  "小样本结果 · 不保证未来仍然成立": "Small sample · future performance is not guaranteed",
  "如果产业的": "What if industry ",
  "瓶颈改变": "bottlenecks shift",
  "？": "?",
  "使用假设参数的四部门模型，比较不同冲击下的产能、成本与 AI 能力。": "Compare capacity, costs, and AI capability under hypothetical shocks in a four-sector model.",
  "选择模拟情景": "Choose simulation scenario",
  "展示指标": "Metric",
  "AI 能力指数": "AI capability index",
  "实际交付量": "Delivered output",
  "市场采购价格": "Market purchase price",
  "生产成本指数": "Production cost index",
  "AI 能力指数随时间变化": "AI capability over time",
  "实线为基准情景，虚线为选定的反事实情景；均为归一化模型输出。": "Solid: baseline. Dashed: selected counterfactual. All values are normalized model outputs.",
  "基准情景 ": "Baseline ",
  "HBM 产能突破": "HBM capacity breakthrough",
  "模拟结果 ≠ 未来预测": "Simulation ≠ forecast",
  "每个环节，都可能成为新瓶颈": "Every sector can become a bottleneck",
  "拖动年份，查看选定情景下各部门归一化的兼容产能。": "Move the year slider to inspect normalized sector capacities.",
  "最小部门产能决定交付上限。": "The least-capable sector constrains delivery.",
  "一组假设，": "One set of assumptions, ",
  "多种结果": "many outcomes",
  "在明确的参数区间内抽样，观察模型结论的稳定性。": "Sample defined parameter ranges to explore model sensitivity.",
  "参数敏感性区间": "Parameter sensitivity ranges",
  "横线表示第 5–95 百分位；圆点为中位数。它们不是统计置信区间。": "Lines span the 5th–95th percentiles; dots show medians. These are not confidence intervals.",
  "认识不确定性，": "Recognizing uncertainty",
  "不等于消除不确定性。": "does not eliminate it.",
  "抽样使用研究者设定的独立均匀分布，并非从历史数据估计出的概率分布。": "Samples use analyst-defined independent uniform ranges, not empirical probability distributions.",
  "暂无可靠证据可将这些区间解释为真实世界的概率。": "These ranges cannot be interpreted as real-world probabilities.",
  "保持可验证，": "Keep it testable,",
  "也保持克制。": "and appropriately cautious.",
  "这是一个开放的探索性研究项目。真实数据、预测基准与产业模拟遵循不同的证据等级。我们公开模型代码、输入数据与识别限制，避免把情景模拟解释成经过实证验证的因果预测。": "This open exploratory project distinguishes observed evidence, forecast baselines, and industry simulations. Code, inputs, and identification limits are public to avoid mistaking scenarios for empirically validated causal forecasts.",
  "阅读验证方法与限制 ↗": "Read validation methods and limitations ↗",
  "真实数据": "Observed evidence",
  "Epoch AI 加速器理论性能/美元、SIA 全球半导体销售额": "Epoch AI accelerator performance per dollar; SIA global semiconductor sales",
  "可检验模型": "Testable baselines",
  "按时间划分训练与测试，比较简单基准和趋势模型": "Time-based train/test splits comparing simple baselines and trend models",
  "假设性模拟": "Hypothetical simulations",
  "产业建设延迟、产能瓶颈及 AI 反馈系数尚未校准": "Build delays, bottlenecks, and AI feedback coefficients remain uncalibrated",
  "基准": "Baseline",
  "关闭 AI 芯片反馈": "Disable AI-to-chip feedback",
  "先进封装短缺": "Advanced packaging shortage",
  "电力供应短缺": "Power shortage",
  "先进晶圆制造": "Advanced wafer fabrication",
  "HBM 存储": "HBM memory",
  "先进封装": "Advanced packaging",
  "电力基础设施": "Power infrastructure",
  "上期值不变": "Last value",
  "历史漂移趋势": "Historical drift",
  "对数线性模型": "Log-linear trend",
  "当前产能瓶颈": "Current bottleneck",
  "归一化供应能力": "Normalized supply capacity",
  "市场价格指数": "Market price index",
  "中位数": "Median",
  "暂无可展示数据": "No data to display",
  "数据未加载：请检查部署产物 data.json。": "Data unavailable: check the deployed data.json.",
  "数据尚未生成。请运行 python site/build_data.py，或查看 Pages 部署日志。": "Data not generated. Run python site/build_data.py or inspect the Pages deployment logs.",
  "研究摘要": "Research summary",
  "2023 到 2025 年季度历史趋势折线图": "Quarterly historical trend, 2023–2025",
  "基准和反事实模型年度对比": "Annual comparison of baseline and counterfactual simulations",
  "选择模拟年份": "Select simulation year",
  "切换明亮或深色主题": "Toggle light/dark theme",
  "切换为深色模式": "Switch to dark mode",
  "切换为白天模式": "Switch to light mode",
  "Feedback Observatory 首页": "Feedback Observatory home",
  " 个样本外预测点": " out-of-sample forecast points",
  "性能/美元": "Performance / USD",
  "基准情景": "Baseline scenario",
  "模型数据，非真实预测。": "Model output, not a real-world forecast."
};
  translations["2025 年预测检验：最低误差"] = "2025 forecast test: lowest error";
  translations["2025 年预测检验"] = "2025 forecast test";
  translations["历史数据预测效果对比"] = "Historical forecast accuracy comparison";
  translations["使用对数均方根误差（Log RMSE）比较预测结果，数值越小越准确。"] = "Compare forecasts using log root mean squared error (Log RMSE); lower values indicate better accuracy.";
  translations["用过去的数据预测之后的季度，再与实际结果比较，检验模型能否预测未知数据。"] = "Forecast later quarters using earlier data, then compare with observations to test performance on unseen data.";
  translations["历史观测数据与模型模拟分开展示。目前仅检验了硬件性能与价格指标的历史预测效果；未来产业情景、建设延迟及 AI 对芯片产业的影响强度尚未用真实数据验证，因此模拟结果不代表未来预测。"] = "Historical observations and simulations are shown separately. Only historical forecasting performance of the hardware performance-price metric has been tested. Future industry scenarios, construction delays, and the strength of AI's impact on chips have not been validated with real-world data. Simulations are not forecasts.";
  translations["按销售金额加权计算的理论算力性价比；未计入实际使用率、网络和电力成本。"] = "Theoretical compute value weighted by sales revenue; excludes actual utilization, networking, and electricity costs.";
  translations["实线表示正常假设下的基准结果，虚线表示改变某项条件后的对比结果。数值均为便于比较的模型指数，不是真实预测值。"] = "Solid line: baseline assumptions. Dashed line: results under an altered assumption. Values are comparative model indices, not real-world forecasts.";
  translations["拖动年份，查看各产业环节在模型中的相对产能指数（不是实际产量）。"] = "Move the year slider to compare modeled relative capacity across sectors (not actual production).";
  translations["横线表示模拟结果中间 90% 的范围，圆点表示中位数。这些范围不代表现实发生概率。"] = "The line covers the middle 90% of simulation results; the dot marks the median. This is not a real-world probability estimate.";
  translations["模拟参数在研究者设定的范围内随机取值，并非根据历史数据计算出真实发生概率。"] = "Model parameters are sampled within analyst-defined ranges, not inferred as real-world probabilities from historical data.";
  translations["这些范围仅反映模型对参数假设的敏感程度，不能用来判断现实中发生的概率。"] = "These ranges reflect sensitivity to modeling assumptions, not real-world likelihood.";
  translations["尚无足够数据证明因果影响"] = "Insufficient data to establish a causal effect";
  translations["每美元理论性能"] = "Theoretical performance per USD";
  translations["推算单位成本"] = "Implied unit cost";
  translations["相对产能指数"] = "Relative capacity index";
  translations[" 个历史预测检验点"] = " historical forecast test points";
  translations["仅为模型模拟，不代表实际预测。"] = "Simulation only; not a real-world forecast.";
  translations["模拟交付量指数"] = "Modeled delivery index";
  translations["模拟交付指数"] = "Modeled delivery index";
  translations["相对指数 · 假设情景模拟（非真实预测）"] = "Relative index · Hypothetical simulation (not a forecast)";
  translations["使用假设参数的四部门模型，比较不同冲击下的产能、成本与 AI 能力。扩产资金包括模型内部投资与单独设定的外部项目融资，资金规模未经实证校准。"] = "Compare four-sector capacity, costs, and AI capability under hypothetical assumptions. Expansion is funded by internal investment and separately assumed external project financing, neither calibrated to observed industry financing.";
  const saved=(()=>{try{return localStorage.getItem("feedback-language")}catch(_){return null}})();
  let locale=saved==="en"||saved==="zh-CN"?saved:(navigator.language&&navigator.language.toLowerCase().startsWith("zh")?"zh-CN":"en");
  const originals=new WeakMap();
  const attrOriginals=new WeakMap();
  const attrs=["aria-label","title","placeholder","content"];
  function translate(source){
    if(!source)return source;
    if(Object.prototype.hasOwnProperty.call(translations,source))return translations[source];
    const trimmed=source.trim();
    if(Object.prototype.hasOwnProperty.call(translations,trimmed))
      return source.replace(trimmed,translations[trimmed]);
    const capacity=source.match(/^(\\d{4}) 年：(.+?)构成供给瓶颈。需求 ([\\d.]+)，实际交付 ([\\d.]+)，市场价格指数 ([\\d.]+)。模型数据，非真实预测。$/);
    if(capacity)return `${capacity[1]}: ${translations[capacity[2]]||capacity[2]} is the supply bottleneck. Demand ${capacity[3]}; delivered ${capacity[4]}; market price index ${capacity[5]}. Model output, not a forecast.`;
    let result=source;
    for(const [zh,en] of Object.entries(translations).sort((a,b)=>b[0].length-a[0].length)){
      if(zh.length>1&&result.includes(zh))result=result.split(zh).join(en);
    }
    result=result.replace(/(\d{4}) 年：(.+?)构成供给瓶颈。需求 ([\d.]+)，实际交付 ([\d.]+)，市场价格指数 ([\d.]+)。模型数据，非真实预测。/,
      (_,year,sector,demand,delivered,price)=>`${year}: ${sector} is the bottleneck. Demand ${demand}; delivered ${delivered}; market price index ${price}. Model output, not a forecast.`);
    return result.replace(/(\d+) 个样本外预测点/,(_,n)=>`${n} out-of-sample forecasts`);
  }
  function updateText(node){
    if(!originals.has(node))originals.set(node,node.nodeValue);
    const base=originals.get(node);
    const target=locale==="en"?translate(base):base;
    if(node.nodeValue!==target)node.nodeValue=target;
  }
  function updateAttrs(el){
    if(!attrOriginals.has(el)){
      const base={};
      for(const attr of attrs)if(el.hasAttribute(attr))base[attr]=el.getAttribute(attr);
      attrOriginals.set(el,base);
    }
    const base=attrOriginals.get(el);
    for(const [key,value] of Object.entries(base)){
      const target=locale==="en"?translate(value):value;
      if(el.getAttribute(key)!==target)el.setAttribute(key,target);
    }
  }
  function walk(root){
    if(root.nodeType===3){if(!root.parentElement?.closest("#languageToggle"))updateText(root);return}
    if(root.nodeType!==1&&root.nodeType!==9&&root.nodeType!==11)return;
    if(root.nodeType===1){
      if(root.closest&&root.closest("script,style,#languageToggle"))return;
      updateAttrs(root);
    }
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
    while(walker.nextNode()){
      const node=walker.currentNode;
      if(node.parentElement&&node.parentElement.closest("script,style,#languageToggle"))continue;
      updateText(node);
    }
    if(root.querySelectorAll)for(const el of root.querySelectorAll("[aria-label],[title],[placeholder],meta[name=description]"))if(el.id!=="languageToggle")updateAttrs(el);
  }
  function render(){
    document.documentElement.lang=locale;
    document.documentElement.dataset.locale=locale;
    document.title=locale==="en"?"AI × Semiconductors | Feedback Observatory":"AI × 半导体 | Feedback Observatory";
    const btn=document.getElementById("languageToggle");
    if(btn){
      btn.textContent=locale==="en"?"中文":"EN";
      btn.setAttribute("aria-label",locale==="en"?"Switch to Chinese":"切换为英文");
      btn.setAttribute("title",locale==="en"?"Switch to Chinese":"Switch to English");
    }
    if(document.body)walk(document.body);
    const meta=document.querySelector('meta[name="description"]');if(meta)updateAttrs(meta);
  }
  function setLocale(next){
    locale=next;
    try{localStorage.setItem("feedback-language",locale)}catch(_){}
    render();
  }
  document.addEventListener("click",event=>{
    if(event.target.closest&&event.target.closest("#languageToggle"))setLocale(locale==="en"?"zh-CN":"en");
  });
  document.addEventListener("DOMContentLoaded",()=>{
    render();
    const observer=new MutationObserver(records=>{
      for(const record of records){
        if(record.type==="childList")for(const node of record.addedNodes)walk(node);
        else if(record.type==="characterData"){
          // New content from charts replaces the original source for this text node.
          const node=record.target;
          if(node.nodeValue!==(locale==="en"?translate(originals.get(node)):originals.get(node))){
            originals.delete(node);updateText(node);
          }
        }
      }
    });
    observer.observe(document.body,{subtree:true,childList:true});
  });
  window.feedbackI18n={getLocale:()=>locale,translate};
})();
