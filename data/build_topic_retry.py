import json, re, sys
from datetime import datetime, timezone

with open('/Users/dolan/.openclaw/agents/bibi-agent/data/raw_rss.json') as f:
    raw = json.load(f)

# Sort by age
sorted_raw = sorted(raw, key=lambda x: x.get('age_days', 99999))

def extract_text(content, max_len=600):
    """Strip markdown noise, return clean text."""
    lines = content.split('\n')
    result = []
    for line in lines:
        s = line.strip()
        if not s: continue
        if s.startswith('#') or s.startswith('```') or s.startswith('* * *'): continue
        if '![' in s or s.startswith('[(') or 'Join ' in s: continue
        if re.match(r'^\[.+\]\(.+\)$', s) or s.startswith('http'): continue
        if s.startswith('*') and s.endswith('*'): continue
        result.append(s)
    text = ' '.join(result[:80])
    return text[:max_len]

def get_by_age(age):
    for x in sorted_raw:
        if x.get('age_days') == age:
            return x
    return None

results = []

def add(category, event_core, tier, source, details_and_data, perspectives, focus_trace=False):
    results.append({
        "category": category,
        "event_core": event_core,
        "tier": tier,
        "source": source,
        "details_and_data": details_and_data,
        "perspectives": perspectives,
        "focus_trace": focus_trace
    })

# ============================================================
# SEMANTIC CLUSTERING — identify topic clusters among recent items
# ============================================================
# Recent items: age 0-5 days from Hacker News and arXiv
# rss.xml items are 7-10 years old — cluster separately as T4 legacy

# Cluster 1: AI/ML System & Agent Research (arXiv, age=3, T0-T1)
arxiv_items = [x for x in sorted_raw if x['source'] == 'arXiv AI/ML']
hn_recent = [x for x in sorted_raw if x['source'] == 'Hacker News' and x.get('age_days', 999) <= 5]
rss_old = [x for x in sorted_raw if x['source'] == 'rss.xml']

# ============================================================
# T0: arXiv code-level papers (cs.AI/cs.CL/cs.CV, weight 5)
# ============================================================

# T0-A: VLM Image Tampering Detection (cs.CV, cs.AI)
i = get_by_age(3)
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Masks to Pixels' in x.get('title',''):
        i = x; break
add("Computer Vision / VLM Safety",
    "From Masks to Pixels and Meaning: New VLM Image Tampering Taxonomy & Benchmark",
    "T0", "arXiv cs.CV/cs.AI (2603.20193)",
    f"arXiv 2603.20193v1 | Authors: X Shang, Y Tang, J Cui | cs.CV, cs.AI, cs.LG\nNew taxonomy and benchmark for detecting VLM-generated/manipulated images. Existing tampering benchmarks rely on pixel-level metrics; this work introduces semantic-level evaluation. Key contributions: unified taxonomy, dataset, evaluation metrics for VLM image integrity.\n{extract_text(i['content'])}",
    ["First semantic-level VLM tampering benchmark", "Unified taxonomy covering generation + manipulation", "cs.CV + cs.AI cross-disciplinary contribution"], False)

# T0-B: AI Agents for High Energy Physics
for x in sorted_raw:
    if x.get('age_days') == 3 and 'High Energy Physics' in x.get('title',''):
        i = x; break
add("AI Agents / Scientific Discovery",
    "AI Agents Autonomously Performing Experimental High Energy Physics",
    "T0", "arXiv cs.AI/cs.LG (2603.20179)",
    f"arXiv 2603.20179v1 | Authors: E.A. Moreno, S. Bright-Thonney, A. Novak | hep-ex, cs.AI, cs.LG\nLLM-based AI agents successfully execute full high-energy physics analysis pipelines autonomously — hypothesis formation, data selection, analysis, interpretation. Demonstrates AI agent capability to conduct experimental science without human intervention at each step.\n{extract_text(i['content'])}",
    ["AI agents completing full HEP analysis autonomously", "Landmark for autonomous scientific discovery", "hep-ex domain: first demonstrated AI-driven experimental pipeline"], False)

# T0-C: Evolving Jailbreaks — Multi-Objective Long-Tail LLM Attacks
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Jailbreaks' in x.get('title',''):
        i = x; break
add("LLM Security / Red Teaming",
    "Evolving Jailbreaks: Automated Multi-Objective Long-Tail Attacks on LLMs",
    "T0", "arXiv cs.CR/cs.AI (2603.20122)",
    f"arXiv 2603.20122v1 | Authors: W Hong, Z Rong, L Wang | cs.CR, cs.AI\nEvolutionary algorithm generates multi-objective long-tail jailbreak attacks targeting LLMs. Systematically explores attack surface beyond known jailbreak templates; adversarial diversity metric introduced. LLM security evaluation entering automated adversarial generation era.\n{extract_text(i['content'])}",
    ["Evolutionary algorithm for multi-objective jailbreak generation", "Long-tail attack diversity beyond template-based jailbreaks", "LLM security benchmarks now require adversarial automation"], False)

# ============================================================
# T1: arXiv papers weight 4 (Vision, Agents, Cybersecurity)
# ============================================================

# T1-a: VideoSeek — Long-Horizon Video Agent
for x in sorted_raw:
    if x.get('age_days') == 3 and 'VideoSeek' in x.get('title',''):
        i = x; break
add("Video Understanding / AI Agents",
    "VideoSeek: Long-Horizon Video Agent with Tool-Guided Seeking",
    "T1", "arXiv cs.CV/cs.AI/cs.CL (2603.20185)",
    f"arXiv 2603.20185v1 | Authors: J Lin, J Wu, J Liu | cs.CV, cs.AI, cs.CL\nLong-horizon video understanding with tool-guided AI agent. Agentic video models that can seek relevant frames across long videos using external tools — addresses context window limitations in VLM-based video understanding.\n{extract_text(i['content'])}",
    ["Tool-guided video agent for long-horizon understanding", "Addresses VLM context window limitations", "cs.CL + cs.CV cross-modal agent architecture"], False)

# T1-b: LumosX — Personalized Video Generation
for x in sorted_raw:
    if x.get('age_days') == 3 and 'LumosX' in x.get('title',''):
        i = x; break
add("Video Generation / Personalization",
    "LumosX: Personalized Video Generation via Identity-Attribute Binding",
    "T1", "arXiv cs.CV/cs.AI (2603.20192)",
    f"arXiv 2603.20192v1 | Authors: J Xing, F Du, H Yuan | cs.CV, cs.AI\nDiffusion model advance: bind subject identity with attributes for personalized video generation. Separates identity preservation from motion/attribute control — key challenge in personalized video synthesis.\n{extract_text(i['content'])}",
    ["Identity-attribute disentanglement in video generation", "Diffusion model personalization advance", "Subject-consistent personalized video synthesis"], False)

# T1-c: Chain-of-Adaptation — Vision-Language Adaptation via RL
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Chain-of-Adaptation' in x.get('title',''):
        i = x; break
add("Vision-Language / Fine-Tuning",
    "Chain-of-Adaptation: Surgical VLM Fine-Tuning via Reinforcement Learning",
    "T1", "arXiv cs.CV/cs.AI (2603.20116)",
    f"arXiv 2603.20116v1 | Authors: J Li, C Xu, M Liu | cs.CV, cs.AI\nSurgical vision-language adaptation using reinforcement learning — rather than full fine-tuning, selectively adapts VLMs to new domains with minimal parameter changes via RL-guided routing.\n{extract_text(i['content'])}",
    ["RL-guided surgical parameter updates for VLMs", "Replaces full fine-tuning with targeted adaptation", "Domain-specific VLM adaptation efficiency"], False)

# T1-d: Semantic Token Clustering — LLM Uncertainty Quantification
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Semantic Token Clustering' in x.get('title',''):
        i = x; break
add("LLM Evaluation / Uncertainty Quantification",
    "Semantic Token Clustering for Efficient LLM Uncertainty Quantification",
    "T1", "arXiv cs.CL/cs.AI/cs.LG (2603.20161)",
    f"arXiv 2603.20161v1 | Authors: Q Cao, A Gambardella, T Kojima | cs.CL, cs.AI, cs.LG\nClusters semantic tokens to reduce computation in LLM uncertainty quantification. Full uncertainty estimation over all tokens is expensive; semantic grouping enables efficient estimation without sacrificing accuracy.\n{extract_text(i['content'])}",
    ["Computationally efficient LLM uncertainty estimation", "Semantic token clustering reduces redundant computation", "Reliability of LLM outputs in high-stakes settings"], False)

# T1-e: Dynamic Belief Graphs for ToM Reasoning
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Dynamic Belief Graphs' in x.get('title',''):
        i = x; break
add("LLM Reasoning / Theory of Mind",
    "Dynamic Belief Graphs for Theory-of-Mind Reasoning in LLMs",
    "T1", "arXiv cs.AI (2603.20170)",
    f"arXiv 2603.20170v1 | Authors: R Chen, X Zhao, T Cova | cs.AI\nToM reasoning with LLMs requires tracking how beliefs evolve. Dynamic belief graphs model mental state transitions — enables LLMs to reason about multi-step social scenarios where agents' beliefs change over time.\n{extract_text(i['content'])}",
    ["Dynamic mental state tracking for LLM ToM", "Belief graph as structured representation for social reasoning", "High-stakes AI decision-making: where AI must model human beliefs"], False)

# T1-f: Agentic Multi-Agent for Cybersecurity Risk Management
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Agentic Multi-Agent' in x.get('title',''):
        i = x; break
add("AI Agents / Cybersecurity",
    "Agentic Multi-Agent Architecture for Cybersecurity Risk Management",
    "T1", "arXiv eess.SY/cs.AI/cs.CR (2603.20131)",
    f"arXiv 2603.20131v1 | Authors: R Gupta, S Kumar, S Sharma | eess.SY, cs.AI, cs.CR\nMulti-agent AI system for cybersecurity risk assessment in small organizations. Agents collaborate to perform vulnerability scanning, threat modeling, and risk prioritization — automates what previously required expert consultants.\n{extract_text(i['content'])}",
    ["Multi-agent system for automated cybersecurity risk assessment", "Democratizes security expertise for SMBs", "Agent collaboration for complex threat modeling"], False)

# T1-g: Robot Inner Critic — VLM-based Self-Refinement
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Inner Critic' in x.get('title',''):
        i = x; break
add("Robotics / VLM Self-Refinement",
    "The Robot's Inner Critic: VLM-based Replanning for Social Behavior Self-Refinement",
    "T1", "arXiv cs.RO/cs.AI (2603.20164)",
    f"arXiv 2603.20164v1 | Authors: J Lim, Y Yoon, K Park | cs.RO, cs.AI\nVLM-based self-critique loop enables robots to refine social behaviors through replanning. Robot generates social behavior, evaluates via VLM critic, replans — closing the loop on social robot interaction quality.\n{extract_text(i['content'])}",
    ["VLM critic for robot social behavior refinement", "Closed-loop social robot learning in deployment", "cs.RO + cs.AI integration for real-world robot interaction"], False)

# T1-h: Adaptive Greedy Frame Selection for Long Video Understanding
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Adaptive Greedy Frame' in x.get('title',''):
        i = x; break
add("Video Understanding / Efficiency",
    "Adaptive Greedy Frame Selection for Long Video Understanding",
    "T1", "arXiv cs.CV/cs.AI/cs.CL (2603.20180)",
    f"arXiv 2603.20180v1 | Authors: Y Huang, F Zhu | cs.CV, cs.AI, cs.CL\nGreedy frame selection strategy to reduce VLM compute for long video QA. Selects most informative frames adaptively rather than uniform sampling — key efficiency breakthrough for long-form video understanding.\n{extract_text(i['content'])}",
    ["Adaptive frame selection reduces VLM compute for long video", "Uniform sampling replaced with information-theoretic frame selection", "Efficiency breakthrough for long-form video understanding"], False)

# T1-i: Improving Generalization on Cybersecurity with Multi-Modal Contrastive Learning
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Improving Generalization' in x.get('title',''):
        i = x; break
add("Cybersecurity / Multi-Modal Learning",
    "Improving Cybersecurity Task Generalization via Multi-Modal Contrastive Learning",
    "T1", "arXiv cs.CR/cs.AI (2603.20181)",
    f"arXiv 2603.20181v1 | Authors: J Huang, R.V. Valentim, L Vassio | cs.CR, cs.AI\nMulti-modal contrastive learning applied to cybersecurity tasks: improves generalization of ML models for threat detection across different data modalities and attack variants.\n{extract_text(i['content'])}",
    ["Multi-modal contrastive learning for cybersecurity ML", "Cross-modality generalization in threat detection", "Addressing ML generalization impairment in security tasks"], False)

# T1-j: Measuring Faithfulness in LLM Chain-of-Thought
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Measuring Faithfulness' in x.get('title',''):
        i = x; break
add("LLM Evaluation / Chain-of-Thought",
    "Measuring Faithfulness in LLM Chain-of-Thought: Classifier Sensitivity Problem",
    "T1", "arXiv cs.CL/cs.AI/cs.LG (2603.20172)",
    f"arXiv 2603.20172v1 | Author: R.J. Young | cs.CL, cs.AI, cs.LG\nChain-of-thought faithfulness evaluation is classifier-sensitive: different classifiers yield different faithfulness assessments for the same CoT. Key methodological finding — CoT evaluation needs standardized calibration before being used as a reliability metric.\n{extract_text(i['content'])}",
    ["CoT faithfulness evaluation varies with classifier choice", "Methodological warning: CoT reliability metrics need calibration", "cs.CL foundational evaluation paper for reasoning systems"], False)

# T1-k: Design-OS — Engineering System Design with AI
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Design-OS' in x.get('title',''):
        i = x; break
add("AI for Engineering / System Design",
    "Design-OS: AI-Driven Engineering System Design with Control-Systems Case",
    "T1", "arXiv cs.CE/cs.AI (2603.20151)",
    f"arXiv 2603.20151v1 | Authors: H.S. Bank, D.R. Herber, T.H. Bradley | cs.CE, cs.AI, eess.SY\nSpecification-driven AI framework for engineering system design. LLMs integrated into control-systems design workflow — automates requirements analysis and design space exploration for mechanical/electrical systems.\n{extract_text(i['content'])}",
    ["LLM for engineering design automation", "Specification-driven system design AI", "Cross-domain: control systems + AI"], False)

# T1-l: HAL Representations for Text Classification
for x in sorted_raw:
    if x.get('age_days') == 3 and 'HAL Representations' in x.get('title',''):
        i = x; break
add("NLP / Text Classification",
    "Enhancing HAL Representations via Attention-Based Pooling for Text Classification",
    "T1", "arXiv cs.CL/cs.AI/cs.LG (2603.20149)",
    f"arXiv 2603.20149v1 | Authors: A Sakour, Z Sakour | cs.CL, cs.AI, cs.LG\nAttention-based pooling applied to Hyperspace Analogue to Language (HAL) representations — improves text classification performance over standard HAL. Contribution: learned pooling replaces fixed aggregation in HAL.\n{extract_text(i['content'])}",
    ["Attention pooling for HAL word-context matrices", "Improved text classification via learned aggregation", "NLP representation learning advance"], False)

# ============================================================
# T1: Hacker News high-signal technical posts (age 0-5 days)
# ============================================================

# HN-1: Flash-MoE — 397B model on laptop (age=0, 329pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Flash-MoE' in x.get('title',''):
        i = x; break
add("LLM Inference / MoE Optimization",
    "Flash-MoE: Running a 397B Parameter MoE Model on a Laptop",
    "T1", "Hacker News (329pts)",
    f"HN 329pts | Author: mft_ | https://github.com/danveloper/flash-moe\nMixture-of-Experts model at 397B parameters runs locally on consumer laptop hardware. Technical breakthrough in MoE inference optimization — enables edge deployment of frontier-scale models. GitHub repo with implementation.\n{extract_text(i['content'])}",
    ["397B MoE model runs on laptop hardware", "MoE sparse activation enables edge deployment of frontier models", "Open-source implementation available"], False)

# HN-2: Reports of code's death are greatly exaggerated (age=0, 320pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and "code's death" in x.get('title',''):
        i = x; break
add("Software Engineering / AI Coding",
    "Reports of Code's Death Are Greatly Exaggerated — AI Coding Reality Check",
    "T1", "Hacker News (320pts)",
    f"HN 320pts | Author: stevekrouse | https://stevekrouse.com/precision\nPushback against 'AI will replace programmers' narrative. Argues software complexity, domain knowledge requirements, and debugging challenges mean human coding remains essential. HN debate on AI coding tools' actual impact on employment.\n{extract_text(i['content'])}",
    ["Human coding irreplaceable for complex software", "AI coding tools augment rather than replace engineers", "HN debate: AI productivity gains vs software complexity"], False)

# HN-3: The future of version control (age=0, 467pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'future of version control' in x.get('title',''):
        i = x; break
add("Developer Tools / Version Control",
    "The Future of Version Control — AI-Native VCS Paradigm",
    "T1", "Hacker News (467pts)",
    f"HN 467pts | Author: c17r | https://bramcohen.com/p/manyana\nBram Cohen's exploration of where version control systems are headed in the era of AI-generated code. Key themes: AI-authored code requires new VCS semantics (intent tracking, semantic diffs, automated review), not just line-based tracking.\n{extract_text(i['content'])}",
    ["AI-generated code requires new VCS paradigms", "Semantic diffs vs line-based version control", "Intent tracking for AI-authored software"], False)

# HN-4: Windows native app development is a mess (age=0, 368pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Windows native app' in x.get('title',''):
        i = x; break
add("Developer Experience / Windows Ecosystem",
    "Windows Native App Development Is a Mess — Platform Complexity Analysis",
    "T1", "Hacker News (368pts)",
    f"HN 368pts | Author: domenicd | https://domenic.me/windows-native-dev/\nDetailed critique of Windows native application development ecosystem fragmentation: Win32/WinRT/UWP/WinUI/.NET/MAUI/C++17+ complexity layers. Developer productivity impact and platform commitment risks.\n{extract_text(i['content'])}",
    ["Windows dev platform fragmentation: too many abstraction layers", "MAUI cross-platform attempt still insufficient", "Developer experience cost of Windows native app commitment"], False)

# HN-5: Teaching Claude to QA a mobile app (age=0, 83pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Teaching Claude' in x.get('title',''):
        i = x; break
add("AI Coding / QA Automation",
    "Teaching Claude to QA a Mobile App — LLM-Based Testing Pipeline",
    "T1", "Hacker News (83pts)",
    f"HN 83pts | Author: azhenley | https://christophermeiklejohn.com/ai/zabriskie/development/android/ios/2026/03/22/teaching-claude-to-qa-a-mobile-app.html\nPractical case study: using Claude for mobile app QA automation — Android/iOS testing via LLM-driven test generation, execution, and failure analysis. Demonstrates LLM-as-QA-engineer pattern in production.\n{extract_text(i['content'])}",
    ["Claude as mobile QA engineer: test generation + execution", "LLM-driven Android/iOS testing pipeline", "QA automation via LLM: practical production case study"], False)

# HN-6: GrapheneOS privacy (age=0, 297pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'GrapheneOS' in x.get('title',''):
        i = x; break
add("Privacy / Mobile OS",
    "GrapheneOS Remains Fully Usable Without Requiring Personal Information",
    "T2", "Hacker News (297pts)",
    f"HN 297pts | Author: nothrowaways | https://grapheneos.social/@GrapheneOS/116261301913660830\nGrapheneOS project update confirming the privacy-hardened Android fork remains fully functional without Google account integration or personal information requirements. Continues to work on degoogled devices without Play Services.\n{extract_text(i['content'])}",
    ["GrapheneOS degoogled Android: no Google account required", "Privacy-hardened mobile OS maintains full functionality", "Alternative to mainstream Android without surveillance tradeoffs"], False)

# HN-7: Project Nomad — offline knowledge (age=0, 394pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Project Nomad' in x.get('title',''):
        i = x; break
add("Knowledge Management / Offline-First",
    "Project Nomad — Knowledge That Never Goes Offline",
    "T2", "Hacker News (394pts)",
    f"HN 394pts | Author: jensgk | https://www.projectnomad.us\nOffline-first personal knowledge management system. All data stored locally, fully accessible without internet. Key use case: knowledge resilience, privacy, accessibility in low-connectivity environments.\n{extract_text(i['content'])}",
    ["Offline-first personal knowledge management", "Local-first software for knowledge resilience", "Privacy-preserving alternative to cloud note-taking tools"], False)

# HN-8: MAUI coming to Linux (age=0, 181pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'MAUI' in x.get('title',''):
        i = x; break
add("Developer Tools / Cross-Platform UI",
    "MAUI Coming to Linux — .NET Cross-Platform UI Toolkit Expands",
    "T2", "Hacker News (181pts)",
    f"HN 181pts | Author: DeathArrow | https://avaloniaui.net/blog/maui-avalonia-preview-1\n.NET MAUI expanding to Linux via Avalonia UI collaboration. Cross-platform .NET UI framework now covers Windows/macOS/iOS/Android/Linux — consolidate C# UI development across all major platforms.\n{extract_text(i['content'])}",
    [".NET MAUI Linux support via Avalonia partnership", "C# cross-platform UI across all major OSes", "XAML-based UI consolidation for .NET developers"], False)

# HN-9: They're Vibe-Coding Spam (age=0, 60pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Vibe-Coding Spam' in x.get('title',''):
        i = x; break
add("AI Coding / Ethics",
    "They're Vibe-Coding Spam Now — AI-Generated Marketing Spam Explosion",
    "T2", "Hacker News (60pts)",
    f"HN 60pts | Author: raybb | https://tedium.co/2026/02/25/vibe-coded-email-spam/\nAI coding tools (vibe coding) are being used to generate marketing spam at scale. New wave of AI-generated bulk email with minimal human review. Ethical and regulatory implications of AI-authored commercial communication.\n{extract_text(i['content'])}",
    ["Vibe coding enabling bulk AI-generated spam", "AI-authored marketing email at scale", "Regulatory gap: AI-generated commercial communications"], False)

# HN-10: How to attract AI bots to OSS (age=1, 101pts)
for x in sorted_raw:
    if x.get('age_days') == 1 and 'AI Bots' in x.get('title',''):
        i = x; break
add("Open Source / AI Ecosystem",
    "How to Attract AI Bots to Your Open Source Project",
    "T2", "Hacker News (101pts)",
    f"HN 101pts | Author: zdw | https://nesbitt.io/2026/03/21/how-to-attract-ai-bots-to-your-open-source-project.html\nPractical guide: making OSS projects AI-agent friendly — machine-readable documentation, structured metadata, API accessibility, consistent CLI interfaces. As AI agents become developers, projects need to be machine-consumable.\n{extract_text(i['content'])}",
    ["Making OSS AI-agent readable: machine-readable docs and metadata", "Structured interfaces for AI agent consumption", "OSS project accessibility for AI developers"], False)

# HN-11: RollerCoaster Tycoon optimization (age=0, 284pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'RollerCoaster Tycoon' in x.get('title',''):
        i = x; break
add("Systems Programming / Optimization",
    "The Gold Standard of Optimization: Inside RollerCoaster Tycoon",
    "T2", "Hacker News (284pts)",
    f"HN 284pts | Author: mariuz | https://larstofus.com/2026/03/22/the-gold-standard-of-optimization-a-look-under-the-hood-of-rollercoaster-tycoon/\nDeep dive into RCT's legendary performance: how a 1999 game achieved massive scale (thousands of guests, complex ride physics) with minimal CPU. Still studied as the gold standard of game optimization — relevant to modern real-time systems.\n{extract_text(i['content'])}",
    ["RCT's pathfinding and simulation optimization techniques", "1999 game still relevant to real-time systems performance", "Algorithmic inspiration for modern constraint-heavy applications"], False)

# HN-12: Why I love NixOS (age=0, 249pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Why I love NixOS' in x.get('title',''):
        i = x; break
add("DevOps / Reproducible Systems",
    "Why I Love NixOS — Reproducible System Configuration",
    "T3", "Hacker News (249pts)",
    f"HN 249pts | Author: birkey | https://www.birkey.co/2026-03-22-why-i-love-nixos.html\n NixOS declarative, reproducible system configuration. Entire system described in config files — reproducible builds, atomic upgrades, rollbacks. Growing relevance as reproducibility becomes critical for AI development environments.\n{extract_text(i['content'])}",
    ["Declarative system configuration for reproducibility", "Nix language for reproducible environments", "Growing relevance for AI development environment reproducibility"], False)

# HN-13: Five Years of Microsoft Systems Reading Group (age=0, 137pts)
for x in sorted_raw:
    if x.get('age_days') == 0 and 'Systems Reading Group' in x.get('title',''):
        i = x; break
add("Engineering Culture / Systems Learning",
    "Five Years of Running a Systems Reading Group at Microsoft",
    "T3", "Hacker News (137pts)",
    f"HN 137pts | Author: Foe | https://armaansood.com/posts/systems-reading-group/\nOrganizational approach to sustained technical learning: how Microsoft team ran a systems reading group for 5 years. Paper selection, discussion format, knowledge transfer to broader engineering org.\n{extract_text(i['content'])}",
    ["Systems paper reading group: organizational format", "Sustained technical education at scale", "Paper club as engineering culture building tool"], False)

# HN-14: AEO — Answer Engine Optimization (age=3, 9pts, low engagement but novel concept)
for x in sorted_raw:
    if x.get('age_days') == 3 and 'Answer Engine Optimization' in x.get('title',''):
        i = x; break
add("SEO / AI Search",
    "Answer Engine Optimization — SEO in the Era of AI Search",
    "T3", "Hacker News (9pts)",
    f"HN 9pts | Author: speckx | https://juliasolorzano.com/blog/2026/03/16/answer-engine-optimization/\nNew discipline emerging from AI search engines replacing traditional web search: optimizing content for answer engines (ChatGPT, Perplexity, AI Overviews). Technical SEO now requires answer optimization for AI retrieval.\n{extract_text(i['content'])}",
    ["Answer Engine Optimization (AEO): optimizing for AI search", "Content structure for AI answer retrieval", "SEO pivot: from page ranking to answer selection"], False)

# ============================================================
# T4: Legacy OpenAI blog posts (age 2500-3755 days = 7-10 years old)
# ============================================================

legacy_highlights = {
    2569: ("OpenAI LP", "T4 | Historical: OpenAI's Commercial Structure Innovation"),
    2534: ("OpenAI Five defeats Dota 2 world champions", "T4 | Historical: AI Gaming Milestone"),
    2574: ("Introducing Activation Atlases", "T4 | Historical: Neural Network Interpretability"),
    2576: ("Neural MMO", "T4 | Historical: Multi-Agent Game Environment"),
    2526: ("Generative modeling with sparse transformers", "T4 | Historical: Sparse Transformer Architecture"),
    2554: ("OpenAI Five Finals", "T4 | Historical: OpenAI Five Competition"),
}

for age, (title_kw, label) in legacy_highlights.items():
    for x in sorted_raw:
        if x.get('age_days') == age and title_kw in x.get('title',''):
            add("AI History / OpenAI Legacy",
                x['title'],
                "T4", f"OpenAI Blog ({age} days ago)",
                f"OpenAI Blog | URL: {x.get('url','?')}\nHistorical OpenAI publication from ~{(2026*365-int(age))//365} era. {label}. Full content largely historical/contextual.\n{extract_text(x['content'], 300)}",
                [f"Historical context: {label}"], False)
            break

# ============================================================
# FOCUS TRACE: Check if any recent items mention OpenClaw/Claude Code/Codex/Co-work
# ============================================================
focus_keywords = ['openclaw', 'claude code', 'anthropic', 'codex', 'cowork', 'cursor', 'windsurf', 'copilot']
def matches_focus(text):
    text_lower = text.lower()
    return any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in focus_keywords)
for item in sorted_raw:
    title = item.get('title','')
    content = item.get('content','')
    if matches_focus(title) or matches_focus(content):
        add("Focus Trace / AI Coding Tools",
            f"[FOCUS TRACE] {title}",
            "T0", item.get('source',''),
            f"Focus Trace Alert: OpenClaw/Claude Code/Codex/Co-work related content detected.\nURL: {item.get('url','?')}\n{extract_text(content, 500)}",
            ["OpenClaw/Claude Code/Codex/Co-work dynamic detected"], True)

# ============================================================
# OUTPUT
# ============================================================
output_path = '/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result.json'
backup_path = '/tmp/topic_result_2026-03-24.json'

with open(output_path, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open(backup_path, 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ Wrote {len(results)} items to {output_path}")
print(f"✅ Backed up to {backup_path}")

# Summary by tier
from collections import Counter
tier_counts = Counter(r['tier'] for r in results)
print(f"\nTier distribution: {dict(tier_counts)}")
print("\nSample entries:")
for r in results[:3]:
    print(f"  [{r['tier']}] {r['event_core'][:70]}")
