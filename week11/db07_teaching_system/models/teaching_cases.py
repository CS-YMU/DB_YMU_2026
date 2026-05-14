"""
DB07 教学案例库 — 10 个覆盖全部课件内容的规范化教学案例

每个案例包含：场景描述、关系模式、函数依赖集、候选键、范式分析、分解方案、知识点
"""

CASES = [
    {
        "id": "case1",
        "title": "学生选课表 — 异常问题演示",
        "section": "课件 7.1.2",
        "tags": ["异常问题", "模式分解引入", "入门"],
        "scenario": (
            "教务处想用一张表记录学生选课的全部信息，包括学生号(S#)、课程号(C#)、"
            "课程名(CName)和授课教师名(TName)。这个设计看似方便，但实际操作中会遇到各种麻烦。"
        ),
        "relation": "R(S#, C#, CName, TName)",
        "attributes": ["S#", "C#", "CName", "TName"],
        "fds": [
            ["C#", "CName"],
            ["C#", "TName"],
        ],
        "candidate_keys": [["S#", "C#"]],
        "highest_nf": "2NF",
        "problems": [
            {
                "type": "数据冗余",
                "detail": "课程C4有3个学生选修，C4的课程名和教师名就会重复存储3次。",
            },
            {
                "type": "修改异常",
                "detail": "要把C4的教师改为LI老师，必须同时修改所有选修C4的学生记录。漏改一条就会造成数据不一致。",
            },
            {
                "type": "插入异常",
                "detail": "新开了一门课程C7(C++)，但还没有学生选修。由于S#是主键的一部分不能为空，这门新课的信息无法插入表中。",
            },
            {
                "type": "删除异常",
                "detail": "学生S8退学了，需要删除他的选课记录。但如果S8是课程C6唯一的选课者，删除后C6的课程名和教师名信息也会一并消失。",
            },
        ],
        "solution": {
            "method": "按'一事一地'原则拆分为两个表",
            "decomposition": [
                {"name": "选课表", "attrs": ["S#", "C#"], "key": ["S#", "C#"]},
                {"name": "课程表", "attrs": ["C#", "CName", "TName"], "key": ["C#"]},
            ],
        },
        "key_points": [
            "一个模式混合多个主题 = 冗余 + 异常",
            "根本原因是存在非主属性对候选键的部分依赖（CName、TName 只依赖 C#，而候选键是 (S#, C#)）",
            "'一事一地'原则是最核心的设计准则",
            "模式分解是解决问题的主要手段",
        ],
        "teaching_tip": "先让学生看异常现象，产生'这表设计有问题'的直觉，再引出函数依赖的概念，理解会深刻很多。",
    },
    {
        "id": "case2",
        "title": "学生-课程-教师综合表 — FD 识别与推理",
        "section": "课件 7.2.1 例7.3",
        "tags": ["函数依赖", "FD推理", "综合"],
        "scenario": (
            "设计一个学生选课管理系统，把所有信息放在一张表里：学号(S#)、姓名(SName)、年龄(Age)、"
            "性别(Sex)、课程号(C#)、课程名(CName)、成绩(Score)、教师工号(T#)、教师姓名(TName)、职称(Title)。"
            "请找出属性之间的函数依赖关系。"
        ),
        "relation": "R(S#, SName, Age, Sex, C#, CName, Score, T#, TName, Title)",
        "attributes": ["S#", "SName", "Age", "Sex", "C#", "CName", "Score", "T#", "TName", "Title"],
        "fds": [
            ["S#", "SName"],
            ["S#", "Age"],
            ["S#", "Sex"],
            ["C#", "CName"],
            ["C#", "T#"],
            ["S#C#", "Score"],
            ["T#", "TName"],
            ["T#", "Title"],
        ],
        "candidate_keys": [["S#", "C#"]],
        "highest_nf": "1NF",
        "problems": [
            {
                "type": "部分依赖",
                "detail": "SName, Age, Sex 仅依赖 S#（候选键的一部分）；CName, T# 仅依赖 C#；TName, Title 通过 T# 传递依赖。",
            },
            {
                "type": "传递依赖",
                "detail": "C# → T# → (TName, Title)，存在非主属性对候选键的传递依赖。",
            },
        ],
        "solution": {
            "method": "按函数依赖逐步分解",
            "decomposition": [
                {"name": "学生表", "attrs": ["S#", "SName", "Age", "Sex"], "key": ["S#"]},
                {"name": "课程表", "attrs": ["C#", "CName", "T#"], "key": ["C#"]},
                {"name": "教师表", "attrs": ["T#", "TName", "Title"], "key": ["T#"]},
                {"name": "选课成绩表", "attrs": ["S#", "C#", "Score"], "key": ["S#", "C#"]},
            ],
        },
        "key_points": [
            "FD 来自业务语义，不是来自当前数据",
            "S#→SName 是因为'学号唯一标识学生'这条业务规则",
            "传递依赖是冗余的重要来源",
            "隐式依赖可被 Armstrong 公理推导（如 S#C#→SName 是平凡+增广的结果）",
        ],
        "teaching_tip": "让学生对照表格，一条一条写出 FD。重点强调'一对一'和'多对一'的业务语义区别。",
    },
    {
        "id": "case3",
        "title": "物流订单系统 — 综合范式判断与 3NF 分解",
        "section": "作业07B 第二题",
        "tags": ["范式判断", "3NF分解", "无损连接", "综合案例"],
        "scenario": (
            "某物流公司用一张订单表记录所有货运信息，包含订单号(OID)、产品号(PID)、客户号(CID)、"
            "客户姓名(CName)、产品名称(PName)、数量(Qty)、仓库号(WID)、仓库地址(WAddr)、送达日期(DDate)。"
            "一个订单可以包含多种产品。"
        ),
        "relation": "R(OID, PID, CID, CName, PName, Qty, WID, WAddr, DDate)",
        "attributes": ["OID", "PID", "CID", "CName", "PName", "Qty", "WID", "WAddr", "DDate"],
        "fds": [
            ["OID", "CID"],
            ["OID", "DDate"],
            ["CID", "CName"],
            ["PID", "PName"],
            ["WID", "WAddr"],
            ["OIDPID", "Qty"],
            ["OIDPID", "WID"],
        ],
        "candidate_keys": [["OID", "PID"]],
        "highest_nf": "2NF",
        "problems": [
            {
                "type": "部分依赖",
                "detail": "CID, DDate 只依赖 OID（候选键的一部分）；CName 通过 CID 间接依赖；PName 只依赖 PID；WAddr 通过 WID 间接依赖。",
            },
            {
                "type": "传递依赖",
                "detail": "OID → CID → CName 形成传递依赖链。",
            },
        ],
        "solution": {
            "method": "3NF 分解算法（先求最小依赖集，按依赖构造子模式，补充候选键）",
            "decomposition": [
                {"name": "订单表", "attrs": ["OID", "CID", "DDate"], "key": ["OID"]},
                {"name": "客户表", "attrs": ["CID", "CName"], "key": ["CID"]},
                {"name": "产品表", "attrs": ["PID", "PName"], "key": ["PID"]},
                {"name": "仓库表", "attrs": ["WID", "WAddr"], "key": ["WID"]},
                {"name": "订单明细表", "attrs": ["OID", "PID", "Qty", "WID"], "key": ["OID", "PID"]},
            ],
            "lossless": True,
            "dependency_preserving": True,
        },
        "key_points": [
            "候选键是 (OID, PID)，因为一个订单可以包含多种产品",
            "CID→CName 是独立的依赖，应单独成表",
            "3NF 分解要基于最小依赖集",
            "如果分解后没有模式包含原候选键，需要补充一个候选键模式",
        ],
        "teaching_tip": "这是一个很好的综合性案例。建议先让学生在白纸上画出属性之间的依赖箭头，再判断范式，最后动手分解。",
    },
    {
        "id": "case4",
        "title": "在线考试系统 — 3NF 分解与插入异常避免",
        "section": "作业07B 第三题",
        "tags": ["范式判断", "3NF分解", "插入异常", "综合案例"],
        "scenario": (
            "某在线考试系统用一张考试记录表存储所有信息：学生号(SID)、学生姓名(SName)、课程号(CID)、"
            "课程名(CName)、考试日期(EDate)、成绩(Score)、批改教师工号(GID)、批改教师姓名(GName)。"
            "一个重要问题是：新开设的课程还没有学生考试时，能否插入课程信息？"
        ),
        "relation": "R(SID, SName, CID, CName, EDate, Score, GID, GName)",
        "attributes": ["SID", "SName", "CID", "CName", "EDate", "Score", "GID", "GName"],
        "fds": [
            ["SID", "SName"],
            ["CID", "CName"],
            ["GID", "GName"],
            ["SIDCIDEDate", "Score"],
            ["SIDCIDEDate", "GID"],
        ],
        "candidate_keys": [["SID", "CID", "EDate"]],
        "highest_nf": "1NF",
        "problems": [
            {
                "type": "插入异常",
                "detail": "新开设的课程（如 C++）还没有学生考试时，因缺少 SID 和 EDate（候选键的一部分不能为空），课程信息无法插入。",
            },
            {
                "type": "数据冗余",
                "detail": "每个选了同一门课的学生记录中，CName 都重复存储。同样，同一个教师的 GName 也多次重复。",
            },
            {
                "type": "部分依赖",
                "detail": "SName 只依赖 SID，CName 只依赖 CID，它们都部分依赖于候选键 (SID, CID, EDate)。",
            },
        ],
        "solution": {
            "method": "3NF 分解，将独立实体分离",
            "decomposition": [
                {"name": "学生表", "attrs": ["SID", "SName"], "key": ["SID"]},
                {"name": "课程表", "attrs": ["CID", "CName"], "key": ["CID"]},
                {"name": "教师表", "attrs": ["GID", "GName"], "key": ["GID"]},
                {"name": "考试记录表", "attrs": ["SID", "CID", "EDate", "Score", "GID"], "key": ["SID", "CID", "EDate"]},
            ],
            "lossless": True,
            "dependency_preserving": True,
        },
        "key_points": [
            "分解后，新课程可以直接插入'课程表'，不再需要等待学生考试",
            "插入异常的根源是非主属性部分依赖或传递依赖于候选键",
            "保持依赖意味着所有原始业务约束都能在分解后的表中检查",
        ],
        "teaching_tip": "重点让学生对比分解前后的插入操作：分解前插入新课需要虚构一个学生和日期，分解后直接 INSERT INTO 课程表即可。",
    },
    {
        "id": "case5",
        "title": "课程-学生-先修课 — BCNF 不够，需要 4NF",
        "section": "课件 7.5.1 例7.14",
        "tags": ["MVD", "4NF", "多值依赖", "高级范式"],
        "scenario": (
            "在课程管理系统中，每门课程(C#)有多个学生(S#)选修，同时每门课程有多门先修课程(PreC#)。"
            "学生和先修课之间没有直接关系，它们仅通过课程间接关联。即使满足了 BCNF，数据冗余依然严重。"
        ),
        "relation": "R(C#, S#, PreC#)",
        "attributes": ["C#", "S#", "PreC#"],
        "fds": [],
        "mvds": [
            ["C#", "S#"],
            ["C#", "PreC#"],
        ],
        "candidate_keys": [["C#", "S#", "PreC#"]],
        "highest_nf": "BCNF",
        "problems": [
            {
                "type": "BCNF 下的数据冗余",
                "detail": "课程C4有2个学生(S1,S2)和3门先修课(C1,C2,C3)，满足1NF需要展开为 2×3=6 行。学生信息和先修课信息独立但被迫做笛卡尔积。",
            },
            {
                "type": "更新异常",
                "detail": "如果C4新增一个学生S3，需要为每个先修课组合插入一行（3行），而不是1行。",
            },
        ],
        "solution": {
            "method": "按多值依赖分解为 4NF",
            "decomposition": [
                {"name": "课程-学生表", "attrs": ["C#", "S#"], "key": ["C#", "S#"]},
                {"name": "课程-先修课表", "attrs": ["C#", "PreC#"], "key": ["C#", "PreC#"]},
            ],
            "lossless": True,
        },
        "key_points": [
            "BCNF 消除了函数依赖导致的问题，但无法解决多值依赖导致的冗余",
            "多值依赖 C#→→S# 的含义：一门课程对应一组学生（与先修课无关）",
            "MVD 的关键特征：两个属性独立地'多对一'于第三个属性",
            "4NF 要求非平凡 MVD 的左部必须是超键",
        ],
        "teaching_tip": "先演示 6 行数据的冗余（让学生数一数重复了几次），再拆成两个 2+3=5 行的表。学生直观感受'行数减少了'，就理解了为什么需要 4NF。",
    },
    {
        "id": "case6",
        "title": "教师工资表 — 传递依赖与 3NF",
        "section": "课件 7.4.3 / 7.3.5",
        "tags": ["传递依赖", "3NF", "保持依赖", "经典案例"],
        "scenario": (
            "一张教师信息表记录了工号(T#)、职称(Title)和工资(Salary)。"
            "业务规则：工号决定职称，而相同职称的教师工资相同（即职称决定工资）。"
            "这种'工号→职称→工资'的链条是典型的传递依赖。"
        ),
        "relation": "R(T#, Title, Salary)",
        "attributes": ["T#", "Title", "Salary"],
        "fds": [
            ["T#", "Title"],
            ["Title", "Salary"],
        ],
        "candidate_keys": [["T#"]],
        "highest_nf": "2NF",
        "problems": [
            {
                "type": "传递依赖",
                "detail": "T# → Title → Salary，Salary 传递依赖于候选键 T#。",
            },
            {
                "type": "数据冗余",
                "detail": "同一职称（如教授）的工资在每个该职称的教师记录中重复存储。",
            },
            {
                "type": "修改异常",
                "detail": "教授涨工资时，需要更新所有教授的记录。",
            },
        ],
        "solution": {
            "method": "3NF 分解",
            "decomposition": [
                {"name": "教师表", "attrs": ["T#", "Title"], "key": ["T#"]},
                {"name": "职称工资表", "attrs": ["Title", "Salary"], "key": ["Title"]},
            ],
            "lossless": True,
            "dependency_preserving": True,
        },
        "key_points": [
            "传递依赖的定义：X→Y, Y→Z, 且 Y↛X, Z⊈Y",
            "3NF 的核心目标就是消除这种传递依赖",
            "不保持依赖的分解示例：若分解为 R1(T#, Title) 和 R2(T#, Salary)，Title→Salary 丢失",
        ],
        "teaching_tip": "对比两种分解方案：好的分解 {T#,Title} + {Title,Salary} vs 坏的分解 {T#,Title} + {T#,Salary}。让学生理解'保持依赖'的实际意义——在坏的分解中，无法约束'同职称同工资'。",
    },
    {
        "id": "case7",
        "title": "供应商-零件-项目 — 连接依赖与 5NF",
        "section": "课件 7.5.5 例7.17",
        "tags": ["连接依赖", "5NF", "连接陷阱", "高级范式"],
        "scenario": (
            "SPJ 数据库记录三个实体之间的关系：供应商(S#)为项目(J#)供应零件(P#)。"
            "只有真正存在的供应关系才被记录。将 SPJ 分解为三个二元关系 SP(S#,P#)、PJ(P#,J#)、JS(J#,S#)后，"
            "自然连接会多出原本不存在的组合——这就是著名的'连接陷阱'。"
        ),
        "relation": "SPJ(S#, P#, J#)",
        "attributes": ["S#", "P#", "J#"],
        "fds": [],
        "candidate_keys": [["S#", "P#", "J#"]],
        "highest_nf": "4NF",
        "problems": [
            {
                "type": "连接陷阱",
                "detail": "分解为 SP(S#,P#)、PJ(P#,J#)、JS(J#,S#) 后，自然连接 SP⋈PJ⋈JS 会产生寄生元组 (s2,p1,j2)，这在原始表中不存在。",
            },
            {
                "type": "插入异常",
                "detail": "插入(s2,p1,j1)时，为满足连接依赖 *{SP,PJ,JS}，需要强制插入(s1,p1,j1)。",
            },
        ],
        "solution": {
            "method": "保持原始 SPJ 表不变（已是 5NF）",
            "decomposition": [
                {"name": "SP", "attrs": ["S#", "P#"], "key": ["S#", "P#"]},
                {"name": "PJ", "attrs": ["P#", "J#"], "key": ["P#", "J#"]},
                {"name": "JS", "attrs": ["J#", "S#"], "key": ["J#", "S#"]},
            ],
            "note": "SPJ 不满足 *(SP, PJ, JS) 这个连接依赖，因此分解为三个二元关系会产生寄生元组，是有损的。保持原始三元关系才是正确的 5NF 设计。",
        },
        "key_points": [
            "连接依赖 *(R1,...,Rn) 存在时，分解才是无损的",
            "5NF 要求每个非平凡连接依赖都由候选键逻辑蕴涵",
            "连接陷阱是多出寄生元组的现象，说明不存在对应的连接依赖",
            "5NF 是规范化的最高级别，但实际中很少需要",
        ],
        "teaching_tip": "这个案例有点抽象。建议用具体的3行数据在黑板上演示：先画SP/PJ/JS三个表，再让学生动手做自然连接，直观看到'凭空多出一行'。",
    },
    {
        "id": "case8",
        "title": "闭包与候选键计算 — 分步演示",
        "section": "课件 7.2.5 例7.5",
        "tags": ["属性闭包", "候选键", "计算演示", "基础"],
        "scenario": (
            "设有属性集 U={A,B,C,D,E,F}，函数依赖集 F={A→B, B→C, C→D, CD→E, E→F}。"
            "通过计算属性闭包来判断超键和候选键。这是规范化理论中最基础也最重要的计算技能。"
        ),
        "relation": "R(A, B, C, D, E, F)",
        "attributes": ["A", "B", "C", "D", "E", "F"],
        "fds": [
            ["A", "B"],
            ["B", "C"],
            ["C", "D"],
            ["CD", "E"],
            ["E", "F"],
        ],
        "candidate_keys": [["A"]],
        "highest_nf": "BCNF",
        "key_points": [
            "A⁺ = {A,B,C,D,E,F} = U，所以 A 是超键，进而也是候选键",
            "B⁺ = {B,C,D,E,F} ≠ U，B 不是超键",
            "闭包计算的核心：反复扫描 F，找到左部已在当前闭包中的依赖",
            "闭包收敛后不再变化，算法终止",
        ],
        "teaching_tip": "闭包计算最容易出错的地方是漏掉可以触发的依赖。建议让学生用纸笔一步步写，每步只加一个属性。",
    },
    {
        "id": "case9",
        "title": "最小依赖集计算 — 三步法演示",
        "section": "课件 7.2.6 例7.6",
        "tags": ["最小依赖集", "冗余消除", "计算演示", "基础"],
        "scenario": (
            "给定 FD 集 F={A→BC, B→C, A→B, AB→C}。这个依赖集中有明显冗余："
            "有些依赖的右部是多属性，有些依赖可以被其他依赖推导出来，有些依赖的左部有多余属性。"
            "求最小依赖集是 3NF 分解算法的前置步骤。"
        ),
        "relation": "R(A, B, C)",
        "attributes": ["A", "B", "C"],
        "fds": [
            ["A", "BC"],
            ["B", "C"],
            ["A", "B"],
            ["AB", "C"],
        ],
        "minimal_cover": [
            ["A", "B"],
            ["B", "C"],
        ],
        "candidate_keys": [["A"]],
        "highest_nf": "BCNF",
        "key_points": [
            "第一步：右部单属性化 → {A→B, A→C, B→C, AB→C}",
            "第二步：消冗余依赖 → A→C 可被 A→B, B→C 推出，删；AB→C 可被推出，删",
            "第三步：消左部冗余属性 → 剩余的 A→B 和 B→C 左部均为单属性，不需处理",
            "最终 Fmin = {A→B, B→C}",
        ],
        "teaching_tip": "三步法每一步都有明确的检查标准。让学生先做第一步（永远是机械操作），第二步是关键也是最容易出错的。",
    },
    {
        "id": "case10",
        "title": "无损 vs 有损分解 — Chase 过程对比",
        "section": "课件 7.3.4 例7.9",
        "tags": ["无损分解", "Chase过程", "对比案例", "基础"],
        "scenario": (
            "关系模式 R(ABCD) 有两种分解方案："
            "方案一 ρ1={AB, BC, CD}，方案二 ρ2={AB, AC, AD}。"
            "其中只有一种是无损分解。通过 Chase 过程可以系统性地判断。"
        ),
        "relation": "R(A, B, C, D)",
        "attributes": ["A", "B", "C", "D"],
        "fds": [
            ["B", "A"],
            ["C", "D"],
        ],
        "candidate_keys": [["B", "C"]],
        "highest_nf": "2NF",
        "key_points": [
            "ρ1={AB, BC, CD} 是无损分解：通过 B→A 和 C→D 的 Chase，BC 行变为全 a",
            "ρ2={AB, AC, AD} 是有损分解：Chase 后没有全 a 行",
            "Chase 的本质：用函数依赖不断'填充'不确定值，最终能否还原出确定行",
            "公共属性决定其中一个子模式，可快速判断二模式分解无损",
        ],
        "teaching_tip": "Chase 过程是教学难点。建议让学生先在纸上画出表格，一行一行地看哪些值可以确定。动画效果会很大帮助。",
    },
]
