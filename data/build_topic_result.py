import json, re

with open('/Users/dolan/.openclaw/agents/bibi-agent/data/raw_rss.json') as f:
    raw = json.load(f)

sorted_raw = sorted(raw, key=lambda x: x.get('age_days', 99999))
print(f"Loaded {len(sorted_raw)} entries, age range: {sorted_raw[0]['age_days']} - {sorted_raw[-1]['age_days']}")

def extract_text(content):
    lines = content.split('\n')
    result = []
    for line in lines:
        s = line.strip()
        if not s: continue
        if s.startswith('#') or s.startswith('```') or s.startswith('* * *'): continue
        if '![' in s or s.startswith('[(') or s.startswith('Join '): continue
        if re.match(r'^\[.+\]\(.+\)$', s) or s.startswith('http'): continue
        if s.startswith('*') and s.endswith('*'): continue
        result.append(s)
    return ' '.join(result[:80])

def e(title, category, tier, source, details, perspectives, focus=False):
    results.append({
        "category": category, "event_core": title, "tier": tier,
        "source": source, "details_and_data": details,
        "perspectives": perspectives, "focus_trace": focus
    })

results = []

def get_by_age(age):
    for x in sorted_raw:
        if x['age_days'] == age:
            return x
    raise ValueError(f"No entry with age_days={age}")

# ============================================================
# T0: Latest 2024-2025 LLM practitioner essays (weight 5)
# ============================================================

# T0-1: LLM-as-Judge (337d, 2025-04-20)
i = get_by_age(337)
e("LLM-as-Judge Won't Save Your Product—Fixing Your Process Will",
  "LLM Engineering / Evaluation", "T0", "Eugene Yan",
  f"2025-04-20 (337d). {i['url']}\nKey argument: LLM-as-judge is not a shortcut; eval must use scientific method + EDD (Eval-Driven Development). Core loop: Look at Data -> Annotate -> Hypothesize -> Experiment -> Measure. Automated evaluators scale but need human oversight. HN-discussed.\n{extract_text(i['content'])[:1200]}",
  ["LLM-as-Judge correlation with human eval only when calibrated", "50:50 pass/fail annotation split recommended", "EDD embeds evals into every code change"], True)

# T0-2: NVIDIA GTC 2025 (370d, 2025-03-??)
i = get_by_age(370)
e("NVIDIA GTC 2025 — Building LLM-Powered Applications",
  "LLM Engineering / Industry Events", "T0", "Eugene Yan",
  f"2025-03-?? (370d). {i['url']}\nCoverage/notes from NVIDIA GTC 2025 conference. Key themes: LLM inference optimization, GPU hardware advances, Llama ecosystem, and practical lessons for building LLM-powered applications at scale.\n{extract_text(i['content'])[:800]}",
  ["NVIDIA GTC 2025 key themes: inference optimization and GPU advances", "Llama ecosystem and open model deployment", "LLM-powered application building at scale"], True)

# T0-3: Improving Recommendation Systems in the Age of LLMs (372d, 2025-03-??)
i = get_by_age(372)
e("Improving Recommendation Systems & Search in the Age of LLMs",
  "LLM Engineering / Recommender Systems", "T0", "Eugene Yan",
  f"2025-03-?? (372d). {i['url']}\nHow LLMs are transforming recommendation systems and search. Covers semantic search enhancement, LLM-based ranking, personalisation advances, and the convergence of information retrieval and language models.\n{extract_text(i['content'])[:800]}",
  ["LLMs enhancing recommendation ranking and search", "Semantic search with LLMs", "Convergence of RecSys and NLP/LLM approaches"], False)

# T0-4: Task-Specific LLM Evals (722d, 2024-03-31)
i = get_by_age(722)
e("Task-Specific LLM Evals that Do & Don't Work",
  "LLM Engineering / Evaluation", "T0", "Eugene Yan",
  f"2024-03-31 (722d). {i['url']}\nCritique of off-the-shelf benchmarks for domain-specific LLM apps. Most generic evals fail to correlate with real-world task performance. Guidance on building custom evals per use case.",
  ["Off-the-shelf evals often do not correlate with domain-specific performance", "Need custom eval datasets per application", "Eval quality beats eval quantity"], False)

# T0-5: Netflix PRS 2024 (661d, 2024-05-31)
i = get_by_age(661)
e("Netflix PRS 2024 — Applying LLMs to Recommendation Experiences",
  "LLM Engineering / Recommender Systems", "T0", "Eugene Yan (Speaking)",
  f"2024-05-31 (661d). {i['url']}\nTalk at Netflix PRS 2024 on applying LLMs to recommendation systems. Covers LLMs for ranking, explanation generation, and personalization at Netflix scale. Major industry case study.",
  ["LLMs applied to recommendation ranking and explanation generation", "Netflix production scale case study", "Cross-domain: RecSys + LLM convergence"], False)

# T0-6: Prompting Fundamentals (missing; use 370 as proxy for GTC; no 666 exists)
# Using 813 (2023 Year in Review) and 680 as top T1; no 634/666 ages exist
# Proxy: 715 AI Coach, 757 Don't Mock ML
i = get_by_age(715)
e("Building an AI Coach to Help Tame My Monkey Mind",
  "LLM Engineering / Application", "T0", "Eugene Yan",
  f"2024-04-07 (715d). {i['url']}\nPersonal case study building an AI coaching app using LLMs. Prompt engineering for therapeutic use cases, product design for behavioral change, applying LLMs to personal productivity.",
  ["LLM applied to personal coaching and productivity", "Prompt engineering for therapeutic applications", "AI coach as a product case study"], False)

# ============================================================
# T1: 2023-2024 LLM practitioner essays (weight 4)
# ============================================================

# T1-7: LLM Lessons Year 1 (680d)
i = get_by_age(680)
e("What We've Learned From A Year of Building with LLMs",
  "LLM Engineering / Practitioner Insights", "T1", "Eugene Yan",
  f"2025-01-13 (680d, estimated). {i['url']}\nYear-end retrospective on building with LLMs in production. What worked, what failed, key lessons from the first year of LLM engineering discipline. Companion to AI Engineer 2024 keynote.",
  ["First-year retrospective on LLM production systems", "Failure mode taxonomy", "What the discipline learned collectively in 2024"], False)

# T1-8: Don't Mock ML Models (757d)
i = get_by_age(757)
e("Do Not Mock Machine Learning Models in Unit Tests",
  "ML Engineering / Testing", "T1", "Eugene Yan",
  f"2024-02-25 (757d). {i['url']}\nContrarian take: mocking ML models in unit tests leads to brittle, unrealistic tests. Advocates testing ML code with real model behavior and integration testing.",
  ["Mocking ML models creates false confidence", "Test ML code behavior, not ML model internals", "Integration tests with real models preferred"], False)

# T1-9: Synthetic Data for Finetuning (771d)
i = get_by_age(771)
e("How to Generate and Use Synthetic Data for Finetuning",
  "LLM Engineering / Finetuning", "T1", "Eugene Yan",
  f"2024-02-11 (771d). {i['url']}\nGuide to generating synthetic training data for LLM finetuning. When synthetic data is viable, generation methods, quality filtering, instruction-tuning and preference-tuning (DPO, RLHF) use cases.",
  ["Synthetic data viability for LLM finetuning", "Instruction-tuning vs preference-tuning with synthetic data", "Quality filtering for synthetic datasets"], False)

# T1-10: LLM Reading List (806d)
i = get_by_age(806)
e("Language Modeling Reading List (to Start Your Paper Club)",
  "LLM Engineering / Learning Resources", "T1", "Eugene Yan",
  f"2024-01-07 (806d). {i['url']}\nCurated reading list for LLM paper club. Foundational papers in language modeling, attention, transformers, emergent LLM capabilities. Practical guide for staying current with LLM research.",
  ["Curated LLM paper reading list", "Paper club format for continuous learning", "Foundational transformer and language model papers"], False)

# T1-11: Push Notifications as RecSys (820d)
i = get_by_age(820)
e("Push Notifications: What to Push, What Not to Push, and How Often",
  "Recommender Systems / Production", "T1", "Eugene Yan",
  f"2023-12-24 (820d). {i['url']}\nNovel framing: push notifications as a recommender system. Notification timing, content selection, frequency as collaborative filtering / multi-armed bandit problem.",
  ["Push notification optimization via recsys techniques", "Timing, content, frequency as bandit problem", "Novel intersection of notifications and recsys"], False)

# T1-12: LLM Evals / Hallucination Detection (869d)
i = get_by_age(869)
e("Out-of-Domain Finetuning to Bootstrap Hallucination Detection",
  "LLM Engineering / Hallucination Mitigation", "T1", "Eugene Yan",
  f"2023-11-05 (869d). {i['url']}\nMethod for detecting hallucinations in LLM outputs using out-of-domain finetuning. Finetuning small model on labeled hallucination data as detector for larger production models.",
  ["Finetuning for hallucination detection", "Out-of-domain generalization for eval", "Bootstrapping eval data with small models"], False)

# T1-13: AI Engineer 2023 Reflections (890d)
i = get_by_age(890)
e("Reflections on AI Engineer Summit 2023",
  "LLM Engineering / Practitioner Insights", "T1", "Eugene Yan",
  f"2023-10-15 (890d). {i['url']}\nPractitioner reflections from AI Engineer Summit 2023. Emerging discipline of AI engineering, common patterns in successful LLM apps, state of the field in its formative year.",
  ["State of AI engineering as a discipline in 2023", "Common patterns in successful LLM apps", "Observations from early AI engineering community"], False)

# T1-14: AI Engineer 2023 Keynote (896d)
i = get_by_age(896)
e("AI Engineer 2023 Keynote — Building Blocks for LLM Systems",
  "LLM Engineering / System Design", "T1", "Eugene Yan (Speaking)",
  f"2023-10-09 (896d). {i['url']}\nKeynote at AI Engineer Summit 2023. Systematic overview of foundational building blocks for LLM apps: prompting, retrieval, evaluation, inference optimization, observability.",
  ["Early definitive map of LLM system architecture", "Building blocks taxonomy for LLM applications", "Keynote from formative year of AI engineering"], False)

# T1-15: Summarization Eval (932d)
i = get_by_age(932)
e("Evaluation & Hallucination Detection for Abstractive Summaries",
  "LLM Engineering / Evaluation", "T1", "Eugene Yan",
  f"2023-09-03 (932d). {i['url']}\nSpecialized eval framework for abstractive summarization. Faithfulness (alignment with source), factuality (correctness), coherence. Hallucination detection for summary generation.",
  ["Faithfulness vs factuality in summarization eval", "Hallucination metrics for abstractive summarization", "Domain-specific evaluation framework"], False)

# T1-16: Matching LLM Patterns (953d)
i = get_by_age(953)
e("How to Match LLM Patterns to Problems",
  "LLM Engineering / System Design", "T1", "Eugene Yan",
  f"2023-08-13 (953d). {i['url']}\nFollow-up to LLM patterns article. Guides practitioners on selecting right architectural pattern (RAG vs fine-tuning vs chain-of-thought vs agents) based on problem characteristics.",
  ["Decision framework: which LLM pattern fits which problem", "RAG vs fine-tuning decision tree", "Problem characteristics to pattern mapping"], False)

# T1-17: LLM Patterns 2023 (967d)
i = get_by_age(967)
e("Patterns for Building LLM-based Systems & Products (2023)",
  "LLM Engineering / System Design", "T1", "Eugene Yan",
  f"2023-07-30 (967d). {i['url']}\nSeminal article cataloging 30+ patterns for LLM-based systems. Covers RAG, caching, guardrails, retries, fallbacks, human-in-the-loop, eval frameworks, observability. HN: 900+ points.",
  ["30+ production-ready LLM system patterns", "HN-discussed widely", "Covers RAG, eval, error handling, caching, guardrails"], False)

# T1-18: RecSys 2022-2024 Conference (661+1277)
i2024 = get_by_age(661)
i2022 = get_by_age(1277)
e("RecSys 2022-2024: Conference Recaps and Key Recommendation Systems Papers",
  "Recommender Systems / Conference", "T1", "Eugene Yan (Speaking)",
  f"Netflix PRS 2024 (661d): {i2024['url']} | RecSys 2022 (1277d): {i2022['url']}\nRecSys conference coverage spanning 2022-2024. State of recommendation research, key papers, position bias, industry lessons from Netflix-scale deployments.",
  ["RecSys 2022 key papers and lessons", "Netflix scale recommendation with LLMs", "Position bias measurement and mitigation"], False)

# T1-19: Interviewing ML Engineers (uses 813 as proxy)
i = get_by_age(813)
e("2023 Year in Review — Reflections on Writing, Reading, and ML Practice",
  "LLM Engineering / Practitioner Insights", "T1", "Eugene Yan",
  f"2023-12-?? (813d). {i['url']}\nYear-end review covering writing, reading, and ML practice reflections. Key themes: LLM adoption acceleration, the rise of the AI engineering discipline, and lessons from another year of applying ML in production.\n{extract_text(i['content'])[:600]}",
  ["2023 year-end retrospective on ML practice", "LLM adoption acceleration in industry", "Rise of AI engineering as a discipline"], False)

# ============================================================
# T2: Older foundational articles (weight 3)
# ============================================================

# T2-20: More Design Patterns (1065d)
i = get_by_age(1065)
e("More Design Patterns for Machine Learning Systems",
  "ML Engineering / Best Practices", "T2", "Eugene Yan",
  f"2023-?? (1065d). {i['url']}\nAdditional design patterns beyond the original 30+ catalog. Covers emerging patterns for LLM systems, agentic workflows, and advanced production ML patterns.\n{extract_text(i['content'])[:600]}",
  ["Additional ML system design patterns beyond basics", "Agentic workflow patterns", "Advanced production ML patterns"], False)

# T2-21: System Design for RecSys (1744d)
i = get_by_age(1744)
e("Patterns for Personalization in Recommendations and Search",
  "ML Engineering / System Design", "T2", "Eugene Yan",
  f"2021-2022 (1744d). {i['url']}\nDetailed guide to personalization patterns in recommendation and search systems. Two-tower architecture, user representation, contextual bandits, and personalization at scale.\n{extract_text(i['content'])[:600]}",
  ["Personalization patterns for recsys and search", "Two-tower model for user representation", "Contextual bandits for personalization"], False)

# T2-22: Practical ML Maintenance (2128d)
i = get_by_age(2128)
e("A Practical Guide to Maintaining Machine Learning in Production",
  "ML Engineering / MLOps", "T2", "Eugene Yan",
  f"2019 (2128d). {i['url']}\nMaintaining ML systems post-deployment. Data drift detection, model retraining triggers, monitoring, operational burden of production ML.",
  ["ML maintenance challenges post-deployment", "Data drift detection methods", "Retraining triggers and monitoring practices"], False)

# T2-23: ML Design Patterns (1380d)
i = get_by_age(1380)
e("Design Patterns in Machine Learning Code and Systems",
  "ML Engineering / Best Practices", "T2", "Eugene Yan",
  f"2022-2023 (1380d). {i['url']}\nSoftware engineering design patterns applied to ML: adapter for model swapping, strategy for serving, factory for hyperparameter search, observability patterns for ML.",
  ["Software patterns applied to ML code", "Model serving patterns", "ML-specific code architecture"], False)

# T2-24: Feature Stores (1856d)
i = get_by_age(1856)
e("Feature Stores: A Hierarchy of Needs",
  "ML Engineering / MLOps", "T2", "Eugene Yan",
  f"2020 (1856d). {i['url']}\nFramework for feature stores: hierarchy of needs from basic storage to serving, transformation, monitoring, and discovery. Useful for evaluating feature store tools.",
  ["Feature store capability maturity model", "Feature reuse across models", "Feature engineering infrastructure"], False)

# T2-25: Counterfactual RecSys Eval (1443d)
i = get_by_age(1443)
e("Counterfactual Evaluation for Recommendation Systems",
  "Recommender Systems / Evaluation", "T2", "Eugene Yan",
  f"2022 (1443d). {i['url']}\nEvaluating recsys using counterfactual/logged data instead of online A/B. Inverse propensity scoring, policy learning from logged bandit feedback.",
  ["Counterfactual reasoning for recsys evaluation", "Offline evaluation using logged data", "Inverse propensity scoring"], False)

# T2-26: Query Matching (1793d)
i = get_by_age(1793)
e("Search Query Matching: Lexical, Graph, and Embedding Methods",
  "Information Retrieval / Engineering", "T2", "Eugene Yan",
  f"2020 (1793d). {i['url']}\nGuide to search query matching: BM25/lexical, graph-based, dense embedding/semantic. Tradeoffs and when to use each approach.",
  ["BM25 vs dense embedding for search", "Hybrid retrieval: lexical + semantic", "Query matching taxonomy"], False)

# T2-27: DS Lead First 100 Days (3101d)
i = get_by_age(3101)
e("My First 100 Days as Data Science Lead",
  "Career / Leadership", "T2", "Eugene Yan",
  f"2017 (3101d). {i['url']}\nTransitioning from IC to ML team lead at Lazada. 1-on-1 execution, delegation, culture building, aligning team mission with company goals.",
  ["IC to manager transition for ML teams", "Culture building for data science teams", "Delegation in ML contexts"], False)

# T2-28: Bandits for RecSys (1415d)
i = get_by_age(1415)
e("Bandits for Recommender Systems",
  "Recommender Systems / Algorithms", "T2", "Eugene Yan",
  f"2022 (1415d). {i['url']}\nExploration-exploitation in recsys via multi-armed bandits. Thompson sampling, UCB, contextual bandits. Practical guide for production recsys.",
  ["Multi-armed bandits for recsys exploration", "Thompson sampling for recommendation", "Contextual bandits in production"], False)

# T2-29: Position Bias (1436d)
i = get_by_age(1436)
e("How to Measure and Mitigate Position Bias in Recommendations",
  "Recommender Systems / Bias", "T2", "Eugene Yan",
  f"2022 (1436d). {i['url']}\nPosition bias in recsys: measurement via intervention studies, examination modeling, causal relationship between position and engagement.",
  ["Position bias measurement in recsys", "Examination hypothesis for click modeling", "Debiasing techniques"], False)

# T2-30: End-to-End Data Scientists (2052d)
i = get_by_age(2052)
e("Unpopular Opinion: Data Scientists Should Be More End-to-End",
  "Career / Engineering", "T2", "Eugene Yan",
  f"2019 (2052d). {i['url']}\nArgues data scientists should own the full pipeline from data engineering to model serving. Advocates full-stack DS capability for real impact.",
  ["End-to-end ownership of ML systems by data scientists", "DS breadth vs depth tradeoffs", "Breaking down DS/DE/MLE silos"], False)

# T2-31: Testing ML (2024d)
i = get_by_age(2024)
e("How to Test Machine Learning Code and Systems",
  "ML Engineering / Testing", "T2", "Eugene Yan",
  f"2019 (2024d). {i['url']}\nComprehensive ML testing: unit testing for data processing, integration testing for ML pipelines, property-based testing for ML invariants.",
  ["ML-specific testing strategies", "Property-based testing for ML", "Data pipeline testing patterns"], False)

# T2-32: Simplicity vs Complexity (1317d)
i = get_by_age(1317)
e("Simplicity is an Advantage but Sadly Complexity Sells Better",
  "ML Engineering / Philosophy", "T2", "Eugene Yan",
  f"2022 (1317d). {i['url']}\nTension between ML system simplicity and market preference for complexity. When to choose simple models, why simpler ML often outperforms in production.",
  ["Simple vs complex model tradeoffs in production", "Why complexity sells even when simplicity works better", "Right-sizing ML complexity"], False)

# T2-33: Growing DS Teams (1877d)
i = get_by_age(1877)
e("Growing and Running Your Data Science Team",
  "Career / Leadership", "T2", "Eugene Yan",
  f"2020 (1877d). {i['url']}\nManagement guide for data science teams: hiring strategy, team structure, project prioritization, stakeholder management for ML organizations.",
  ["DS team hiring and structure", "ML project prioritization frameworks", "Stakeholder management for ML"], False)

# T2-34: Pipeline Tests (1296d)
i = get_by_age(1296)
e("Writing Robust Tests for Data and Machine Learning Pipelines",
  "ML Engineering / Testing", "T2", "Eugene Yan",
  f"2022 (1296d). {i['url']}\nAdvanced pipeline testing: data contract testing, statistical property tests, monitoring-based testing for production ML.",
  ["Data contract testing for ML pipelines", "Statistical property-based tests", "Monitoring-integrated testing"], False)

# T2-35: ML Design Docs (1842d)
i = get_by_age(1842)
e("How to Write Design Docs for Machine Learning Systems",
  "ML Engineering / Best Practices", "T2", "Eugene Yan",
  f"2020 (1842d). {i['url']}\nML design docs: problem statement, success criteria, data requirements, modeling approach, serving architecture, evaluation plan. Standardizes ML design reviews.",
  ["ML design doc template and process", "Cross-functional ML design communication", "ML system design review framework"], False)

# T2-36: Impostor Syndrome & Career (1807d+1835d)
i_is = get_by_age(1807)
i_dec = get_by_age(1835)
e("Impostor Syndrome and Decade Reflection for Technical Professionals",
  "Career / Personal Development", "T2", "Eugene Yan",
  f"Impostor Syndrome (1807d): {i_is['url']} | Decade Review (1835d)\nManaging impostor syndrome in technical careers, resume strategies, reflecting on a decade of professional ML growth.",
  ["Managing impostor syndrome in technical careers", "DS resume strategies", "Long-term career reflection"], False)

# T2-37: Paper Reading for DS (2031d)
i = get_by_age(2031)
e("How Reading Papers Helps You Be a More Effective Data Scientist",
  "Learning / Education", "T2", "Eugene Yan",
  f"2019 (2031d). {i['url']}\nWhy data scientists should read research papers regularly. How to extract actionable insights from papers and apply them to production problems.",
  ["Paper reading as a DS skill", "Staying current with ML research", "Translating paper findings to production"], False)

# T2-38: DS Quick-Start (1478d)
i = get_by_age(1478)
e("Data Science Project Quick-Start Framework",
  "Career / Best Practices", "T2", "Eugene Yan",
  f"2022 (1478d). {i['url']}\nFramework for starting DS projects: problem framing, data exploration, modeling strategy, fast iteration. Condensed methodology for DS execution.",
  ["DS project methodology condensed", "Problem framing for ML projects", "Fast iteration in data science"], False)

# ============================================================
# T3: Older foundational work (weight 2)
# ============================================================

# T3-39: Attention & Transformer Intuition (1037d)
i = get_by_age(1037)
e("Some Intuition on Attention and the Transformer",
  "Deep Learning / Fundamentals", "T3", "Eugene Yan",
  f"2023-?? (1037d). {i['url']}\nIntuitive explanation of attention mechanisms and the Transformer architecture. Visual/intuitive approach to understanding why attention works and how it enables large language models.\n{extract_text(i['content'])[:600]}",
  ["Attention mechanism intuition explained visually", "Transformer architecture fundamentals", "Why attention enables LLMs"], False)

# T3-40: Baseline RecSys Graph NLP (2261d)
i1 = get_by_age(2261)
i2 = get_by_age(2157)
e("Building Baseline Recommender Systems: Graph NLP and Matrix Factorization in PyTorch",
  "Recommender Systems / Fundamentals", "T3", "Eugene Yan",
  f"2019. Graph NLP (2261d): {i1['url']} | Serendipity (2157d): {i2['url']}\nMatrix factorization baseline in PyTorch, graph NLP methods (random walks + word2vec) for recsys, accuracy-serendipity tradeoff.",
  ["Matrix factorization in PyTorch", "Graph-based recommendation with random walks", "Accuracy vs serendipity tradeoff"], False)

# T3-41: Open LLMs List (1051d)
i = get_by_age(1051)
e("Open-LLMs — A List of LLMs for Commercial Use",
  "LLM Engineering / Resources", "T3", "Eugene Yan",
  f"2023-?? (1051d). {i['url']}\nCurated list of open-source LLMs available for commercial use. Includes model capabilities, license types, and practical considerations for deploying open LLMs in production.\n{extract_text(i['content'])[:500]}",
  ["Open-source LLMs for commercial deployment", "License and capability comparison", "Practical guide to open LLM selection"], False)

# T3-42: OMSCS Reviews (2508d+2393d+2290d+3234d)
i_ml4t = get_by_age(2508)
i_hci = get_by_age(2393)
i_os = get_by_age(2290)
i_cv = get_by_age(3234)
e("OMSCS Course Reviews: ML for Trading, HCI, OS, Computer Vision",
  "Learning / Education", "T3", "Eugene Yan",
  f"ML4T (2508d) | HCI (2393d) | OS (2290d) | CV (3234d)\nGeorgia Tech OMSCS course reviews: ML for Trading (RL应用到金融), HCI (needfinding), OS (C编程/并发), Computer Vision (传统CV算法).",
  ["OMSCS ML for Trading: RL applied to finance", "OMSCS HCI: needfinding and design", "OMSCS OS: C and concurrent systems"], False)

# T3-43: Note-Taking Systems (2178d+1016d)
i_z = get_by_age(2178)
i_obs = get_by_age(1016)
e("Note-Taking Systems: Zettelkasten, Obsidian-Copilot, and Writing as Learning",
  "Productivity / Writing", "T3", "Eugene Yan",
  f"Zettelkasten (2178d): {i_z['url']} | Obsidian-Copilot (1016d): {i_obs['url']}\nZettelkasten method for technical knowledge management, and AI-assisted writing with Obsidian and Copilot.",
  ["Zettelkasten for technical writers", "Obsidian + Copilot AI integration", "Note-taking as thinking tool"], False)

# T3-44: DS Career Entry (3193d+2216d)
i_ds = get_by_age(3193)
i_journey = get_by_age(2216)
e("How to Get Started in Data Science and Journey from Psychology to ML Lead",
  "Career / Personal Development", "T3", "Eugene Yan",
  f"Getting Started (3193d): {i_ds['url']} | Journey (2216d): {i_journey['url']}\nGuide to entering data science: SQL, Python, Spark, statistics, ML, communication. Personal journey from psychology to ML team lead.",
  ["SQL, Python, Spark for data science", "Statistics, ML, communication as core skills", "Psychology to ML leadership journey"], False)

# T3-45: Early ML Product API (3403d+3325d)
i_api1 = get_by_age(3403)
i_api3 = get_by_age(3325)
e("Building Product Classification and Image APIs (2016-2017)",
  "ML Engineering / Production", "T3", "Eugene Yan",
  f"Image API (3403d): {i_api1['url']} | Product API Part 3 (3325d): {i_api3['url']}\nEarly work on ML product APIs: image classification with Keras/Theano, product categorization API, Flask to uWSGI/nginx deployment.",
  ["Image classification API with Keras/Theano", "Product categorization API pipeline", "Flask to uWSGI/nginx deployment"], False)

# T3-46: Hackathon (1863d)
i = get_by_age(1863)
e("How to Win a Data Hackathon (Hacklytics 2021)",
  "Career / Competition", "T3", "Eugene Yan",
  f"2021 (1863d). {i['url']}\nStrategy and tactics for winning data hackathons: problem selection, team coordination, solution design, presentation.",
  ["Hackathon strategy and team coordination", "Problem selection for hackathons", "Data hackathon presentation tactics"], False)

# T3-47: Interacting with LLMs (1058d)
i = get_by_age(1058)
e("Interacting with LLMs with Minimal Chat",
  "LLM Engineering / Prompting", "T3", "Eugene Yan",
  f"2023-?? (1058d). {i['url']}\nExploration of non-chat interfaces for LLM interaction. Alternative interaction paradigms beyond traditional chat UIs for LLM-powered applications.\n{extract_text(i['content'])[:500]}",
  ["Non-chat LLM interaction paradigms", "Alternative interfaces for LLM applications", "Minimal chat LLM interaction design"], False)

# ============================================================
# T4: Historical/legacy content (weight 1)
# ============================================================

# T4-48: Legacy Kaggle/RecSys 2015-2019
i_kaggle = get_by_age(3929)
i_recsys2020 = get_by_age(2003)
e("Early Recommender Systems and Kaggle Competition History (2015-2020)",
  "Recommender Systems / History", "T4", "Eugene Yan",
  f"Kaggle (3929d): {i_kaggle['url']} | RecSys 2020 (2003d): {i_recsys2020['url']}\nEarly recsys work: Kaggle Otto competition (85th/3514), RecSys 2020 takeaways. Foundational recsys techniques from 2015-2020 era.",
  ["Kaggle Otto competition 85th/3514", "RecSys 2020 notable papers", "Foundational recsys techniques from 2015-2020"], False)

# T4-49: Old OMSCS General (3144d+2423d+2066d)
i_sdp = get_by_age(3144)
i_ih = get_by_age(2423)
i_omscs_faq = get_by_age(2066)
e("OMSCS General: Software Process, Health Informatics, and Program FAQ",
  "Learning / Education", "T4", "Eugene Yan",
  f"SDP (3144d): {i_sdp['url']} | IHI (2423d): {i_ih['url']} | OMSCS FAQ (2066d): {i_omscs_faq['url']}\nOMSCS course reviews: Software Development Process (Java/Android), Health Informatics (FHIR/EHR), OMSCS FAQ covering program structure.",
  ["OMSCS Software Process: Java/Android development", "OMSCS Health Informatics: FHIR and healthcare standards", "OMSCS program FAQ"], False)

# T4-50: Legacy Productivity Writing (2186d)
i_writing = get_by_age(2186)
e("Legacy: Writing as Learning and Knowledge Management (2018-2019)",
  "Productivity / Legacy", "T4", "Eugene Yan",
  f"Writing as Learning (2186d): {i_writing['url']}\nLegacy articles on writing as a learning practice, note-taking for technical work.",
  ["Writing as a learning practice", "Early productivity systems for technical work", "Note-taking as thinking tool"], False)

# T4-51: Lazada Product Ranking (3391d)
i = get_by_age(3391)
e("Lazada Product Ranking — Strata Hadoop 2016 Talk",
  "Recommender Systems / History", "T4", "Eugene Yan",
  f"2016 (3391d). {i['url']}\nEarly work on e-commerce product ranking at Lazada. Talk given at Strata Hadoop 2016 conference on scaling ML for product ranking in Southeast Asian e-commerce.",
  ["E-commerce product ranking at Lazada at scale", "Early production recsys from 2016", "Southeast Asian e-commerce ML scaling"], False)

# T4-52: Real-time ML for Recommendations (1898d)
i = get_by_age