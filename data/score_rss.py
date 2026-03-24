# -*- coding: utf-8 -*-
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('/Users/dolan/.openclaw/agents/bibi-agent/data/raw_rss.json', encoding='utf-8') as f:
    raw_items = json.load(f)

historical = set()
try:
    for item in json.load(open('/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result_2026-03-23.json', encoding='utf-8')):
        historical.add(item.get('event_core', '').lower())
except: pass

SKIP = {
    'introducing openai', 'team++', 'openai gym beta', 'welcome, pieter and shivon',
    'team update', 'adversarial training methods', 'weight normalization',
    'generative models', 'openai technical goals', 'concrete ai safety problems',
    'special projects', 'machine learning unconference', 'infrastructure for deep learning',
    'report from the self-organizing', 'semi-supervised knowledge transfer',
    'transfer from simulation', 'extensions and limitations of the neural gpu',
    'variational lossy autoencoder', 'rlo7', "conway's game of life",
    'side-effectful expressions in c', 'an unsolicited guide to being a researcher',
    'finding all regex matches', 'can you get root with only a cigarette lighter',
    'general motors is assisting', 'dune3d: a parametric 3d cad', 'digs: ios app',
    'is it a pint', 'collaboration is bullshit', 'next-generation electricity',
    'two pilots dead', 'us and totalenergies reach', 'bets on us-iran ceasefire',
    'migrating to the eu', 'chat gpt 5.2 cannot explain', 'local stack archived',
    'an incoherent rust',
}

INSIGHTS = {
    'iPhone 17 Pro Demonstrated Running a 400B LLM': 'iPhone 17 Pro演示本地运行400B参数LLM，端侧AI推理里程碑验证，边缘部署新阶段',
    'Walmart: ChatGPT checkout converted 3x worse than website': 'Walmart测试显示ChatGPT Checkout转化率仅为网站1/3，AI电商落地遭遇冷现实检验',
    'AI Agents Can Already Autonomously Perform Experimental High Energy Physics': 'AI Agent成功自主完成高能物理分析全流程，科研自动化进入实用阶段，物理学家角色被重新定义',
    'VideoSeek: Long-Horizon Video Agent with Tool-Guided Seeking': 'VideoSeek用93%更少帧数超越GPT-5，视频理解效率突破性提升，主动推理框架成关键',
    'Evolving Jailbreaks: Automated Multi-Objective Long-Tail Attacks on Large Language Models': '进化算法自动生成多目标长尾越狱攻击，LLM安全评估进入系统性对抗时代',
    'Trivy under attack again: Widespread GitHub Actions tag compromise secrets': 'Trivy遭GitHub Actions供应链攻击，开发者工具链安全警钟再响',
    'How I\'m Productive with Claude Code': '开发者详述Claude Code提效实践，AI编程工具已进入生产成熟期而非实验阶段',
    'Flipper Zero gets an AI upgrade': '黑客工具Flipper Zero集成AI能力，硬件安全研究工具平民化普及',
    'AI Risks "Hypernormal" Science': 'AI生成超常态科学知识可能污染人类科学基础，真伪鉴别成科研新挑战',
    'I built an AI receptionist for a mechanic shop': '独立开发者为修理厂构建AI接待员，垂直行业AI落地成本门槛已降至数千美元',
    'GitHub appears to be struggling with measly three nines availability': 'GitHub可用性持续危机，AI编码工具依赖云基础设施的脆弱性暴露',
    'America tells private firms to "hack back"': '美国授权私人企业黑客反击网络攻击，网络战规则被改写引发法律争议',
    'Autoresearch on an old research idea': '自动化研究框架Eclip让科学家重拾被忽视的研究想法，科研AI加速知识发现',
    'Bombadil: Property-based testing for web UIs': 'Bombadil将属性化测试引入Web UI自动化，测试覆盖度与效率双突破',
    'BIO: The Bao I/O Coprocessor': 'Bunnie Huang设计BIO I/O协处理器，硬件极客文化与AI边缘计算的新交汇',
    'LumosX: Relate Any Identities with Their Attributes for Personalized Video Generation': 'LumosX实现多主体身份-属性对齐的个性化视频生成，ID一致性难题突破',
    'The Robot\'s Inner Critic: Self-Refinement of Social Behaviors through VLM-based Replanning': 'VLM自批评驱动机器人社交行为自进化，跨平台通用框架首次实现',
    'An Agentic Multi-Agent Architecture for Cybersecurity Risk Management': '六Agent网络安全评估系统达CISSP 85%准确率，15分钟完成传统数周工作，自动化网安评估商用化',
    'Semantic Token Clustering for Efficient Uncertainty Quantification in Large Language Models': '语义Token聚类实现单次推理LLM不确定性量化，计算开销降低一个数量级',
    'Measuring Faithfulness Depends on How You Measure: Classifier Sensitivity in LLM Chain-of-Thought Evaluation': 'LLM CoT忠实度评估高度依赖分类器选择，同一模型排名可被完全逆转',
    'Chain-of-Adaptation: Surgical Vision-Language Adaptation with Reinforcement Learning': 'CoA通过强化学习手术式适配VLM，保持通用能力同时获取领域专业知识',
    'Adaptive Greedy Frame Selection for Long Video Understanding': '自适应贪婪帧选择将视频FPS压缩10倍同时提升精度，长视频理解效率革命',
    'From Masks to Pixels and Meaning: A New Taxonomy, Benchmark, and Metrics for VLM Image Tampering': 'VLM图像篡改检测从Mask走向像素级语义定位，检测标准新范式确立',
    'Improving Generalization on Cybersecurity Tasks with Multi-Modal Contrastive Learning': '多模态对比学习将文本知识迁移至载荷分类，网络安全ML泛化难题新解法',
    'Design-OS: A Specification-Driven Framework for Engineering System Design with a Control-Systems Design Case': 'Design-OS将规格驱动工作流引入物理工程设计，AI从解决方案生成渗透到问题定义阶段',
    'Learning Dynamic Belief Graphs for Theory-of-mind Reasoning': '动态信念图谱赋能LLM心智理论推理，高风险决策场景AI理解力提升',
    'Enhancing Hyperspace Analogue to Language (HAL) Representations via Attention-Based Pooling': 'HAL模型引入注意力池化机制，文本分类精度提升6.74%，语义可解释性同步增强',
}

def hn(item):
    if item.get('source') != 'Hacker News': return 0
    try: return int(item['content'].split('Score:')[1].split('points')[0].strip())
    except: return 0

def is_dup(title):
    tl = title.lower()
    if tl in historical: return True
    for h in historical:
        if len(h) > 8 and (h in tl or tl in h): return True
    return False

def kw(text, kws):
    tl = text.lower()
    return sum(1 for k in kws if k in tl)

def score_item(item):
    title = item.get('title', '')
    source = item.get('source', '')
    content = item.get('content', '')
    url = item.get('url', '')
    age = item.get('age_days', 0)

    if age > 500: return None
    tl = title.lower()
    if any(s in tl for s in SKIP): return None

    is_new = not is_dup(title)
    recency = max(0, 1 - age / 14.0)
    h = hn(item)
    txt = (title + ' ' + content[:500]).lower()

    # AI keyword density
    AI = ['ai','llm','gpt','agent','vlm','model','neural','deep learn',
           'vision-language','robot','autonomous','physics','arxiv','claude',
           'jailbreak','uncertainty','reasoning','belief','semantic','checkout',
           'receptionist','cybersecurity','security','attack','benchmark','video']
    ai = kw(txt, AI)

    T_KW = ['arxiv','agent','llm','vlm','model','neural','vision-language',
             'robot','physics','jailbreak','uncertainty','reasoning','semantic',
             'video','fine-tun','framework','benchmark','contrastive','multi-modal',
             'attention','embedding','generative','property-based']
    L_KW = ['agent','autonomous','physics','reasoning','llm','model','breakthrough',
              'evolution','science','benchmark','taxonomy','framework','generative','foundation']
    I_KW = ['github','checkout','shop','deploy','claude code','autonomous','robot','cybersecurity']
    D_KW = ['jailbreak','risk','hack','attack','threat','safety','hypernormal','supply chain','fail']

    # Radar (1-10)
    tech = min(10, 3 + kw(txt, T_KW) + (5 if source=='arXiv AI/ML' else 0) + (2 if ai>=2 else 0))
    longterm = min(10, 4 + kw(txt, L_KW) + (4 if source=='arXiv AI/ML' else 0) + (2 if ai>=2 else 0))
    industry = min(10, 3 + kw(txt, I_KW) + (ai >= 2 and 2 or 0))
    invest = min(10, 4 + min(h//60, 4) + int(recency*2))
    debate = min(10, 2 + kw(txt, D_KW) + (2 if 'security' in txt or 'walmart' in txt else 0))
    china = min(10, 1 + kw(txt,['china','chinese','bytedance','alibaba','tencent','baidu','huawei','taiwan'])*2)

    radar = {'tech':tech,'industry':industry,'invest':invest,'debate':debate,'china':china,'longterm':longterm}

    # Base weight
    if source == 'arXiv AI/ML':
        bw = 6
    elif h > 0:
        bw = 3 + min(h/80, 4)
    else:
        bw = 3

    weight = round(bw * (1 + recency*0.4) * (1 + (0.3 if is_new else 0)), 2)

    # Composite ranking score
    composite = (
        radar['tech'] * 1.5 +   # tech most important
        radar['longterm'] * 1.3 +
        radar['industry'] * 1.0 +
        radar['invest'] * 0.5 +  # reduce weight of pure engagement
        radar['debate'] * 0.8 +
        radar['china'] * 0.3
    ) / 6.3 * weight * (1.3 if is_new else 1.0) * (1 + ai*0.15)

    insight = INSIGHTS.get(title, title[:50])

    return {
        'title': title, 'source': source, 'url': url,
        'radar': radar, 'weight': weight,
        'is_new': is_new, 'key_insight': insight,
        '_h': h, '_age': age, '_ai': ai,
        '_comp': composite
    }

scored = [s for s in (score_item(i) for i in raw_items) if s]
scored.sort(key=lambda x: -x['_comp'])

print(f"Total: {len(scored)}, new: {sum(1 for s in scored if s['is_new'])}")
print("\n=== TOP 25 ===")
for i, s in enumerate(scored[:25]):
    r = s['radar']
    print(f"{i+1:2d}. [{s['source'][:15]:15}] w={s['weight']:.1f} hn={s['_h']:3d} ai={s['_ai']} T{r['tech']}I{r['industry']}V{r['invest']}D{r['debate']}C{r['china']}L{r['longterm']} | {s['title'][:55]}")

top15 = []
for s in scored[:15]:
    title = s['title']
    insight = s['key_insight']
    summary = f"{title}。{insight}"[:100]
    top15.append({
        'title': title,
        'summary': summary,
        'source': s['source'],
        'url': s['url'],
        'radar': s['radar'],
        'weight': s['weight'],
        'is_new': s['is_new'],
        'key_insight': insight
    })

for p in ['/Users/dolan/.openclaw/agents/bibi-agent/data/topic_result.json',
           '/tmp/topic_result_2026-03-24.json']:
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(top15, f, ensure_ascii=False, indent=2)
print(f"\nWritten {len(top15)} items.")
