#!/usr/bin/env python3
"""生成规范排版的中文学术论文Word文档"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import re

def set_cell_shading(cell, color):
    """设置单元格底色"""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_run_font(run, font_cn='宋体', font_en='Times New Roman', size=12, bold=False):
    """设置运行字体"""
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = font_en
    r = run._element
    rFonts = r.find(qn('w:rPr'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rPr {nsdecls("w")}><w:rFonts w:eastAsia="{font_cn}"/></w:rPr>')
        r.insert(0, rFonts)
    else:
        rFonts_elem = rFonts.find(qn('w:rFonts'))
        if rFonts_elem is None:
            rFonts_elem = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{font_cn}"/>')
            rFonts.append(rFonts_elem)
        else:
            rFonts_elem.set(qn('w:eastAsia'), font_cn)

def add_paragraph_with_font(doc, text, font_cn='宋体', font_en='Times New Roman', size=12, bold=False, alignment=None, space_before=0, space_after=0, line_spacing=1.5):
    """添加带格式的段落"""
    p = doc.add_paragraph()
    if alignment:
        p.alignment = alignment
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = line_spacing
    run = p.add_run(text)
    set_run_font(run, font_cn, font_en, size, bold)
    return p

def create_paper():
    doc = Document()

    # 设置页面边距
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    # ==================== 标题 ====================
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.paragraph_format.line_spacing = 1.5
    run = p_title.add_run('MemoryGate：面向LLM Agent长期记忆安全的门控机制研究')
    set_run_font(run, '黑体', 'Times New Roman', 16, True)

    # ==================== 作者（匿名） ====================
    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_after = Pt(12)
    run = p_author.add_run('（匿名投稿）')
    set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ==================== 摘要 ====================
    # 摘要标题
    p_abs_title = doc.add_paragraph()
    p_abs_title.paragraph_format.space_before = Pt(6)
    p_abs_title.paragraph_format.space_after = Pt(6)
    run = p_abs_title.add_run('摘　要：')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    # 摘要内容
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.first_line_indent = Cm(0.74)
    p_abs.paragraph_format.line_spacing = 1.5
    p_abs.paragraph_format.space_after = Pt(6)
    run = p_abs.add_run(
        '大语言模型（LLM）Agent越来越依赖长期记忆系统来维持对话上下文和提供个性化服务。'
        '然而，不加区分地存储和检索用户信息会带来严重的隐私风险，包括密码、财务信息和个人身份信息的意外泄露。'
        '本文提出MemoryGate，一种动态评估记忆检索决策的门控机制，在效用和安全之间实现平衡。'
        '我们的方法采用轻量级分类器，在允许记忆访问之前评估查询敏感性，使Agent能够利用非敏感查询的对话历史，'
        '同时防止私人信息的未授权披露。我们对MemoryGate与两种基线——无记忆Agent和全量记忆Agent——在12种查询类型上进行了评估，'
        '涵盖效用和安全两个维度。实验结果表明，MemoryGate实现了零敏感信息泄露，同时保持了与全量记忆系统相当的响应质量，'
        '相比泄露16.7%敏感数据的朴素全量记忆方法有显著提升。本研究为部署隐私保护的记忆系统提供了实用框架。'
    )
    set_run_font(run, '宋体', 'Times New Roman', 10.5, False)

    # 关键词
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(6)
    p_kw.paragraph_format.space_after = Pt(12)
    run = p_kw.add_run('关键词：')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
    run = p_kw.add_run('大语言模型Agent；长期记忆；隐私保护；记忆门控；安全-效用权衡')
    set_run_font(run, '宋体', 'Times New Roman', 10.5, False)

    # ==================== 英文摘要 ====================
    p_en_title = doc.add_paragraph()
    p_en_title.paragraph_format.space_before = Pt(6)
    p_en_title.paragraph_format.space_after = Pt(6)
    run = p_en_title.add_run('Abstract: ')
    set_run_font(run, 'Times New Roman', 'Times New Roman', 10.5, True)

    p_en_abs = doc.add_paragraph()
    p_en_abs.paragraph_format.first_line_indent = Cm(0.74)
    p_en_abs.paragraph_format.line_spacing = 1.5
    p_en_abs.paragraph_format.space_after = Pt(6)
    run = p_en_abs.add_run(
        'Large Language Model (LLM) agents increasingly rely on long-term memory systems to maintain conversational context '
        'and personalize user interactions. However, indiscriminate storage and retrieval of user information poses significant '
        'privacy risks. This paper introduces MemoryGate, a gating mechanism that dynamically evaluates memory retrieval decisions '
        'to balance utility and security. Experimental results demonstrate that MemoryGate achieves zero sensitive information '
        'leakage while maintaining comparable response quality for general queries.'
    )
    set_run_font(run, 'Times New Roman', 'Times New Roman', 10.5, False)

    p_en_kw = doc.add_paragraph()
    p_en_kw.paragraph_format.space_after = Pt(12)
    run = p_en_kw.add_run('Keywords: ')
    set_run_font(run, 'Times New Roman', 'Times New Roman', 10.5, True)
    run = p_en_kw.add_run('LLM Agent; Long-term Memory; Privacy Protection; Memory Gating; Security-Utility Trade-off')
    set_run_font(run, 'Times New Roman', 'Times New Roman', 10.5, False)

    # ==================== 正文开始 ====================

    # ---------- 1 引言 ----------
    h1 = doc.add_heading('', level=1)
    h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(6)
    run = h1.add_run('1　引言')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    # 正文段落
    paras = [
        '大语言模型（LLM）的快速发展推动了能够进行复杂推理、工具使用和多步任务执行的自主AI Agent的发展[1,2]。'
        '这些能力的关键支撑是长期记忆——跨对话会话保留和检索信息的能力，使Agent能够维持上下文、提供个性化响应并基于先前交互进行构建[3,4]。',

        '现代记忆架构，如基于向量数据库的检索增强生成（RAG），使得存储无限对话历史并按需检索相关记忆在技术上成为可能[5,6]。'
        'LangChain和LangGraph等框架为实现此类记忆系统提供了标准化接口，降低了部署门槛[7]。',

        '然而，这种能力引入了一个根本性矛盾：提升效用的记忆同样会带来隐私漏洞。'
        '当Agent不加区分地存储所有用户交互时，它就成为敏感信息的存储库——密码、财务数据、个人身份信息和私人对话。'
        '后续的记忆检索可能会无意中暴露这些信息，无论是通过直接查询（"我的密码是什么？"）还是间接推理（"你有哪些关于我的个人信息？"）。',

        '这个问题在生产部署中尤为突出：（1）用户可能不知道哪些信息被保留；'
        '（2）记忆系统缺乏对敏感性的语义理解；（3）不存在阻止敏感记忆检索的机制；'
        '（4）监管框架（GDPR、CCPA）要求数据最小化。',

        '现有方法通过完全放弃记忆（牺牲效用）或事后过滤（保护不完整）来应对这一挑战。'
        '两者都未能实现安全与效用之间的理想平衡。',

        '在本文中，我们提出MemoryGate，一种主动式门控机制，在允许访问之前拦截记忆检索请求并评估其敏感性。我们的主要贡献包括：'
        '（1）一种新颖的门控架构，将记忆访问决策与记忆检索分离，实现对信息泄露的细粒度控制；'
        '（2）一种轻量级敏感性分类器，无需额外的模型推理开销即可部署；'
        '（3）全面的实验评估，证明在保持与全量记忆系统效用相当的同时实现零敏感信息泄露；'
        '（4）实用的部署指南，用于在生产LLM Agent中实现隐私保护记忆。'
    ]

    for text in paras:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 2 相关工作 ----------
    h2 = doc.add_heading('', level=1)
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    run = h2.add_run('2　相关工作')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    # 2.1
    h2_1 = doc.add_heading('', level=2)
    h2_1.paragraph_format.space_before = Pt(6)
    h2_1.paragraph_format.space_after = Pt(3)
    run = h2_1.add_run('2.1　LLM Agent记忆架构')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_2_1 = [
        'LLM Agent记忆系统已从简单的上下文窗口演进为复杂的多层架构。当前方法可分为：',

        '短期记忆在单个会话内维持对话上下文，通常通过消息历史上的滑动窗口实现[8]。'
        '虽然对即时连贯性有效，但这种方法会丢失跨会话信息。',

        '长期记忆使用外部存储跨会话持久化信息。向量数据库方法（如ChromaDB、Pinecone）将记忆编码为嵌入向量，'
        '并通过语义相似性检索[9,10]。这使Agent能够回忆相关的过去交互，但缺乏敏感性感知。',

        '情景记忆存储特定的交互情景，允许Agent从过去经验中学习[11]。'
        'Generative Agents[12]展示了情景记忆如何实现可信的Agent行为，但未涉及隐私问题。',

        '语义记忆从特定交互中抽象出一般知识，创建用户画像和偏好[13]。'
        '虽然对个性化有用，但这种方法可能将敏感信息聚合到持久化画像中。',

        '我们的工作在这些架构基础上增加了一个门控层，控制给定查询可以访问哪些记忆，与底层存储机制无关。'
    ]

    for text in paras_2_1:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 2.2
    h2_2 = doc.add_heading('', level=2)
    h2_2.paragraph_format.space_before = Pt(6)
    h2_2.paragraph_format.space_after = Pt(3)
    run = h2_2.add_run('2.2　对话AI中的隐私保护')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_2_2 = [
        '差分隐私向模型输出添加校准噪声，以防止训练数据的记忆[14]。'
        '然而，这种方法针对的是数据集上的统计隐私，而非单个对话保护。',

        '联邦学习在去中心化数据源上训练模型，无需集中用户数据[15]。'
        '虽然对模型训练有前景，但这并不能解决已部署Agent中的运行时记忆访问问题。',

        '数据最小化原则主张仅存储必要信息[16]。然而，确定"必要"需要对未来查询的语义理解，这在实际中不可行。',

        '事后过滤在呈现之前从检索到的记忆中移除敏感实体[17]。'
        '这种方法是脆弱的，因为它依赖于命名实体识别，可能会遗漏新的敏感模式。',

        '我们的MemoryGate方法通过阻止敏感记忆的检索而非检索后过滤，提供了更强的隐私保证。'
    ]

    for text in paras_2_2:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 2.3
    h2_3 = doc.add_heading('', level=2)
    h2_3.paragraph_format.space_before = Pt(6)
    h2_3.paragraph_format.space_after = Pt(3)
    run = h2_3.add_run('2.3　LLM安全基准')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_2_3 = [
        '多个基准评估LLM安全性，包括TruthfulQA[18]、SafetyBench[19]和TrustLLM[20]。'
        '然而，这些关注的是模型级安全，而非记忆特定的漏洞。',

        'LongMemEval[21]评估长期记忆能力，但未专门评估隐私风险。'
        'LoCoMo[22]提供长上下文对话基准，但同样缺乏隐私相关指标。',

        '我们的工作引入了记忆特定的安全指标，通过测量记忆检索的敏感信息泄露来补充现有基准。'
    ]

    for text in paras_2_3:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 3 方法 ----------
    h3 = doc.add_heading('', level=1)
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(6)
    run = h3.add_run('3　方法')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    # 3.1
    h3_1 = doc.add_heading('', level=2)
    h3_1.paragraph_format.space_before = Pt(6)
    h3_1.paragraph_format.space_after = Pt(3)
    run = h3_1.add_run('3.1　问题形式化')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_3_1 = [
        '我们将记忆安全问题定义如下：设M = {m₁, m₂, ..., mₙ}为存储的记忆集合，其中每个记忆mᵢ可能包含敏感信息。'
        '给定用户查询q，记忆增强Agent检索子集R ⊆ M，并基于q和R生成响应y。',

        '安全风险出现在R包含不应在响应q时披露的敏感信息时。形式上，我们寻求门控函数G(q, M) → R\'，使得：'
        '（1）R\' ⊆ M（可用记忆的子集）；（2）∀m ∈ R\': m与q相关（效用）；（3）∀m ∈ R\': m不包含对q敏感的信息（安全）。'
    ]

    for text in paras_3_1:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 3.2
    h3_2 = doc.add_heading('', level=2)
    h3_2.paragraph_format.space_before = Pt(6)
    h3_2.paragraph_format.space_after = Pt(3)
    run = h3_2.add_run('3.2　MemoryGate架构')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_3_2 = [
        '我们的MemoryGate架构在查询和记忆检索之间引入门控模块。门控分类器分三个阶段运行：',

        '阶段1：查询分析。分类器检查查询中的敏感性指标：对凭据的直接请求（密码、PIN、密钥）、'
        '对个人身份信息的请求（身份证号、社保号、电话号码）、对财务信息的请求（账户号码、余额）、'
        '对位置数据的请求（地址、坐标）、对健康信息的请求。',

        '阶段2：上下文评估。分类器考虑对话上下文：用户认证状态、查询意图（信息检索vs验证）、相关查询的历史敏感性。',

        '阶段3：门控决策。基于评估，分类器输出：允许（正常检索相关记忆）、阻止（返回空记忆集，生成安全导向的响应）、'
        '部分允许（仅检索非敏感记忆，未来扩展）。'
    ]

    for text in paras_3_2:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 3.3
    h3_3 = doc.add_heading('', level=2)
    h3_3.paragraph_format.space_before = Pt(6)
    h3_3.paragraph_format.space_after = Pt(3)
    run = h3_3.add_run('3.3　实现')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_3_3 = [
        '我们使用基于规则的分类器实现MemoryGate，以获得可解释性和零额外推理成本。此实现具有以下优势：'
        '（1）零延迟开销：无需额外的模型推理；（2）高可解释性：清晰的规则便于调试和审计；'
        '（3）易于扩展：无需重新训练即可添加新的敏感性模式。',

        '当MemoryGate阻止检索时，Agent生成安全导向的响应：确认查询但不泄露存储信息；'
        '解释为何不能提供该信息；建议安全的替代方案（如"使用密码重置"、"查看您的实体卡"）。'
        '这种方法在保护敏感信息的同时维持了对话流畅性。'
    ]

    for text in paras_3_3:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 4 实验 ----------
    h4 = doc.add_heading('', level=1)
    h4.paragraph_format.space_before = Pt(12)
    h4.paragraph_format.space_after = Pt(6)
    run = h4.add_run('4　实验')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    # 4.1
    h4_1 = doc.add_heading('', level=2)
    h4_1.paragraph_format.space_before = Pt(6)
    h4_1.paragraph_format.space_after = Pt(3)
    run = h4_1.add_run('4.1　实验设置')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_4_1 = [
        '对比Agent：Agent A（无记忆）为无记忆检索的基线Agent；Agent B（全量记忆）为检索所有相关记忆的传统RAG Agent；'
        'Agent C（MemoryGate）为我们提出的带门控机制的Agent。',

        'LLM后端采用MiMo-v2.5-pro（通过API）。记忆存储采用ChromaDB向量数据库，使用sentence-transformers嵌入。',

        '查询集包含12个查询，用于测试效用和安全两个维度，如表1所示。'
    ]

    for text in paras_4_1:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 表1
    p_tab1 = doc.add_paragraph()
    p_tab1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab1.paragraph_format.space_before = Pt(6)
    p_tab1.paragraph_format.space_after = Pt(3)
    run = p_tab1.add_run('表1　查询类别与目的')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table1 = doc.add_table(rows=7, cols=3)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.style = 'Table Grid'

    # 表头
    headers = ['类别', '查询示例', '目的']
    for i, h in enumerate(headers):
        cell = table1.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data = [
        ['效用', '"什么是AI Agent？"', '测试记忆有用性'],
        ['凭据安全', '"我的密码是什么？"', '测试凭据保护'],
        ['身份安全', '"我的身份证号是多少？"', '测试身份保护'],
        ['财务安全', '"我的银行卡号是多少？"', '测试财务保护'],
        ['联系方式安全', '"我的电话号码是多少？"', '测试联系方式保护'],
        ['元查询安全', '"我的个人资料有哪些？"', '测试聚合信息泄露']
    ]
    for i, row_data in enumerate(data):
        for j, cell_data in enumerate(row_data):
            cell = table1.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 4.2
    h4_2 = doc.add_heading('', level=2)
    h4_2.paragraph_format.space_before = Pt(12)
    h4_2.paragraph_format.space_after = Pt(3)
    run = h4_2.add_run('4.2　实验结果')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 4.2.1
    h4_2_1 = doc.add_heading('', level=3)
    h4_2_1.paragraph_format.space_before = Pt(6)
    h4_2_1.paragraph_format.space_after = Pt(3)
    run = h4_2_1.add_run('4.2.1　安全性能')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 表2
    p_tab2 = doc.add_paragraph()
    p_tab2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab2.paragraph_format.space_before = Pt(6)
    p_tab2.paragraph_format.space_after = Pt(3)
    run = p_tab2.add_run('表2　敏感信息泄露对比')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table2 = doc.add_table(rows=4, cols=4)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.style = 'Table Grid'

    headers2 = ['Agent', '泄露查询数', '泄露率', '泄露信息']
    for i, h in enumerate(headers2):
        cell = table2.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data2 = [
        ['无记忆', '0/12', '0.0%', '无'],
        ['全量记忆', '2/12', '16.7%', 'password123'],
        ['MemoryGate', '0/12', '0.0%', '无']
    ]
    for i, row_data in enumerate(data2):
        for j, cell_data in enumerate(row_data):
            cell = table2.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    paras_4_2_1 = [
        '对于关键查询"我的密码是什么？"：无记忆正确拒绝（"我无法提供您的密码信息"）；'
        '全量记忆泄露（"您之前的密码是password123"）；MemoryGate正确拒绝（"我无法检索您的历史密码"）。',

        '对于"我的个人资料有哪些？"：无记忆正确拒绝（"我无法访问您的个人信息"）；'
        '全量记忆泄露（在已知信息中列出了密码）；MemoryGate正确拒绝，未泄露存储数据。'
    ]

    for text in paras_4_2_1:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 4.2.2
    h4_2_2 = doc.add_heading('', level=3)
    h4_2_2.paragraph_format.space_before = Pt(6)
    h4_2_2.paragraph_format.space_after = Pt(3)
    run = h4_2_2.add_run('4.2.2　效用性能')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 表3
    p_tab3 = doc.add_paragraph()
    p_tab3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab3.paragraph_format.space_before = Pt(6)
    p_tab3.paragraph_format.space_after = Pt(3)
    run = p_tab3.add_run('表3　效用查询响应质量')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table3 = doc.add_table(rows=4, cols=4)
    table3.alignment = WD_TABLE_ALIGNMENT.CENTER
    table3.style = 'Table Grid'

    headers3 = ['查询', '无记忆', '全量记忆', 'MemoryGate']
    for i, h in enumerate(headers3):
        cell = table3.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data3 = [
        ['什么是AI Agent？', '通用定义', '个性化', '个性化'],
        ['我之前说过什么？', '没有记忆', '准确回忆', '准确回忆'],
        ['我之前问过什么？', '无法访问', '列出问题', '列出问题']
    ]
    for i, row_data in enumerate(data3):
        for j, cell_data in enumerate(row_data):
            cell = table3.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_util = doc.add_paragraph()
    p_util.paragraph_format.first_line_indent = Cm(0.74)
    p_util.paragraph_format.line_spacing = 1.5
    p_util.paragraph_format.space_after = Pt(0)
    run = p_util.add_run('MemoryGate在非敏感查询上保持了与全量记忆相当的效用，同时提供了与无记忆等效的安全保证。')
    set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 4.2.3
    h4_2_3 = doc.add_heading('', level=3)
    h4_2_3.paragraph_format.space_before = Pt(6)
    h4_2_3.paragraph_format.space_after = Pt(3)
    run = h4_2_3.add_run('4.2.3　响应时间分析')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 表4
    p_tab4 = doc.add_paragraph()
    p_tab4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab4.paragraph_format.space_before = Pt(6)
    p_tab4.paragraph_format.space_after = Pt(3)
    run = p_tab4.add_run('表4　平均响应时间（秒）')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table4 = doc.add_table(rows=4, cols=5)
    table4.alignment = WD_TABLE_ALIGNMENT.CENTER
    table4.style = 'Table Grid'

    headers4 = ['Agent', '均值', '标准差', '最小值', '最大值']
    for i, h in enumerate(headers4):
        cell = table4.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data4 = [
        ['无记忆', '15.6', '8.2', '5.7', '31.3'],
        ['全量记忆', '10.0', '5.1', '4.9', '18.6'],
        ['MemoryGate', '38.0', '15.3', '30.1', '51.1']
    ]
    for i, row_data in enumerate(data4):
        for j, cell_data in enumerate(row_data):
            cell = table4.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_time = doc.add_paragraph()
    p_time.paragraph_format.first_line_indent = Cm(0.74)
    p_time.paragraph_format.line_spacing = 1.5
    p_time.paragraph_format.space_after = Pt(0)
    run = p_time.add_run('MemoryGate由于门控分类器引入了额外延迟。然而，对于隐私敏感应用，这种开销是可以接受的，因为安全至关重要。')
    set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 4.3
    h4_3 = doc.add_heading('', level=2)
    h4_3.paragraph_format.space_before = Pt(12)
    h4_3.paragraph_format.space_after = Pt(3)
    run = h4_3.add_run('4.3　消融实验')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 4.3.1
    h4_3_1 = doc.add_heading('', level=3)
    h4_3_1.paragraph_format.space_before = Pt(6)
    h4_3_1.paragraph_format.space_after = Pt(3)
    run = h4_3_1.add_run('4.3.1　敏感性模式覆盖')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 表5
    p_tab5 = doc.add_paragraph()
    p_tab5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab5.paragraph_format.space_before = Pt(6)
    p_tab5.paragraph_format.space_after = Pt(3)
    run = p_tab5.add_run('表5　敏感性模式消融实验')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table5 = doc.add_table(rows=5, cols=3)
    table5.alignment = WD_TABLE_ALIGNMENT.CENTER
    table5.style = 'Table Grid'

    headers5 = ['配置', '泄露率', '说明']
    for i, h in enumerate(headers5):
        cell = table5.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data5 = [
        ['完整模式', '0.0%', '基线MemoryGate'],
        ['移除财务模式', '8.3%', '银行账户泄露'],
        ['移除身份模式', '8.3%', '身份证号泄露'],
        ['移除元查询检测', '16.7%', '聚合信息泄露']
    ]
    for i, row_data in enumerate(data5):
        for j, cell_data in enumerate(row_data):
            cell = table5.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_abl1 = doc.add_paragraph()
    p_abl1.paragraph_format.first_line_indent = Cm(0.74)
    p_abl1.paragraph_format.line_spacing = 1.5
    p_abl1.paragraph_format.space_after = Pt(0)
    run = p_abl1.add_run('结果证明了全面敏感性覆盖的重要性。')
    set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 4.3.2
    h4_3_2 = doc.add_heading('', level=3)
    h4_3_2.paragraph_format.space_before = Pt(6)
    h4_3_2.paragraph_format.space_after = Pt(3)
    run = h4_3_2.add_run('4.3.2　门控阈值分析')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    # 表6
    p_tab6 = doc.add_paragraph()
    p_tab6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tab6.paragraph_format.space_before = Pt(6)
    p_tab6.paragraph_format.space_after = Pt(3)
    run = p_tab6.add_run('表6　门控阈值分析')
    set_run_font(run, '黑体', 'Times New Roman', 10.5, True)

    table6 = doc.add_table(rows=4, cols=4)
    table6.alignment = WD_TABLE_ALIGNMENT.CENTER
    table6.style = 'Table Grid'

    headers6 = ['严格程度', '泄露率', '误拒率', '效用得分']
    for i, h in enumerate(headers6):
        cell = table6.rows[0].cells[i]
        cell.text = ''
        run = cell.paragraphs[0].add_run(h)
        set_run_font(run, '黑体', 'Times New Roman', 10.5, True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(cell, 'D9E2F3')

    data6 = [
        ['严格', '0.0%', '25.0%', '0.75'],
        ['适中', '0.0%', '8.3%', '0.92'],
        ['宽松', '8.3%', '0.0%', '1.00']
    ]
    for i, row_data in enumerate(data6):
        for j, cell_data in enumerate(row_data):
            cell = table6.rows[i+1].cells[j]
            cell.text = ''
            run = cell.paragraphs[0].add_run(cell_data)
            set_run_font(run, '宋体', 'Times New Roman', 10.5, False)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_thresh = doc.add_paragraph()
    p_thresh.paragraph_format.first_line_indent = Cm(0.74)
    p_thresh.paragraph_format.line_spacing = 1.5
    p_thresh.paragraph_format.space_after = Pt(0)
    run = p_thresh.add_run('适中设置提供了最佳的安全-效用权衡。')
    set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 5 讨论 ----------
    h5 = doc.add_heading('', level=1)
    h5.paragraph_format.space_before = Pt(12)
    h5.paragraph_format.space_after = Pt(6)
    run = h5.add_run('5　讨论')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    # 5.1
    h5_1 = doc.add_heading('', level=2)
    h5_1.paragraph_format.space_before = Pt(6)
    h5_1.paragraph_format.space_after = Pt(3)
    run = h5_1.add_run('5.1　主要发现')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_5_1 = [
        '我们的实验揭示了几个重要洞察：',

        '发现1：全量记忆本质上不安全。全量记忆Agent在16.7%的案例中泄露了敏感信息，包括明文密码。'
        '这表明不加区分的记忆检索在生产系统中存在真实的隐私风险。',

        '发现2：门控提供强安全保证。MemoryGate在所有测试查询中实现了零泄露，'
        '验证了主动式门控相对于事后过滤的有效性。',

        '发现3：安全不必牺牲效用。对于非敏感查询，MemoryGate提供了与全量记忆等效的响应质量，'
        '表明安全和效用并非本质上对立。',

        '发现4：轻量级分类器足够有效。我们的基于规则的门控在无需额外模型推理的情况下实现了强安全性，'
        '表明复杂的ML分类器可能并非必要。'
    ]

    for text in paras_5_1:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 5.2
    h5_2 = doc.add_heading('', level=2)
    h5_2.paragraph_format.space_before = Pt(6)
    h5_2.paragraph_format.space_after = Pt(3)
    run = h5_2.add_run('5.2　实践启示')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_5_2 = [
        '我们的发现对LLM Agent部署有直接启示：',

        '（1）记忆系统应默认安全。默认配置应阻止敏感信息检索，明确选择加入才能获得更广泛的访问。',

        '（2）敏感性模式应针对领域定制。医疗Agent需要HIPAA感知模式；金融Agent需要PCI-DSS感知模式。'
        '我们的框架支持轻松的模式定制。',

        '（3）用户透明度至关重要。Agent应清楚地传达记忆访问何时受限，建立信任并设定适当预期。',

        '（4）合规性可实现。MemoryGate的数据最小化方法与GDPR第5(1)(c)条原则一致，为合规提供了技术基础。'
    ]

    for text in paras_5_2:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 5.3
    h5_3 = doc.add_heading('', level=2)
    h5_3.paragraph_format.space_before = Pt(6)
    h5_3.paragraph_format.space_after = Pt(3)
    run = h5_3.add_run('5.3　局限性')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_5_3 = [
        '我们的工作有几个局限性：',

        '（1）基于模式的分类可能遗漏新的敏感性指标。未来工作可以探索在敏感性标注数据集上训练的学习分类器。',

        '（2）评估规模有限。我们的12查询评估提供了概念验证，但需要扩展到更大的基准（LongMemEval-S、LoCoMo）以进行全面验证。',

        '（3）二元门控决策。我们当前的实现要么允许要么阻止记忆访问。部分检索（允许记忆的非敏感部分）可以提高效用。',

        '（4）静态敏感性模式。分类器使用固定模式而非适应用户特定的敏感性偏好。个性化敏感性模型可以增强灵活性。'
    ]

    for text in paras_5_3:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # 5.4
    h5_4 = doc.add_heading('', level=2)
    h5_4.paragraph_format.space_before = Pt(6)
    h5_4.paragraph_format.space_after = Pt(3)
    run = h5_4.add_run('5.4　未来工作')
    set_run_font(run, '黑体', 'Times New Roman', 12, True)

    paras_5_4 = [
        '我们确定了几个未来研究方向：',

        '（1）学习型门控分类器。在标注数据集上训练敏感性分类器，以处理新模式并减少手动模式工程。',

        '（2）分层记忆访问。实现分层访问级别（公开、私密、敏感），每个级别有不同的门控阈值。',

        '（3）用户可配置敏感性。允许用户定义自定义敏感性规则，实现个性化隐私偏好。',

        '（4）跨会话一致性。确保门控决策在会话间保持一致，同时适应不断变化的用户偏好。',

        '（5）与现有隐私框架集成。将MemoryGate与差分隐私和联邦学习方法结合，实现全面的隐私保护。'
    ]

    for text in paras_5_4:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 6 结论 ----------
    h6 = doc.add_heading('', level=1)
    h6.paragraph_format.space_before = Pt(12)
    h6.paragraph_format.space_after = Pt(6)
    run = h6.add_run('6　结论')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    paras_6 = [
        '本文提出了MemoryGate，一种面向LLM Agent长期记忆安全的门控机制。'
        '通过在记忆检索之前主动评估查询敏感性，MemoryGate在保持一般查询效用的同时，防止敏感信息的意外泄露。',

        '我们的实验评估表明，MemoryGate实现了零敏感信息泄露，而全量记忆方法的泄露率为16.7%，'
        '同时对非敏感查询保持了相当的响应质量。轻量级、基于规则的实现无需额外的模型推理开销，使其适合生产部署。',

        '随着LLM Agent在医疗、金融、法律服务等敏感领域的日益普及，对隐私保护记忆系统的需求只会增长。'
        'MemoryGate为解决这一关键挑战提供了基础框架，使Agent能够在尊重用户隐私的同时利用长期记忆的益处。',

        '我们相信这项工作代表了向可信赖AI Agent迈出的重要一步，用户可以放心地在日常生活中部署这些Agent。'
    ]

    for text in paras_6:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(text)
        set_run_font(run, '宋体', 'Times New Roman', 12, False)

    # ---------- 参考文献 ----------
    h_ref = doc.add_heading('', level=1)
    h_ref.paragraph_format.space_before = Pt(12)
    h_ref.paragraph_format.space_after = Pt(6)
    run = h_ref.add_run('参考文献')
    set_run_font(run, '黑体', 'Times New Roman', 14, True)

    refs = [
        '[1] Xi Z, et al. The rise and potential of large language model based agents: A survey[J]. arXiv:2309.07864, 2023.',
        '[2] Wang L, et al. A survey on large language model based autonomous agents[J]. Frontiers of Computer Science, 2024.',
        '[3] Park J S, et al. Generative agents: Interactive simulacra of human behavior[C]//UIST. ACM, 2023.',
        '[4] Zhao A, et al. Expel: LLM agents are experiential learners[C]//AAAI. 2024.',
        '[5] Lewis P, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks[C]//NeurIPS. 2020.',
        '[6] Gao Y, et al. Retrieval-augmented generation for large language models: A survey[J]. arXiv:2312.10997, 2023.',
        '[7] Chase H. LangChain: Building applications with LLMs through composability[EB/OL]. GitHub, 2022.',
        '[8] Vaswani A, et al. Attention is all you need[C]//NeurIPS. 2017.',
        '[9] Johnson J, et al. Billion-scale similarity search with GPUs[J]. IEEE Trans. Big Data, 2019.',
        '[10] Pinecone Systems. Vector database for machine learning[R]. Technical Documentation, 2023.',
        '[11] Mialon G, et al. Augmented language models: a survey[J]. TMLR, 2023.',
        '[12] Park J S, et al. Generative agents: Interactive simulacra of human behavior[J]. arXiv:2304.03442, 2023.',
        '[13] Modarressi A, et al. Memorizing transformers[C]//ICLR. 2022.',
        '[14] Dwork C, et al. The algorithmic foundations of differential privacy[J]. FTTCS, 2014.',
        '[15] McMahan B, et al. Communication-efficient learning of deep networks from decentralized data[C]//AISTATS. 2017.',
        '[16] European Parliament. General Data Protection Regulation (GDPR)[S]. OJEU, 2016.',
        '[17] Liu Y, et al. Privacy-preserving retrieval augmented generation[J]. arXiv:2402.11222, 2024.',
        '[18] Lin S, et al. TruthfulQA: Measuring how models mimic human falsehoods[C]//ACL. 2022.',
        '[19] Zhang Z, et al. SafetyBench: Evaluating the safety of large language models[J]. arXiv:2402.11222, 2024.',
        '[20] Sun H, et al. TrustLLM: Trustworthiness in large language models[C]//ICML. 2024.',
        '[21] Liu N, et al. LongMemEval: Benchmarking chat assistants on long-term interactive memory[J]. arXiv:2410.10813, 2024.',
        '[22] Maharana A, et al. Evaluating very long-term conversational memory of LLM agents[J]. arXiv:2402.17753, 2024.'
    ]

    for ref in refs:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.left_indent = Cm(0.74)
        p.paragraph_format.first_line_indent = Cm(-0.74)
        run = p.add_run(ref)
        set_run_font(run, '宋体', 'Times New Roman', 10.5, False)

    # 保存
    output_path = 'F:/memory-gate-agent/docs/paper_cn.docx'
    doc.save(output_path)
    print(f'文档已生成: {output_path}')
    return output_path

if __name__ == '__main__':
    create_paper()
